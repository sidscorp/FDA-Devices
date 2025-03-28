import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from fda_data import DISPLAY_COLUMNS

def prepare_data_for_llm(df, source_type):
    """Convert a pandas DataFrame to structured JSON for LLM input, optimized for token efficiency"""
    if df.empty:
        return {}
    
    # Define essential fields per source type to reduce data volume
    essential_fields = {
        "510K": ["k_number", "device_name", "decision_date", "applicant"],
        "PMA": ["pma_number", "trade_name", "decision_date", "applicant"],
        "CLASSIFICATION": ["device_name", "device_class", "medical_specialty_description"],
        "UDI": ["brand_name", "device_description", "company_name"],
        "RECALL": ["event_date_initiated", "recalling_firm", "product_description", "recall_classification", "reason_for_recall"],
        "EVENT": ["date_received", "manufacturer_name", "product_problems", "device.brand_name", "device.generic_name"]
    }
    
    # Get essential fields for this source type, or use all if not specified
    fields = essential_fields.get(source_type, df.columns.tolist())
    
    # Filter to only include fields that exist in the dataframe
    available_fields = [field for field in fields if field in df.columns]
    
    # If no matching fields, fallback to first few columns
    if not available_fields and len(df.columns) > 0:
        available_fields = df.columns[:min(5, len(df.columns))].tolist()
    
    # Limit to first 5-10 rows (depending on source type complexity)
    sample_size = 5 if source_type in ["RECALL", "EVENT"] else 8
    df_sample = df.head(sample_size).copy()
    
    # Select only the essential columns
    if available_fields:
        df_sample = df_sample[available_fields]
    
    # Convert to dict for JSON serialization
    records = df_sample.to_dict(orient='records')
    
    # Create JSON structure with summary stats instead of full data
    data_json = {
        "source_type": source_type,
        "num_total_records": len(df),
        "num_sample_records": len(records),
        "sample_records": records,
        "date_range": {
            "earliest": df["date_received"].min() if "date_received" in df.columns else None,
            "latest": df["date_received"].max() if "date_received" in df.columns else None
        }
    }
    
    return data_json

def create_system_prompt():
    return """You are an FDA regulatory intelligence SENTINEL constantly monitoring for emerging safety signals and regulatory patterns in medical device data.

    As a vigilant monitor of the regulatory landscape, your mission is to analyze the 20 MOST RECENT FDA records to identify early warning signs and noteworthy regulatory developments. Provide BRIEF, SPECIFIC insights that:
    1. Identify 2-3 KEY emerging patterns or signals in this RECENT data (be concrete, not general). Pay special attention to dates, timing, and any acceleration in events.
    2. For each identified signal, provide a concise, actionable interpretation of its regulatory implications. What should stakeholders be ALERT to?
    3. Keep your analysis of each emerging pattern or signal 100 words - you are providing an urgent alert, not a comprehensive report.
    4. End with ONE brief line about monitoring limitations."""

def generate_llm_prompt(data_json, source_type, query, query_type, section_results=None):
    """Generate consistent, structured prompts for LLM analysis"""
    # Base instructions that enforce consistent structure
    system_instructions = create_structured_system_prompt(query_type, source_type)
    
    # Data-specific descriptions
    descriptions = {
        "manufacturer": {
            "510K": "recent 510(k) clearance strategy and regulatory approach",
            "PMA": "recent PMA applications for high-risk devices",
            "EVENT": "recent adverse events reported for their devices",
            "RECALL": "recent product recalls and corrective actions",
            "UDI": "recent device registrations and identifiers"
        },
        "device": {
            "510K": "recent regulatory clearance pathways and technological variations",
            "PMA": "recent approval applications and clinical evidence",
            "CLASSIFICATION": "regulatory risk classification and requirements",
            "UDI": "device variations and manufacturer diversity",
            "EVENT": "recent adverse event patterns and patient impacts",
            "RECALL": "recent recall patterns and correction strategies"
        }
    }
    
    # Get the appropriate description
    description = descriptions.get(query_type, {}).get(source_type, "recent regulatory activity")
    
    # Create a consistent narrative prompt
    prompt = f"""Analyze the {data_json.get('num_sample_records', 0)} MOST RECENT records about {description} for {'manufacturer' if query_type == 'manufacturer' else 'device type'} '{query}'.

    Sample data:
    {json.dumps(data_json.get('sample_records', []), indent=2)}
    """
    
    # Add narrative continuity if we have previous sections
    if section_results:
        continuity_context = maintain_narrative_continuity(section_results, source_type, query, query_type)
        prompt = f"{prompt}\n\n{continuity_context}"
    
    # Complete prompt with system instructions
    full_prompt = f"{system_instructions}\n\n{prompt}"
    return full_prompt


def run_llm_analysis(df, source_type, query, query_type="device", custom_prompt=None, section_results=None):
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
            prompt = generate_llm_prompt(data_json, source_type, query, query_type, section_results)
        
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
        # Generate and display AI summary with narrative continuity
        with st.spinner("Analyzing data..."):
            summary = run_llm_analysis(
                df, 
                source, 
                query, 
                query_type, 
                custom_prompt=None, 
                section_results=st.session_state.section_results
            )
            # Store this section's results for future sections
            st.session_state.section_results[source] = summary
            
        # Format the summary for better display
        formatted_summary = format_llm_summary(summary)
        st.markdown(formatted_summary)
        
        # Display data with appropriate columns in an expander
        with st.expander("View Detailed Data"):
            cols = DISPLAY_COLUMNS.get(source, [])
            filtered_cols = [col for col in cols if col in df.columns] if cols else df.columns
            st.dataframe(df[filtered_cols] if filtered_cols else df)
    else:
        st.info(f"No data found for {title}.")

def format_llm_summary(summary):
    """Format the LLM summary for better display in Streamlit"""
    # Replace section titles with markdown formatting
    formatted = summary
    
    if "KEY TREND:" in formatted:
        formatted = formatted.replace("KEY TREND:", "**KEY TREND:**")
    
    if "REGULATORY IMPLICATIONS:" in formatted:
        formatted = formatted.replace("REGULATORY IMPLICATIONS:", "**REGULATORY IMPLICATIONS:**")
    
    if "NOTABLE PATTERNS:" in formatted:
        formatted = formatted.replace("NOTABLE PATTERNS:", "**NOTABLE PATTERNS:**")
    
    if "MONITORING LIMITATION:" in formatted:
        formatted = formatted.replace("MONITORING LIMITATION:", "**MONITORING LIMITATION:**")
    
    # Ensure proper line breaks between sections
    formatted = formatted.replace("\n\n", "\n\n")
    
    return formatted

def create_structured_system_prompt(query_type, section_name):
    """Create a system prompt with consistent structure and formatting"""
    base_instructions = """You are an FDA regulatory intelligence SENTINEL monitoring for emerging safety signals and regulatory patterns in medical device data.

    Analyze the 20 MOST RECENT FDA records to identify emerging warning signs and noteworthy developments. 
    
    FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS WITH LINE BREAKS AFTER EACH SECTION:
    
    KEY TREND:
    [1-2 sentence description of most important trend]
    
    REGULATORY IMPLICATIONS:
    [1-2 sentence analysis of what this means]
    
    NOTABLE PATTERNS:
    [1-2 sentence description of secondary patterns]
    
    MONITORING LIMITATION:
    [1 brief sentence on data limitations]
    
    Keep your total response under 150 words. Be specific about dates, frequencies, and concrete observations."""
    
    # Add context specific to query type
    if query_type == "manufacturer":
        context = f"For this {section_name} analysis, focus on how this manufacturer's regulatory profile and quality systems may be evolving based on recent activity."
    else:  # device
        context = f"For this {section_name} analysis, focus on how this device category's safety profile and regulatory status may be changing based on recent activity."
    
    return f"{base_instructions}\n\n{context}"

def maintain_narrative_continuity(section_results, current_section, query, query_type):
    """Provide context from previous sections to maintain narrative continuity"""
    # Skip if this is the first section
    if not section_results:
        return ""
        
    # Create context from previous sections
    context_lines = []
    for section, insights in section_results.items():
        # Extract just the first sentence of previous insights to keep context concise
        first_sentence = insights.split('.')[0] + '.' if '.' in insights else insights
        context_lines.append(f"In the {section} analysis, you noted: {first_sentence}")
    
    return "PREVIOUS ANALYSES CONTEXT:\n" + "\n".join(context_lines)