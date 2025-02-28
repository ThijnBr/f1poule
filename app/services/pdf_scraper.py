import requests
import pdfplumber
from bs4 import BeautifulSoup
import re
from app.database.connection import get_db_cursor

# Constants
BASE_URL = "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season/season-2024-2043"
PDF_BASE_URL = "https://fia.com/sites/default/files/decision-document/2024%20{}%20-%20Final%20Race%20Classification.pdf"
PDF_PROVISIONAL = "https://fia.com/sites/default/files/decision-document/2024%20{}%20-%20Provisional%20Race%20Classification.pdf"
PDF_BASE_QUALI_URL = "https://fia.com/sites/default/files/decision-document/2024%20{}%20-%20Final%20Starting%20Grid.pdf"

def get_available_races():
    """Fetch available race names from the FIA website."""
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")
        select_element = soup.find('select', {'id': 'facetapi_select_facet_form_2'})

        if select_element is None:
            print("Select element not found.")
            return []

        # Extract event names from the dropdown options
        event_names = [option.text.strip() for option in select_element.find_all('option') if "Grand Prix" in option.text]
        return event_names

    except requests.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return []

def download_pdf(url, grand_prix_name=None):
    """Download a PDF from a given URL and return the file path."""
    response = requests.get(url)
    if response.status_code == 200:
        pdf_path = "race_classification.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        return pdf_path
    elif grand_prix_name != None:
        print(f"Failed to download the PDF from {url}")
        pdf_url = PDF_PROVISIONAL.format(grand_prix_name.replace(' ', '%20'))
        return download_pdf(pdf_url)
    return None


def extract_text_from_pdf(pdf_path):
    """Extract text from the given PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)


def get_results(grand_prix_name, isRace):
    """Fetch race results for a given Grand Prix."""
    if isRace:
        pdf_url = PDF_BASE_URL.format(grand_prix_name.replace(' ', '%20'))
    else:
        pdf_url = PDF_BASE_QUALI_URL.format(grand_prix_name.replace(' ', '%20'))
    pdf_path = download_pdf(pdf_url, grand_prix_name)
    
    if pdf_path:
        results = extract_text_from_pdf(pdf_path)
        if isRace:
            return process_race_results(results)
        else:
            return process_quali_results(results)
    return None

def process_quali_results(quali_results):
    lines = quali_results.splitlines()
    gather_data = False
    driver = True
    results = []
    for i, line in enumerate(lines):   
        if re.search('\d+\s+\d', line):
            results.append(line)
    return results, None, None

def process_race_results(race_results):
    get_results = False
    results = []
    dnfs = []
    fastest_lap = None

    lines = race_results.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if "NO DRIVER" in line:
            get_results = True
        if get_results:
            if "DNF" in line:
                dnfs.append(line)
            elif "FASTEST LAP" in line:
                fastest_lap = lines[i+1]
                print(fastest_lap)
                get_results = False
            else:
                if not ("NO DRIVER" in line or "NOT CLASSIFIED" in line or "FASTEST LAP ELIGIBLE" in line):
                    results.append(line)

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
    for result in results:
        matched = next((driver for driver in driver_names if driver.lower() in result.lower()), result)
        final_results.append(matched)
    return final_results

def get_final_race_results(track_name):
    results = get_results(track_name, True)
    if results:
        driver_names = fetch_driver_names()
        final_results = match_driver_names(results[0], driver_names)
        dnfs = match_driver_names(results[1], driver_names)
        fastest_lap = match_driver_names([results[2]], driver_names)[0]
        return final_results, dnfs, fastest_lap
    return [], [], None

def get_final_quali_results(track_name):
    results = get_results(track_name, False)
    if results:
        driver_names = fetch_driver_names()
        final_results = match_driver_names(results[0], driver_names)
        dnfs = []
        fastest_lap = None
        return final_results, dnfs, fastest_lap
    return [], [], None 