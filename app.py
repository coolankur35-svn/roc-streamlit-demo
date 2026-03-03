import streamlit as st
import pandas as pd

# --- Upload/Read Excel/CSV ---
uploaded_file = st.file_uploader("Upload alarm data", type=["csv", "xlsx"])
if uploaded_file is not None:
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
    
    st.write("Columns detected:", df.columns.tolist())

    # --- Sidebar filters ---
    st.sidebar.header("Filters")
    filters = {}
    possible_filters = ["Priority", "Severity", "Alarm Type", "Device", "Status"]  # add more if needed

    for col in possible_filters:
        if col in df.columns:
            selected = st.sidebar.multiselect(f"{col}", options=df[col].unique())
            if selected:
                filters[col] = selected

    # --- Apply filters dynamically ---
    filtered_df = df.copy()
    for col, selected_values in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

    # --- Display filtered data ---
    st.write(f"Showing {len(filtered_df)} rows after filtering")
    st.dataframe(filtered_df)