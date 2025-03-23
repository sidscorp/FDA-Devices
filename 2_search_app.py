import streamlit as st
import pandas as pd
from fda_data import get_fda_data, DISPLAY_COLUMNS

@st.cache_data(ttl=3600, show_spinner=False)
def cached_get_fda_data(query, limit=100):
    """Cached wrapper for the FDA data retrieval function"""
    return get_fda_data(query, limit)

def display_section(title, df, source):
    """Display a section of FDA data with appropriate columns"""
    st.subheader(title)
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

def display_device_view(results):
    """Display device-centric view of FDA data"""
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
            display_section(title, results[key], key)

def display_manufacturer_view(results):
    """Display manufacturer-centric view of FDA data"""
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
            display_section(title, results[key], key)

def main():
    """Main application entry point"""
    st.set_page_config(page_title="FDA Device Explorer", layout="wide")
    st.title("🧠 FDA Device Explorer (Dual View)")
    
    query = st.text_input("Enter search term (device or manufacturer)", 
                          placeholder="e.g. Medtronic, pacemaker")

    if query:
        with st.spinner("Crunching data from FDA..."):
            results = cached_get_fda_data(query)
            
        # Display results in both views
        display_device_view(results.get("device"))
        display_manufacturer_view(results.get("manufacturer"))

        # Debug information (optional)
        with st.expander("Show DataFrames Info"):
            for view, tables in results.items():
                st.write(f"=== {view.upper()} VIEW ===")
                for source, df in tables.items():
                    st.write(f"{source} columns:", list(df.columns))

if __name__ == "__main__":
    main()