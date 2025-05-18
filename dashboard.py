# dashboard.py
import streamlit as st
import pandas as pd
import os
from utils import load_all_data

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Toast Multi-Location Dashboard")

# --- Sidebar filters ---
location = st.sidebar.selectbox("Select Location", ["57130", "57138"])
export_base = "./toast_exports"
location_path = os.path.join(export_base, location)

if not os.path.exists(location_path):
    st.error("No data found for selected location.")
    st.stop()

available_dates = sorted(os.listdir(location_path), reverse=True)
if not available_dates:
    st.error("No data files found.")
    st.stop()

date = st.sidebar.selectbox("Select Date", available_dates)
data = load_all_data(location, date)

if not data:
    st.warning("No data files found for this date/location.")
    st.stop()

# --- Load core data ---
items = data.get("AllItemsReport")
checks = data.get("CheckDetails")
labor = data.get("TimeEntries")
kitchen = data.get("KitchenTimings")
orders = data.get("OrderDetails")

# --- Summary Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"${items['Net Amount'].sum():,.2f}" if items is not None else "N/A")
col2.metric("🧾 Checks", len(checks) if checks is not None else "N/A")
col3.metric("👥 Employees", labor['Employee'].nunique() if labor is not None else "N/A")

# --- Top Menu Items ---
if items is not None:
    st.subheader("🍽️ Top Selling Items")
    top_items = items[["Menu Item", "Item Qty", "Gross Amount", "Discount Amount", "Net Amount"]]
    st.dataframe(top_items.sort_values(by="Net Amount", ascending=False).head(20))

# --- Kitchen Timings ---
if kitchen is not None and "Fulfillment Time" in kitchen:
    st.subheader("⏱️ Kitchen Fulfillment Times")
    kitchen_filtered = kitchen.dropna(subset=["Fulfillment Time"])
    st.write(f"Average Fulfillment Time: {kitchen_filtered['Fulfillment Time'].mean()}")
    st.dataframe(kitchen_filtered[["Check #", "Station", "Fulfillment Time"]].head(15))

# --- Labor Summary ---
if labor is not None:
    st.subheader("🧑‍🍳 Labor Summary by Role")
    summary = labor.groupby("Job Title")["Total Pay"].sum().reset_index().sort_values(by="Total Pay", ascending=False)
    st.dataframe(summary)

# --- Export Option ---
if items is not None:
    st.sidebar.download_button("Download 'All Items' CSV", data=items.to_csv(index=False), file_name="AllItems.csv")
