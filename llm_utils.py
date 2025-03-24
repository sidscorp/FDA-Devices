import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from fda_data import DISPLAY_COLUMNS

def prepare_data_for_llm(df, source_type):
    """Convert a pandas DataFrame to structured JSON for LLM input"""
    if df.empty:
        return {}
    
    # Truncate dataframe to first 10 rows to provide more data to the LLM
    df_sample = df.head(10).copy()
    
    # Convert to dict for JSON serialization
    records = df_sample.to_dict(orient='records')
    
    # Create JSON structure
    data_json = {
        "source_type": source_type,
        "num_total_records": len(df),
        "num_sample_records": len(records),
        "sample_records": records
    }
    
    return data_json

def create_system_prompt():
    """Create the system prompt for the LLM"""
    return """You are an FDA regulatory intelligence expert analyzing medical device data.
    
    This demo app pulls sample data (typically 5 records) from the openFDA API to demonstrate 
    regulatory intelligence capabilities. Provide insightful analysis that:
    1. Identifies notable patterns in the sample
    2. Provides regulatory context and implications
    3. Is specific about the data shown
    4. Includes a brief mention of sample limitations at the end"""

def generate_llm_prompt(data_json, source_type, query, query_type):
    """Generate the main prompt for the LLM based on the data and query type"""
    # Different prompt templates based on query type
    manufacturer_templates = {
        "510K": f"Analyze this sample of 510(k) submissions from manufacturer '{query}'. Focus on product strategy and regulatory approaches.",
        "PMA": f"Review this sample of PMA submissions from '{query}'. Consider their high-risk device portfolio and approval pathways.",
        "EVENT": f"Evaluate this sample of adverse events for '{query}' devices. Look for recurring issues and severity patterns.",
        "RECALL": f"Assess this sample of recalls from '{query}'. Consider nature, severity, and quality implications.",
        "UDI": f"Analyze this sample of UDI entries for '{query}'. Examine product types and characteristics."
    }
    
    device_templates = {
        "510K": f"Analyze this sample of 510(k) submissions for '{query}' devices. Consider regulatory pathways and technologies.",
        "PMA": f"Review this sample of PMA submissions for '{query}' devices. Consider approval requirements and features.",
        "CLASSIFICATION": f"Examine this classification data for '{query}'. Note risk classifications and regulatory requirements.",
        "UDI": f"Analyze this sample of UDI entries for '{query}' devices. Consider variations and manufacturers.",
        "EVENT": f"Evaluate this sample of adverse events for '{query}' devices. Look for failure patterns and patient impacts.",
        "RECALL": f"Assess this sample of recalls for '{query}' devices. Consider issue types and corrective actions."
    }
    
    if query_type == "manufacturer":
        prompt_templates = manufacturer_templates
        base_prompt = prompt_templates.get(source_type, f"Analyze this FDA data sample for manufacturer '{query}'.")
    else:  # device
        prompt_templates = device_templates
        base_prompt = prompt_templates.get(source_type, f"Analyze this FDA data sample for device type '{query}'.")
    
    prompt = f"""{base_prompt}

    DEMO CONTEXT: This app shows a sample of {data_json.get('num_sample_records', 0)} records from a total of {data_json.get('num_total_records', 0)} found.

    Sample data:
    {json.dumps(data_json.get('sample_records', []), indent=2)}

    Provide informative insights about visible patterns for '{query}'. End with a brief mention of sample limitations.
    """
    return prompt

def run_llm_analysis(df, source_type, query, query_type="device", custom_prompt=None):
    """Process data with LLM and return the generated summary"""
    try:
        # Check if API key is configured
        if not hasattr(genai, 'configured') or not genai.configured:
            load_dotenv()
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                return "API key not configured. Unable to generate summary."
        
        # Use custom prompt if provided
        if custom_prompt:
            prompt = custom_prompt
        else:
            # Prepare data and prompts
            data_json = prepare_data_for_llm(df, source_type)
            system_instructions = create_system_prompt()
            prompt = generate_llm_prompt(data_json, source_type, query, query_type)
            prompt = f"{system_instructions}\n\n{prompt}"
        
        # Generate content
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        return response.text.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def display_section_with_ai_summary(title, df, source, query, query_type):
    """Display a section with AI summary and data in an expandable container"""
    st.subheader(title)
    
    if not df.empty:
        # Generate and display AI summary
        with st.spinner("Analyzing data..."):
            summary = run_llm_analysis(df, source, query, query_type)
            
        st.info(f"**Key Insights**: {summary}")
        
        # Display data with appropriate columns in an expander
        with st.expander("View Detailed Data"):
            cols = DISPLAY_COLUMNS.get(source, [])
            filtered_cols = [col for col in cols if col in df.columns] if cols else df.columns
            st.dataframe(df[filtered_cols] if filtered_cols else df)
    else:
        st.info(f"No data found for {title}.")