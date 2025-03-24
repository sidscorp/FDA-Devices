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
    
    # Truncate dataframe to first 5 rows to avoid overwhelming the LLM
    df_sample = df.head(5).copy()
    
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
    return """You are an FDA regulatory intelligence expert analyzing medical device data for a demo application.

    IMPORTANT CONTEXT ABOUT THIS DEMO APP:
    - This is a demonstration app that pulls sample data from the openFDA API
    - You are only seeing a small sample of data (typically 5 records), NOT the complete dataset
    - The samples shown may be recent but are not necessarily representative of all data
    - Your analysis should acknowledge these limitations while still providing useful insights
    - The purpose is to demonstrate what a more complete analysis could look like with more comprehensive data
    
    Your task is to provide insightful analysis of the FDA data sample that highlights potential trends, safety considerations, and regulatory implications.
    Your analysis should:
    1. Acknowledge the limited sample nature of the data
    2. Identify any notable patterns in the sample
    3. Provide regulatory context and potential implications
    4. Suggest what a more comprehensive analysis might reveal
    
    Be specific about the sample data while being clear about its limitations. Use precise dates, device types, and regulatory statuses where available."""

def generate_llm_prompt(data_json, source_type, query, query_type):
    """Generate the main prompt for the LLM based on the data and query type"""
    # Different prompt templates based on query type
    manufacturer_templates = {
        "510K": f"Analyze this sample of 510(k) clearance submissions from manufacturer '{query}'. Focus on: any visible patterns in their product strategy, types of submissions, and regulatory approaches.",
        "PMA": f"Review this sample of Pre-Market Approval submissions from manufacturer '{query}'. Consider: their high-risk device portfolio, approval pathways, and potential innovation trends.",
        "EVENT": f"Evaluate this sample of adverse events reported for '{query}' devices. Look for: any recurring issues, severity patterns, and potential quality considerations visible in this limited sample.",
        "RECALL": f"Assess this sample of recalls issued by '{query}'. Consider: the nature of these specific recalls, their severity classifications, and what they might suggest about quality systems.",
        "UDI": f"Analyze this sample of Unique Device Identifier (UDI) entries for manufacturer '{query}'. Look at: the types of products represented and their characteristics within this limited sample."
    }
    
    device_templates = {
        "510K": f"Analyze this sample of 510(k) clearance submissions related to '{query}' devices. Consider: the regulatory pathways, technologies, and manufacturers represented in this limited sample.",
        "PMA": f"Review this sample of Pre-Market Approval submissions for '{query}' devices. Consider: the approval requirements, conditions, and technological features visible in this limited dataset.",
        "CLASSIFICATION": f"Examine this sample of FDA device classification data for '{query}'. Consider: the risk classifications, regulatory requirements, and product characteristics shown.",
        "UDI": f"Analyze this sample of Unique Device Identifier (UDI) entries for '{query}' devices. Consider: the variations, features, and manufacturers represented in this limited sample.",
        "EVENT": f"Evaluate this sample of adverse event reports related to '{query}' devices. Look for: any patterns in failure modes, patient impacts, or reporting sources visible in this limited dataset.",
        "RECALL": f"Assess this sample of recall records related to '{query}' devices. Consider: the types of issues, affected manufacturers, and corrective actions represented in this limited dataset."
    }
    
    if query_type == "manufacturer":
        prompt_templates = manufacturer_templates
        base_prompt = prompt_templates.get(source_type, f"Analyze this sample of FDA data for manufacturer '{query}'. Consider what patterns might be visible in this limited dataset.")
    else:  # device
        prompt_templates = device_templates
        base_prompt = prompt_templates.get(source_type, f"Analyze this sample of FDA data for device type '{query}'. Consider what patterns might be visible in this limited dataset.")
    
    # Demo app context
    demo_context = """DEMO APP CONTEXT: This is a demonstration application that pulls random samples from the openFDA API. The sample data shown may not be representative of all relevant records and may not necessarily show the most recent data. Your analysis should acknowledge these limitations while still providing insights about what patterns a more comprehensive analysis might reveal."""
    
    # Query-type specific context
    if query_type == "manufacturer":
        specific_context = f"""You are examining a small sample of data related to manufacturer '{query}'. While not comprehensive, this sample provides a glimpse into their regulatory activities, product issues, and portfolio characteristics."""
    else:  # device
        specific_context = f"""You are examining a small sample of data related to device type '{query}'. While not comprehensive, this sample provides a glimpse into the regulatory landscape, safety patterns, and characteristics of this device category."""
    
    prompt = f"""{base_prompt}

    {demo_context}

    {specific_context}

    Data details:
    - Total records found: {data_json.get('num_total_records', 0)}
    - Sample size shown: {data_json.get('num_sample_records', 0)} (IMPORTANT: This is just a sample)

    Sample data:
    {json.dumps(data_json.get('sample_records', []), indent=2)}

    Reasoning steps:
    1. Identify any notable patterns in this limited sample
    2. Consider what these specific records might suggest about {query_type}-specific trends
    3. Acknowledge data limitations while still providing useful insights
    4. Suggest what a more comprehensive analysis might reveal

    Provide an analysis that acknowledges the demo nature of this app while still offering valuable insights about the visible patterns in this sample for '{query}'.
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
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        return response.text.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def display_section_with_ai_summary(title, df, source, query, query_type):
    """Display a section with AI summary and data in an expandable container"""
    st.subheader(title)
    
    if not df.empty:
        # Generate and display AI summary
        with st.spinner("Analyzing recent data..."):
            summary = run_llm_analysis(df, source, query, query_type)
            
        st.info(f"**Key Insights**: {summary}")
        
        # Display data with appropriate columns in an expander
        with st.expander("View Detailed Data"):
            cols = DISPLAY_COLUMNS.get(source, [])
            if cols:
                existing_cols = [col for col in cols if col in df.columns]
                if existing_cols:
                    st.dataframe(df[existing_cols])
                else:
                    st.dataframe(df)
            else:
                st.dataframe(df)
    else:
        st.info(f"No recent data found for {title}.")