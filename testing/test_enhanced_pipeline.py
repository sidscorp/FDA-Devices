"""
Test script for the enhanced FDA data pipeline
Tests the complete flow from query to comprehensive analysis.
"""

import sys
sys.path.append('..')  # Add parent directory to path

from data_retrieval_enhanced import EnhancedFDARetriever
from query_intelligence import QueryIntelligence
from data_relationships import DataRelationshipMapper
import pandas as pd
from datetime import datetime

def test_complete_pipeline(query: str):
    """Test the complete enhanced pipeline."""
    print(f"Testing Enhanced FDA Pipeline for: '{query}'")
    print("=" * 60)
    
    # Step 1: Query Intelligence
    print("\n1. QUERY ANALYSIS")
    qi = QueryIntelligence()
    context = qi.analyze_query(query)
    
    print(f"Query Type: {context.query_type}")
    print(f"Expanded Terms: {context.expanded_terms[:3]}")
    print(f"Medical Context: {context.medical_terms}")
    print(f"Regulatory Context: {context.regulatory_keywords}")
    
    # Step 2: Enhanced Data Retrieval
    print("\n2. DATA RETRIEVAL")
    retriever = EnhancedFDARetriever(rate_limit_delay=0.1)  # Faster for testing
    
    # Get comprehensive data
    fda_data = retriever.get_cross_referenced_data(query, lookback_years=2)
    
    total_records = sum(len(df) for df in fda_data.values())
    print(f"Total Records Retrieved: {total_records}")
    
    for source, df in fda_data.items():
        if not df.empty:
            print(f"  {source}: {len(df)} records")
            # Show sample data
            print(f"    Sample columns: {list(df.columns)[:5]}")
        else:
            print(f"  {source}: No data")
    
    # Step 3: Relationship Mapping
    print("\n3. RELATIONSHIP MAPPING")
    mapper = DataRelationshipMapper()
    
    if fda_data:
        profile = mapper.create_comprehensive_profile(fda_data, query)
        summary = mapper.generate_regulatory_summary(profile)
        
        print(f"Device Profile Created:")
        print(f"  Risk Score: {profile.risk_score}")
        print(f"  Manufacturers: {len(profile.manufacturers)}")
        print(f"  Product Codes: {len(profile.product_codes)}")
        print(f"  Timeline Events: {len(profile.timeline)}")
        
        print(f"\nRegulatory Summary:")
        print(f"  510K Clearances: {summary['regulatory_history']['total_510k_clearances']}")
        print(f"  Recalls: {summary['regulatory_history']['total_recalls']}")
        print(f"  Adverse Events: {summary['regulatory_history']['total_adverse_events']}")
        print(f"  Class I Recalls: {summary['safety_signals']['class_1_recalls']}")
        
        # Show recent timeline
        if profile.timeline:
            print(f"\nRecent Activity (last 5 events):")
            for date, event_type, description in profile.timeline[-5:]:
                date_str = date.strftime("%Y-%m-%d") if date else "Unknown"
                print(f"  {date_str}: {event_type} - {description[:80]}...")
    else:
        print("No data available for relationship mapping")
    
    return fda_data, profile if 'profile' in locals() else None

def compare_with_original():
    """Compare enhanced pipeline with original approach."""
    print("\n" + "=" * 60)
    print("COMPARISON WITH ORIGINAL APPROACH")
    print("=" * 60)
    
    # Import original functions
    from fda_data import get_fda_data
    
    test_query = "insulin pump"
    
    # Original approach
    print(f"\nOriginal approach for '{test_query}':")
    original_data = get_fda_data(test_query, "device", limit=100, date_months=6)
    
    original_total = 0
    for category in original_data.values():
        for source, df in category.items():
            original_total += len(df)
            
    print(f"Original total records: {original_total}")
    
    # Enhanced approach
    print(f"\nEnhanced approach for '{test_query}':")
    enhanced_data, profile = test_complete_pipeline(test_query)
    
    enhanced_total = sum(len(df) for df in enhanced_data.values())
    print(f"Enhanced total records: {enhanced_total}")
    
    print(f"\nImprovement: {enhanced_total - original_total} additional records")
    print(f"Ratio: {enhanced_total / max(original_total, 1):.2f}x more data")

if __name__ == "__main__":
    # Test with different query types
    test_queries = [
        "insulin pump",
        "Medtronic",
        "hip replacement",
        "pacemaker recall"
    ]
    
    for query in test_queries:
        try:
            fda_data, profile = test_complete_pipeline(query)
            print("\n" + "-" * 40 + "\n")
        except Exception as e:
            print(f"Error testing '{query}': {e}")
            continue
    
    # Run comparison
    try:
        compare_with_original()
    except Exception as e:
        print(f"Error in comparison: {e}")