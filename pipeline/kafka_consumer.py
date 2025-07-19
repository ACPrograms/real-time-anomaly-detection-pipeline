import json
import sys
from confluent_kafka import Consumer, KafkaException, KafkaError

# Kafka consumer configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'iot-data-consumer-group', # Consumer group ID
    'auto.offset.reset': 'earliest' # Start reading from the beginning of the topic
}

# The topic from which we will consume messages
TOPIC_NAME = 'iot-data-stream'

def main():
    """
    Main function to consume data from Kafka.
    """
    print("Starting Kafka consumer...")
    consumer = Consumer(KAFKA_CONFIG)

    # Subscribe to the topic
    consumer.subscribe([TOPIC_NAME])
    print(f'Subscribed to topic "{TOPIC_NAME}"')

    print("Waiting for messages... Press Ctrl+C to stop.")
    try:
        while True:
            # Poll for new messages
            msg = consumer.poll(timeout=1.0) # Timeout of 1 second

            if msg is None:
                # No message received within the timeout period
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event this is not an error
                    sys.stderr.write(f'%% {msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')
                elif msg.error():
                    # Real error
                    raise KafkaException(msg.error())
            else:
                # Proper message received
                # The value is in bytes so what we do is decode it
                value = msg.value().decode('utf-8')
                # this is optional but this is to convert JSON string back to Python dict
                data = json.loads(value)
                
                print(f"Received message from sensor {data['sensor_id']}: {data}")

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    finally:
        # Close the consumer connection cleanly
        print("Closing consumer...")
        consumer.close()
        print("Consumer shut down.")

if __name__ == '__main__':
    main()