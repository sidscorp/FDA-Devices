"""
Simple test of the enhanced retrieval with fixed API syntax
"""

import sys
sys.path.append('..')

from data_retrieval_enhanced import EnhancedFDARetriever
import pandas as pd

def test_enhanced_retrieval():
    """Test the enhanced retrieval with a simple query."""
    
    print("Testing Enhanced FDA Retrieval")
    print("=" * 40)
    
    retriever = EnhancedFDARetriever(rate_limit_delay=0.2)
    
    # Test with insulin pump - we know this works
    query = "insulin pump"
    print(f"Testing query: '{query}'")
    
    # Test individual sources first
    sources = ["event", "recall"]  # Start with sources we know work
    
    for source in sources:
        print(f"\nTesting {source.upper()} source:")
        try:
            df = retriever.get_comprehensive_data(query, source, max_records=50)
            print(f"  Records found: {len(df)}")
            
            if not df.empty:
                print(f"  Columns: {list(df.columns)[:8]}")
                
                # Show some sample data
                if source == "event":
                    for i, row in df.head(3).iterrows():
                        device = row.get('device.brand_name', 'N/A')
                        generic = row.get('device.generic_name', 'N/A')
                        print(f"    Sample {i+1}: {device} / {generic}")
                        
                elif source == "recall":
                    for i, row in df.head(3).iterrows():
                        product = row.get('product_description', 'N/A')
                        firm = row.get('recalling_firm', 'N/A')
                        print(f"    Sample {i+1}: {product[:50]}... / {firm}")
                        
        except Exception as e:
            print(f"  Error: {e}")
    
    # Test cross-referenced data
    print(f"\nTesting cross-referenced data retrieval:")
    try:
        all_data = retriever.get_cross_referenced_data(query, lookback_years=1)
        
        total_records = sum(len(df) for df in all_data.values())
        print(f"Total records across all sources: {total_records}")
        
        for source, df in all_data.items():
            if not df.empty:
                print(f"  {source}: {len(df)} records")
            else:
                print(f"  {source}: No data")
                
        return all_data
        
    except Exception as e:
        print(f"Error in cross-referenced retrieval: {e}")
        return {}

def compare_with_original():
    """Quick comparison with original approach."""
    print(f"\n\nComparison with Original")
    print("=" * 40)
    
    try:
        from fda_data import get_fda_data
        
        query = "insulin pump"
        
        # Original approach
        original_data = get_fda_data(query, "device", limit=100, date_months=6)
        original_total = sum(sum(len(df) for df in category.values()) for category in original_data.values())
        print(f"Original approach: {original_total} records")
        
        # Enhanced approach  
        enhanced_data = test_enhanced_retrieval()
        enhanced_total = sum(len(df) for df in enhanced_data.values())
        print(f"Enhanced approach: {enhanced_total} records")
        
        if original_total > 0:
            ratio = enhanced_total / original_total
            print(f"Improvement ratio: {ratio:.2f}x")
        else:
            print("Original returned no data for comparison")
            
    except Exception as e:
        print(f"Comparison failed: {e}")

if __name__ == "__main__":
    test_enhanced_retrieval()
    compare_with_original()