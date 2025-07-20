import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Singleton pattern to ensure only one engine is created
_engine = None

def get_db_engine():
    """Returns a singleton SQLAlchemy engine instance."""
    global _engine
    if _engine is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable not set.")
        _engine = create_engine(DATABASE_URL)
    return _engine

def store_sensor_data(data_point):
    """Stores a raw sensor data point in the sensor_data table."""
    engine = get_db_engine()
    try:
        with engine.connect() as connection:
            stmt = text("""
                INSERT INTO sensor_data (sensor_id, metric_type, value, timestamp)
                VALUES (:sensor_id, :metric_type, :value, :timestamp)
            """)
            connection.execute(stmt, parameters=data_point)
            connection.commit()
    except Exception as e:
        print(f"Error storing sensor data: {e}")

def store_anomaly(anomaly_data):
    """Stores a detected anomaly in the anomalies table."""
    engine = get_db_engine()
    try:
        with engine.connect() as connection:
            stmt = text("""
                INSERT INTO anomalies (sensor_id, metric_type, value, z_score, timestamp)
                VALUES (:sensor_id, :metric_type, :value, :z_score, :timestamp)
            """)
            connection.execute(stmt, parameters=anomaly_data)
            connection.commit()
    except Exception as e:
        print(f"Error storing anomaly data: {e}")