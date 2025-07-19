# Real Time Anomaly Detection Pipeline

### **How to Run and Test Week 1**

1.  **Navigate to the project directory:**
    ```bash
    cd real-time-anomaly-detection-pipeline
    ```
2.  **Run the data generator:**
    ```bash
    python data_generator/simulate_data.py
    ```
3.  **Observe the output:** You should see a stream of JSON objects printed to your terminal every two seconds. Occasionally, you will see a value that is clearly an anomaly (e.g., `temperature` above 50).

    **Example Output:**
    ```
    Starting data simulation stream...
    Press Ctrl+C to stop.
    {"sensor_id": "sensor-05", "metric_type": "pressure", "value": 1012.34, "timestamp": "2025-07-19T10:52:10.123456Z"}
    {"sensor_id": "sensor-02", "metric_type": "temperature", "value": 22.81, "timestamp": "2025-07-19T10:52:12.123456Z"}
    {"sensor_id": "sensor-09", "metric_type": "humidity", "value": 95.45, "timestamp": "2025-07-19T10:52:14.123456Z"}  <-- ANOMALY!
    {"sensor_id": "sensor-07", "metric_type": "temperature", "value": 28.55, "timestamp": "2025-07-19T10:52:16.123456Z"}
    ```
