import json
import sys
from confluent_kafka import Consumer, KafkaException, KafkaError

# Local module imports
from anomaly_detector import AnomalyDetector
from alert_system import send_slack_alert
from etl import store_sensor_data, store_anomaly

# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'iot-data-processing-group',
    'auto.offset.reset': 'earliest'
}
TOPIC_NAME = 'iot-data-stream'

def main():
    print("Starting data processing consumer...")
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
                data_point = json.loads(msg.value().decode('utf-8'))
                
                # Store every raw data point
                store_sensor_data(data_point)
                
                # Check for anomalies
                result = detector.check(data_point)
                
                if result.get('is_anomaly'):
                    print(f"ANOMALY DETECTED: {result}")
                    # Store the anomaly
                    store_anomaly(result)
                    # Send an alert
                    send_slack_alert(result)
                else:
                    print(f"Processed normal data point for sensor {result['sensor_id']}")

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    finally:
        consumer.close()
        print("Consumer shut down.")

if __name__ == '__main__':
    main()