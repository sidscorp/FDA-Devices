#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fda_data import get_fda_data
from llm_utils import run_llm_analysis

def test_basic_workflow():
    print("🧪 Basic FDA + AI Test")
    print("=" * 30)
    
    # Test FDA data retrieval
    print("1. Testing FDA data retrieval...")
    try:
        results = get_fda_data("pacemaker", "device", limit=3, date_months=12)
        
        if results and "device" in results:
            data = results["device"]
            total_records = sum(len(df) for df in data.values())
            print(f"   ✓ Retrieved {total_records} records")
            
            # Find first non-empty dataset
            for source, df in data.items():
                if not df.empty:
                    print(f"   ✓ Found {source} data: {len(df)} records")
                    
                    # Test AI analysis on this data
                    print(f"2. Testing AI analysis on {source}...")
                    summary = run_llm_analysis(df, source, "pacemaker", "device")
                    
                    if "unavailable" in summary:
                        print(f"   ✗ AI failed: {summary}")
                        return False
                    else:
                        print(f"   ✓ AI analysis successful!")
                        print(f"   Summary: {summary[:150]}...")
                        return True
            
            print("   ⚠ No data found in any source")
            return False
        else:
            print("   ✗ No results returned")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_basic_workflow()
    if success:
        print("\n🎉 Basic workflow works! Ready to run the full app.")
    else:
        print("\n❌ Basic workflow failed.")
    sys.exit(0 if success else 1)