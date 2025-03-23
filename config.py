QUERY_LIMIT = 100
CACHE_TTL = 3600

DISPLAY_COLUMNS = {
    "510K": ["k_number", "device_name", "applicant", "decision_date"],
    "PMA": ["pma_number", "device_name", "applicant", "decision_date"],
    "CLASSIFICATION": ["product_code", "device_class", "classification_name"],
    "UDI": ["device_identifier", "device_name", "company_name"],
    "EVENT": [ "event_type", "date_received", "date_of_event","manufacturer_name", "product_problems", "device.brand_name", "device.generic_name", "device.device_report_product_code"],
    "RECALL": ["event_date_initiated", "recalling_firm", "product_description", "recall_classification", "reason_for_recall"]
}