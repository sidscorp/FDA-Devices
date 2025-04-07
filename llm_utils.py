# llm_utils.py (Improved Version)

import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd # Make sure pandas is imported if not already
from fda_data import DISPLAY_COLUMNS # Assuming this import is correct

# --- Data Preparation (Minor tweaks or comments if needed, largely unchanged) ---

def prepare_data_for_llm(df, source_type):
    """Convert a pandas DataFrame to structured JSON for LLM input, optimized for token efficiency"""
    if df.empty:
        return {}

    # Define essential fields per source type to reduce data volume
    # (These seem reasonable for basic insights, keeping them)
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

    if not available_fields and len(df.columns) > 0:
        available_fields = df.columns[:min(5, len(df.columns))].tolist()

    # Limit sample size (Consider if this sample size is sufficient for meaningful "patterns")
    sample_size = 5 if source_type in ["RECALL", "EVENT"] else 8
    df_sample = df.head(sample_size).copy()

    if available_fields:
        df_sample = df_sample[available_fields]

    records = df_sample.to_dict(orient='records')

    # Extract date range if possible (using a common date column if available)
    date_col = None
    if "date_received" in df.columns:
        date_col = "date_received"
    elif "decision_date" in df.columns:
         date_col = "decision_date"
    elif "event_date_initiated" in df.columns:
        date_col = "event_date_initiated"

    earliest_date = pd.to_datetime(df[date_col]).min().strftime('%Y-%m-%d') if date_col and date_col in df.columns else "N/A"
    latest_date = pd.to_datetime(df[date_col]).max().strftime('%Y-%m-%d') if date_col and date_col in df.columns else "N/A"


    data_json = {
        "source_type": source_type,
        "num_total_records_in_source": len(df), # Clarify this is total in source, not sample
        "num_sample_records_analyzed": len(records),
        "sample_records": records,
        "approx_date_range_in_source": f"{earliest_date} to {latest_date}" # Provide range if possible
    }

    return data_json

# --- Core LLM Prompting (Significant Changes) ---

def create_structured_system_prompt(query_type, section_name):
    """Create a system prompt focused on clarity for a general audience."""

    # Simplified persona and goal
    base_instructions = """You are a helpful assistant analyzing FDA data samples. Your goal is to summarize potential points of interest in simple, clear language for a non-expert audience.

    VERIFICATION STEP - REQUIRED:
    1. First, carefully check if the specific manufacturer or device name mentioned in the query is actually present in the 'sample_records' provided below.
    2. If the exact name is NOT found in the sample data, respond ONLY with: "No specific data for '[query]' was found in this data sample." (Replace [query] with the actual device/manufacturer name).
    3. DO NOT provide insights about unrelated topics if the specific query subject isn't in the data.

    If (and only if) the specific query subject IS found in the data, analyze the sample records and provide a brief summary.

    FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS (Use these headers and ensure a blank line between each section):

    MAIN OBSERVATION:
    [1-2 sentences describing the most noticeable point or activity in this data sample. Be specific and mention counts or dates if relevant and helpful.]

    WHAT THIS MIGHT MEAN:
    [1-2 sentences explaining the potential significance of the main observation in simple terms. Avoid jargon.]

    OTHER DETAILS:
    [1-2 sentences mentioning any secondary points or patterns noticed in the sample.]

    IMPORTANT NOTE:
    [1 sentence reminding the user that this analysis is based *only* on the small sample of recent records provided.]

    Keep your entire response concise (around 100-150 words total). Use clear, straightforward language suitable for anyone, regardless of their FDA knowledge."""

    # Context specific to query type (phrased more simply)
    if query_type == "manufacturer":
        context = f"For this '{section_name}' data sample, focus on recent activities related to the specified manufacturer."
    else:  # device
        context = f"For this '{section_name}' data sample, focus on recent activities related to the specified device type."

    return f"{base_instructions}\n\n{context}"

def generate_llm_prompt(data_json, source_type, query, query_type, section_results=None):
    """Generate structured prompts for LLM analysis with simplified language."""
    system_instructions = create_structured_system_prompt(query_type, source_type)

    # Simplified data descriptions
    descriptions = {
        "manufacturer": {
            "510K": "recent 510(k) submissions",
            "PMA": "recent PMA submissions",
            "EVENT": "recent adverse event reports linked to their devices",
            "RECALL": "recent product recalls initiated",
            "UDI": "recent device registrations (UDI)"
        },
        "device": {
            "510K": "recent 510(k) clearances for similar devices",
            "PMA": "recent PMA submissions for similar devices",
            "CLASSIFICATION": "regulatory classification info",
            "UDI": "device registrations (UDI)",
            "EVENT": "recent adverse event reports for this device type",
            "RECALL": "recent recalls involving this device type"
        }
    }

    description = descriptions.get(query_type, {}).get(source_type, "recent regulatory activity")

    # Construct the user part of the prompt
    prompt = f"""Please analyze the following sample data about {description} related to the {'manufacturer' if query_type == 'manufacturer' else 'device type'} '{query}'.

    Data Sample Details:
    - Total records in original source: {data_json.get('num_total_records_in_source', 'N/A')}
    - Number of records analyzed in this sample: {data_json.get('num_sample_records_analyzed', 'N/A')}
    - Approximate date range of original source: {data_json.get('approx_date_range_in_source', 'N/A')}

    Sample Records Data (JSON format):
    {json.dumps(data_json.get('sample_records', []), indent=2)}
    """

    # Add narrative continuity if available (Simplified context phrasing)
    if section_results:
        continuity_context = maintain_narrative_continuity(section_results, source_type, query, query_type)
        prompt = f"{prompt}\n\n{continuity_context}" # Add space before context

    # Combine system instructions and user prompt
    full_prompt = f"{system_instructions}\n\n{prompt}"
    # print(f"--- PROMPT for {source_type} --- \n{full_prompt}\n --- END PROMPT ---") # Optional: for debugging
    return full_prompt

def maintain_narrative_continuity(section_results, current_section, query, query_type):
    """Provide simplified context from previous sections."""
    if not section_results:
        return ""

    context_lines = []
    for section, insights in section_results.items():
        # Extract first sentence or main observation if possible (simple split for now)
        first_sentence = insights.split('.')[0].split('\n')[0] + '.' if '.' in insights else insights.split('\n')[0]
        # Make sure it's not the "No data found" message
        if "No specific data" not in first_sentence:
             context_lines.append(f"* Context from previous '{section}' analysis: {first_sentence}")

    if not context_lines:
        return ""

    return "CONTEXT FROM PREVIOUS ANALYSES (for reference only):\n" + "\n".join(context_lines)


# --- LLM Execution (Unchanged, ensure API key handling is robust) ---

def run_llm_analysis(df, source_type, query, query_type="device", custom_prompt=None, section_results=None):
    """Process data with LLM and return the generated summary"""
    try:
        # Check if API key is configured (ensure genai is imported/configured)
        if not hasattr(genai, 'configured') or not genai.configured:
            load_dotenv()
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                # Consider logging this instead of returning a user-facing string here
                print("Warning: GOOGLE_API_KEY not found.")
                return "AI analysis unavailable: API key not configured."

        if custom_prompt:
            prompt = custom_prompt
        elif df is None or df.empty:
             # Handle case where DataFrame is None or empty before preparing data
             return f"No data provided for {source_type} analysis."
        else:
            data_json = prepare_data_for_llm(df, source_type)
            # If prepare_data_for_llm returned empty dict because df was empty
            if not data_json.get("sample_records"):
                 return f"No specific data found for '{query}' in this section's sample."
            prompt = generate_llm_prompt(data_json, source_type, query, query_type, section_results)

        # Generate content (ensure model name is correct/available)
        # Using gemini-1.5-flash as it's generally good and fast
        model = genai.GenerativeModel("gemini-1.5-flash") # Changed from 2.0
        response = model.generate_content(prompt)

        # Basic check for blocked response
        if not response.parts:
             # Handle safety blocks or empty responses
             print(f"Warning: LLM response blocked or empty for query '{query}', section '{source_type}'. Prompt:\n{prompt}")
             # Try to get feedback if available
             feedback = response.prompt_feedback if hasattr(response, 'prompt_feedback') else 'No feedback available.'
             return f"AI analysis could not be completed. (Reason: {feedback})"


        return response.text.strip()
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during LLM analysis for query '{query}', section '{source_type}': {str(e)}")
        # Provide a user-friendly error message
        return f"An error occurred while generating the AI summary. Please try again later."

# --- Output Formatting (Updated for new headers) ---

def format_llm_summary(summary):
    """Format the LLM summary for better display in Streamlit using new headers."""
    formatted = summary

    # Use the new, simpler headers
    headers_to_bold = [
        "MAIN OBSERVATION:",
        "WHAT THIS MIGHT MEAN:",
        "OTHER DETAILS:",
        "IMPORTANT NOTE:"
        # Add any other headers you might use
    ]

    for header in headers_to_bold:
        formatted = formatted.replace(header, f"**{header}**")

    # Ensure proper line breaks (Markdown needs double space or double newline)
    # Replace single newlines unless they follow the header pattern, ensure double newline otherwise
    # This is a bit tricky, might need refinement based on actual LLM output spacing
    formatted = '\n\n'.join(line.strip() for line in formatted.split('\n') if line.strip())


    # Handle the "No specific data found" case - make it stand out
    if "No specific data" in formatted:
         return f"*{formatted}*" # Italicize this specific message

    return formatted


# --- Function used in app.py (Assuming this structure is called from app.py) ---
# Needs to be updated to handle potential lack of summary more gracefully

def display_section_with_ai_summary(title, df, source, query, query_type):
    """Display a section with AI summary and data, using improved prompts."""
    st.subheader(title)

    if df is None or df.empty:
        st.info(f"No data found for {title}.")
        # Ensure no attempt to run LLM analysis if df is empty
        st.session_state.section_results[source] = f"No data provided for {source}." # Store placeholder
        return # Stop processing this section

    # Generate and display AI summary
    summary = None
    with st.spinner(f"Analyzing {source} data..."):
        summary = run_llm_analysis(
            df,
            source,
            query,
            query_type,
            custom_prompt=None,
            # Pass only relevant previous results if needed, check maintain_narrative_continuity logic
            section_results=st.session_state.get('section_results', {})
        )
        # Store result (even if it's an error message or "no data found")
        st.session_state.section_results[source] = summary

    # Display the summary (or error/message)
    if summary:
        formatted_summary = format_llm_summary(summary)
        # Use st.warning or st.info based on content?
        if "No specific data" in summary or "AI analysis unavailable" in summary or "An error occurred" in summary:
             st.warning(formatted_summary) # Use warning for issues
        else:
             st.markdown(formatted_summary)
    else:
        # Should ideally not happen if run_llm_analysis returns messages
        st.error("Could not retrieve AI analysis.")


    # Display data in an expander (Unchanged)
    with st.expander("View Detailed Data Sample"):
        # Using DISPLAY_COLUMNS mapping if available
        cols_to_display = DISPLAY_COLUMNS.get(source, df.columns.tolist())
        # Filter to columns actually present in the dataframe
        filtered_cols = [col for col in cols_to_display if col in df.columns]
        if not filtered_cols: # Fallback if no DISPLAY_COLUMNS match
             filtered_cols = df.columns.tolist()
        st.dataframe(df[filtered_cols])