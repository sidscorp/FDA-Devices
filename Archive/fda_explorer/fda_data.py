import pandas as pd
import random

def get_fda_data(query, limit=100):
    return {
        "device": {
            "510K": sample_df("510K", limit),
            "PMA": sample_df("PMA", limit),
            "CLASSIFICATION": sample_df("CLASSIFICATION", limit),
            "UDI": sample_df("UDI", limit),
            "EVENT": sample_df("EVENT", limit),
            "RECALL": sample_df("RECALL", limit),
        },
        "manufacturer": {
            "RECALL": sample_df("RECALL", limit),
            "EVENT": sample_df("EVENT", limit),
            "510K": sample_df("510K", limit),
            "PMA": sample_df("PMA", limit),
            "UDI": sample_df("UDI", limit),
        }
    }

def sample_df(source, limit):
    cols = {
        "510K": ["k_number", "device_name", "applicant", "decision_date"],
        "PMA": ["pma_number", "device_name", "applicant", "decision_date"],
        "CLASSIFICATION": ["product_code", "device_class", "classification_name"],
        "UDI": ["device_identifier", "device_name", "company_name"],
        "EVENT": ["event_type", "date_received", "device_name"],
        "RECALL": ["recall_number", "reason", "status", "recalling_firm"]
    }
    data = {col: [f"{col}_{random.randint(1, 1000)}" for _ in range(limit)] for col in cols[source]}
    return pd.DataFrame(data)