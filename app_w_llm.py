import streamlit as st
import pandas as pd
from data_retrieval_enhanced import EnhancedFDARetriever
from config import SAMPLE_SIZE_OPTIONS, DATE_RANGE_OPTIONS, DEFAULT_SAMPLE_SIZE, DEFAULT_DATE_MONTHS
import os
import json
from llm_utils import display_section_with_ai_summary, run_llm_analysis

@st.cache_data(ttl=3600, show_spinner=False)
def cached_get_fda_data(query, query_type, limit=20, date_months=6):
    """Enhanced cached wrapper for FDA data retrieval"""
    
    # Use enhanced retrieval
    retriever = EnhancedFDARetriever(rate_limit_delay=0.2)
    lookback_years = max(1, date_months / 12)  # Convert months to years
    
    # Get enhanced data
    enhanced_data = retriever.get_cross_referenced_data(query, lookback_years=lookback_years)
    
    # Adapt enhanced data format to match original app expectations
    # Original app expects: {"device": {"SOURCE": df}, "manufacturer": {"SOURCE": df}}
    
    results = {"device": {}, "manufacturer": {}}
    
    # Map enhanced data to both views (since enhanced data is comprehensive)
    for source, df in enhanced_data.items():
        if not df.empty:
            # Limit to requested sample size
            sampled_df = df.head(limit)
            
            # Add to both device and manufacturer views 
            # (enhanced data is comprehensive enough for both)
            results["device"][source] = sampled_df
            results["manufacturer"][source] = sampled_df
    
    return results

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

def display_device_view(results, query, show_raw_data=False):
    st.session_state.section_results = {}

    if not results:
        st.write("No recent device-related data found.")
        return

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
  
        if "RECALL" in results:
            display_section_with_ai_summary("🚨 Recent Recalls", results["RECALL"], "RECALL", query, "device", show_raw_data)
        else:
            st.subheader("🚨 Recent Recalls")
            st.info("No recent recall data found.")
    with row1_col2:
        if "EVENT" in results:
            display_section_with_ai_summary("⚠️ Recent Adverse Events", results["EVENT"], "EVENT", query, "device", show_raw_data)
        else:
            st.subheader("⚠️ Recent Adverse Events")
            st.info("No recent adverse event data found.")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        if "PMA" in results:
            display_section_with_ai_summary("📄 Recent PMA Submissions", results["PMA"], "PMA", query, "device", show_raw_data)
        else:
            st.subheader("📄 Recent PMA Submissions")
            st.info("No recent PMA submission data found.")
    with row2_col2:
        if "510K" in results:
            display_section_with_ai_summary("📄 Latest 510(k) Submissions", results["510K"], "510K", query, "device", show_raw_data)
        else:
            st.subheader("📄 Latest 510(k) Submissions")
            st.info("No recent 510(k) submission data found.")

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        if "UDI" in results:
            display_section_with_ai_summary("🔗 UDI Database Entries", results["UDI"], "UDI", query, "device", show_raw_data)
        else:
            st.subheader("🔗 UDI Database Entries")
            st.info("No UDI database entries found.")
    with row3_col2:
        if "CLASSIFICATION" in results:
            display_section_with_ai_summary("🧪 Regulatory Classification", results["CLASSIFICATION"], "CLASSIFICATION", query, "device", show_raw_data)
        else:
            st.subheader("🧪 Regulatory Classification")
            st.info("No classification data found.")



def display_manufacturer_view(results, query, show_raw_data=False):
    """Display manufacturer-centric view of FDA data with AI summaries in fixed layout"""
    
    # Clear previous section results at the beginning of a new search
    st.session_state.section_results = {}
    
    if not results:
        st.write("No recent manufacturer-related data found.")
        return
    
    # Row 1: Recalls and Events
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        if "RECALL" in results:
            display_section_with_ai_summary("🚨 Recent Recalls", results["RECALL"], "RECALL", query, "manufacturer", show_raw_data)
        else:
            st.subheader("🚨 Recent Recalls")
            st.info("No recent recall data found.")
    
    with row1_col2:
        if "EVENT" in results:
            display_section_with_ai_summary("⚠️ Recent Adverse Events", results["EVENT"], "EVENT", query, "manufacturer", show_raw_data)
        else:
            st.subheader("⚠️ Recent Adverse Events")
            st.info("No recent adverse event data found.")
    
    # Row 2: PMA and 510K
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        if "PMA" in results:
            display_section_with_ai_summary("📄 Recent PMA Submissions", results["PMA"], "PMA", query, "manufacturer", show_raw_data)
        else:
            st.subheader("📄 Recent PMA Submissions")
            st.info("No recent PMA submission data found.")
    
    with row2_col2:
        if "510K" in results:
            display_section_with_ai_summary("📄 Latest 510(k) Submissions", results["510K"], "510K", query, "manufacturer", show_raw_data)
        else:
            st.subheader("📄 Latest 510(k) Submissions")
            st.info("No recent 510(k) submission data found.")
    
    # Row 3: UDI and Classification (Note: Manufacturer view might not have Classification data)
    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        if "UDI" in results:
            display_section_with_ai_summary("🔗 UDI Database Entries", results["UDI"], "UDI", query, "manufacturer", show_raw_data)
        else:
            st.subheader("🔗 UDI Database Entries")
            st.info("No UDI database entries found.")
    
    with row3_col2:
        if "CLASSIFICATION" in results:
            display_section_with_ai_summary("🧪 Regulatory Classification", results["CLASSIFICATION"], "CLASSIFICATION", query, "manufacturer", show_raw_data)
        else:
            st.subheader("🧪 Regulatory Classification")
            st.info("No classification data found.")

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

    st.markdown("## 🔍 FDA Data Explorer")
    st.caption("Developed by Dr. Sidd Nambiar · Sr. Lead Scientist @ Booz Allen Hamilton")
    
    st.error("""
    ⚠️ **UNOFFICIAL TOOL**: This is an independent research demo and is NOT affiliated with, endorsed by, 
    or representing the U.S. Food and Drug Administration. All data comes from the public openFDA API.
    """)

    st.markdown("""
    <div style='font-size: 0.9rem; color: gray; margin-bottom: 1rem;'>
    This app provides a demo of real-time FDA regulatory activity monitoring using openFDA data and AI-powered insights.
    </div>
    """, unsafe_allow_html=True)

    add_about_button()

    with st.expander("⚙️ Configuration", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            sample_size = st.selectbox("Sample Size", SAMPLE_SIZE_OPTIONS, index=0)
        with col2:
            date_range = st.selectbox("Date Range (months)", DATE_RANGE_OPTIONS, index=1)
        with col3:
            show_raw_data = st.checkbox("Show Raw Data", value=False)
            
    st.success("""
    **🚀 Enhanced Analysis**: This tool now uses comprehensive data retrieval across all FDA databases 
    with intelligent query processing. Results provide much more complete regulatory intelligence compared 
    to simple sampling approaches.
    """)

    query = st.text_input("Enter device name or manufacturer", 
                        placeholder="e.g. Medtronic, pacemaker, insulin pump")


    if query:
        with st.spinner("Analyzing query..."):
            corrected_query, query_type = determine_query_type(query)
            
        st.info(f"🚀 Using enhanced retrieval for this {query_type}: **{corrected_query}**")
            
        with st.spinner("Gathering comprehensive FDA data (this may take 30-60 seconds)..."):
            results = cached_get_fda_data(corrected_query, query_type, sample_size, date_range)
        
        if query_type == "device":
            display_device_view(results.get("device"), query, show_raw_data)
        else:
            display_manufacturer_view(results.get("manufacturer"), query, show_raw_data)

        st.caption(f"""
        📊 **Enhanced Analysis**: Retrieved comprehensive data across all FDA sources, displaying top {sample_size} records per section 
        from the last {date_range} months. AI insights analyze the full dataset for more accurate regulatory intelligence.
        """)

        with st.expander("🔍 Developer Information"):
            for view, tables in results.items():
                if view == query_type:
                    st.write(f"**{view.upper()} VIEW DATA**")
                    for source, df in tables.items():
                        st.write(f"- {source}: {len(df)} records, {len(df.columns)} fields")
                        if not df.empty:
                            date_col = next((col for col in ["date_received", "decision_date", "event_date_initiated"] if col in df.columns), None)
                            if date_col:
                                min_date = pd.to_datetime(df[date_col]).min().strftime('%Y-%m-%d')
                                max_date = pd.to_datetime(df[date_col]).max().strftime('%Y-%m-%d')
                                st.write(f"  Date range: {min_date} to {max_date}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.stop()