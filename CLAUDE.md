# FDA Data Explorer - Claude Memory

## Project Overview
Interactive Streamlit app for exploring FDA medical device regulatory data with AI-powered narrative summaries. Retrieves data from 6 FDA databases (510k, PMA, adverse events, recalls, UDI, classification) and provides intelligent analysis.

## Current Architecture

### Core Components
- **app_w_llm.py**: Main Streamlit application with dual device/manufacturer views
- **fda_data.py**: FDA API integration with date filtering and multi-source queries
- **llm_utils.py**: AI analysis using OpenRouter API with fallback models
- **openrouter_api.py**: API wrapper for OpenRouter with free/paid model selection
- **config.py**: Configuration constants and display column definitions

### Key Features
- Automatic query classification (device vs manufacturer detection)
- Configurable sampling (20/50/100 records, 3/6/12 months)
- AI narrative summaries with structured prompts
- Smart caching and error handling
- Comprehensive test suite

## API Integration

### OpenRouter Setup
- Uses OpenRouter API with model fallback strategy
- Free models tried first: Llama 3.1, Gemma 2, Mistral 7B
- Paid fallbacks: GPT-4o Mini, Claude Haiku, Gemini Flash
- API key loaded from: api_keys.env, .env, or OPENROUTER_API_KEY env var

### FDA Data Sources
- **510k**: Device clearance submissions
- **PMA**: Pre-market approval applications  
- **EVENT**: Adverse event reports
- **RECALL**: Device recall notices
- **UDI**: Unique device identifiers
- **CLASSIFICATION**: Device classification records

## Development Status

### Working Features
- Basic query processing and data retrieval
- AI-powered narrative generation
- Dual view layouts (device/manufacturer)
- Configuration panel for sampling
- Test suite for validation

### Areas Needing Development
1. **Comprehensive data retrieval**: Current sampling approach misses relevant data
2. **Intelligent data structuring**: Need better aggregation and relationship mapping
3. **Enhanced display logic**: Raw data and AI summaries need better organization
4. **Search optimization**: Query processing could be more sophisticated
5. **Data completeness**: May need multiple API calls for thorough coverage

## Commands to Remember

### Running the Application
```bash
source venv/bin/activate
streamlit run app_w_llm.py
```

### Testing
```bash
python test_openrouter.py          # Test API connectivity
python test_simple.py              # Basic workflow test
python test_full_workflow.py       # Comprehensive test
```

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Important Notes
- Project rebranded from "FDA Device Intelligence Center" to avoid regulatory confusion
- Clear unofficial disclaimers added throughout interface
- Uses sample-based analysis approach (not comprehensive data coverage)
- Built for research/demo purposes, not clinical decision-making

## Next Development Priorities
1. Improve data retrieval completeness for comprehensive searches
2. Design better data structuring and relationship mapping
3. Enhance UI for both raw data and AI summary presentation
4. Optimize search algorithms for better query matching