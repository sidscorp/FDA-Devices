import streamlit as st
import pandas as pd
from fda_data import get_fda_data, DISPLAY_COLUMNS
from llm_utils import display_section_with_ai_summary

@st.cache_data(ttl=3600, show_spinner=False)
def cached_get_fda_data(query, limit=100):
    """Cached wrapper for the FDA data retrieval function"""
    return get_fda_data(query, limit)

def display_device_view(results, query):
    """Display device-centric view of FDA data with AI summaries"""
    st.header("🔍 Device-Centric View")
    if not results:
        st.write("No device-related data found.")
        return
        
    sections = {
        "510K": "📄 Recent 510(k) Submissions",
        "PMA": "📄 Recent PMA Submissions",
        "CLASSIFICATION": "🧪 Classification Info",
        "UDI": "🔗 UDI Information",
        "EVENT": "⚠️ Adverse Events",
        "RECALL": "🚨 Recalls"
    }
    
    for key, title in sections.items():
        if key in results:
            display_section_with_ai_summary(title, results[key], key, query)

def display_manufacturer_view(results, query):
    """Display manufacturer-centric view of FDA data with AI summaries"""
    st.header("🏭 Manufacturer-Centric View")
    if not results:
        st.write("No manufacturer-related data found.")
        return
        
    sections = {
        "RECALL": "🚨 Recent Recalls",
        "EVENT": "⚠️ Adverse Events",
        "510K": "📄 510(k) Submissions",
        "PMA": "📄 PMA Submissions",
        "UDI": "🔗 UDI Entries"
    }
    
    for key, title in sections.items():
        if key in results:
            display_section_with_ai_summary(title, results[key], key, query)

def main():
    """Main application entry point"""
    st.set_page_config(page_title="FDA Device Explorer", layout="wide")
    st.title("🧠 FDA Device Explorer (Dual View with AI Insights)")
    
    query = st.text_input("Enter search term (device or manufacturer)", 
                          placeholder="e.g. Medtronic, pacemaker")

    if query:
        with st.spinner("Crunching data from FDA..."):
            results = cached_get_fda_data(query)
            
        # Display results in both views with AI summaries
        display_device_view(results.get("device"), query)
        display_manufacturer_view(results.get("manufacturer"), query)

        # Debug information (optional)
        with st.expander("Show DataFrames Info"):
            for view, tables in results.items():
                st.write(f"=== {view.upper()} VIEW ===")
                for source, df in tables.items():
                    st.write(f"{source} columns:", list(df.columns))

if __name__ == "__main__":
    main()