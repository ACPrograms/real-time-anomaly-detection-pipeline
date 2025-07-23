import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file at the project root
load_dotenv()

# Use the specific database URL meant for the dashboard running on the host
DATABASE_URL = os.getenv("RENDER_POSTGRES_URL", os.getenv("DASHBOARD_DATABASE_URL"))

# Page configuration
st.set_page_config(
    page_title="Real-Time Data Anomaly Dashboard",
    page_icon="📊",
    layout="wide",
)

@st.cache_resource
def get_db_engine():
    """Returns a singleton SQLAlchemy engine instance."""
    if not DATABASE_URL:
        st.error("DASHBOARD_DATABASE_URL not set. Please configure it in your .env file.")
        st.stop()
    return create_engine(DATABASE_URL)

def fetch_data(query, engine):
    """Fetches data from the database using a SQL query."""
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()

# --- Dashboard UI ---
st.title("📊 Real-Time IoT Anomaly Detection Dashboard")

# Create placeholders for live updates
latest_data_placeholder = st.empty()
anomaly_table_placeholder = st.empty()
charts_placeholder = st.empty()

# Main loop to refresh the dashboard
while True:
    engine = get_db_engine()

    # --- Fetch Data ---
    latest_data_query = "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;"
    anomalies_query = "SELECT * FROM anomalies ORDER BY timestamp DESC;"
    
    latest_data_df = fetch_data(latest_data_query, engine)
    anomalies_df = fetch_data(anomalies_query, engine)

    # --- Display Latest Data ---
    with latest_data_placeholder.container():
        st.subheader("📡 Live Data Feed")
        st.dataframe(latest_data_df, use_container_width=True)

    # --- Display Anomalies ---
    with anomaly_table_placeholder.container():
        st.subheader("⚠️ Detected Anomalies")
        st.dataframe(anomalies_df, use_container_width=True)

    # --- Display Charts ---
    if not anomalies_df.empty:
        with charts_placeholder.container():
            st.subheader("📈 Anomaly Analytics")
            
            col1, col2 = st.columns(2)

            with col1:
                st.write("Anomalies by Sensor ID")
                anomaly_count_by_sensor = anomalies_df['sensor_id'].value_counts()
                st.bar_chart(anomaly_count_by_sensor)

            with col2:
                st.write("Anomalies by Metric Type")
                anomaly_count_by_type = anomalies_df['metric_type'].value_counts()
                st.bar_chart(anomaly_count_by_type)

    # Auto-refresh interval
    time.sleep(5)