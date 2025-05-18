import os
import streamlit as st
import pandas as pd
from utils import load_all_data

st.set_page_config(page_title="VisualOps: Toast Dashboard", layout="wide")
st.title("📊 VisualOps: Toast Multi-Location Dashboard")

# Path to data
DATA_DIR = "/opt/render/project/src/coreidentity-agents/toast_exports"

# Ensure directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    st.warning(f"Created missing export directory at: {DATA_DIR}")
    st.stop()

# Load all data
data = load_all_data(DATA_DIR)

if not data:
    st.warning("No data found in toast_exports.")
    st.stop()

# Sidebar - Select Location and Date
locations = sorted(data.keys())
selected_location = st.sidebar.selectbox("Select Location", locations)

if not selected_location or selected_location not in data:
    st.warning("Please select a valid location.")
    st.stop()

dates = sorted(data[selected_location].keys(), reverse=True)
selected_date = st.sidebar.selectbox("Select Date", dates)

if not selected_date or selected_date not in data[selected_location]:
    st.warning("Please select a valid date.")
    st.stop()

exports = data[selected_location][selected_date]

st.markdown(f"### 📍 Location: {selected_location} | 📅 Date: {selected_date}")

# Tabs for each dataset
tab_names = list(exports.keys())
tabs = st.tabs(tab_names)

for tab, name in zip(tabs, tab_names):
    with tab:
        df = exports[name]
        if isinstance(df, pd.DataFrame) and not df.empty:
            st.dataframe(df)
        elif isinstance(df, dict):
            st.json(df)
        else:
            st.info(f"No data found for {name}.")
