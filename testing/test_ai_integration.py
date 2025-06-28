"""
Test AI integration with enhanced data
"""

import sys
sys.path.append('..')

from data_retrieval_enhanced import EnhancedFDARetriever
from data_relationships import DataRelationshipMapper
from query_intelligence import QueryIntelligence
from llm_utils import run_llm_analysis
import pandas as pd

def test_enhanced_ai_pipeline():
    """Test the complete enhanced pipeline with AI analysis."""
    
    print("Testing Enhanced AI Pipeline")
    print("=" * 50)
    
    # Step 1: Query Intelligence
    query = "insulin pump"
    qi = QueryIntelligence()
    context = qi.analyze_query(query)
    
    print(f"Query: {query}")
    print(f"Type: {context.query_type}")
    print(f"Expanded terms: {context.expanded_terms[:3]}")
    print(f"Medical context: {context.medical_terms}")
    
    # Step 2: Enhanced Data Retrieval
    print(f"\nData Retrieval:")
    retriever = EnhancedFDARetriever(rate_limit_delay=0.1)
    fda_data = retriever.get_cross_referenced_data(query, lookback_years=1)
    
    total_records = sum(len(df) for df in fda_data.values())
    print(f"Total records: {total_records}")
    
    # Step 3: Relationship Mapping
    print(f"\nRelationship Analysis:")
    mapper = DataRelationshipMapper()
    profile = mapper.create_comprehensive_profile(fda_data, query)
    summary = mapper.generate_regulatory_summary(profile)
    
    print(f"Risk Score: {profile.risk_score}")
    print(f"Manufacturers: {list(profile.manufacturers)[:3]}")
    print(f"Timeline events: {len(profile.timeline)}")
    print(f"Class I recalls: {summary['safety_signals']['class_1_recalls']}")
    
    # Step 4: AI Analysis of Different Data Types
    print(f"\nAI Analysis:")
    
    ai_results = {}
    
    # Analyze each source with substantial data
    for source, df in fda_data.items():
        if len(df) >= 10:  # Only analyze sources with enough data
            print(f"\nAnalyzing {source} ({len(df)} records)...")
            
            try:
                # Use enhanced data preparation
                sample_size = min(20, len(df))
                sample_df = df.head(sample_size)
                
                # Create custom prompts based on source type
                custom_prompt = create_enhanced_prompt(sample_df, source, query, profile)
                
                analysis = run_llm_analysis(
                    sample_df, 
                    source, 
                    query, 
                    context.query_type, 
                    custom_prompt=custom_prompt
                )
                
                ai_results[source] = analysis
                print(f"✓ {source} analysis completed")
                print(f"Preview: {analysis[:100]}...")
                
            except Exception as e:
                print(f"✗ {source} analysis failed: {e}")
                ai_results[source] = f"Analysis failed: {str(e)}"
    
    # Step 5: Generate Comprehensive Summary
    print(f"\nGenerating Comprehensive Summary...")
    
    comprehensive_summary = generate_comprehensive_summary(
        query, profile, summary, ai_results
    )
    
    print("=" * 50)
    print("COMPREHENSIVE ANALYSIS RESULTS")
    print("=" * 50)
    print(comprehensive_summary)
    
    return profile, ai_results, comprehensive_summary

def create_enhanced_prompt(df, source, query, profile):
    """Create enhanced prompts based on source type and regulatory context."""
    
    base_context = f"Analyzing {source} data for '{query}' with {len(df)} records"
    
    if source == "RECALL":
        return f"""
{base_context}. Focus on recall patterns, classifications, and safety implications.

Device Risk Context:
- Risk Score: {profile.risk_score}
- Total Recalls: {len(profile.recalls)}
- Class I Recalls: {len([r for r in profile.recalls if 'I' in str(r.get('recall_classification', ''))])}

Key Questions:
1. What are the most serious recall patterns?
2. Which manufacturers have multiple recalls?
3. What are the common failure modes?
4. Are there any Class I (life-threatening) recalls?

Provide a regulatory-focused analysis with specific risk implications.
"""
    
    elif source == "EVENT":
        return f"""
{base_context}. Focus on adverse event patterns and safety signals.

Device Risk Context:
- Risk Score: {profile.risk_score}
- Total Adverse Events: {len(profile.adverse_events)}
- Known Manufacturers: {list(profile.manufacturers)[:3]}

Key Questions:
1. What are the most common adverse events?
2. Are there patterns indicating systemic issues?
3. Which manufacturers have the most serious events?
4. What are the patient safety implications?

Provide a clinical safety-focused analysis.
"""
    
    elif source == "510K":
        return f"""
{base_context}. Focus on regulatory approval patterns and predicate devices.

Regulatory Context:
- Total 510K Clearances: {len(profile.clearances)}
- Known Product Codes: {list(profile.product_codes)[:3]}
- Timeline Span: {len(profile.timeline)} events

Key Questions:
1. What types of devices are being cleared?
2. Are there patterns in clearance types?
3. Which manufacturers dominate this space?
4. What do predicate relationships tell us?

Provide a regulatory pathway analysis.
"""
    
    else:
        return f"""
{base_context}. Provide comprehensive analysis focusing on:

1. Key patterns and trends
2. Major manufacturers and devices
3. Regulatory implications
4. Safety considerations

Context: Risk Score {profile.risk_score}, {len(profile.timeline)} regulatory events total.
"""

def generate_comprehensive_summary(query, profile, summary, ai_results):
    """Generate a comprehensive summary combining all analyses."""
    
    summary_parts = []
    
    # Executive Summary
    summary_parts.append(f"""
## Executive Summary for '{query}'

**Risk Assessment**: {profile.risk_score}/100 risk score
**Regulatory Activity**: {summary['regulatory_history']['total_510k_clearances']} clearances, {summary['regulatory_history']['total_recalls']} recalls, {summary['regulatory_history']['total_adverse_events']} adverse events
**Key Manufacturers**: {', '.join(list(profile.manufacturers)[:3])}

""")
    
    # Safety Signals
    if summary['safety_signals']['class_1_recalls'] > 0:
        summary_parts.append(f"""
⚠️ **CRITICAL SAFETY ALERT**: {summary['safety_signals']['class_1_recalls']} Class I (life-threatening) recalls identified.
""")
    
    # AI Analysis Results
    summary_parts.append("## Detailed Analysis by Data Source\n")
    
    for source, analysis in ai_results.items():
        if "failed" not in analysis.lower():
            summary_parts.append(f"""
### {source} Analysis
{analysis}

""")
    
    # Recent Activity
    if summary['recent_activity']['last_30_days']:
        summary_parts.append(f"""
## Recent Activity (Last 30 Days)
{len(summary['recent_activity']['last_30_days'])} recent events:
""")
        for date, event_type, description in summary['recent_activity']['last_30_days'][:5]:
            date_str = date.strftime("%Y-%m-%d") if date else "Unknown"
            summary_parts.append(f"- {date_str}: {description}\n")
    
    # Regulatory Timeline Highlights
    if profile.timeline:
        summary_parts.append(f"""
## Key Regulatory Milestones
Recent timeline highlights:
""")
        for date, event_type, description in profile.timeline[-5:]:
            date_str = date.strftime("%Y-%m-%d") if date else "Unknown"
            summary_parts.append(f"- {date_str}: {description}\n")
    
    return ''.join(summary_parts)

if __name__ == "__main__":
    try:
        profile, ai_results, summary = test_enhanced_ai_pipeline()
    except Exception as e:
        print(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()