"""
Cross-Source Data Relationship Mapping
Links related records across FDA databases for comprehensive device profiles.
"""

import pandas as pd
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

@dataclass
class DeviceProfile:
    device_name: str
    manufacturers: Set[str]
    product_codes: Set[str]
    clearances: List[Dict]
    approvals: List[Dict]
    recalls: List[Dict]
    adverse_events: List[Dict]
    classifications: List[Dict]
    risk_score: float
    timeline: List[Tuple[datetime, str, str]]  # (date, event_type, description)

class DataRelationshipMapper:
    def __init__(self):
        self.product_code_cache = {}
        self.manufacturer_aliases = {}
        
    def create_comprehensive_profile(self, fda_data: Dict[str, pd.DataFrame], primary_query: str) -> DeviceProfile:
        """Create a comprehensive device profile by linking related records."""
        
        # Extract all potential device identifiers
        identifiers = self._extract_device_identifiers(fda_data, primary_query)
        
        # Build device profile
        profile = DeviceProfile(
            device_name=primary_query,
            manufacturers=set(),
            product_codes=set(),
            clearances=[],
            approvals=[],
            recalls=[],
            adverse_events=[],
            classifications=[],
            risk_score=0.0,
            timeline=[]
        )
        
        # Process each data source
        for source, df in fda_data.items():
            if df.empty:
                continue
                
            if source == "510K":
                self._process_510k_data(df, profile, identifiers)
            elif source == "PMA":
                self._process_pma_data(df, profile, identifiers)
            elif source == "RECALL":
                self._process_recall_data(df, profile, identifiers)
            elif source == "EVENT":
                self._process_event_data(df, profile, identifiers)
            elif source == "CLASSIFICATION":
                self._process_classification_data(df, profile, identifiers)
                
        # Calculate risk score
        profile.risk_score = self._calculate_risk_score(profile)
        
        # Sort timeline
        profile.timeline.sort(key=lambda x: x[0] if x[0] else datetime.min)
        
        return profile
    
    def _extract_device_identifiers(self, fda_data: Dict[str, pd.DataFrame], query: str) -> Dict[str, Set[str]]:
        """Extract all potential device identifiers for cross-referencing."""
        identifiers = {
            "device_names": set(),
            "product_codes": set(), 
            "manufacturers": set(),
            "k_numbers": set(),
            "pma_numbers": set()
        }
        
        # Add original query variations
        identifiers["device_names"].add(query.lower())
        identifiers["device_names"].add(query.lower().replace(" ", ""))
        
        # Extract from each source
        for source, df in fda_data.items():
            if df.empty:
                continue
                
            # Device names
            name_fields = ["device_name", "trade_name", "generic_name", "product_description", 
                          "device.brand_name", "device.generic_name", "brand_name"]
            for field in name_fields:
                if field in df.columns:
                    names = df[field].dropna().str.lower().unique()
                    identifiers["device_names"].update(names)
            
            # Product codes
            code_fields = ["product_code", "device.device_report_product_code"]
            for field in code_fields:
                if field in df.columns:
                    codes = df[field].dropna().unique()
                    identifiers["product_codes"].update(codes)
                    
            # Manufacturers
            mfg_fields = ["applicant", "manufacturer_name", "recalling_firm", "company_name"]
            for field in mfg_fields:
                if field in df.columns:
                    mfgs = df[field].dropna().str.lower().unique()
                    identifiers["manufacturers"].update(mfgs)
                    
            # Regulatory numbers
            if "k_number" in df.columns:
                k_nums = df["k_number"].dropna().unique()
                identifiers["k_numbers"].update(k_nums)
            if "pma_number" in df.columns:
                pma_nums = df["pma_number"].dropna().unique()
                identifiers["pma_numbers"].update(pma_nums)
                
        return identifiers
    
    def _process_510k_data(self, df: pd.DataFrame, profile: DeviceProfile, identifiers: Dict[str, Set[str]]):
        """Process 510K clearance data."""
        for _, row in df.iterrows():
            # Add to profile
            if pd.notna(row.get("applicant")):
                profile.manufacturers.add(row["applicant"])
            if pd.notna(row.get("product_code")):
                profile.product_codes.add(row["product_code"])
                
            clearance = {
                "k_number": row.get("k_number"),
                "device_name": row.get("device_name"),
                "decision_date": row.get("decision_date"),
                "applicant": row.get("applicant"),
                "clearance_type": row.get("clearance_type"),
                "product_code": row.get("product_code")
            }
            profile.clearances.append(clearance)
            
            # Add to timeline
            if pd.notna(row.get("decision_date")):
                date = pd.to_datetime(row["decision_date"])
                description = f"510K Clearance: {row.get('device_name', 'Device')} by {row.get('applicant', 'Unknown')}"
                profile.timeline.append((date, "510K_CLEARANCE", description))
    
    def _process_pma_data(self, df: pd.DataFrame, profile: DeviceProfile, identifiers: Dict[str, Set[str]]):
        """Process PMA approval data."""
        for _, row in df.iterrows():
            if pd.notna(row.get("applicant")):
                profile.manufacturers.add(row["applicant"])
            if pd.notna(row.get("product_code")):
                profile.product_codes.add(row["product_code"])
                
            approval = {
                "pma_number": row.get("pma_number"),
                "trade_name": row.get("trade_name"),
                "decision_date": row.get("decision_date"),
                "applicant": row.get("applicant"),
                "supplement_reason": row.get("supplement_reason")
            }
            profile.approvals.append(approval)
            
            # Add to timeline
            if pd.notna(row.get("decision_date")):
                date = pd.to_datetime(row["decision_date"])
                description = f"PMA Approval: {row.get('trade_name', 'Device')} by {row.get('applicant', 'Unknown')}"
                profile.timeline.append((date, "PMA_APPROVAL", description))
    
    def _process_recall_data(self, df: pd.DataFrame, profile: DeviceProfile, identifiers: Dict[str, Set[str]]):
        """Process recall data with severity assessment."""
        for _, row in df.iterrows():
            if pd.notna(row.get("recalling_firm")):
                profile.manufacturers.add(row["recalling_firm"])
                
            recall = {
                "event_date": row.get("event_date_initiated"),
                "recalling_firm": row.get("recalling_firm"),
                "product_description": row.get("product_description"),
                "recall_classification": row.get("recall_classification"),
                "reason_for_recall": row.get("reason_for_recall"),
                "recall_status": row.get("recall_status")
            }
            profile.recalls.append(recall)
            
            # Add to timeline with severity
            if pd.notna(row.get("event_date_initiated")):
                date = pd.to_datetime(row["event_date_initiated"])
                classification = row.get("recall_classification", "Unknown")
                reason = row.get("reason_for_recall", "Unspecified")
                description = f"Class {classification} Recall: {reason[:50]}..."
                profile.timeline.append((date, "RECALL", description))
    
    def _process_event_data(self, df: pd.DataFrame, profile: DeviceProfile, identifiers: Dict[str, Set[str]]):
        """Process adverse event data."""
        for _, row in df.iterrows():
            if pd.notna(row.get("manufacturer_name")):
                profile.manufacturers.add(row["manufacturer_name"])
                
            event = {
                "report_number": row.get("report_number"),
                "date_received": row.get("date_received"),
                "event_type": row.get("event_type"),
                "manufacturer_name": row.get("manufacturer_name"),
                "product_problems": row.get("product_problems"),
                "adverse_event_flag": row.get("adverse_event_flag"),
                "patient_outcomes": row.get("patient_outcomes"),
                "device_brand": row.get("device.brand_name")
            }
            profile.adverse_events.append(event)
            
            # Add to timeline
            if pd.notna(row.get("date_received")):
                date = pd.to_datetime(row["date_received"])
                problem = row.get("product_problems", "Adverse event")
                # Handle case where problem might be a list, float/NaN, or other type
                try:
                    if pd.isna(problem):
                        problem = "Adverse event"
                    elif isinstance(problem, list):
                        problem = ', '.join(str(p) for p in problem) if problem else "Adverse event"
                    elif not isinstance(problem, str):
                        problem = str(problem) if problem else "Adverse event"
                except (ValueError, TypeError):
                    problem = "Adverse event"
                description = f"Adverse Event: {str(problem)[:50]}..."
                profile.timeline.append((date, "ADVERSE_EVENT", description))
    
    def _process_classification_data(self, df: pd.DataFrame, profile: DeviceProfile, identifiers: Dict[str, Set[str]]):
        """Process device classification data."""
        for _, row in df.iterrows():
            if pd.notna(row.get("product_code")):
                profile.product_codes.add(row["product_code"])
                
            classification = {
                "device_name": row.get("device_name"),
                "device_class": row.get("device_class"),
                "product_code": row.get("product_code"),
                "medical_specialty": row.get("medical_specialty_description"),
                "regulation_number": row.get("regulation_number")
            }
            profile.classifications.append(classification)
    
    def _calculate_risk_score(self, profile: DeviceProfile) -> float:
        """Calculate a risk score based on regulatory history."""
        score = 0.0
        
        # Recall penalties
        for recall in profile.recalls:
            classification = recall.get("recall_classification", "")
            if "I" in str(classification):  # Class I (most serious)
                score += 30
            elif "II" in str(classification):  # Class II
                score += 15
            elif "III" in str(classification):  # Class III
                score += 5
                
        # Adverse event penalties
        serious_events = 0
        for event in profile.adverse_events:
            if event.get("adverse_event_flag") == "Y":
                serious_events += 1
        score += serious_events * 2
        
        # Device class consideration
        high_risk_classes = ["III", "3"]
        for classification in profile.classifications:
            if classification.get("device_class") in high_risk_classes:
                score += 10
                break
                
        # Normalize to 0-100 scale
        return min(score, 100.0)
    
    def generate_regulatory_summary(self, profile: DeviceProfile) -> Dict[str, any]:
        """Generate a structured regulatory summary."""
        return {
            "device_overview": {
                "primary_name": profile.device_name,
                "manufacturers": list(profile.manufacturers),
                "product_codes": list(profile.product_codes),
                "risk_score": profile.risk_score
            },
            "regulatory_history": {
                "total_510k_clearances": len(profile.clearances),
                "total_pma_approvals": len(profile.approvals),
                "total_recalls": len(profile.recalls),
                "total_adverse_events": len(profile.adverse_events)
            },
            "recent_activity": {
                "last_30_days": [event for event in profile.timeline 
                               if event[0] and event[0] > datetime.now() - timedelta(days=30)],
                "last_90_days": [event for event in profile.timeline 
                               if event[0] and event[0] > datetime.now() - timedelta(days=90)]
            },
            "safety_signals": {
                "class_1_recalls": len([r for r in profile.recalls 
                                      if "I" in str(r.get("recall_classification", ""))]),
                "serious_adverse_events": len([e for e in profile.adverse_events 
                                             if e.get("adverse_event_flag") == "Y"])
            }
        }


if __name__ == "__main__":
    # Test the relationship mapper
    mapper = DataRelationshipMapper()
    
    # Mock data for testing
    mock_data = {
        "510K": pd.DataFrame([
            {"k_number": "K123456", "device_name": "Test Pump", "applicant": "Test Corp", "product_code": "LZG"}
        ]),
        "RECALL": pd.DataFrame([
            {"product_description": "Test Pump", "recalling_firm": "Test Corp", "recall_classification": "II"}
        ]),
        "EVENT": pd.DataFrame([
            {"manufacturer_name": "Test Corp", "product_problems": "Malfunction", "adverse_event_flag": "Y"}
        ])
    }
    
    profile = mapper.create_comprehensive_profile(mock_data, "insulin pump")
    summary = mapper.generate_regulatory_summary(profile)
    
    print(f"Risk Score: {profile.risk_score}")
    print(f"Manufacturers: {profile.manufacturers}")
    print(f"Timeline events: {len(profile.timeline)}")