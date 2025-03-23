import requests
import pandas as pd

# Constants
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
    "PMA": ["pma_number", "supplement_number", "trade_name", "generic_name", "decision_date","supplement_reason", "applicant", "product_code"],
    "CLASSIFICATION": ["device_name", "classification_name", "product_code", "device_class", "regulation_number", "medical_specialty_description"],
    "UDI": ["brand_name", "device_description", "company_name", "device_identifier", "version_or_model_number", "device_status"],
    "RECALL": ["event_date_initiated", "recalling_firm", "product_description", "recall_classification", "reason_for_recall"],
    "EVENT": [
        "report_number", "event_type", "date_received", "date_of_event",
        "manufacturer_name", "product_problems", "adverse_event_flag",
        "remedial_action", "event_location", "reporter_occupation_code",
        "device.brand_name", "device.generic_name", "device.device_report_product_code"
    ]
}

def search_fda(query, category, source, limit=100):
    """
    Search FDA database for a specific category and source
    """
    results_df = pd.DataFrame()
    url = FDA_ENDPOINTS.get(source.lower())
    if not url:
        return results_df
        
    for field in SEARCH_FIELDS[category][source.lower()]:
        try:
            params = {"search": f"{field}:{query}", "limit": limit}
            if source.lower() != "recall":
                params["sort"] = "date_received:desc"
                
            res = requests.get(url, params=params)
            res.raise_for_status()
            data = res.json()
            
            if 'results' in data and data['results']:
                df = pd.json_normalize(data['results'], sep='.')
                
                # Special handling for EVENT data
                if source.upper() == "EVENT":
                    process_event_data(df, data['results'])
                
                # Ensure all expected columns exist
                add_missing_columns(df, source)
                
                return df
                
        except Exception as e:
            print(f"Error querying {source.upper()} with field {field}: {e}")
            continue
            
    return results_df

def process_event_data(df, results):
    """Process the nested event data structure"""
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

def add_missing_columns(df, source):
    """Ensure all expected columns exist in the dataframe"""
    expected_cols = DISPLAY_COLUMNS.get(source.upper(), [])
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

def get_fda_data(query, limit=100):
    """
    Main function to get all FDA data for a query
    Returns a dictionary with device and manufacturer views
    """
    results = {"device": {}, "manufacturer": {}}
    
    for category in SEARCH_FIELDS:
        for source in SEARCH_FIELDS[category]:
            df = search_fda(query, category, source, limit)
            if not df.empty:
                results[category][source.upper()] = df
                
    return results