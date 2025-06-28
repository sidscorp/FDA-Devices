"""
Debug FDA API query syntax issues
"""

import requests
import pandas as pd
from urllib.parse import urlencode

def test_simple_queries():
    """Test simple working queries to understand proper syntax."""
    
    base_url = "https://api.fda.gov/device/event.json"
    
    # Test queries that should work
    test_cases = [
        {"search": "device.brand_name:medtronic", "description": "Simple brand search"},
        {"search": "device.generic_name:pump", "description": "Simple generic search"},
        {"search": "device.brand_name:insulin", "description": "Simple insulin search"},
        {"search": "manufacturer_name:medtronic", "description": "Manufacturer search"},
        {"search": "(device.brand_name:medtronic OR manufacturer_name:medtronic)", "description": "OR query"},
        {"search": "device.brand_name:insulin AND device.generic_name:pump", "description": "AND query"},
    ]
    
    print("Testing FDA API Query Syntax")
    print("=" * 50)
    
    for test in test_cases:
        try:
            params = {"search": test["search"], "limit": 5}
            response = requests.get(base_url, params=params, timeout=10)
            
            print(f"\n{test['description']}:")
            print(f"Query: {test['search']}")
            print(f"URL: {response.url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("meta", {}).get("results", {}).get("total", 0)
                results_count = len(data.get("results", []))
                print(f"Total available: {total}")
                print(f"Returned: {results_count}")
                
                if results_count > 0:
                    # Show first result structure
                    first_result = data["results"][0]
                    print(f"Sample fields: {list(first_result.keys())[:5]}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

def test_recall_api():
    """Test recall API specifically."""
    
    base_url = "https://api.fda.gov/device/recall.json"
    
    test_cases = [
        {"search": "product_description:pump", "description": "Product description search"},
        {"search": "recalling_firm:medtronic", "description": "Recalling firm search"},
        {"search": "recall_status:ongoing", "description": "Status search"},
    ]
    
    print("\n\nTesting Recall API")
    print("=" * 50)
    
    for test in test_cases:
        try:
            params = {"search": test["search"], "limit": 3}
            response = requests.get(base_url, params=params, timeout=10)
            
            print(f"\n{test['description']}:")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("meta", {}).get("results", {}).get("total", 0)
                print(f"Total: {total}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

def test_working_insulin_pump_search():
    """Find the right way to search for insulin pump data."""
    
    print("\n\nFinding Working Insulin Pump Searches")
    print("=" * 50)
    
    # Test different approaches for insulin pump
    searches = [
        "device.brand_name:insulin",
        "device.generic_name:pump", 
        "device.generic_name:insulin",
        "manufacturer_name:medtronic",
        "product_problems:insulin",
        "device.brand_name:omnipod",
        "device.brand_name:tandem"
    ]
    
    base_url = "https://api.fda.gov/device/event.json"
    
    for search in searches:
        try:
            params = {"search": search, "limit": 1}
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("meta", {}).get("results", {}).get("total", 0)
                if total > 0:
                    print(f"✓ '{search}' found {total} records")
                    
                    # Show sample data
                    if data.get("results"):
                        result = data["results"][0]
                        device_info = result.get("device", [{}])[0] if result.get("device") else {}
                        brand = device_info.get("brand_name", "N/A")
                        generic = device_info.get("generic_name", "N/A") 
                        mfg = result.get("manufacturer_name", "N/A")
                        print(f"  Sample: Brand={brand}, Generic={generic}, Mfg={mfg}")
                else:
                    print(f"✗ '{search}' found 0 records")
            else:
                print(f"✗ '{search}' failed: {response.status_code}")
                
        except Exception as e:
            print(f"✗ '{search}' error: {e}")

if __name__ == "__main__":
    test_simple_queries()
    test_recall_api()
    test_working_insulin_pump_search()