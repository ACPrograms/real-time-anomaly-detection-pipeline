import json
import random
import time
from datetime import datetime, timezone

# Configuration for the sensors and their normal operating ranges
SENSOR_CONFIG = {
    "temperature": {"normal_range": (15, 30), "anomaly_range": (50, 100)},
    "humidity": {"normal_range": (30, 60), "anomaly_range": (80, 100)},
    "pressure": {"normal_range": (1000, 1020), "anomaly_range": (950, 1050)},
}

SENSORS = [f"sensor-{i:02d}" for i in range(1, 11)] # sensor-01 to sensor-10
METRIC_TYPES = list(SENSOR_CONFIG.keys())

def generate_data_point(sensor_id, metric_type):
    """
    Generates a single data point for a given sensor and metric type.
    There is a 5% chance of generating an anomalous value.
    """
    is_anomaly = random.random() < 0.05  # 5% chance of an anomaly

    if is_anomaly:
        # Generate an anomalous value
        min_val, max_val = SENSOR_CONFIG[metric_type]["anomaly_range"]
    else:
        # Generate a normal value
        min_val, max_val = SENSOR_CONFIG[metric_type]["normal_range"]

    value = round(random.uniform(min_val, max_val), 2)
    
    data_point = {
        "sensor_id": sensor_id,
        "metric_type": metric_type,
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return data_point

def stream_data(frequency_seconds=2):
    """
    Continuously streams data by printing JSON objects to the console.
    
    Args:
        frequency_seconds (int): The time to wait between generating data points.
    """
    print("Starting data simulation stream...")
    print("Press Ctrl+C to stop.")
    while True:
        try:
            # Randomly select a sensor and a metric type for each data point
            sensor_id = random.choice(SENSORS)
            metric_type = random.choice(METRIC_TYPES)
            
            data = generate_data_point(sensor_id, metric_type)
            
            # Print the JSON data to stdout to simulate a stream
            print(json.dumps(data))
            
            time.sleep(frequency_seconds)
        except KeyboardInterrupt:
            print("\nData simulation stopped.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(frequency_seconds * 2) # Wait longer after an error

if __name__ == "__main__":
    stream_data()