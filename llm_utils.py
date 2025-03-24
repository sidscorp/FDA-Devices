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

def generate_llm_prompt(data_json, source_type, query, query_type):
    """Generate the main prompt for the LLM based on the data and query type"""
    # Different prompt templates based on query type
    manufacturer_templates = {
        "510K": f"Analyze these recent 510(k) clearance submissions from manufacturer '{query}'. Focus on: product portfolio strategy, technology trends across their submissions, regulatory approval patterns, and competitive positioning in the market.",
        "PMA": f"Review these recent Pre-Market Approval submissions from manufacturer '{query}'. Analyze: their high-risk device strategy, approval timelines compared to industry averages, conditions of approval patterns, and innovation trends in their Class III portfolio.",
        "EVENT": f"Evaluate these recent adverse events reported for '{query}' devices. Identify: recurring device issues across their product lines, severity trends, potential quality system implications, and how these events compare to previous reporting periods.",
        "RECALL": f"Assess these recent recalls issued by '{query}'. Analyze: quality system implications, impact on their product portfolio, recall classification severity patterns, and potential regulatory enforcement risk for the manufacturer.",
        "UDI": f"Analyze these Unique Device Identifier (UDI) entries for manufacturer '{query}'. Focus on: product line diversity, recent additions to their portfolio, device risk classifications, and market positioning."
    }
    
    device_templates = {
        "510K": f"Analyze these recent 510(k) clearance submissions related to '{query}' devices. Focus on: technological innovations, predicate device patterns, regulatory requirements, and competitive landscape for this device type.",
        "PMA": f"Review these recent Pre-Market Approval submissions for '{query}' devices. Analyze: clinical requirements, safety and efficacy standards, approval conditions, and technological advancements for this specific device category.",
        "CLASSIFICATION": f"Examine this FDA device classification data for '{query}'. Analyze: risk classification assignments, special controls, applicable standards, and regulatory requirements specific to this device type.",
        "UDI": f"Analyze these Unique Device Identifier (UDI) entries for '{query}' devices. Focus on: variations between models, technological features, competitive positioning, and market distribution.",
        "EVENT": f"Evaluate these recent adverse event reports related to '{query}' devices. Identify: common failure modes, patient impact patterns, usage environment factors, and potential design or labeling implications.",
        "RECALL": f"Assess these recent recall records related to '{query}' devices. Analyze: common defects or issues, design implications, user impact, and corrective actions taken across manufacturers."
    }
    
    if query_type == "manufacturer":
        prompt_templates = manufacturer_templates
        base_prompt = prompt_templates.get(source_type, f"Analyze this recent FDA data for manufacturer '{query}'. What are the key trends and implications?")
    else:  # device
        prompt_templates = device_templates
        base_prompt = prompt_templates.get(source_type, f"Analyze this recent FDA data for device type '{query}'. What are the key trends and implications?")
    
    # Additional context based on query type
    if query_type == "manufacturer":
        context = f"""Context: This analysis is focused on the manufacturer '{query}' and their regulatory activities, quality performance, and product portfolio. Consider trends specific to this company versus industry norms."""
    else:  # device
        context = f"""Context: This analysis is focused on the device category '{query}' across different manufacturers. Consider technological trends, safety patterns, and regulatory approaches specific to this device type."""
    
    prompt = f"""{base_prompt}

    {context}

    Data details:
    - Total records found: {data_json.get('num_total_records', 0)}
    - Sample size analyzed: {data_json.get('num_sample_records', 0)}
    - This data represents the most recent FDA information available

    Sample data:
    {json.dumps(data_json.get('sample_records', []), indent=2)}

    Reasoning steps:
    1. Identify the most recent and significant entries in the data
    2. Look for patterns or trends specific to this {query_type}
    3. Consider regulatory implications for {query_type}-specific stakeholders
    4. Determine any actionable insights or recommendations relevant to this {query_type}

    Provide a concise but detailed analysis that would be valuable to a regulatory professional tracking developments for this {query_type}: '{query}'.
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