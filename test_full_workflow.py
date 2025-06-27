#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fda_data import get_fda_data
from llm_utils import run_llm_analysis
from openrouter_api import OpenRouterAPI
import pandas as pd

def test_api_connection():
    """Test basic OpenRouter API connectivity"""
    print("🔧 Testing OpenRouter API connection...")
    try:
        api = OpenRouterAPI()
        print(f"✓ API key loaded: {api.api_key[:8]}...")
        
        messages = [{"role": "user", "content": "Reply with just: API_TEST_SUCCESS"}]
        result = api.chat_with_fallback(messages, max_tokens=20, temperature=0.1)
        
        if result['success']:
            print(f"✓ API connection successful!")
            print(f"✓ Model: {result['model']}")
            print(f"✓ Response: {result['response'].strip()}")
            return True
        else:
            print(f"✗ API connection failed: {result['error']}")
            return False
    except Exception as e:
        print(f"✗ API test failed: {str(e)}")
        return False

def test_fda_data_retrieval():
    """Test FDA data retrieval functionality"""
    print("\n🔍 Testing FDA data retrieval...")
    
    test_queries = [
        ("pacemaker", "device"),
        ("Medtronic", "manufacturer")
    ]
    
    for query, query_type in test_queries:
        print(f"\n  Testing: '{query}' as {query_type}")
        try:
            results = get_fda_data(query, query_type, limit=5, date_months=6)
            
            if results and query_type in results:
                data = results[query_type]
                total_records = sum(len(df) for df in data.values())
                
                print(f"  ✓ Retrieved {total_records} total records")
                for source, df in data.items():
                    if not df.empty:
                        print(f"    - {source}: {len(df)} records")
                
                if total_records > 0:
                    return results, query, query_type
                    
            print(f"  ⚠ No data found for {query}")
            
        except Exception as e:
            print(f"  ✗ FDA data retrieval failed: {str(e)}")
    
    return None, None, None

def test_ai_analysis(results, query, query_type):
    """Test AI analysis of FDA data"""
    print(f"\n🤖 Testing AI analysis for '{query}' ({query_type})...")
    
    if not results or query_type not in results:
        print("  ✗ No data to analyze")
        return False
    
    data = results[query_type]
    analysis_count = 0
    
    for source, df in data.items():
        if not df.empty:
            print(f"\n  Analyzing {source} data ({len(df)} records)...")
            try:
                summary = run_llm_analysis(df, source, query, query_type)
                
                if "AI analysis unavailable" in summary:
                    print(f"    ✗ Analysis failed: {summary}")
                else:
                    print(f"    ✓ Analysis successful!")
                    print(f"    Summary preview: {summary[:100]}...")
                    analysis_count += 1
                    
            except Exception as e:
                print(f"    ✗ Analysis error: {str(e)}")
    
    if analysis_count > 0:
        print(f"\n✓ AI analysis successful for {analysis_count} data sources")
        return True
    else:
        print("\n✗ No successful AI analyses")
        return False

def test_query_classification():
    """Test AI-powered query classification"""
    print("\n🔍 Testing query classification...")
    
    from app_w_llm import determine_query_type
    
    test_cases = [
        ("insulin pump", "device"),
        ("Medtronic Inc", "manufacturer"),
        ("pacemaker", "device"),
        ("Abbott", "manufacturer")
    ]
    
    success_count = 0
    for query, expected_type in test_cases:
        try:
            corrected_query, detected_type = determine_query_type(query)
            print(f"  '{query}' -> '{corrected_query}' ({detected_type})")
            
            if detected_type == expected_type:
                print(f"    ✓ Correct classification")
                success_count += 1
            else:
                print(f"    ⚠ Expected {expected_type}, got {detected_type}")
                
        except Exception as e:
            print(f"    ✗ Classification failed: {str(e)}")
    
    print(f"\n✓ Query classification: {success_count}/{len(test_cases)} correct")
    return success_count > 0

def main():
    """Run complete workflow test"""
    print("🧪 FDA Data Explorer - Complete Workflow Test")
    print("=" * 50)
    
    # Test 1: API Connection
    api_ok = test_api_connection()
    if not api_ok:
        print("\n❌ FAILED: Cannot proceed without API connection")
        return False
    
    # Test 2: FDA Data Retrieval
    results, query, query_type = test_fda_data_retrieval()
    if not results:
        print("\n❌ FAILED: Cannot retrieve FDA data")
        return False
    
    # Test 3: AI Analysis
    analysis_ok = test_ai_analysis(results, query, query_type)
    if not analysis_ok:
        print("\n❌ FAILED: AI analysis not working")
        return False
    
    # Test 4: Query Classification
    classification_ok = test_query_classification()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"✓ OpenRouter API: {'PASS' if api_ok else 'FAIL'}")
    print(f"✓ FDA Data Retrieval: {'PASS' if results else 'FAIL'}")
    print(f"✓ AI Analysis: {'PASS' if analysis_ok else 'FAIL'}")
    print(f"✓ Query Classification: {'PASS' if classification_ok else 'FAIL'}")
    
    all_tests_passed = all([api_ok, results, analysis_ok, classification_ok])
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED - Ready to run the app!")
        print("\nTo start the app, run:")
        print("  streamlit run app_w_llm.py")
    else:
        print("\n⚠️  Some tests failed - check the errors above")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)