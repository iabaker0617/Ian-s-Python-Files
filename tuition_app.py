import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Tuition Model Prototyper", layout="wide")

st.title("Net Tuition Revenue: Block vs. Per-Credit Model")

# 2. File Path Definition
DEFAULT_FILE_PATH = r"C:\Users\iabaker\OneDrive - Boston University\Data Projects\Operations\Tuition change prototyping\Tuition change data modeling demo data.xlsx"

# 3. Sidebar: Model Levers
st.sidebar.header("Model Assumptions")

new_rate = st.sidebar.number_input(
    "Proposed Per-Credit Rate ($)", 
    min_value=0, 
    value=2200, 
    step=50
)

# 4. Data Loading Logic (Auto-load with Manual Backup)
df = None

if os.path.exists(DEFAULT_FILE_PATH):
    try:
        df = pd.read_excel(DEFAULT_FILE_PATH)
        st.sidebar.success("Loaded data from OneDrive.")
    except Exception as e:
        st.sidebar.error(f"Auto-load failed: {e}")

uploaded_file = st.sidebar.file_uploader("Override with different Excel file", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.sidebar.info("Using uploaded file source.")

# 5. App Logic
if df is not None:
    try:
        df.columns = df.columns.str.strip()
        
        required_cols = ['StudentID', 'Discount Rate', 'Block Rate', 'Credits Taken']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Data missing required columns: {required_cols}")
            st.stop()

        # Calculation: Current State
        df['Current_NTR'] = df['Block Rate'] * (1 - df['Discount Rate'])
        
        # Calculation: Proposed State
        df['Proposed_NTR'] = (df['Credits Taken'] * new_rate) * (1 - df['Discount Rate'])
        
        # Revenue Difference
        df['Revenue_Delta'] = df['Proposed_NTR'] - df['Current_NTR']

        # 6. Dashboard Metrics
        total_current = df['Current_NTR'].sum()
        total_proposed = df['Proposed_NTR'].sum()
        total_delta = total_proposed - total_current
        pct_change = (total_delta / total_current) * 100 if total_current != 0 else 0

        # KPI Cards
        c1, c2, c3 = st.columns(3)
        
        c1.metric("Current Total NTR", f"${total_current:,.0f}")

        # FIX: Passing the raw float to 'delta' ensures Streamlit colors negative values RED.
        # Streamlit handles the prefixing and formatting when passed a number.
        c2.metric(
            "Proposed Total NTR", 
            f"${total_proposed:,.0f}", 
            delta=float(total_delta),
            delta_color="normal" 
        )
        
        c3.metric(
            "Percent Change", 
            f"{pct_change:.2f}%", 
            delta=f"{pct_change:.2f}%",
            delta_color="normal"
        )

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
    st.warning("No data found. Please ensure the OneDrive file exists or upload a file manually.")