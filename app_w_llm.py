import streamlit as st
import pandas as pd
from fda_data import get_fda_data, DISPLAY_COLUMNS
import os
from llm_utils import display_section_with_ai_summary, run_llm_analysis

@st.cache_data(ttl=3600, show_spinner=False)
def cached_get_fda_data(query, limit=20):
    """Cached wrapper for the FDA data retrieval function"""
    return get_fda_data(query, limit)

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
    """Display device-centric view of FDA data with AI summaries in single column layout"""
    st.header("📊 Recent FDA Activity for this Device")
    
    st.session_state.section_results = {}
    
    if not results:
        st.write("No recent device-related data found.")
        return
        
    sections = {
        "EVENT": "⚠️ Recent Adverse Events",
        "RECALL": "🚨 Recent Recalls",
        "510K": "📄 Latest 510(k) Submissions",
        "PMA": "📄 Recent PMA Submissions",
        "CLASSIFICATION": "🧪 Regulatory Classification",
        "UDI": "🔗 UDI Database Entries"
    }
    
    # Process each section in a single column layout
    for key, title in sections.items():
        if key in results:
            with st.container():
                display_section_with_ai_summary(title, results[key], key, query, "device")


def add_about_button():
    """Add an About button that shows the content of about.md in a modal when clicked"""
    if os.path.exists("about.md"):
        with open("about.md", "r") as f:
            about_content = f.read()
    with st.expander("About FDA Medical Device Intelligence Demo", expanded=False):
        st.markdown(about_content)



def display_manufacturer_view(results, query):
    """Display manufacturer-centric view of FDA data with AI summaries in single column layout"""
    st.header("📈 Recent FDA Activity for this Manufacturer")
    
    # Clear previous section results at the beginning of a new search
    st.session_state.section_results = {}
    
    if not results:
        st.write("No recent manufacturer-related data found.")
        return
        
    sections = {
        "RECALL": "🚨 Recent Recalls",
        "EVENT": "⚠️ Recent Adverse Events",
        "510K": "📄 Latest 510(k) Submissions",
        "PMA": "📄 Recent PMA Submissions",
        "UDI": "🔗 UDI Database Entries"
    }
    
    # Process each section in a single column layout
    for key, title in sections.items():
        if key in results:
            with st.container():
                display_section_with_ai_summary(title, results[key], key, query, "manufacturer")

def main():
    """Main application entry point"""
    st.set_page_config(page_title="FDA Device Intelligence Demo", layout="wide")
    
    # Initialize session state for tracking narrative
    if 'section_results' not in st.session_state:
        st.session_state.section_results = {}

    st.title("🔍 FDA Medical Device Intelligence Center")
    st.caption("""Demo developed by Dr. Sidd Nambiar, Sr. Lead Scientist at Booz Allen Hamilton.  
                  Contact: nambiar_siddhartha@bah.com""")
    # add about button to the top right
    add_about_button()
    st.subheader("Explore News, Events, and Regulatory Activities")
    
    # Add demo app disclaimer
    st.warning("""
    **DEMO APP NOTICE**: This application pulls the 20 MOST RECENT records from the openFDA API to 
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
            results = cached_get_fda_data(corrected_query)
        
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