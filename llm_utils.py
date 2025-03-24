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
    return """You are an FDA regulatory intelligence expert analyzing recent medical device news and events for healthcare professionals. 
    Your task is to provide insightful analysis of FDA data that highlights important trends, potential safety concerns, and regulatory implications.
    Your analysis should:
    1. Highlight the most recent and significant developments
    2. Identify patterns or emerging trends
    3. Provide regulatory context and implications
    4. Include at least one actionable insight for stakeholders
    
    Be specific, insightful, and concise (4-5 sentences). Use precise dates, device types, and regulatory statuses where available."""

def generate_llm_prompt(data_json, source_type, query):
    """Generate the main prompt for the LLM based on the data"""
    prompt_templates = {
        "510K": f"Analyze these recent 510(k) clearance submissions related to '{query}'. Focus on: timing patterns, novel technologies, significant regulatory decisions, and implications for market access or competition.",
        "PMA": f"Review these recent Pre-Market Approval submissions related to '{query}'. Analyze: approval timelines, innovative technologies, conditions of approval, and potential market impact of these Class III devices.",
        "CLASSIFICATION": f"Examine this FDA device classification data for '{query}'. Analyze: risk classification patterns, regulatory requirements, predicate devices, and market positioning implications.",
        "UDI": f"Analyze these Unique Device Identifier (UDI) entries for '{query}'. Focus on: product diversity, verification status, key features, and supply chain implications.",
        "EVENT": f"Evaluate these recent adverse event reports related to '{query}'. Identify: emerging safety signals, severity patterns, reported malfunctions, potential root causes, and implications for risk management.",
        "RECALL": f"Assess these recent recall records related to '{query}'. Analyze: recall classification severity, root causes, affected units, market impact, and necessary compliance actions."
    }
    
    base_prompt = prompt_templates.get(source_type, f"Analyze this recent FDA data related to '{query}'. What are the key trends and implications?")
    
    prompt = f"""{base_prompt}

Data details:
- Total records found: {data_json.get('num_total_records', 0)}
- Sample size analyzed: {data_json.get('num_sample_records', 0)}
- This data represents the most recent FDA information available

Sample data:
{json.dumps(data_json.get('sample_records', []), indent=2)}

Reasoning steps:
1. Identify the most recent and significant entries in the data
2. Look for patterns or trends across multiple records
3. Consider regulatory implications for stakeholders
4. Determine any actionable insights or recommendations

Provide a concise but detailed analysis that would be valuable to a regulatory professional tracking developments for '{query}'.
"""
    return prompt

def display_section_with_ai_summary(title, df, source, query):
    """Display a section with AI summary and data in an expandable container"""
    st.subheader(title)
    
    if not df.empty:
        # Generate and display AI summary
        with st.spinner("Analyzing recent data..."):
            summary = run_llm_analysis(df, source, query)
            
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