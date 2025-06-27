# FDA Data Explorer

An interactive data exploration tool for FDA medical device regulatory information with AI-powered narrative summaries.

## Overview

This application provides an interface to query and analyze FDA device regulatory data from multiple public databases. It features intelligent query classification, configurable data sampling, and AI-generated narrative summaries to help understand patterns in regulatory activities.

**Important:** This is an independent research tool and is NOT affiliated with, endorsed by, or representing the U.S. Food and Drug Administration.

## Features

- **Dual search modes**: Automatically detects device names vs. manufacturer queries
- **Multi-source data integration**: Pulls from 6 FDA databases (510k, PMA, adverse events, recalls, UDI, classification)
- **Configurable sampling**: Adjustable sample sizes (20/50/100 records) and date ranges (3/6/12 months)
- **AI narrative summaries**: Uses OpenRouter API to generate insights from data patterns
- **Interactive interface**: Clean Streamlit-based web application

## Data Sources

All data is retrieved from the public openFDA API:
- Device 510(k) Clearance Database
- Device Pre-Market Approval (PMA) Database
- Device Adverse Event Reports
- Device Recall Database
- Device Classification Database
- Unique Device Identification (UDI) Database

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

2. **Start the application:**
   ```bash
   streamlit run app_w_llm.py
   ```

3. **Open your browser** to `http://localhost:8501`

### Testing

Run the test suite to verify everything is working:

```bash
# Test OpenRouter API connection
python test_openrouter.py

# Test basic FDA data + AI workflow
python test_simple.py

# Full comprehensive test (takes longer)
python test_full_workflow.py
```

## Usage

1. **Enter a search query** - device name (e.g., "pacemaker", "insulin pump") or manufacturer (e.g., "Medtronic", "Abbott")

2. **Configure settings** - adjust sample size and date range in the configuration panel

3. **View results** - the app automatically determines query type and displays relevant FDA data with AI summaries

4. **Explore data** - expand sections to view raw data tables and detailed information

## Project Structure

```
FDA-Devices/
├── app_w_llm.py           # Main Streamlit application
├── fda_data.py            # FDA API integration and data processing
├── llm_utils.py           # AI analysis and formatting utilities
├── openrouter_api.py      # OpenRouter API wrapper
├── config.py              # Display configuration settings
├── utils.py               # Additional utility functions
├── requirements.txt       # Python dependencies
├── test_*.py             # Test scripts
├── about.md              # Application information
└── API Info/             # FDA API documentation and field references
```

## Configuration

The application uses several configurable parameters:

- **Sample sizes**: 20, 50, or 100 records per data source
- **Date ranges**: 3, 6, or 12 months of recent data
- **AI models**: Automatically uses free models with paid fallbacks
- **Cache duration**: 1 hour for FDA API responses

## AI Models

The application uses OpenRouter's API with intelligent model fallback:

**Free models (tried first):**
- Meta Llama 3.1 8B Instruct
- Google Gemma 2 9B IT
- Mistral 7B Instruct

**Paid fallbacks (if free models fail):**
- OpenAI GPT-4o Mini
- Anthropic Claude 3 Haiku
- Google Gemini Flash 1.5

## API Rate Limits

- **FDA API**: No API key required, but has rate limits
- **OpenRouter**: Requires API key, free tier available with generous limits
- **Caching**: Reduces API calls through intelligent caching

## Limitations

- **Sample-based analysis**: Shows recent samples, not comprehensive historical data
- **Rate limits**: Subject to both FDA and OpenRouter API limitations
- **Demo purpose**: Intended for research and demonstration, not clinical decisions
- **Data lag**: FDA data may have reporting delays

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Disclaimer

This tool is for informational and research purposes only. It is not intended for clinical decision-making or as a substitute for professional regulatory intelligence. Always consult official FDA resources for authoritative information.

The developers are not responsible for any decisions made based on information provided by this tool. Users should verify all information through official FDA channels before taking any action.