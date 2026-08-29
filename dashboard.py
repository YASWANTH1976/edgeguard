import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# Set up the Streamlit page layout
st.set_page_config(page_title="EdgeGuard SecOps Dashboard", page_icon="🛡️", layout="wide")
st.title("🛡️ EdgeGuard SecOps & Compliance Dashboard")

DB_PATH = "secure_audit_ledger.db"

def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM compliance_logs", conn)
    conn.close()
    
    if not df.empty:
        # Convert string timestamp to datetime for graphing
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

# Build the Interface
if not df.empty:
    st.sidebar.header("System Status")
    st.sidebar.success("✅ Cryptographic Database Connected")
    st.sidebar.info(f"Last sync: {df['timestamp'].iloc[-1]}")
    
    # Top KPI Metrics
    st.subheader("Real-Time Threat Analytics")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Security Events Logged", value=len(df))
    
    high_threats = len(df[df['threat_level'] == 'Critical'])
    col2.metric(label="Critical Action Triggers", value=high_threats)
    
    unique_objects = df['object_label'].nunique()
    col3.metric(label="Unique Threat Vectors", value=unique_objects)
    
    st.markdown("---")
    
    # Charts Row
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Pie Chart showing what objects triggered the system
        fig = px.pie(df, names='object_label', title="Distribution of Intercepted Threats")
        st.plotly_chart(fig, use_container_width=True)
        
    with chart_col2:
        # Time series graph showing when threats occur
        timeline_df = df.groupby(df['timestamp'].dt.hour).size().reset_index(name='count')
        timeline_df.columns = ['Hour of Day', 'Total Incidents']
        fig2 = px.bar(timeline_df, x='Hour of Day', y='Total Incidents', title="Threat Heatmap (By Hour)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    
    # Data Table for Cryptographic Hashes
    st.subheader("Immutable Cryptographic Audit Ledger (SHA-256)")
    st.write("This ledger proves the integrity of security logs for compliance reviews.")
    display_df = df[['id', 'timestamp', 'threat_level', 'action', 'current_hash']].copy()
    st.dataframe(display_df.sort_values(by='id', ascending=False), use_container_width=True)

else:
    st.warning("No security logs found yet. Please run `main.py` and allow EdgeGuard to log an event first!")