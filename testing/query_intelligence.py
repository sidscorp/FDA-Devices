"""
Intelligent Query Processing and Enhancement
Transforms user queries into comprehensive FDA search strategies.
"""

import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass

@dataclass
class QueryContext:
    original_query: str
    query_type: str  # "device", "manufacturer", "indication", "mixed"
    expanded_terms: List[str]
    product_codes: List[str]
    regulatory_keywords: List[str]
    medical_terms: List[str]

class QueryIntelligence:
    def __init__(self):
        # Common device name variations and synonyms
        self.device_synonyms = {
            "insulin pump": ["insulin infusion pump", "continuous subcutaneous insulin infusion", "CSII"],
            "pacemaker": ["cardiac pacemaker", "implantable pacemaker", "permanent pacemaker"],
            "stent": ["coronary stent", "vascular stent", "drug eluting stent", "bare metal stent"],
            "catheter": ["intravascular catheter", "central venous catheter", "urinary catheter"],
            "implant": ["medical implant", "surgical implant", "prosthetic implant"],
            "ventilator": ["mechanical ventilator", "respiratory ventilator", "breathing machine"],
            "defibrillator": ["implantable defibrillator", "ICD", "automated external defibrillator", "AED"],
            "hip replacement": ["total hip arthroplasty", "hip prosthesis", "hip implant"],
            "knee replacement": ["total knee arthroplasty", "knee prosthesis", "knee implant"]
        }
        
        # Common manufacturer variations
        self.manufacturer_synonyms = {
            "medtronic": ["medtronic plc", "medtronic inc", "medtronic usa"],
            "johnson": ["johnson & johnson", "j&j", "ethicon", "depuy"],
            "abbott": ["abbott laboratories", "abbott medical"],
            "boston scientific": ["boston scientific corp", "bsc"],
            "edwards": ["edwards lifesciences", "edwards lifesciences corp"],
            "stryker": ["stryker corporation", "stryker corp"],
            "zimmer": ["zimmer biomet", "zimmer holdings"]
        }
        
        # Medical specialty keywords
        self.medical_specialties = {
            "cardiology": ["cardiac", "heart", "coronary", "vascular", "cardiovascular"],
            "orthopedics": ["bone", "joint", "spine", "orthopedic", "musculoskeletal"],
            "neurology": ["brain", "neural", "neurological", "neurosurgical"],
            "diabetes": ["diabetic", "glucose", "insulin", "blood sugar"],
            "respiratory": ["lung", "pulmonary", "breathing", "airway"],
            "urology": ["kidney", "bladder", "urinary", "renal"],
            "ophthalmology": ["eye", "ocular", "vision", "retinal"],
            "gastroenterology": ["digestive", "gastrointestinal", "stomach", "intestinal"]
        }
        
        # Regulatory action keywords
        self.regulatory_keywords = {
            "safety": ["recall", "warning", "alert", "adverse", "malfunction", "failure"],
            "approval": ["clearance", "approved", "authorized", "permitted", "510k", "pma"],
            "market": ["withdrawn", "discontinued", "suspended", "banned"],
            "quality": ["inspection", "violation", "deviation", "corrective", "preventive"]
        }
        
    def analyze_query(self, query: str) -> QueryContext:
        """Analyze and classify the user query."""
        query_lower = query.lower().strip()
        
        # Determine query type
        query_type = self._classify_query_type(query_lower)
        
        # Generate expanded terms
        expanded_terms = self._expand_query_terms(query_lower, query_type)
        
        # Extract relevant product codes (would need FDA product code database)
        product_codes = self._extract_product_codes(query_lower)
        
        # Identify regulatory keywords
        regulatory_keywords = self._identify_regulatory_context(query_lower)
        
        # Extract medical terms
        medical_terms = self._extract_medical_context(query_lower)
        
        return QueryContext(
            original_query=query,
            query_type=query_type,
            expanded_terms=expanded_terms,
            product_codes=product_codes,
            regulatory_keywords=regulatory_keywords,
            medical_terms=medical_terms
        )
    
    def _classify_query_type(self, query: str) -> str:
        """Classify whether query is about device, manufacturer, or mixed."""
        
        # Company/manufacturer indicators
        company_indicators = ["inc", "corp", "company", "ltd", "llc", "laboratories", "medical", "systems"]
        manufacturer_keywords = list(self.manufacturer_synonyms.keys())
        
        # Check for manufacturer patterns
        if any(indicator in query for indicator in company_indicators):
            return "manufacturer"
        if any(mfg in query for mfg in manufacturer_keywords):
            return "manufacturer"
            
        # Device indicators
        device_indicators = ["device", "pump", "catheter", "implant", "stent", "replacement", "monitor"]
        if any(device in query for device in device_indicators):
            return "device"
            
        # Medical condition indicators (usually device-related)
        medical_indicators = ["diabetes", "heart", "knee", "hip", "eye", "kidney"]
        if any(med in query for med in medical_indicators):
            return "device"
            
        # Default to device if unclear
        return "device"
    
    def _expand_query_terms(self, query: str, query_type: str) -> List[str]:
        """Generate expanded search terms based on query analysis."""
        expanded = [query]
        
        # Add synonyms based on query type
        if query_type in ["device", "mixed"]:
            for device, synonyms in self.device_synonyms.items():
                if device in query:
                    expanded.extend(synonyms)
                    
        if query_type in ["manufacturer", "mixed"]:
            for manufacturer, variations in self.manufacturer_synonyms.items():
                if manufacturer in query:
                    expanded.extend(variations)
        
        # Add medical specialty variations
        for specialty, terms in self.medical_specialties.items():
            if any(term in query for term in terms):
                expanded.extend(terms)
                
        # Remove duplicates and original query
        expanded = list(set(expanded))
        if query in expanded:
            expanded.remove(query)
            
        return [query] + expanded[:10]  # Limit to prevent overload
    
    def _extract_product_codes(self, query: str) -> List[str]:
        """Extract or infer FDA product codes from query."""
        # This would ideally use a comprehensive FDA product code database
        # For now, implementing common patterns
        
        common_codes = {
            "insulin pump": ["LZG", "MKJ"],
            "pacemaker": ["DXX", "DTC", "DTB"],
            "stent": ["NIR", "NIT"],
            "catheter": ["DQO", "FOZ"],
            "defibrillator": ["MKJ", "MLC"],
            "hip replacement": ["JDH", "KWP"],
            "knee replacement": ["KWK", "JDI"]
        }
        
        codes = []
        for device, device_codes in common_codes.items():
            if device in query:
                codes.extend(device_codes)
                
        return codes
    
    def _identify_regulatory_context(self, query: str) -> List[str]:
        """Identify regulatory action context in query."""
        context = []
        
        for category, keywords in self.regulatory_keywords.items():
            if any(keyword in query for keyword in keywords):
                context.append(category)
                
        return context
    
    def _extract_medical_context(self, query: str) -> List[str]:
        """Extract medical specialty context."""
        context = []
        
        for specialty, terms in self.medical_specialties.items():
            if any(term in query for term in terms):
                context.append(specialty)
                
        return context
    
    def generate_fda_search_strategies(self, context: QueryContext) -> Dict[str, List[str]]:
        """Generate optimized search strategies for each FDA database."""
        strategies = {}
        
        base_terms = context.expanded_terms[:5]  # Use top 5 expanded terms
        
        # 510K search strategy
        strategies["510k"] = []
        for term in base_terms:
            strategies["510k"].extend([
                f'device_name:"{term}"',
                f'device_name:{term}*',
                f'applicant:"{term}"' if context.query_type == "manufacturer" else f'product_code:{term}'
            ])
            
        # Event search strategy  
        strategies["event"] = []
        for term in base_terms:
            strategies["event"].extend([
                f'device.brand_name:"{term}"',
                f'device.generic_name:"{term}"',
                f'manufacturer_name:"{term}"' if context.query_type == "manufacturer" else f'device.brand_name:{term}*'
            ])
            
        # Recall search strategy
        strategies["recall"] = []
        for term in base_terms:
            strategies["recall"].extend([
                f'product_description:"{term}"',
                f'product_description:{term}*',
                f'recalling_firm:"{term}"' if context.query_type == "manufacturer" else f'manufacturer_name:{term}*'
            ])
        
        # Add product code searches if available
        if context.product_codes:
            for code in context.product_codes:
                strategies["510k"].append(f'product_code:{code}')
                strategies["classification"].append(f'product_code:{code}')
                
        return strategies


if __name__ == "__main__":
    # Test the query intelligence
    qi = QueryIntelligence()
    
    test_queries = [
        "insulin pump",
        "Medtronic pacemaker recalls", 
        "hip replacement complications",
        "Johnson & Johnson knee implant"
    ]
    
    for query in test_queries:
        print(f"\nAnalyzing: '{query}'")
        context = qi.analyze_query(query)
        print(f"Type: {context.query_type}")
        print(f"Expanded terms: {context.expanded_terms[:3]}")
        print(f"Medical context: {context.medical_terms}")
        print(f"Regulatory context: {context.regulatory_keywords}")
        
        strategies = qi.generate_fda_search_strategies(context)
        print(f"510K strategies: {strategies['510k'][:2]}")