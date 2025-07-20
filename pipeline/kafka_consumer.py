import json
import sys
from confluent_kafka import Consumer, KafkaException, KafkaError

from anomaly_detector import AnomalyDetector
from alert_system import send_slack_alert

# Kafka consumer configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'iot-anomaly-detector-group', # Use a new group.id for the new logic
    'auto.offset.reset': 'earliest'
}

TOPIC_NAME = 'iot-data-stream'

def main():
    """
    Main function to consume data, detect anomalies, and send alerts.
    """
    print("Starting anomaly detection consumer...")
    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe([TOPIC_NAME])
    
    # Initialize our anomaly detector
    detector = AnomalyDetector(window_size=30, z_score_threshold=3.0)
    
    print(f'Subscribed to topic "{TOPIC_NAME}"')
    print("Waiting for messages... Press Ctrl+C to stop.")
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write(f'%% {msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Message received successfully
                data_point = json.loads(msg.value().decode('utf-8'))
                
                # Check for anomalies
                result = detector.check(data_point)
                
                # Print the result to the console, highlighting anomalies
                if result['is_anomaly']:
                    print(f"ANOMALY DETECTED: {result}")
                    # Send an alert
                    send_slack_alert(result)
                else:
                    print(f"Received normal data point: {result}")

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    finally:
        print("Closing consumer...")
        consumer.close()
        print("Consumer shut down.")

if __name__ == '__main__':
    main()