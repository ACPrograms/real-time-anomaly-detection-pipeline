import json
import time
import sys
from confluent_kafka import Producer

# Import the data generator from sibling directory
sys.path.append('..')
from data_generator.simulate_data import generate_data_point, SENSORS, METRIC_TYPES
import random

# Kafka producer configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:29092',
    'client.id': 'iot-data-producer'
}

# The topic to which we will publish messages
TOPIC_NAME = 'iot-data-stream'

def delivery_report(err, msg):
    """ 
    Callback function to report the delivery status of a message.
    Called once for each message produced.
    """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        # Acknowledged by the broker
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def main():
    """
    Main function to produce data to Kafka.
    """
    print("Starting Kafka producer...")
    producer = Producer(KAFKA_CONFIG)
    
    print("Press Ctrl+C to stop.")
    try:
        while True:
            # Generate a data point
            sensor_id = random.choice(SENSORS)
            metric_type = random.choice(METRIC_TYPES)
            data_point = generate_data_point(sensor_id, metric_type)
            
            # Convert dictionary to JSON string then encode to bytes
            data_str = json.dumps(data_point)
            data_bytes = data_str.encode('utf-8')

            # Produce the message to the Kafka topic
            # The poll(0) is non-blocking and triggers callbacks for delivery reports
            producer.poll(0)
            
            # The key is used by Kafka for partitioning which ensures data from the same sensor
            # goes to the same partition and that preserves order.
            producer.produce(
                TOPIC_NAME, 
                key=data_point['sensor_id'].encode('utf-8'), 
                value=data_bytes, 
                callback=delivery_report
            )
            
            # This is to wait for a short interval before sending the next message
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nProducer stopped by user.")
    finally:
        # This will wait for all messages in the producer queue to be delivered.
        print("Flushing messages...")
        producer.flush()
        print("Producer shut down.")

if __name__ == '__main__':
    main()