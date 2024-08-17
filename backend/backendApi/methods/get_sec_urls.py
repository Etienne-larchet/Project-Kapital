import posixpath
from datetime import datetime
from typing import Dict, List, Literal, Optional

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class SECDataError(Exception):
    pass


def get_cik(ticker: str, headers: dict) -> str:
    url = f"https://efts.sec.gov/LATEST/search-index?keysTyped={ticker}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SECDataError(f"Error getting CIK number for '{ticker}': {e}")

    try:
        data = response.json()
        if data["hits"]["total"]["value"] == 0:
            raise SECDataError(f"No CIK number associated with ticker '{ticker}'")
        return data["hits"]["hits"][0]["_id"]
    except (ValueError, KeyError) as e:
        raise SECDataError(f"Error parsing CIK response for '{ticker}': {e}")


def format_cik(cik: str) -> str:
    if not cik.isdigit() or len(cik) > 10:
        raise SECDataError(f"Invalid CIK format: '{cik}'")
    padding = 10 - len(cik)
    return "CIK" + "0" * padding + cik


def fetch_sec_data(cik_full: str, headers: dict) -> Dict:
    sec_register_url = f"https://data.sec.gov/submissions/{cik_full}.json"
    try:
        sec_register = requests.get(sec_register_url, headers=headers, timeout=10)
        sec_register.raise_for_status()
        return sec_register.json()
    except requests.RequestException as e:
        raise SECDataError(f"Error fetching SEC data for CIK '{cik_full}': {e}")
    except ValueError as e:
        raise SECDataError(f"Error parsing SEC data for CIK '{cik_full}': {e}")


def parse_sec_data(data: Dict, cik: str) -> Dict:
    try:
        recent = data["filings"]["recent"]
        result = {
            form_type: {} for form_type in ["4", "8-K", "10-Q", "10-K", "11-K", "ARS"]
        }
        form_types: List[str] = recent["form"]
        id_base: List[str] = recent["accessionNumber"]
        dates: List[str] = recent["reportDate"]
        id_end: List[str] = recent["primaryDocument"]
        base_url = "https://www.sec.gov/Archives/edgar/data/"

        for index, form_type in enumerate(form_types):
            if form_type in result:
                form_url = posixpath.join(
                    base_url, cik, id_base[index].replace("-", ""), id_end[index]
                )
                date = datetime.strptime(dates[index], "%Y-%m-%d").strftime("%d/%m/%Y")
                if date not in result[form_type]:
                    result[form_type][date] = []
                result[form_type][date].append(form_url)

        return result
    except (KeyError, ValueError, IndexError) as e:
        raise SECDataError(f"Error parsing SEC filings data: {e}")


def get_sec_urls(
    ticker: str,
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    formType: Optional[Literal["4", "8k", "10q", "10k", "11k", "ars"]] = None,
) -> dict:

    cik = get_cik(ticker, HEADERS)
    cik_full = format_cik(cik)
    sec_data = fetch_sec_data(cik_full, HEADERS)
    parsed_data = parse_sec_data(sec_data, cik)
    return parsed_data


if __name__ == "__main__":
    from pprint import pprint

    result = get_sec_urls("MMM")
    pprint(result)
