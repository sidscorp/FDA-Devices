# fda_data.py
import requests
import pandas as pd
import logging
from typing import List, Dict
from datetime import datetime, timedelta

# Constants (no changes needed)
FDA_ENDPOINTS = {
    "510k": "https://api.fda.gov/device/510k.json",
    "event": "https://api.fda.gov/device/event.json",
    "recall": "https://api.fda.gov/device/recall.json",
    "classification": "https://api.fda.gov/device/classification.json",
    "pma": "https://api.fda.gov/device/pma.json",
    "udi": "https://api.fda.gov/device/udi.json"
}

SEARCH_FIELDS = {
    "device": {
        "510k": ["device_name"],
        "event": ["device.brand_name", "device.generic_name"],
        "recall": ["product_description"],
        "classification": ["device_name"],
        "pma": ["trade_name"],
        "udi": ["brand_name", "device_description"]
    },
    "manufacturer": {
        "510k": ["applicant"],
        "event": ["manufacturer_d_name", "manufacturer_name"],
        "recall": ["recalling_firm", "manufacturer_name"],
        "pma": ["applicant"],
        "udi": ["company_name"]
    }
}

DISPLAY_COLUMNS = {
    "510K": ["k_number", "device_name", "decision_date", "decision_description", "applicant", "product_code", "clearance_type"],
    "PMA": ["pma_number", "supplement_number", "trade_name", "generic_name", "decision_date", "supplement_reason", "applicant", "product_code"],
    "CLASSIFICATION": ["device_name", "classification_name", "product_code", "device_class", "regulation_number", "medical_specialty_description"],
    "UDI": ["brand_name", "device_description", "company_name", "device_identifier", "version_or_model_number", "device_status"],
    "RECALL": ["event_date_initiated", "recalling_firm", "product_description", "recall_status", "reason_for_recall"],
    "EVENT": [
        "report_number", "event_type", "date_received", "date_of_event",
        "manufacturer_name", "product_problems", "adverse_event_flag",
        "remedial_action", "event_location", "reporter_occupation_code",
        "device.brand_name", "device.generic_name", "device.device_report_product_code"
    ]
}

# --- Helper Functions ---
def setup_logging():
    """Set up basic logging configuration."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data(url: str, params: Dict) -> Dict | None:
    """Fetch data from the given URL with the specified parameters."""
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.error(f"Request to {url} timed out")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to {url} failed: {e}")
        return None
    except ValueError as e:
        logging.error(f"Invalid JSON response from {url}: {e}")
        return None

def process_results(data: Dict, source: str) -> pd.DataFrame:
    """Process the API results and return a DataFrame."""

    if not data or 'results' not in data:
        return pd.DataFrame()

    df = pd.json_normalize(data['results'], sep='.')
    if source.lower() != "event" and 'results' in data:
        for i, row in enumerate(data['results']):
            if 'openfda' in row:
                for key in ['device_class', 'regulation_number', 'medical_specialty_description']:
                    if key in row['openfda']:
                        df.at[i, f'openfda.{key}'] = row['openfda'][key]

    if source.upper() == "EVENT":
        df = process_event_data(df, data['results'])

    df = add_missing_columns(df, source)
    return df

def process_event_data(df: pd.DataFrame, results: List[Dict]) -> pd.DataFrame:
    """Process the nested event data structure."""

    for result_idx, result in enumerate(results):
        # Extract device data
        if 'device' in result and result['device']:
            for device_field in ['brand_name', 'generic_name', 'device_report_product_code']:
                if device_field in result['device'][0]:
                    df.at[result_idx, f'device.{device_field}'] = result['device'][0][device_field]
        if 'openfda' in result:
            for key in ['device_class', 'regulation_number', 'medical_specialty_description']:
                if key in result['openfda']:
                    df.at[result_idx, f'openfda.{key}'] = result['openfda'][key]


        # Extract patient outcome
        if 'patient' in result and result['patient'] and len(result['patient']) > 0:
            if 'sequence_number_outcome' in result['patient'][0] and result['patient'][0]['sequence_number_outcome']:
                df.at[result_idx, 'patient.outcome'] = result['patient'][0]['sequence_number_outcome'][0]

        # Extract remedial action
        if 'remedial_action' in result and result['remedial_action'] and len(result['remedial_action']) > 0:
            df.at[result_idx, 'remedial_action'] = result['remedial_action'][0]
    return df

def add_missing_columns(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Ensure all expected columns exist in the dataframe."""

    expected_cols = DISPLAY_COLUMNS.get(source.upper(), [])
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    return df

def search_fda(query: str, category: str, source: str, limit: int = 100) -> pd.DataFrame:
    """Search FDA database for a specific category and source."""

    results_df = pd.DataFrame()
    url = FDA_ENDPOINTS.get(source.lower())
    if not url:
        logging.warning(f"Invalid source: {source}")
        return results_df

    formatted_query = query.strip().replace(" ", "+")
    if len(formatted_query) > 3 and "*" not in formatted_query and '"' not in formatted_query:
        formatted_query = f"{formatted_query}*"

    search_fields = SEARCH_FIELDS.get(category, {}).get(source.lower(), [])

    params = {"search": f"({' OR '.join([f'{f}:{formatted_query}' for f in search_fields])})", "limit": limit}
    if source.lower() in ["event", "recall", "pma", "510k"]:
        date_field = None
        if source.lower() == 'recall':
            date_field = 'event_date_initiated'
        elif source.lower() == 'event':
            date_field = 'date_received'
        elif source.lower() == 'pma' or source.lower() == '510k':
            date_field = 'decision_date'
        if date_field:
            params["sort"] = f"{date_field}:desc"

    data = fetch_data(url, params)
    if data:
        df = process_results(data, source)
        if not df.empty:
            results_df = pd.concat([results_df, df], ignore_index=True)  # Accumulate results
    else:
        logging.warning(f"No results found for {source.upper()} with fields {search_fields} and query '{query}'")
    return results_df

def filter_by_date(df: pd.DataFrame, source: str, months: int = 6) -> pd.DataFrame:
    """Filter DataFrame to include only records from the last N months."""
    date_field = None
    if source.upper() == 'RECALL':
        date_field = 'event_date_initiated'
    elif source.upper() == 'EVENT':
        date_field = 'date_received'
    elif source.upper() == 'PMA' or source.upper() == '510K':
        date_field = 'decision_date'

    if date_field and date_field in df.columns:
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        df[date_field] = pd.to_datetime(df[date_field], errors='coerce')
        df_filtered = df[df[date_field] >= cutoff_date]
        return df_filtered
    return df

def get_fda_data(query: str, query_type: str, limit: int = 100, date_months: int = 6) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Main function to get all FDA data for a query.
    Returns a dictionary with device and manufacturer views, filtered by date.
    """

    results: Dict[str, Dict[str, pd.DataFrame]] = {"device": {}, "manufacturer": {}}
    setup_logging()  # Initialize logging
    fei_numbers = set()
    if query_type == "manufacturer":
        fei_df = search_fda(query, "manufacturer", "registrationlisting", limit=1000)
        if "registration.registration_number" in fei_df.columns:
            fei_numbers.update(fei_df["registration.registration_number"].dropna().astype(str).unique())
        if "openfda.fei_number" in fei_df.columns:
            flat = fei_df["openfda.fei_number"].dropna().explode()
            fei_numbers.update(flat.astype(str).unique())
    # Determine which categories to search based on query_type
    categories_to_search = [query_type] if query_type in SEARCH_FIELDS else list(SEARCH_FIELDS.keys())

    for category in categories_to_search:
        for source in SEARCH_FIELDS[category]:
            df = search_fda(query, category, source, limit)
            if query_type == "manufacturer" and not df.empty and fei_numbers and "firm_fei_number" in df.columns:
                df = df[df["firm_fei_number"].astype(str).isin(fei_numbers)]

            if not df.empty:
                if source.upper() in ["RECALL", "EVENT", "PMA", "510K"]:
                    df = filter_by_date(df, source, date_months)
                results[category][source.upper()] = df

    return results

def fetch_count_trends(field: str, query: str, source: str, date_field: str = "date_received") -> pd.DataFrame:
    url = FDA_ENDPOINTS.get(source.lower())
    if not url:
        return pd.DataFrame()
    formatted_query = "+".join(query.split())
    params = {
        "search": f"{field}:{formatted_query}",
        "count": f"{date_field}"
    }
    data = fetch_data(url, params)
    if not data or 'results' not in data:
        return pd.DataFrame()
    return pd.DataFrame(data['results'])
