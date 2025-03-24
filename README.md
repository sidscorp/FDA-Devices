# 🧠 FDA Device Explorer

> **⚠️ DEVELOPMENT ONLY**: This project is in active development and not ready for production use.

This Streamlit app lets you search FDA device/manufacturer data and see results in both device-centric and manufacturer-centric views.

## 🚀 How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔍 Features

- Dual views: device and manufacturer
- Cached API data for performance
- Debug info for devs
- Modular codebase ready for production

## 📦 Folder Structure

- `app.py` — Streamlit UI
- `fda_data.py` — FDA data layer (mock for now)
- `utils.py` — UI helper functions
- `config.py` — Settings and display column configs