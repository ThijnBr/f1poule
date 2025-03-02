import requests
import pdfplumber
from bs4 import BeautifulSoup
import re
from app.database.connection import get_db_cursor

# Constants
BASE_URL_2024 = "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season/season-2024-2043"
BASE_URL_2025 = "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season/season-2025-2071"

def get_pdf_urls(year):
    """Get PDF URLs for the specified year."""
    return {
        'race': f"https://fia.com/sites/default/files/decision-document/{year}%20{{}}%20-%20Final%20Race%20Classification.pdf",
        'provisional': f"https://fia.com/sites/default/files/decision-document/{year}%20{{}}%20-%20Provisional%20Race%20Classification.pdf",
        'quali': f"https://fia.com/sites/default/files/decision-document/{year}%20{{}}%20-%20Final%20Starting%20Grid.pdf"
    }

def get_available_races(year=2024):
    """Fetch available race names from the FIA website for the specified year."""
    try:
        # Select the correct base URL based on the year
        base_url = BASE_URL_2024 if year == 2024 else BASE_URL_2025
        print(f"Fetching races for year {year} from URL: {base_url}")  # Debug log
        
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")
        select_element = soup.find('select', {'id': 'facetapi_select_facet_form_2'})

        if select_element is None:
            print(f"Select element not found for year {year}")
            return []

        # Extract event names from the dropdown options
        event_names = [option.text.strip() for option in select_element.find_all('option') if "Grand Prix" in option.text]
        print(f"Found {len(event_names)} races for year {year}")  # Debug log
        return event_names

    except requests.RequestException as e:
        print(f"An error occurred while fetching data for year {year}: {e}")
        return []

def download_pdf(url, grand_prix_name=None, year=2024):
    """Download a PDF from a given URL and return the file path."""
    response = requests.get(url)
    if response.status_code == 200:
        pdf_path = "race_classification.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        return pdf_path
    elif grand_prix_name != None:
        print(f"Failed to download the PDF from {url}")
        urls = get_pdf_urls(year)
        pdf_url = urls['provisional'].format(grand_prix_name.replace(' ', '%20'))
        return download_pdf(pdf_url)
    return None

def extract_text_from_pdf(pdf_path):
    """Extract text from the given PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def get_results(grand_prix_name, isRace, year=2024):
    """Fetch race results for a given Grand Prix."""
    urls = get_pdf_urls(year)
    if isRace:
        pdf_url = urls['race'].format(grand_prix_name.replace(' ', '%20'))
    else:
        pdf_url = urls['quali'].format(grand_prix_name.replace(' ', '%20'))
    pdf_path = download_pdf(pdf_url, grand_prix_name, year)
    
    if pdf_path:
        results = extract_text_from_pdf(pdf_path)
        if isRace:
            return process_race_results(results)
        else:
            return process_quali_results(results)
    return None

def process_quali_results(quali_results):
    """Process qualifying results from PDF text."""
    lines = quali_results.splitlines()
    results = []
    
    for line in lines:
        # Look for lines that start with a position number (1-20) followed by a number (usually car number)
        if re.match(r'^\s*\d{1,2}\s+\d', line.strip()):
            # Keep the full line to preserve position information
            results.append(line.strip())
            print(f"Found qualifying result: {line.strip()}")  # Debug log
    
    # Sort results by the position number at the start of each line
    results.sort(key=lambda x: int(re.match(r'^\s*(\d+)', x).group(1)))
    print(f"Sorted qualifying results: {results}")  # Debug log
    return results, None, None

def process_race_results(race_results):
    """Process race results from PDF text."""
    get_results = False
    results = []
    dnfs = []
    fastest_lap = None
    
    lines = race_results.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if "NO DRIVER" in line:
            get_results = True
            continue
            
        if get_results:
            if "DNF" in line:
                dnfs.append(line)
                print(f"Found DNF: {line}")  # Debug log
            elif "FASTEST LAP" in line and i + 1 < len(lines):
                fastest_lap = lines[i+1].strip()
                print(f"Found fastest lap: {fastest_lap}")  # Debug log
                get_results = False
            elif line and not any(skip in line for skip in ["NO DRIVER", "NOT CLASSIFIED", "FASTEST LAP ELIGIBLE"]):
                if re.match(r'^\s*\d{1,2}\s+\d', line):
                    results.append(line)
                    print(f"Found race result: {line}")  # Debug log
    
    # Sort results by the position number at the start of each line
    results.sort(key=lambda x: int(re.match(r'^\s*(\d+)', x).group(1)))
    print(f"Sorted race results: {results}")  # Debug log
    return results, dnfs, fastest_lap


def fetch_driver_names():
    """Fetch the list of driver names from the database."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT driver_name FROM driver")
        query_results = cursor.fetchall()
        return [driver_name[0] for driver_name in query_results]


def match_driver_names(results, driver_names):
    """Match results with driver names and return a final list."""
    final_results = []
    position_map = {}  # Store position-to-driver mapping
    
    print(f"Input results for matching: {results}")  # Debug log
    print(f"Available driver names: {driver_names}")  # Debug log
    
    # First pass: extract positions and create position map
    for result in results:
        # Extract position number from the start of the line
        position_match = re.match(r'^\s*(\d+)', result)
        if position_match:
            position = int(position_match.group(1))
            # Find matching driver name
            matched_driver = None
            result_lower = result.lower()
            for driver in driver_names:
                if driver.lower() in result_lower:
                    matched_driver = driver
                    break
            
            if matched_driver:
                position_map[position] = matched_driver
                print(f"Matched position {position} to driver {matched_driver}")  # Debug log
            else:
                position_map[position] = result
                print(f"No match found for position {position}, using original: {result}")  # Debug log
    
    # Second pass: create ordered list based on positions
    for pos in sorted(position_map.keys()):
        final_results.append(position_map[pos])
    
    print(f"Final ordered results: {final_results}")  # Debug log
    return final_results

def get_final_race_results(track_name, year=2024):
    results = get_results(track_name, True, year)
    if results:
        driver_names = fetch_driver_names()
        final_results = match_driver_names(results[0], driver_names)
        dnfs = match_driver_names(results[1], driver_names)
        fastest_lap = match_driver_names([results[2]], driver_names)[0]
        return final_results, dnfs, fastest_lap
    return [], [], None

def get_final_quali_results(track_name, year=2024):
    results = get_results(track_name, False, year)
    if results:
        driver_names = fetch_driver_names()
        final_results = match_driver_names(results[0], driver_names)
        dnfs = []
        fastest_lap = None
        return final_results, dnfs, fastest_lap
    return [], [], None 