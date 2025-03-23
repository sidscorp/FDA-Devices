import requests
import pandas as pd
import json
from typing import Dict, List, Any, Tuple, Optional
import time

class FDADeviceRetriever:
    """Class to retrieve FDA device data based on product code"""
    
    BASE_URL = "https://api.fda.gov/device"
    ENDPOINTS = {
        "classification": "/classification.json",
        "510k": "/510k.json",
        "pma": "/pma.json",
        "registrationlisting": "/registrationlisting.json",
        "recall": "/recall.json",
        "enforcement": "/enforcement.json",
        "event": "/event.json",
        "udi": "/udi.json"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.results = {}
        
    def _create_query_url(self, endpoint: str, product_code: str, limit: int = 100) -> str:
        """Create the appropriate query URL based on endpoint and product code"""
        base = f"{self.BASE_URL}{endpoint}?search=product_code:{product_code}"
        
        # Add API key if provided
        if self.api_key:
            base += f"&api_key={self.api_key}"
            
        # Add limit
        base += f"&limit={limit}"
        
        return base
    
    def _make_request(self, url: str) -> Dict:
        """Make an API request and handle errors"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                # No results found
                return {"error": "No results found", "status_code": 404}
            else:
                return {"error": str(e), "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def _normalize_results(self, data: Dict, endpoint: str) -> pd.DataFrame:
        """Convert API results to a DataFrame"""
        if "error" in data:
            # Return empty DataFrame with error message
            return pd.DataFrame({"error": [data["error"]]})
        
        # Check if results exist
        if "results" not in data or not data["results"]:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.json_normalize(data["results"])
        
        # Add source column to identify which endpoint data came from
        df["data_source"] = endpoint
        
        return df
    
    def get_device_data(self, product_code: str, endpoints: Optional[List[str]] = None, 
                        limit: int = 100, delay: float = 0.1) -> Dict[str, pd.DataFrame]:
        """
        Retrieve device data for a specific product code from specified endpoints
        
        Args:
            product_code: The FDA product code to search for
            endpoints: List of specific endpoints to query (default: all endpoints)
            limit: Maximum number of records to retrieve per endpoint
            delay: Time delay between API calls in seconds
            
        Returns:
            Dictionary of DataFrames with endpoint names as keys
        """
        # Reset results
        self.results = {}
        
        # Determine which endpoints to query
        if endpoints is None:
            endpoints_to_query = self.ENDPOINTS.keys()
        else:
            endpoints_to_query = [ep for ep in endpoints if ep in self.ENDPOINTS]
        
        # Query each endpoint
        for endpoint_name in endpoints_to_query:
            endpoint_url = self.ENDPOINTS[endpoint_name]
            query_url = self._create_query_url(endpoint_url, product_code, limit)
            
            # Make the request
            response_data = self._make_request(query_url)
            
            # Process the results
            self.results[endpoint_name] = self._normalize_results(response_data, endpoint_name)
            
            # Delay to avoid rate limiting
            time.sleep(delay)
        
        return self.results
    
    def get_combined_data(self) -> pd.DataFrame:
        """Combine all results into a single DataFrame with a source column"""
        if not self.results:
            return pd.DataFrame()
        
        # Combine all DataFrames
        dfs = []
        for endpoint, df in self.results.items():
            if not df.empty and "error" not in df.columns:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
            
        return pd.concat(dfs, ignore_index=True)
    
    def get_device_details(self, product_code: str) -> Dict[str, Any]:
        """Get a summary of key device details from classification endpoint"""
        # Query the classification endpoint
        classification = self.get_device_data(product_code, ["classification"])
        
        if "classification" not in classification or classification["classification"].empty:
            return {"error": "No classification data found for this product code"}
        
        df = classification["classification"]
        
        if "error" in df.columns:
            return {"error": df["error"].iloc[0]}
        
        # Extract key information
        device_info = {
            "product_code": product_code,
            "device_name": df["device_name"].iloc[0] if "device_name" in df.columns else "Unknown",
            "device_class": df["device_class"].iloc[0] if "device_class" in df.columns else "Unknown",
            "regulation_number": df["regulation_number"].iloc[0] if "regulation_number" in df.columns else "Unknown",
            "medical_specialty": df["medical_specialty_description"].iloc[0] if "medical_specialty_description" in df.columns else "Unknown"
        }
        
        return device_info

# Example usage:
def get_fda_device_data(product_code, api_key=None):
    """
    Retrieve comprehensive FDA device data for a given product code
    
    Args:
        product_code: The FDA product code to search for (3-letter code)
        api_key: Optional API key for higher rate limits
        
    Returns:
        Dictionary containing DataFrames for each data category and a device summary
    """
    retriever = FDADeviceRetriever(api_key)
    
    # Get device summary first
    device_summary = retriever.get_device_details(product_code)
    
    # If there was an error with the basic lookup, return early
    if "error" in device_summary:
        return {"summary": device_summary, "data": {}}
    
    # Get all data
    all_data = retriever.get_device_data(product_code)
    
    # Return both the summary and detailed data
    return {
        "summary": device_summary,
        "data": all_data,
        "combined": retriever.get_combined_data()
    }

# Interactive usage example
if __name__ == "__main__":
    product_code = input("Enter FDA product code (e.g., LLZ for Radiology Picture Archiving System): ")
    result = get_fda_device_data(product_code)
    
    # Print summary
    print("\nDevice Summary:")
    for key, value in result["summary"].items():
        print(f"{key}: {value}")
    
    # Print data availability
    print("\nData Available From:")
    for endpoint, df in result["data"].items():
        if not df.empty and "error" not in df.columns:
            print(f"- {endpoint}: {len(df)} records")
        else:
            print(f"- {endpoint}: No data available")