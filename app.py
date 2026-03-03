import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="ROC Dashboard", layout="wide")
st.title("ROC Dashboard")

# --- Upload Excel/CSV ---
uploaded_file = st.file_uploader("Upload PowerBI alarm export", type=["csv", "xlsx"])

if uploaded_file is not None:
    # --- Read file ---
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    # --- Clean column names ---
    df.columns = df.columns.str.strip()

    st.sidebar.header("Filters")
    filters = {}
    possible_filters = ["Severity", "Alarm Type", "Device", "Status"]  # add more if needed

    for col in possible_filters:
        if col in df.columns:
            selected = st.sidebar.multiselect(f"{col}", options=df[col].unique())
            if selected:
                filters[col] = selected

    # --- Apply filters dynamically ---
    filtered_df = df.copy()
    for col, values in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(values)]

    # --- KPI / Metrics Cards ---
    kpi_cols = st.columns(5)

    total_alarms = len(filtered_df)
    critical = len(filtered_df[filtered_df["Severity"]=="Critical"]) if "Severity" in df.columns else 0
    high = len(filtered_df[filtered_df["Severity"]=="High"]) if "Severity" in df.columns else 0
    medium = len(filtered_df[filtered_df["Severity"]=="Medium"]) if "Severity" in df.columns else 0
    low = len(filtered_df[filtered_df["Severity"]=="Low"]) if "Severity" in df.columns else 0

    kpi_cols[0].metric("Total Alarms", total_alarms)
    kpi_cols[1].metric("Critical", critical)
    kpi_cols[2].metric("High", high)
    kpi_cols[3].metric("Medium", medium)
    kpi_cols[4].metric("Low", low)

    # --- Charts ---
    chart_cols = st.columns(2)

    # Severity Bar Chart
    if "Severity" in filtered_df.columns:
        fig_sev = px.bar(filtered_df, x="Severity", title="Alarms by Severity", color="Severity",
                         color_discrete_map={"Critical":"red","High":"orange","Medium":"yellow","Low":"green"})
        chart_cols[0].plotly_chart(fig_sev, use_container_width=True)

    # Device Pie Chart
    if "Device" in filtered_df.columns:
        fig_dev = px.pie(filtered_df, names="Device", title="Alarms by Device")
        chart_cols[1].plotly_chart(fig_dev, use_container_width=True)

    # Alarm trend over time
    if "Date" in filtered_df.columns:
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors='coerce')
        trend = filtered_df.groupby(filtered_df["Date"].dt.date).size().reset_index(name="Count")
        st.subheader("Alarms Trend Over Time")
        fig_trend = px.line(trend, x="Date", y="Count", title="Alarms Trend Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- Filtered Data Table ---
    st.subheader("Filtered Data Table")
    st.dataframe(filtered_df)

    # --- Download filtered data ---
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_alarms.csv',
        mime='text/csv',
    )

else:
    st.info("Please upload a PowerBI export file to view the ROC dashboard.")