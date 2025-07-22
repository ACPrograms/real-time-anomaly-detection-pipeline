import os
import json
import time
import requests
from confluent_kafka import Producer
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Use environment variable for Kafka, default to localhost for local dev
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092')
KAFKA_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': 'weather-data-producer'
}
TOPIC_NAME = 'iot-data-stream'
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY_NAME")
API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def delivery_report(err, msg):
    """Callback function to report message delivery status."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def fetch_weather_data():
    """Fetches weather data from the OpenWeatherMap API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OpenWeatherMap API: {e}")
        return None

def transform_data(raw_data):
    """Transforms raw API data into our pipeline's standardized format."""
    transformed_points = []
    timestamp = datetime.now(timezone.utc).isoformat()
    city_name_as_sensor = raw_data['name'].replace(" ", "_")

    # Temperature
    transformed_points.append({
        "sensor_id": f"{city_name_as_sensor}-temp",
        "metric_type": "temperature",
        "value": raw_data['main']['temp'],
        "timestamp": timestamp
    })
    # Humidity
    transformed_points.append({
        "sensor_id": f"{city_name_as_sensor}-humidity",
        "metric_type": "humidity",
        "value": raw_data['main']['humidity'],
        "timestamp": timestamp
    })
    # Pressure
    transformed_points.append({
        "sensor_id": f"{city_name_as_sensor}-pressure",
        "metric_type": "pressure",
        "value": raw_data['main']['pressure'],
        "timestamp": timestamp
    })
    
    return transformed_points

def main():
    """Main function to produce real-time weather data to Kafka."""
    if not API_KEY or not CITY:
        raise ValueError("OPENWEATHER_API_KEY and CITY_NAME must be set in the .env file.")

    producer = Producer(KAFKA_CONFIG)
    print("Starting real-time weather producer...")
    print(f"Fetching data for city: {CITY}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            raw_data = fetch_weather_data()
            if raw_data:
                data_points = transform_data(raw_data)
                
                print(f"Fetched and transformed data: {data_points}")

                for point in data_points:
                    producer.poll(0)
                    producer.produce(
                        TOPIC_NAME,
                        key=point['sensor_id'].encode('utf-8'),
                        value=json.dumps(point).encode('utf-8'),
                        callback=delivery_report
                    )
                
                producer.flush()

            # Wait for 15 seconds before the next API call to respect free-tier limits
            time.sleep(15)

    except KeyboardInterrupt:
        print("\nProducer stopped by user.")
    finally:
        producer.flush()
        print("Producer shut down.")

if __name__ == '__main__':
    main()