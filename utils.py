import streamlit as st
from config import DISPLAY_COLUMNS

def display_section(title, df, source):
    st.subheader(title)
    cols = DISPLAY_COLUMNS.get(source, [])
    if not df.empty:
        filtered_cols = [col for col in cols if col in df.columns]
        st.dataframe(df[filtered_cols] if filtered_cols else df)
    else:
        st.info(f"No data found for {title}.")

def display_view(results, view_type):
    view_titles = {
        "device": {
            "510K": "📄 Recent 510(k) Submissions",
            "PMA": "📄 Recent PMA Submissions",
            "CLASSIFICATION": "🧪 Classification Info",
            "UDI": "🔗 UDI Information",
            "EVENT": "⚠️ Adverse Events",
            "RECALL": "🚨 Recalls"
        },
        "manufacturer": {
            "RECALL": "🚨 Recent Recalls",
            "EVENT": "⚠️ Adverse Events",
            "510K": "📄 510(k) Submissions",
            "PMA": "📄 PMA Submissions",
            "UDI": "🔗 UDI Entries"
        }
    }

    st.header("🔍 Device-Centric View" if view_type == "device" else "🏭 Manufacturer-Centric View")
    sections = view_titles.get(view_type, {})

    if not results:
        st.write("No data found.")
        return

    for key, title in sections.items():
        if key in results:
            display_section(title, results[key], key)