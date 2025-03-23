import streamlit as st
from config import QUERY_LIMIT, CACHE_TTL
from fda_data import get_fda_data
from utils import display_view

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def cached_get_fda_data(query, limit=QUERY_LIMIT):
    try:
        return get_fda_data(query, limit)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return {}

def main():
    st.set_page_config(page_title="FDA Device Explorer", layout="wide")
    st.title("🧠 FDA Device Explorer")

    query = st.text_input("Enter search term (device or manufacturer)", placeholder="e.g. Medtronic, pacemaker")

    if query:
        with st.spinner("Crunching data from FDA..."):
            results = cached_get_fda_data(query)

        if results:
            display_view(results.get("device"), "device")
            display_view(results.get("manufacturer"), "manufacturer")

            with st.expander("🛠 Debug Info"):
                for view, tables in results.items():
                    st.markdown(f"**{view.upper()} VIEW**")
                    for source, df in tables.items():
                        st.write(f"{source} → columns:", list(df.columns))
        else:
            st.warning("No results found for your query.")

if __name__ == "__main__":
    main()