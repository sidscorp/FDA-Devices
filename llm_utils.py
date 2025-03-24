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
    return """You are an FDA regulatory expert analyzing medical device data for healthcare professionals. 
    Your task is to provide a concise, insightful summary of the FDA data provided.
    Focus on identifying patterns, potential concerns, and actionable insights.
    Your summary should be 3-4 sentences and professional in tone.
    Highlight any important regulatory considerations or safety issues if present."""

def generate_llm_prompt(data_json, source_type, query):
    """Generate the main prompt for the LLM based on the data"""
    prompt_templates = {
        "510K": f"Analyze these 510(k) clearance submissions related to '{query}'. What are the key insights about regulatory clearance patterns, device types, or applicants?",
        "PMA": f"Review these Pre-Market Approval submissions related to '{query}'. What insights can you provide about these Class III devices?",
        "CLASSIFICATION": f"Examine this FDA device classification data for '{query}'. What classification category, regulatory requirements, and risk levels are represented?",
        "UDI": f"Analyze these Unique Device Identifier (UDI) entries for '{query}'. What can you determine about the device identifiers and their significance?",
        "EVENT": f"Evaluate these adverse event reports related to '{query}'. Are there any concerning patterns or safety signals that emerge?",
        "RECALL": f"Assess these recall records related to '{query}'. What is the nature and severity of these recalls, and what might they indicate?"
    }
    
    base_prompt = prompt_templates.get(source_type, f"Analyze this FDA data related to '{query}'. What are the key insights?")
    
    # Add data context
    prompt = f"""{base_prompt}

Data details:
- Total records found: {data_json.get('num_total_records', 0)}
- Sample size analyzed: {data_json.get('num_sample_records', 0)}

Sample data:
{json.dumps(data_json.get('sample_records', []), indent=2)}

Provide a concise, informative summary (3-4 sentences) that highlights the most important aspects of this data.
"""
    return prompt

def run_llm_analysis(df, source_type, query, custom_prompt=None):
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
            prompt = generate_llm_prompt(data_json, source_type, query)
            prompt = f"{system_instructions}\n\n{prompt}"
        
        # Generate content
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        return response.text.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"
        

def display_section_with_ai_summary(title, df, source, query):
    """Display a section with AI summary and data"""
    st.subheader(title)
    
    if not df.empty:
        # Generate and display AI summary
        with st.spinner("Generating insights..."):
            summary = run_llm_analysis(df, source, query)
            
        st.info(f"**AI Summary**: {summary}")
        
        # Display data with appropriate columns
        cols = DISPLAY_COLUMNS.get(source, [])
        if cols:
            existing_cols = [col for col in cols if col in df.columns]
            if existing_cols:
                st.dataframe(df[existing_cols])
            else:
                st.info(f"No expected columns found for {source}. Showing all data.")
                st.dataframe(df)
        else:
            st.dataframe(df)
    else:
        st.info(f"No data found for {title}.")