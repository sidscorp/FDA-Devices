import json
import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from dotenv import load_dotenv
from fda_data import DISPLAY_COLUMNS

def prepare_data_for_llm(df, source_type):
    if df.empty:
        return {}

    essential_fields = {
        "510K": ["k_number", "device_name", "decision_date", "applicant"],
        "PMA": ["pma_number", "trade_name", "decision_date", "applicant"],
        "CLASSIFICATION": ["device_name", "device_class", "medical_specialty_description"],
        "UDI": ["brand_name", "device_description", "company_name"],
        "RECALL": ["event_date_initiated", "recalling_firm", "product_description", "recall_classification", "reason_for_recall"],
        "EVENT": ["date_received", "manufacturer_name", "product_problems", "device.brand_name", "device.generic_name"]
    }

    fields = essential_fields.get(source_type, df.columns.tolist())
    available_fields = [field for field in fields if field in df.columns]
    df_sample = df.head(10 if source_type in ["RECALL", "EVENT"] else 20).copy()
    df_sample = df_sample[available_fields]

    for col in df_sample.columns:
        if pd.api.types.is_datetime64_any_dtype(df_sample[col]):
            df_sample[col] = df_sample[col].dt.strftime('%Y-%m-%d')

    records = df_sample.to_dict(orient='records')

    date_col = next((col for col in ["date_received", "decision_date", "event_date_initiated"] if col in df.columns), None)
    earliest = pd.to_datetime(df[date_col]).min().strftime('%Y-%m-%d') if date_col else "N/A"
    latest = pd.to_datetime(df[date_col]).max().strftime('%Y-%m-%d') if date_col else "N/A"

    return {
        "source_type": source_type,
        "num_total_records_in_source": len(df),
        "num_sample_records_analyzed": len(records),
        "sample_records": records,
        "approx_date_range_in_source": f"{earliest} to {latest}"
    }

def create_structured_system_prompt(query_type, section_name, is_simple):
    if is_simple:
        return f"You are an assistant listing classification or UDI records. Identify common device types, companies, and classifications for this {query_type}."
    return f"""You are a helpful assistant analyzing FDA data. First verify if the query appears in the data. If not, say: 'No specific data for [query] was found in this data sample.'

MAIN OBSERVATION:
[Key finding]

WHAT THIS MIGHT MEAN:
[Interpretation]

OTHER DETAILS:
[Secondary patterns]

IMPORTANT NOTE:
This is based only on a small sample of recent records."""

def generate_llm_prompt(data_json, source_type, query, query_type, is_simple, section_results=None):
    prompt = f"""Analyze the following sample related to '{query}' ({source_type} - {query_type}):
Total Records: {data_json['num_total_records_in_source']}
Analyzed: {data_json['num_sample_records_analyzed']}
Date Range: {data_json['approx_date_range_in_source']}

Sample Records:
{json.dumps(data_json['sample_records'], indent=2)}"""

    if section_results and not is_simple:
        context = "\n".join([f"* {k}: {v.split('.')[0]}" for k, v in section_results.items() if "No specific" not in v])
        if context:
            prompt += f"\n\nContext from earlier sections:\n{context}"
    return prompt

def run_llm_analysis(df, source_type, query, query_type="device", custom_prompt=None, section_results=None):
    try:
        if not hasattr(genai, 'configured') or not genai.configured:
            load_dotenv()
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                return "AI analysis unavailable: API key not configured."

        is_simple = source_type in ["UDI", "CLASSIFICATION"]

        if custom_prompt:
            prompt = custom_prompt
        elif df.empty:
            return f"No data provided for {source_type} analysis."
        else:
            data_json = prepare_data_for_llm(df, source_type)
            if not data_json.get("sample_records"):
                return f"No specific data found for '{query}' in this section's sample."

            system = create_structured_system_prompt(query_type, source_type, is_simple)
            prompt = f"{system}\n\n{generate_llm_prompt(data_json, source_type, query, query_type, is_simple, section_results)}"

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        if not response.parts:
            return "AI analysis could not be completed."
        return response.text.strip()
    except Exception as e:
        return f"LLM error: {str(e)}"

def format_llm_summary(summary):
    headers = ["MAIN OBSERVATION:", "WHAT THIS MIGHT MEAN:", "OTHER DETAILS:", "IMPORTANT NOTE:"]
    for header in headers:
        summary = summary.replace(header, f"**{header}**")
    summary = '\n\n'.join([line.strip() for line in summary.split('\n') if line.strip()])
    if "No specific data" in summary:
        return f"*{summary}*"
    return summary

def display_section_with_ai_summary(title, df, source, query, query_type):
    st.subheader(title)
    if df.empty:
        st.info(f"No data found for {title}.")
        st.session_state.section_results[source] = f"No data provided for {source}."
        return

    with st.spinner(f"Analyzing {source} data..."):
        summary = run_llm_analysis(
            df, source, query, query_type, section_results=st.session_state.get('section_results', {})
        )
        st.session_state.section_results[source] = summary

    formatted_summary = format_llm_summary(summary)
    if "No specific data" in summary or "AI analysis unavailable" in summary or "error" in summary.lower():
        st.warning(formatted_summary)
    else:
        st.markdown(formatted_summary)

    with st.expander("View Detailed Data Sample"):
        cols_to_display = DISPLAY_COLUMNS.get(source, df.columns.tolist())
        filtered_cols = [col for col in cols_to_display if col in df.columns]
        st.dataframe(df[filtered_cols])
