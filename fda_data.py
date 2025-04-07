import requests
import pandas as pd
import logging
from typing import List, Dict

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
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to {url} failed: {e}")
        return None

def process_results(data: Dict, source: str) -> pd.DataFrame:
    """Process the API results and return a DataFrame."""

    if not data or 'results' not in data:
        return pd.DataFrame()

    df = pd.json_normalize(data['results'], sep='.')

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

def search_fda(query: str, category: str, source: str, limit: int = 20) -> pd.DataFrame:
    """Search FDA database for a specific category and source."""

    results_df = pd.DataFrame()
    url = FDA_ENDPOINTS.get(source.lower())
    if not url:
        logging.warning(f"Invalid source: {source}")
        return results_df

    formatted_query = "+".join(query.split())
    
    # Use the query_type to select the correct fields
    search_fields = SEARCH_FIELDS.get(category, {}).get(source.lower(), [])
    
    for field in search_fields:
        params = {"search": f"{field}:{formatted_query}", "limit": limit}
        if source.lower() in ["event", "recall", "pma", "510k"]:
            params["sort"] = f"{'decision_date' if source.lower() in ['pma', '510k'] else 'event_date_initiated' if source.lower() == 'recall' else 'date_received'}:desc"

        data = fetch_data(url, params)
        if data:
            df = process_results(data, source)
            if not df.empty:
                results_df = pd.concat([results_df, df], ignore_index=True)  # Accumulate results
        else:
            logging.warning(f"No results found for {source.upper()} with field {field} and query '{query}'")
    return results_df

def get_fda_data(query: str, query_type: str, limit: int = 100) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Main function to get all FDA data for a query.
    Returns a dictionary with device and manufacturer views.
    """

    results: Dict[str, Dict[str, pd.DataFrame]] = {"device": {}, "manufacturer": {}}
    setup_logging()  # Initialize logging

    # Determine which categories to search based on query_type
    categories_to_search = [query_type] if query_type in SEARCH_FIELDS else list(SEARCH_FIELDS.keys())

    for category in categories_to_search:
        for source in SEARCH_FIELDS[category]:
            df = search_fda(query, category, source, limit)
            if not df.empty:
                results[category][source.upper()] = df

    return results