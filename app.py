import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ROC Dashboard", layout="wide")
st.title("ROC Dashboard")

# --- Upload file ---
uploaded_file = st.file_uploader("Upload PowerBI export", type=["csv", "xlsx"])

if uploaded_file is not None:
    # --- Read file ---
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()  # clean column names

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    filters = {}
    for col in ["Severity", "Alarm Type", "Device", "Status"]:
        if col in df.columns:
            selected = st.sidebar.multiselect(f"{col}", options=df[col].unique())
            if selected:
                filters[col] = selected

    filtered_df = df.copy()
    for col, values in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(values)]

    # --- KPI Cards ---
    kpi_cols = st.columns(5)
    total = len(filtered_df)
    critical = len(filtered_df[filtered_df["Severity"]=="Critical"]) if "Severity" in df.columns else 0
    high = len(filtered_df[filtered_df["Severity"]=="High"]) if "Severity" in df.columns else 0
    medium = len(filtered_df[filtered_df["Severity"]=="Medium"]) if "Severity" in df.columns else 0
    low = len(filtered_df[filtered_df["Severity"]=="Low"]) if "Severity" in df.columns else 0

    kpi_cols[0].metric("Total Alarms", total)
    kpi_cols[1].metric("Critical", critical)
    kpi_cols[2].metric("High", high)
    kpi_cols[3].metric("Medium", medium)
    kpi_cols[4].metric("Low", low)

    # --- Charts Row ---
    chart_cols = st.columns(3)

    # Severity Bar Chart
    if "Severity" in filtered_df.columns:
        fig_sev = px.bar(filtered_df, x="Severity", color="Severity",
                         color_discrete_map={"Critical":"red","High":"orange","Medium":"yellow","Low":"green"},
                         title="Alarms by Severity", text_auto=True)
        chart_cols[0].plotly_chart(fig_sev, use_container_width=True)

    # Device Pie Chart
    if "Device" in filtered_df.columns:
        fig_dev = px.pie(filtered_df, names="Device", title="Alarms by Device",
                         hover_data=[filtered_df["Device"]])
        chart_cols[1].plotly_chart(fig_dev, use_container_width=True)

    # Trend Line Chart
    if "Date" in filtered_df.columns:
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors='coerce')
        trend = filtered_df.groupby(filtered_df["Date"].dt.date).size().reset_index(name="Count")
        fig_trend = px.line(trend, x="Date", y="Count", title="Alarms Trend Over Time",
                            markers=True, text="Count")
        chart_cols[2].plotly_chart(fig_trend, use_container_width=True)

    # --- Filtered Table with Conditional Formatting ---
    st.subheader("Filtered Alarm Data")
    if "Severity" in filtered_df.columns:
        def highlight_severity(row):
            color = ""
            if row["Severity"] == "Critical":
                color = "background-color: red; color: white"
            elif row["Severity"] == "High":
                color = "background-color: orange; color: black"
            elif row["Severity"] == "Medium":
                color = "background-color: yellow; color: black"
            elif row["Severity"] == "Low":
                color = "background-color: green; color: white"
            return [color]*len(row)
        st.dataframe(filtered_df.style.apply(highlight_severity, axis=1))
    else:
        st.dataframe(filtered_df)

    # --- Download Filtered Data ---
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Filtered Data", csv, "filtered_alarms.csv", "text/csv")

else:
    st.info("Please upload a PowerBI export to display the dashboard.")