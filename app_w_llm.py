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
    """Use LLM to determine if the query is for a device or manufacturer"""
    prompt = f"""Determine if '{query}' is more likely a medical device or a manufacturer name.
    Respond with only one word: 'device' or 'manufacturer'."""
    
    result = run_llm_analysis(pd.DataFrame(), "QUERY_TYPE", query, custom_prompt=prompt)
    
    if "manufacturer" in result.lower():
        return "manufacturer"
    else:
        return "device"

def display_device_view(results, query):
    """Display device-centric view of FDA data with AI summaries in side-by-side layout"""
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
    
    # Create rows of 2 items each
    section_items = list(sections.items())
    
    # Process sections in pairs
    for i in range(0, len(section_items), 2):
        cols = st.columns(2)
        
        # First column
        if i < len(section_items) and section_items[i][0] in results:
            key, title = section_items[i]
            with cols[0]:
                with st.container():
                    display_section_with_ai_summary(title, results[key], key, query, "device")
        
        # Second column
        if i+1 < len(section_items) and section_items[i+1][0] in results:
            key, title = section_items[i+1]
            with cols[1]:
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
    """Display manufacturer-centric view of FDA data with AI summaries in side-by-side layout"""
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
    
    # Create rows of 2 items each
    section_items = list(sections.items())
    
    # Process sections in pairs
    for i in range(0, len(section_items), 2):
        cols = st.columns(2)
        
        # First column
        if i < len(section_items) and section_items[i][0] in results:
            key, title = section_items[i]
            with cols[0]:
                with st.container():
                    display_section_with_ai_summary(title, results[key], key, query, "manufacturer")
        
        # Second column
        if i+1 < len(section_items) and section_items[i+1][0] in results:
            key, title = section_items[i+1]
            with cols[1]:
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
            query_type = determine_query_type(query)
            
        st.info(f"Retrieving FDA data sample for this {query_type}: **{query}**")
            
        with st.spinner("Gathering FDA data samples..."):
            results = cached_get_fda_data(query)
        
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