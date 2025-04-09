import streamlit as st
import pandas as pd
from fda_data import get_fda_data, DISPLAY_COLUMNS
import os
import json
from llm_utils import display_section_with_ai_summary, run_llm_analysis

@st.cache_data(ttl=3600, show_spinner=False)
def cached_get_fda_data(query, query_type, limit=20):
    """Cached wrapper for the FDA data retrieval function"""
    return get_fda_data(query, query_type, limit)

def determine_query_type(query):
    """Use LLM to determine if the query is for a device or manufacturer and fix spelling"""
    prompt = f"""For the query '{query}':
    1. First, correct any spelling or grammatical errors
    2. Then, determine if the corrected query is more likely a medical device or a manufacturer name
    
    Respond in this JSON format:
    {{
        "corrected_query": "the corrected spelling of the query",
        "type": "device or manufacturer"
    }}
    """
    
    result = run_llm_analysis(pd.DataFrame(), "QUERY_TYPE", query, custom_prompt=prompt)
    
    try:
        # Parse the JSON response
        response_data = json.loads(result)
        corrected_query = response_data.get("corrected_query", query)
        query_type = response_data.get("type", "device")
        
        # Update the query if it was corrected
        if corrected_query != query:
            st.info(f"Query corrected to: **{corrected_query}**")
            
        # Return both the corrected query and type
        return corrected_query, query_type
    except:
        # Fallback to original behavior if JSON parsing fails
        if "manufacturer" in result.lower():
            return query, "manufacturer"
        else:
            return query, "device"

def display_device_view(results, query):
    st.header("📊 Recent FDA Activity for this Device")
    st.session_state.section_results = {}

    if not results:
        st.write("No recent device-related data found.")
        return

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
  
        if "RECALL" in results:
            display_section_with_ai_summary("🚨 Recent Recalls", results["RECALL"], "RECALL", query, "device")
        else:
            st.write("No recent recall data found.")
    with row1_col2:
        if "EVENT" in results:
            display_section_with_ai_summary("⚠️ Recent Adverse Events", results["EVENT"], "EVENT", query, "device")
        else:
            st.write("No recent adverse event data found.")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        if "PMA" in results:
            display_section_with_ai_summary("📄 Recent PMA Submissions", results["PMA"], "PMA", query, "device")
        else:
            st.write("No recent PMA submission data found.")
    with row2_col2:
        if "510K" in results:
            display_section_with_ai_summary("📄 Latest 510(k) Submissions", results["510K"], "510K", query, "device")
        else:
            st.write("No recent 510(k) submission data found.")

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        if "UDI" in results:
            display_section_with_ai_summary("🔗 UDI Database Entries", results["UDI"], "UDI", query, "device")
        else:
            st.write("No UDI database entries found.")
    with row3_col2:
        if "CLASSIFICATION" in results:
            display_section_with_ai_summary("🧪 Regulatory Classification", results["CLASSIFICATION"], "CLASSIFICATION", query, "device")
        else:
            st.write("No classification data found.")



def display_manufacturer_view(results, query):
    """Display manufacturer-centric view of FDA data with AI summaries in fixed layout"""
    st.header("📈 Recent FDA Activity for this Manufacturer")
    
    # Clear previous section results at the beginning of a new search
    st.session_state.section_results = {}
    
    if not results:
        st.write("No recent manufacturer-related data found.")
        return
    
    # Row 1: Recalls and Events
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        if "RECALL" in results:
            display_section_with_ai_summary("🚨 Recent Recalls", results["RECALL"], "RECALL", query, "manufacturer")
        else:
            st.subheader("🚨 Recent Recalls")
            st.write("No recent recall data found.")
    
    with row1_col2:
        if "EVENT" in results:
            display_section_with_ai_summary("⚠️ Recent Adverse Events", results["EVENT"], "EVENT", query, "manufacturer")
        else:
            st.subheader("⚠️ Recent Adverse Events")
            st.write("No recent adverse event data found.")
    
    # Row 2: PMA and 510K
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        if "PMA" in results:
            display_section_with_ai_summary("📄 Recent PMA Submissions", results["PMA"], "PMA", query, "manufacturer")
        else:
            st.subheader("📄 Recent PMA Submissions")
            st.write("No recent PMA submission data found.")
    
    with row2_col2:
        if "510K" in results:
            display_section_with_ai_summary("📄 Latest 510(k) Submissions", results["510K"], "510K", query, "manufacturer")
        else:
            st.subheader("📄 Latest 510(k) Submissions")
            st.write("No recent 510(k) submission data found.")
    
    # Row 3: UDI and Classification (Note: Manufacturer view might not have Classification data)
    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        if "UDI" in results:
            display_section_with_ai_summary("🔗 UDI Database Entries", results["UDI"], "UDI", query, "manufacturer")
        else:
            st.subheader("🔗 UDI Database Entries")
            st.write("No UDI database entries found.")
    
    with row3_col2:
        if "CLASSIFICATION" in results:
            display_section_with_ai_summary("🧪 Regulatory Classification", results["CLASSIFICATION"], "CLASSIFICATION", query, "manufacturer")
        else:
            st.subheader("🧪 Regulatory Classification")
            st.write("No classification data found.")

def add_about_button():
    """Add an About button that shows the content of about.md in a modal when clicked"""
    if os.path.exists("about.md"):
        with open("about.md", "r") as f:
            about_content = f.read()
    with st.expander("About FDA Medical Device Intelligence Demo", expanded=False):
        st.markdown(about_content)

def main():
    """Main application entry point"""
    st.set_page_config(page_title="FDA Device Intelligence", layout="wide")

    st.markdown("## 🔍 FDA Medical Device Intelligence Center")
    st.caption("Developed by Dr. Sidd Nambiar · Sr. Lead Scientist @ Booz Allen Hamilton")

    st.markdown("""
    <div style='font-size: 0.9rem; color: gray; margin-bottom: 1rem;'>
    This app provides a demo of real-time FDA regulatory activity monitoring using openFDA data and AI-powered insights.
    </div>
    """, unsafe_allow_html=True)

    add_about_button()

    st.warning("""
    **DEMO APP NOTICE**: This application pulls a few of the most recent records from the openFDA API to 
    monitor recent regulatory activities. The analysis focuses on identifying key trends in recent 
    FDA submissions, events, and recalls. This limited sample may not represent all relevant records,
    and should be considered illustrative of real-time monitoring capabilities.
    """)

    query = st.text_input("Enter device name or manufacturer", 
                        placeholder="e.g. Medtronic, pacemaker, insulin pump")


    if query:
        with st.spinner("Analyzing query..."):
            corrected_query, query_type = determine_query_type(query)
            
        st.info(f"Retrieving FDA data sample for this {query_type}: **{corrected_query}**")
            
        with st.spinner("Gathering FDA data samples..."):
            results = cached_get_fda_data(corrected_query, query_type)
        
        # Only display the relevant view
        if query_type == "device":
            display_device_view(results.get("device"), query)
        else:
            display_manufacturer_view(results.get("manufacturer"), query)

        # Add sample size explanation
        st.caption("""
        Note: Each section shows a sample of available data. AI insights are based on these samples 
        and should be considered illustrative of what a more comprehensive analysis could reveal.
        """)

        # Debug information (optional)
        with st.expander("Developer Information"):
            st.write("Data structure information")
            for view, tables in results.items():
                if view == query_type:
                    st.write(f"=== {view.upper()} VIEW ===")
                    for source, df in tables.items():
                        st.write(f"{source} columns:", list(df.columns))

if __name__ == "__main__":
    main()