import pandas as pd
import requests
from collections import defaultdict
import streamlit as st
from typing import List, Dict, Tuple

def fetch_fda_data(search_term=None) -> Tuple[List, Dict]:
    """
    Fetch data from FDA API based on search term
    Returns tuple of (results, field_matches)
    """
    base_url = "https://api.fda.gov/device/udi.json"
    
    if search_term:
        # Search in each field separately to track matches
        fields = ['device_description', 'brand_name', 'gmdn_terms.name']
        results = []
        field_matches = defaultdict(list)
        
        for field in fields:
            try:
                search_query = f"{field}:{search_term}"
                params = {
                    "search": search_query,
                    "limit": 100
                }
                response = requests.get(base_url, params=params)
                if response.status_code == 200:
                    field_data = response.json().get('results', [])
                    field_matches[field] = field_data
                    results.extend(field_data)
            except Exception as e:
                st.error(f"Error searching {field}: {str(e)}")
        
        return results, field_matches
    else:
        try:
            params = {"limit": 100, "search": "brand_name:*"}
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                return response.json().get('results', []), {}
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    return [], {}

def create_device_filters(df: pd.DataFrame) -> Dict:
    """Create filter controls for device data"""
    st.sidebar.header("Filters")
    
    # Company filter
    if 'company_name' in df.columns:
        companies = sorted(df['company_name'].dropna().unique())
        selected_companies = st.sidebar.multiselect(
            "Companies",
            companies,
            default=[]
        )
    else:
        selected_companies = []
    
    # Device class filter
    if 'device_class' in df.columns:
        device_classes = sorted(df['device_class'].dropna().unique())
        selected_classes = st.sidebar.multiselect(
            "Device Classes",
            device_classes,
            default=[]
        )
    else:
        selected_classes = []
    
    # MRI safety filter
    if 'mri_safety' in df.columns:
        mri_options = sorted(df['mri_safety'].dropna().unique())
        selected_mri = st.sidebar.multiselect(
            "MRI Safety",
            mri_options,
            default=[]
        )
    else:
        selected_mri = []
    
    # Additional filters with toggles
    col1, col2 = st.sidebar.columns(2)
    with col1:
        rx_only = st.checkbox("Prescription Only")
        sterile = st.checkbox("Sterile Devices")
    with col2:
        single_use = st.checkbox("Single Use")
    
    return {
        'companies': selected_companies,
        'device_classes': selected_classes,
        'mri_safety': selected_mri,
        'rx_only': rx_only,
        'sterile': sterile,
        'single_use': single_use
    }

def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Apply selected filters to the DataFrame"""
    filtered_df = df.copy()
    
    if filters['companies'] and 'company_name' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['company_name'].isin(filters['companies'])]
    
    if filters['device_classes'] and 'device_class' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['device_class'].isin(filters['device_classes'])]
    
    if filters['mri_safety'] and 'mri_safety' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['mri_safety'].isin(filters['mri_safety'])]
    
    # Modified these conditions to check for string 'true'
    if filters['rx_only'] and 'is_rx' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['is_rx'] == 'true']
    
    if filters['sterile'] and 'sterilization.is_sterile' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['sterilization.is_sterile'] == 'true']
    
    if filters['single_use'] and 'is_single_use' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['is_single_use'] == 'true']
    
    return filtered_df

def display_device_details(device: Dict):
    """Display detailed information for a single device"""
    cols = st.columns(2)
    
    with cols[0]:
        st.markdown("### Basic Information")
        st.write(f"**Brand Name:** {device.get('brand_name', 'N/A')}")
        st.write(f"**Description:** {device.get('device_description', 'N/A')}")
        if 'gmdn_terms' in device and device['gmdn_terms']:
            st.write(f"**GMDN Category:** {device['gmdn_terms'][0].get('name', 'N/A')}")
        
        st.markdown("### Regulatory Information")
        st.write(f"**Device Class:** {device.get('device_class', 'N/A')}")
        st.write(f"**MRI Safety:** {device.get('mri_safety', 'N/A')}")
        st.write(f"**Prescription Required:** {device.get('is_rx', 'N/A')}")
        st.write(f"**Single Use:** {device.get('is_single_use', 'N/A')}")
    
    with cols[1]:
        st.markdown("### Identifiers")
        if 'identifiers' in device:
            for identifier in device['identifiers']:
                st.write(f"**ID:** {identifier.get('id', 'N/A')}")
                st.write(f"**Type:** {identifier.get('type', 'N/A')}")
                st.write(f"**Issuing Agency:** {identifier.get('issuing_agency', 'N/A')}")
                st.write("---")
        
        st.markdown("### Manufacturing Info")
        st.write(f"**Company:** {device.get('company_name', 'N/A')}")
        if 'sterilization' in device:
            st.write("**Sterilization:**")
            st.write(f"- Sterile: {device['sterilization'].get('is_sterile', 'N/A')}")
            st.write(f"- Methods: {', '.join(device['sterilization'].get('sterilization_methods', ['N/A']))}")
            
            
            
            
def get_primary_di_list(df: pd.DataFrame) -> list:
    """Extract primary DIs from the device data"""
    primary_dis = []
    for _, row in df.iterrows():
        if 'identifiers' in row and row['identifiers']:
            for identifier in row['identifiers']:
                if identifier.get('type') == 'Primary':
                    primary_dis.append({
                        'di': identifier.get('id'),
                        'brand_name': row.get('brand_name'),
                        'company': row.get('company_name')
                    })
                    break  # Only get the first Primary DI per device
    return primary_dis

def display_primary_di_section(df: pd.DataFrame):
    """Display section with Primary DIs and AccessGUDID links"""
    with st.container():
        st.subheader("🔑 Primary Device Identifiers")
        
        # Get list of primary DIs
        primary_dis = get_primary_di_list(df)
        
        # Add search/filter for DIs
        di_search = st.text_input("Search Primary DIs or device names")
        
        # Create a scrollable container for the DIs
        with st.container():
            st.caption(f"Found {len(primary_dis)} Primary DIs")
            
            # Filter based on search if provided
            if di_search:
                filtered_dis = [
                    di for di in primary_dis 
                    if (di_search.lower() in di['di'].lower() or 
                        di_search.lower() in di['brand_name'].lower())
                ]
            else:
                filtered_dis = primary_dis
            
            # Display DIs in a clean table format
            for di_info in filtered_dis:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{di_info['brand_name']}** - {di_info['company']}")
                        accessgudid_link = f"https://accessgudid.nlm.nih.gov/devices/{di_info['di']}"
                        st.markdown(f"Primary DI: [{di_info['di']}]({accessgudid_link})")
                    with col2:
                        st.markdown(f"[View in AccessGUDID ↗]({accessgudid_link})")
                st.markdown("---")