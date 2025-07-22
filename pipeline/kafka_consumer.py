import json
import sys
import os
import time
from threading import Thread
from confluent_kafka import Consumer, KafkaException, KafkaError
from prometheus_client import start_http_server, Counter, Gauge, Histogram

# Local module imports
from anomaly_detector import AnomalyDetector
from alert_system import send_slack_alert
from etl import store_sensor_data, store_anomaly

# - Prometheus Metrics -
# These objects track metrics that will be exposed on an HTTP endpoint.
MESSAGES_PROCESSED = Counter('messages_processed_total', 'Total number of messages processed')
ANOMALIES_DETECTED = Counter('anomalies_detected_total', 'Total number of anomalies detected', ['metric_type'])
CURRENT_SENSOR_VALUE = Gauge('current_sensor_value', 'The most recent value of a sensor', ['sensor_id', 'metric_type'])
PROCESSING_LATENCY = Histogram('processing_latency_seconds', 'Time taken to process a message')

# Use environment variable, default to internal Docker name for local dev
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'iot-data-processing-group',
    'auto.offset.reset': 'earliest'
}
TOPIC_NAME = 'iot-data-stream'

def main():
    print("Starting data processing consumer with metrics...")
    
    # Start the Prometheus metrics server in a background thread
    # This will expose metrics on port 8000
    start_http_server(8000)
    print("Prometheus metrics server started on port 8000")

    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe([TOPIC_NAME])
    
    detector = AnomalyDetector(window_size=30, z_score_threshold=3.0)
    
    print(f'Subscribed to topic "{TOPIC_NAME}". Waiting for messages...')
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write(f'%% End of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}\n')
                else:
                    raise KafkaException(msg.error())
            else:
                start_time = time.time()
                
                # --- Metric Instrumentation ---
                MESSAGES_PROCESSED.inc()
                
                data_point = json.loads(msg.value().decode('utf-8'))
                
                store_sensor_data(data_point)
                result = detector.check(data_point)
                
                CURRENT_SENSOR_VALUE.labels(
                    sensor_id=result['sensor_id'], 
                    metric_type=result['metric_type']
                ).set(result['value'])
                
                if result.get('is_anomaly'):
                    ANOMALIES_DETECTED.labels(metric_type=result['metric_type']).inc()
                    print(f"ANOMALY DETECTED: {result}")
                    store_anomaly(result)
                    send_slack_alert(result)
                else:
                    print(f"Processed normal data point for sensor {result['sensor_id']}")

                # Record the processing time
                latency = time.time() - start_time
                PROCESSING_LATENCY.observe(latency)

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    finally:
        consumer.close()
        print("Consumer shut down.")

if __name__ == '__main__':
    main()