import requests
import pdfplumber
from bs4 import BeautifulSoup
import re
from app.database.connection import get_db_cursor

# Constants
BASE_URL_2025 = "https://www.fia.com/events/fia-formula-one-world-championship/season-2025/2025-fia-formula-one-world-championship"

def get_pdf_urls(year):
    """Get PDF URLs for the specified year."""
    return {
        'race': f"https://www.fia.com/system/files/decision-document/{year}_{{}}_grand_prix_-_final_race_classification.pdf",
        'provisional': f"https://www.fia.com/system/files/decision-document/{year}_{{}}_grand_prix_-_provisional_race_classification.pdf",
        'quali': f"https://www.fia.com/system/files/decision-document/{year}_{{}}_grand_prix_-_final_starting_grid.pdf"
    }

def get_available_races(year=2025):
    """Fetch available race names from the FIA website for the specified year."""
    try:
        base_url = f"https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-{year}-2071"
        print(f"Fetching races for year {year} from URL: {base_url}")  # Debug log
        
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find the select element with id 'facetapi_select_facet_form_2'
        select = soup.find('select', {'id': 'facetapi_select_facet_form_2'})
        
        if not select:
            print("Select element not found")  # Debug log
            return []
            
        # Get all option elements except the first one (which is the "Event" placeholder)
        options = select.find_all('option')[1:]
        
        # Extract race names and filter out non-Grand Prix events
        event_names = []
        for option in options:
            race_name = option.text.strip()
            if "Grand Prix" in race_name and "Tests" not in race_name:
                event_names.append(race_name)
        
        print(f"Found {len(event_names)} races for year {year}")  # Debug log
        return event_names

    except requests.RequestException as e:
        print(f"An error occurred while fetching data for year {year}: {e}")
        return []

def download_pdf(url, grand_prix_name=None, year=2025):
    """Download a PDF from a given URL and return the file path."""
    response = requests.get(url)
    if response.status_code == 200:
        pdf_path = "tmp/race_classification.pdf"
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

def get_results(grand_prix_name, isRace, year=2025):
    """Fetch race results for a given Grand Prix."""
    urls = get_pdf_urls(year)
    formatted_name = grand_prix_name.lower().replace(' grand prix', '').strip().replace(' ', '_')
    
    if isRace:
        pdf_url = urls['race'].format(formatted_name)
    else:
        pdf_url = urls['quali'].format(formatted_name)
    
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
    current_position = 1
    
    print("Raw qualifying lines:")  # Debug log
    for line in lines:
        print(f"Line: {line}")  # Debug log
    
    # Find the line that starts with "Final Starting Grid"
    start_processing = False
    for i, line in enumerate(lines):
        if "Final Starting Grid" in line:
            start_processing = True
            continue
        
        if not start_processing:
            continue
            
        line = line.strip()
        # Look for lines containing position, number and driver name
        # Format: "1 81 Oscar PIASTRI 1:29.841"
        if re.search(rf"^{current_position}\s+\d{{1,2}}\s+[A-Za-z]+\s+[A-Z]+", line):
            try:
                # Split by the time at the end if present
                parts = re.split(r'\s+\d:\d{2}\.\d{3}', line)[0]
                # Split remaining parts
                parts = parts.split()
                if len(parts) >= 4:  # position, number, firstname, lastname
                    # Get driver name (everything after position and number)
                    driver_name = " ".join(parts[2:])
                    # Remove any asterisk
                    driver_name = driver_name.replace('*', '').strip()
                    
                    results.append(f"{current_position} {driver_name}")
                    print(f"Found qualifying result: Position {current_position} - {driver_name}")  # Debug log
                    current_position += 1
            except Exception as e:
                print(f"Error processing line: {line}, Error: {e}")  # Debug log
        # Also check for driver names at the start of team lines
        # Format: "McLaren Formula 1 Team 2 16 Charles LECLERC 1:30.175"
        elif re.search(r'\d{1,2}\s+\d{1,2}\s+[A-Za-z]+\s+[A-Z]+', line):
            try:
                # Find the driver portion (after team name)
                match = re.search(r'(\d{1,2})\s+\d{1,2}\s+([A-Za-z]+\s+[A-Z]+)', line)
                if match:
                    position = int(match.group(1))
                    driver_name = match.group(2)
                    # Remove any asterisk
                    driver_name = driver_name.replace('*', '').strip()
                    
                    if position == current_position:
                        results.append(f"{position} {driver_name}")
                        print(f"Found qualifying result: Position {position} - {driver_name}")  # Debug log
                        current_position += 1
            except Exception as e:
                print(f"Error processing line: {line}, Error: {e}")  # Debug log
    
    # Sort results by the position number
    results.sort(key=lambda x: int(x.split()[0]))
    # Remove the position numbers after sorting
    results = [" ".join(r.split()[1:]) for r in results]
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
    
    print(f"Input results for matching: {results}")  # Debug log
    print(f"Available driver names: {driver_names}")  # Debug log
    
    for result in results:
        result = result.strip()
        # Try to find the best matching driver name
        best_match = None
        for driver in driver_names:
            # Convert both to lowercase and remove spaces for comparison
            driver_clean = driver.lower().replace(" ", "")
            result_clean = result.lower().replace(" ", "")
            
            # Check if driver name is in the result
            if driver_clean in result_clean:
                if best_match is None or len(driver) > len(best_match):
                    best_match = driver
        
        if best_match:
            final_results.append(best_match)
            print(f"Matched {result} to driver {best_match}")  # Debug log
        else:
            # If no match found, use the result as is
            final_results.append(result)
            print(f"No match found for {result}, using as is")  # Debug log
    
    print(f"Final ordered results: {final_results}")  # Debug log
    return final_results

def get_final_race_results(track_name, year=2025):
    results = get_results(track_name, True, year)
    if results:
        driver_names = fetch_driver_names()
        final_results = match_driver_names(results[0], driver_names)
        dnfs = match_driver_names(results[1], driver_names)
        fastest_lap = match_driver_names([results[2]], driver_names)[0]
        return final_results, dnfs, fastest_lap
    return [], [], None

def get_final_quali_results(track_name, year=2025):
    results = get_results(track_name, False, year)
    if results:
        driver_names = fetch_driver_names()
        final_results = match_driver_names(results[0], driver_names)
        dnfs = []
        fastest_lap = None
        return final_results, dnfs, fastest_lap
    return [], [], None 