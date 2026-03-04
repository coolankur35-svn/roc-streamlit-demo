import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("⚡ ROC Unified Alarm Dashboard")

df = pd.read_excel("alarms.xlsx")

# Clean column names
df.columns = df.columns.str.strip()

# Convert datetime
df["Alert Start DateTime"] = pd.to_datetime(df["Alert Start DateTime"], errors="coerce")

# Sidebar filters
st.sidebar.header("Filters")

site_filter = st.sidebar.multiselect(
    "SCADA Site",
    df["SCADA Site"].dropna().unique(),
    default=df["SCADA Site"].dropna().unique()
)

customer_filter = st.sidebar.multiselect(
    "Customer",
    df["Customer"].dropna().unique(),
    default=df["Customer"].dropna().unique()
)

filtered_df = df[
    (df["SCADA Site"].isin(site_filter)) &
    (df["Customer"].isin(customer_filter))
]

# KPIs
total_alarms = len(filtered_df)
ack_count = filtered_df["Acknowledged?"].str.lower().eq("yes").sum()
unack_count = total_alarms - ack_count
unique_sites = filtered_df["SCADA Site"].nunique()
unique_equipment = filtered_df["Equipment"].nunique()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Alarms", total_alarms)
col2.metric("Acknowledged", ack_count)
col3.metric("Unacknowledged", unack_count)
col4.metric("Sites", unique_sites)
col5.metric("Equipment", unique_equipment)

st.markdown("---")

# Row 1 Charts
col6, col7 = st.columns(2)

ack_pie = px.pie(
    filtered_df,
    names="Acknowledged?",
    title="Acknowledgement Distribution"
)
col6.plotly_chart(ack_pie, use_container_width=True)

site_bar = px.bar(
    filtered_df["SCADA Site"].value_counts().head(10),
    title="Top 10 Sites by Alarm Count"
)
col7.plotly_chart(site_bar, use_container_width=True)

# Row 2 Charts
col8, col9 = st.columns(2)

trend = (
    filtered_df
    .groupby(filtered_df["Alert Start DateTime"].dt.date)
    .size()
    .reset_index(name="Count")
)

trend_chart = px.line(
    trend,
    x="Alert Start DateTime",
    y="Count",
    title="Alarm Trend Over Time"
)
col8.plotly_chart(trend_chart, use_container_width=True)

hardware_bar = px.bar(
    filtered_df["Hardware"].value_counts().head(10),
    title="Top 10 Hardware Generating Alarms"
)
col9.plotly_chart(hardware_bar, use_container_width=True)

st.markdown("---")
st.subheader("Alarm Details")
st.dataframe(filtered_df, use_container_width=True)