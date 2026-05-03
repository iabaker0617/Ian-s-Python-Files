import streamlit as st
import pandas as pd
import numpy as np

# Set page to wide mode for better visualization
st.set_page_config(layout="wide")

st.title("Net Tuition Revenue: Block vs. Per-Credit Model")
st.markdown("""
This app simulates the revenue impact of moving from a flat block rate to a per-credit hour model. 
Adjust the variables in the sidebar to see real-time shifts in net revenue.
""")

# 1. Load Data
file_path = r"C:\Users\iabaker\OneDrive - Boston University\Data Projects\Operations\Tuition change prototyping\Tuition change data modeling demo data.xlsx"

@st.cache_data
def load_data(path):
    # Using 'r' before the string to handle backslashes in Windows paths
    df = pd.read_excel(path)
    return df

try:
    df_raw = load_data(file_path).copy()
    
    # 2. Sidebar Parameters
    st.sidebar.header("Model Assumptions")
    
    # Let users override the 'Proposed Per Credit Rate' constant from the sheet
    suggested_rate = st.sidebar.number_input(
        "New Per-Credit Rate ($)", 
        min_value=0, 
        value=2200, 
        step=50
    )
    
    # Let users simulate a shift in the overall discount rate (scholarships)
    # This defaults to the average in your current data
    current_avg_discount = df_raw['Discount Rate'].mean()
    new_discount_target = st.sidebar.slider(
        "Projected Average Discount (%)", 
        0.0, 1.0, float(current_avg_discount),
        help="Adjusting this changes the discount applied to the new per-credit model."
    )

    # 3. Calculations
    # Current State (as defined in your notes)
    df_raw['Current_NTR'] = df_raw['Block Rate'] * (1 - df_raw['Discount Rate'])
    
    # Proposed State
    df_raw['Proposed_Gross'] = df_raw['Credits Taken'] * suggested_rate
    df_raw['Proposed_NTR'] = df_raw['Proposed_Gross'] * (1 - new_discount_target)
    
    # Impact
    df_raw['Revenue_Delta'] = df_raw['Proposed_NTR'] - df_raw['Current_NTR']
    
    # 4. Dashboard Metrics
    total_current = df_raw['Current_NTR'].sum()
    total_proposed = df_raw['Proposed_NTR'].sum()
    total_delta = total_proposed - total_current
    pct_change = (total_delta / total_current) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Total Net Revenue", f"${total_current:,.0f}")
    col2.metric("Proposed Total Net Revenue", f"${total_proposed:,.0f}", f"{total_delta:,.0f}")
    col3.metric("Percent Change", f"{pct_change:.2f}%")

    # 5. Visual Analysis
    st.subheader("Revenue Impact by Credit Load")
    
    # Grouping by credits to see who pays more vs less
    credit_analysis = df_raw.groupby('Credits Taken').agg({
        'Current_NTR': 'mean',
        'Proposed_NTR': 'mean',
        'Revenue_Delta': 'mean',
        'StudentID': 'count'
    }).rename(columns={'StudentID': 'Student Count'})
    
    st.bar_chart(credit_analysis['Revenue_Delta'])
    
    st.write("### Raw Impact Data (Preview)")
    st.dataframe(df_raw[['StudentID', 'Credits Taken', 'Current_NTR', 'Proposed_NTR', 'Revenue_Delta']].head(10))

except Exception as e:
    st.error(f"Could not load the file. Check if the path is correct and the file is not open in Excel. Error: {e}")
    