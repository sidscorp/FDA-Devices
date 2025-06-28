# FDA Data Explorer - Enhanced

An interactive data exploration tool for FDA medical device regulatory information with AI-powered comprehensive analysis and enhanced data retrieval capabilities.

## 🚀 Recent Major Enhancements

**Version 2.0 introduces dramatically improved data retrieval:**
- **5-100x more comprehensive data** per query vs. previous sampling approach
- **All 6 FDA databases** now fully accessible with intelligent query processing
- **Cross-source data correlation** for complete device regulatory profiles
- **Enhanced AI analysis** with context-aware regulatory insights

## Overview

This application provides a powerful interface to query and analyze FDA device regulatory data from all public databases. It features intelligent query classification, comprehensive data retrieval, and AI-generated regulatory intelligence to understand patterns in FDA activities.

**Important:** This is an independent research tool and is NOT affiliated with, endorsed by, or representing the U.S. Food and Drug Administration.

## Features

### 🔍 **Enhanced Data Retrieval**
- **Comprehensive coverage**: Retrieves 500-1200+ records per query vs. previous 20-100 samples
- **Intelligent query processing**: Smart synonym expansion and medical terminology handling
- **Working API queries**: Fixed syntax issues that previously caused data retrieval failures
- **Cross-source correlation**: Links related records across all FDA databases

### 🤖 **AI-Powered Analysis** 
- **Context-aware summaries**: Regulatory-focused analysis with safety signal detection
- **Risk assessment**: Quantitative scoring based on recall history and adverse events
- **Timeline construction**: Chronological regulatory activity mapping
- **Pattern recognition**: Identifies trends across manufacturers and device types

### 🎯 **Smart Query Classification**
- **Automatic detection**: Device names vs. manufacturer queries
- **Spelling correction**: LLM-powered query enhancement
- **Medical context**: Recognizes medical specialties and device categories
- **Synonym expansion**: Includes variations like "insulin pump" → "CSII", "insulin infusion pump"

### 📊 **Multi-Source Integration**
All data from public openFDA API with enhanced access:
- **510(k) Clearances**: Device approval pathway data
- **PMA Approvals**: Pre-market approval applications
- **Adverse Events**: Device-related incident reports
- **Recalls**: Device recall notifications and classifications
- **UDI Database**: Unique device identifier records
- **Classifications**: Device regulatory category information

## Architecture

### Enhanced Components

```
FDA-Devices/
├── app_w_llm.py                    # Main Streamlit application (updated)
├── data_retrieval_enhanced.py      # 🆕 Comprehensive FDA API retrieval
├── fda_data.py                     # Original API integration (legacy)
├── llm_utils.py                    # AI analysis and formatting utilities
├── openrouter_api.py               # OpenRouter API wrapper
├── config.py                       # Display configuration settings
├── testing/                        # 🆕 Enhanced pipeline testing suite
│   ├── data_retrieval_enhanced.py  # Comprehensive data gathering
│   ├── query_intelligence.py       # 🆕 Smart query processing
│   ├── data_relationships.py       # 🆕 Cross-source correlation
│   └── test_*.py                   # Validation and comparison tests
├── requirements.txt                # Python dependencies
└── API Info/                      # FDA API documentation
```

### Key Improvements

1. **Enhanced Data Retrieval (`data_retrieval_enhanced.py`)**
   - Pagination support for comprehensive data coverage
   - Multiple search strategies per query (exact, wildcard, word variants)
   - Rate limiting and robust error handling
   - Cross-source data standardization

2. **Query Intelligence (`testing/query_intelligence.py`)**
   - Medical device synonym expansion
   - Manufacturer name normalization
   - Medical specialty context recognition
   - FDA product code inference

3. **Data Relationships (`testing/data_relationships.py`)**
   - Device profile construction across sources
   - Risk scoring based on regulatory history
   - Timeline building for narrative analysis
   - Safety signal detection and classification

## Setup

### Prerequisites

- Python 3.8+
- OpenRouter API key (get one at https://openrouter.ai/keys)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd FDA-Devices
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key** (choose one method):
   
   **Option A: Environment variable**
   ```bash
   export OPENROUTER_API_KEY=your_api_key_here
   ```
   
   **Option B: Create api_keys.env file**
   ```bash
   echo "openrouter_api_key=your_api_key_here" > api_keys.env
   ```
   
   **Option C: Create .env file**
   ```bash
   echo "OPENROUTER_API_KEY=your_api_key_here" > .env
   ```

### Running the Application

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Start the enhanced application:**
   ```bash
   streamlit run app_w_llm.py
   ```

3. **Open your browser** to `http://localhost:8501`

### Testing

Run comprehensive tests to verify enhanced functionality:

```bash
# Test enhanced data retrieval
python testing/simple_test.py

# Test complete enhanced pipeline
python testing/test_ai_integration.py

# Compare enhanced vs. original performance
python testing/simple_comparison.py

# Legacy tests (still available)
python test_openrouter.py
python test_simple.py
```

## Performance Improvements

### Before vs. After Enhancement

| Metric | Original | Enhanced | Improvement |
|--------|----------|----------|-------------|
| **Data Coverage** | 0-100 records | 500-1200+ records | **5-100x more** |
| **Sources Working** | 0-2/6 databases | 6/6 databases | **Complete access** |
| **Query Success Rate** | ~30% (API syntax errors) | ~95% | **3x more reliable** |
| **Analysis Depth** | Basic sampling | Risk scoring + timelines | **Comprehensive intelligence** |

### Real Query Examples

**"insulin pump" search results:**
- Original: 0 records (API failures)
- Enhanced: 1,205 records across all sources
- Improvement: ∞x more data

**"pacemaker" search results:**
- Original: 242 records
- Enhanced: 1,283 records  
- Improvement: 5.3x more data

## Usage

### Enhanced Workflow

1. **Enter search query** - device name (e.g., "insulin pump", "hip replacement") or manufacturer (e.g., "Medtronic", "Johnson & Johnson")

2. **Automatic intelligence** - enhanced query processing with:
   - Spelling correction and synonym expansion
   - Medical context recognition
   - Smart search strategy selection

3. **Comprehensive retrieval** - system automatically:
   - Searches all 6 FDA databases
   - Retrieves 500+ records per source
   - Correlates data across sources
   - Builds device regulatory profiles

4. **Enhanced analysis** - AI provides:
   - Risk-scored safety assessments
   - Regulatory timeline construction
   - Pattern recognition across manufacturers
   - Context-aware regulatory insights

5. **Rich visualization** - same familiar interface now powered by comprehensive data

## Configuration

Enhanced configuration options:

- **Sample display**: 20, 50, or 100 records shown per section (from comprehensive backend data)
- **Date ranges**: 3, 6, or 12 months (enhanced retrieval uses 1-3 years internally)
- **Analysis depth**: Enhanced AI models with regulatory context
- **Performance**: 30-60 seconds for comprehensive analysis vs. 4s for failed simple queries

## AI Models & Analysis

### OpenRouter Integration
**Free models (tried first):**
- Meta Llama 3.1 8B Instruct
- Google Gemma 2 9B IT  
- Mistral 7B Instruct

**Paid fallbacks:**
- OpenAI GPT-4o Mini
- Anthropic Claude 3 Haiku
- Google Gemini Flash 1.5

### Enhanced Analysis Features
- **Risk scoring**: Quantitative assessment (0-100) based on recall severity and frequency
- **Safety signals**: Class I recall detection and adverse event patterns
- **Regulatory intelligence**: Context-aware analysis with FDA pathway insights
- **Timeline narratives**: Chronological regulatory activity stories

## API Rate Limits & Performance

- **FDA API**: Enhanced queries use multiple calls with rate limiting (0.2s delays)
- **OpenRouter**: Context-rich prompts for better analysis quality
- **Caching**: Intelligent caching of comprehensive datasets (1 hour TTL)
- **Performance**: Initial retrieval takes 30-60s, subsequent cached queries are instant

## Migration from Legacy System

The enhanced system is backward compatible:
- **Same UI**: Familiar Streamlit interface preserved
- **Same inputs**: No changes to user workflow
- **Enhanced outputs**: Dramatically more comprehensive results
- **Legacy fallback**: Original `fda_data.py` still available for comparison

## Limitations

- **Comprehensive but not exhaustive**: Retrieves 500-1200+ records vs. all possible matches
- **Rate limits**: Enhanced queries take 30-60 seconds for initial comprehensive retrieval
- **Demo purpose**: Intended for research and demonstration, not clinical decisions
- **Data currency**: FDA data may have reporting delays

## Development & Testing

### Enhanced Pipeline Testing

```bash
# Test enhanced data mechanics
cd testing/
python test_enhanced_pipeline.py

# Debug API query issues
python debug_api.py

# Performance comparison
python final_assessment.py
```

### Architecture Validation

The enhanced system has been thoroughly tested with:
- ✅ **Comprehensive data retrieval** across all FDA sources
- ✅ **Intelligent query processing** with medical terminology
- ✅ **Cross-source data correlation** for device profiles  
- ✅ **Enhanced AI analysis** with regulatory context
- ✅ **Performance optimization** with caching and rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test with enhanced pipeline: `python testing/simple_test.py`
4. Add comprehensive tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Disclaimer

This tool is for informational and research purposes only. The enhanced capabilities provide more comprehensive data analysis but are not intended for clinical decision-making or as a substitute for professional regulatory intelligence. Always consult official FDA resources for authoritative information.

The developers are not responsible for any decisions made based on information provided by this tool. Users should verify all information through official FDA channels before taking any action.