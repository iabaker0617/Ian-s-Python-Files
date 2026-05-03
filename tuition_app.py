import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Tuition Model Prototyper", layout="wide")

st.title("Net Tuition Revenue: Block vs. Per-Credit Model")

# 2. File Path Definition
# Using a raw string for your specific BU OneDrive path
DEFAULT_FILE_PATH = r"C:\Users\iabaker\OneDrive - Boston University\Data Projects\Operations\Tuition change prototyping\Tuition change data modeling demo data.xlsx"

# 3. Sidebar: Model Levers
st.sidebar.header("Model Assumptions")

# Proposed rate input
new_rate = st.sidebar.number_input(
    "Proposed Per-Credit Rate ($)", 
    min_value=0, 
    value=2200, 
    step=50
)

# 4. Data Loading Logic (Auto-load with Manual Backup)
df = None

# Try to auto-load from the hardcoded path first
if os.path.exists(DEFAULT_FILE_PATH):
    try:
        df = pd.read_excel(DEFAULT_FILE_PATH)
        st.sidebar.success("Loaded data from OneDrive automatically.")
    except Exception as e:
        st.sidebar.error(f"Auto-load failed: {e}")

# Allow manual upload to override or replace if auto-load fails
uploaded_file = st.sidebar.file_uploader("Override with different Excel file", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.sidebar.info("Using uploaded file instead of OneDrive source.")

# 5. App Logic (Runs only if df exists)
if df is not None:
    try:
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Verify columns
        required_cols = ['StudentID', 'Discount Rate', 'Block Rate', 'Credits Taken']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Data missing required columns: {required_cols}")
            st.stop()

        # Calculation: Current State
        df['Current_NTR'] = df['Block Rate'] * (1 - df['Discount Rate'])
        
        # Calculation: Proposed State
        # Using the same discount rate for now unless you want a separate slider
        df['Proposed_NTR'] = (df['Credits Taken'] * new_rate) * (1 - df['Discount Rate'])
        
        # Revenue Difference
        df['Revenue_Delta'] = df['Proposed_NTR'] - df['Current_NTR']

        # 6. Dashboard Metrics
        total_current = df['Current_NTR'].sum()
        total_proposed = df['Proposed_NTR'].sum()
        total_delta = total_proposed - total_current
        pct_change = (total_delta / total_current) * 100 if total_current != 0 else 0

        # KPI Cards with Corrected Coloring
        # 'normal' means green is up, red is down.
        # If your delta is a loss, it will now show as red automatically.
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Total NTR", f"${total_current:,.0f}")
        c2.metric(
            "Proposed Total NTR", 
            f"${total_proposed:,.0f}", 
            delta=f"${total_delta:,.0f}",
            delta_color="normal" 
        )
        c3.metric("Percent Change", f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")

        st.divider()

        # 7. Visual Analysis
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Avg Revenue Change by Credits")
            impact_by_credit = df.groupby('Credits Taken')['Revenue_Delta'].mean()
            st.bar_chart(impact_by_credit)

        with col_right:
            st.subheader("Student Count by Credit Load")
            credit_counts = df['Credits Taken'].value_counts().sort_index()
            st.bar_chart(credit_counts)

        # 8. Data Preview
        with st.expander("View Student-Level Breakdown"):
            st.dataframe(df[['StudentID', 'Credits Taken', 'Current_NTR', 'Proposed_NTR', 'Revenue_Delta']], use_container_width=True)

    except Exception as e:
        st.error(f"Error processing data: {e}")
else:
    st.warning("No data found. Please ensure the OneDrive file exists or upload a file manually in the sidebar.")