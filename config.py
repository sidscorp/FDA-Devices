QUERY_LIMIT = 100
CACHE_TTL = 3600

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

DEFAULT_SAMPLE_SIZE = 20
DEFAULT_DATE_MONTHS = 6
SAMPLE_SIZE_OPTIONS = [20, 50, 100]
DATE_RANGE_OPTIONS = [3, 6, 12]