import requests
import json
import posixpath
from typing import List, Dict
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_cik(ticker: str, headers: dict) -> List[str]:
    url = f'https://efts.sec.gov/LATEST/search-index?keysTyped={ticker}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Status code while fetching CIK number for '{ticker}'")

    data = response.json()
    if data['hits']['total']['value'] == 0:
        raise ValueError(f"No CIK number associated with ticker '{ticker}'")
    
    return [hit['_id'] for hit in data['hits']['hits']]

def format_cik(cik: str) -> str:
    padding = 10 - len(cik)
    return 'CIK' + '0' * padding + cik

def fetch_sec_data(cik_full: str, headers: dict) -> Dict:
    sec_register_url = f'https://data.sec.gov/submissions/{cik_full}.json'
    sec_register = requests.get(sec_register_url, headers=headers)
    if sec_register.status_code != 200:
        raise ValueError(f"Failed to fetch SEC data for CIK '{cik_full}' with status code {sec_register.status_code}")
    return sec_register.json()

def parse_sec_data(data: Dict, cik: str) -> Dict:
    recent = data['filings']['recent']
    result = {form_type: {} for form_type in ['4', '8-K', '10-Q', '10-K', '11-K', 'ARS']}
    form_types: List[str] = recent['form']
    id_base: List[str] = recent['accessionNumber']
    dates: List[str] = recent['reportDate']
    id_end: List[str] = recent['primaryDocument']

    base_url = 'https://www.sec.gov/Archives/edgar/data/'
    
    for index, form_type in enumerate(form_types):
        if form_type in result:
            form_url = posixpath.join(base_url, cik, id_base[index].replace('-', ''), id_end[index])
            date = datetime.strptime(dates[index], '%Y-%m-%d').strftime('%d/%m/%Y')
            if date not in result[form_type]:
                result[form_type][date] = []
            result[form_type][date].append(form_url)
    
    return result

def save_to_file(data: Dict, filename: str):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    symbol = 'MMM'
    cik = get_cik(symbol, HEADERS)[0]
    cik_full = format_cik(cik)
    sec_data = fetch_sec_data(cik_full, HEADERS)
    parsed_data = parse_sec_data(sec_data, cik)
    save_to_file(parsed_data, f'{symbol}_sec_urls.json')

if __name__ == "__main__":
    main()