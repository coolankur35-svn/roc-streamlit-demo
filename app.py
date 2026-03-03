import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("ROC Unified Dashboard - Demo")

df = pd.read_excel("alarms.xlsx")

st.sidebar.header("Filters")

priority_filter = st.sidebar.multiselect(
    "Select Priority",
    options=df["Priority"].unique(),
    default=df["Priority"].unique()
)

site_filter = st.sidebar.multiselect(
    "Select SCADA Site",
    options=df["SCADASite"].unique(),
    default=df["SCADASite"].unique()
)

filtered_df = df[
    (df["Priority"].isin(priority_filter)) &
    (df["SCADASite"].isin(site_filter))
]

col1, col2, col3 = st.columns(3)

col1.metric("High", len(filtered_df[filtered_df["Priority"] == "high"]))
col2.metric("Medium", len(filtered_df[filtered_df["Priority"] == "medium"]))
col3.metric("Normal", len(filtered_df[filtered_df["Priority"] == "normal"]))

st.subheader("Equipment Breakdown")

equipment_chart = px.bar(
    filtered_df.groupby("Hardware").size().reset_index(name="Count"),
    x="Hardware",
    y="Count"
)

st.plotly_chart(equipment_chart, use_container_width=True)

st.subheader("Alarms Table")
st.dataframe(filtered_df)