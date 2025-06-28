"""
Enhanced FDA Data Retrieval with Comprehensive Coverage
Addresses limitations of current sampling approach.
"""

import requests
import pandas as pd
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

FDA_ENDPOINTS = {
    "510k": "https://api.fda.gov/device/510k.json",
    "event": "https://api.fda.gov/device/event.json", 
    "recall": "https://api.fda.gov/device/recall.json",
    "classification": "https://api.fda.gov/device/classification.json",
    "pma": "https://api.fda.gov/device/pma.json",
    "udi": "https://api.fda.gov/device/udi.json"
}

class EnhancedFDARetriever:
    def __init__(self, rate_limit_delay=0.5):
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """Make rate-limited API request with error handling."""
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return None
            
    def get_comprehensive_data(self, query: str, source: str, max_records: int = 1000) -> pd.DataFrame:
        """Retrieve comprehensive data using pagination."""
        url = FDA_ENDPOINTS.get(source.lower())
        if not url:
            return pd.DataFrame()
            
        all_results = []
        skip = 0
        limit = 100  # FDA API limit per request
        
        # Build search query with multiple field variants
        search_queries = self._build_comprehensive_search(query, source)
        
        for search_query in search_queries:
            skip = 0
            while len(all_results) < max_records:
                params = {
                    "search": search_query,
                    "limit": min(limit, max_records - len(all_results)),
                    "skip": skip
                }
                
                # Add sorting for consistent pagination
                if source.lower() in ["event", "recall"]:
                    params["sort"] = "date_received:desc" if source.lower() == "event" else "event_date_initiated:desc"
                elif source.lower() in ["510k", "pma"]:
                    params["sort"] = "decision_date:desc"
                    
                data = self._make_request(url, params)
                if not data or 'results' not in data or not data['results']:
                    break
                    
                all_results.extend(data['results'])
                
                # Check if we got fewer results than requested (end of data)
                if len(data['results']) < limit:
                    break
                    
                skip += limit
                
            # If we found enough results with first query, break
            if len(all_results) >= max_records * 0.8:
                break
                
        return self._process_results(all_results, source)
    
    def _build_comprehensive_search(self, query: str, source: str) -> List[str]:
        """Build multiple search variants for comprehensive coverage."""
        queries = []
        
        # Clean query - use spaces, not + for multi-word terms
        words = query.strip().lower().split()
        
        # Search field mappings per source (using working fields only)
        field_maps = {
            "510k": ["device_name", "applicant"],
            "event": ["device.brand_name", "device.generic_name"],  # manufacturer_name doesn't work
            "recall": ["product_description", "recalling_firm"],
            "classification": ["device_name", "medical_specialty_description"],
            "pma": ["trade_name", "generic_name", "applicant"],
            "udi": ["brand_name", "device_description", "company_name"]
        }
        
        fields = field_maps.get(source.lower(), [])
        if not fields:
            return []
        
        # Strategy 1: AND search for multi-word queries
        if len(words) > 1:
            and_conditions = []
            for field in fields:
                field_conditions = []
                for word in words:
                    field_conditions.append(f"{field}:{word}")
                and_conditions.append(f"({' AND '.join(field_conditions)})")
            queries.append(f"({' OR '.join(and_conditions)})")
        
        # Strategy 2: Individual word searches across fields
        for word in words:
            if len(word) > 2:  # Skip very short words
                word_queries = [f"{field}:{word}" for field in fields]
                queries.append(f"({' OR '.join(word_queries)})")
        
        # Strategy 3: Exact phrase in each field (for single words or quoted phrases)
        single_query = ' '.join(words)
        if ' ' not in single_query or len(words) == 1:
            exact_queries = [f"{field}:{single_query}" for field in fields]
            queries.append(f"({' OR '.join(exact_queries)})")
        
        return queries[:3]  # Limit to 3 strategies to avoid overload
    
    def _process_results(self, results: List[Dict], source: str) -> pd.DataFrame:
        """Process raw API results into structured DataFrame."""
        if not results:
            return pd.DataFrame()
            
        df = pd.json_normalize(results, sep='.')
        
        # Enhanced processing for nested structures
        if source.upper() == "EVENT":
            df = self._process_event_data(df, results)
        
        # Standardize date columns
        df = self._standardize_dates(df, source)
        
        # Add metadata columns
        df['source'] = source.upper()
        df['retrieved_at'] = datetime.now()
        
        return df
    
    def _process_event_data(self, df: pd.DataFrame, results: List[Dict]) -> pd.DataFrame:
        """Enhanced processing for complex event data structure."""
        for idx, result in enumerate(results):
            # Extract device information
            if 'device' in result and result['device']:
                for device in result['device'][:3]:  # Process up to 3 devices per report
                    for field in ['brand_name', 'generic_name', 'device_report_product_code']:
                        if field in device:
                            df.at[idx, f'device.{field}'] = device[field]
            
            # Extract patient outcomes
            if 'patient' in result and result['patient']:
                outcomes = []
                for patient in result['patient']:
                    if 'sequence_number_outcome' in patient:
                        outcomes.extend(patient['sequence_number_outcome'])
                if outcomes:
                    df.at[idx, 'patient_outcomes'] = '; '.join(outcomes)
                    
        return df
    
    def _standardize_dates(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Standardize date formats across sources."""
        date_fields = {
            "event": ["date_received", "date_of_event"],
            "recall": ["event_date_initiated", "recall_initiation_date"],
            "510k": ["decision_date", "date_received"],
            "pma": ["decision_date", "date_received"]
        }
        
        fields = date_fields.get(source.lower(), [])
        for field in fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')
                
        return df
    
    def get_cross_referenced_data(self, query: str, lookback_years: int = 3) -> Dict[str, pd.DataFrame]:
        """Get comprehensive cross-referenced data across all sources."""
        results = {}
        cutoff_date = datetime.now() - timedelta(days=lookback_years * 365)
        
        # Priority order for data retrieval
        source_priority = ["classification", "udi", "510k", "pma", "recall", "event"]
        
        for source in source_priority:
            print(f"Retrieving {source.upper()} data...")
            df = self.get_comprehensive_data(query, source, max_records=500)
            
            if not df.empty:
                # Apply date filtering where appropriate
                if source in ["recall", "event", "510k", "pma"]:
                    df = self._filter_by_date(df, source, cutoff_date)
                    
                results[source.upper()] = df
                print(f"Found {len(df)} records in {source.upper()}")
            else:
                print(f"No data found in {source.upper()}")
                
        return results
    
    def _filter_by_date(self, df: pd.DataFrame, source: str, cutoff_date: datetime) -> pd.DataFrame:
        """Filter DataFrame by date with source-specific logic."""
        date_field_map = {
            "recall": "event_date_initiated",
            "event": "date_received", 
            "510k": "decision_date",
            "pma": "decision_date"
        }
        
        date_field = date_field_map.get(source.lower())
        if date_field and date_field in df.columns:
            return df[df[date_field] >= cutoff_date]
        return df


if __name__ == "__main__":
    # Test the enhanced retrieval
    retriever = EnhancedFDARetriever()
    
    # Test with a sample query
    test_query = "insulin pump"
    print(f"Testing enhanced retrieval for: {test_query}")
    
    results = retriever.get_cross_referenced_data(test_query, lookback_years=2)
    
    print("\nSummary:")
    for source, df in results.items():
        print(f"{source}: {len(df)} records")