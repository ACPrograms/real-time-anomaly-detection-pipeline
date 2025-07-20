import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(anomaly_data):
    """
    Sends a formatted alert to a Slack channel via an Incoming Webhook.
    
    Args:
        anomaly_data (dict): The dictionary containing details of the detected anomaly.
    """
    if not SLACK_WEBHOOK_URL:
        print("Error: SLACK_WEBHOOK_URL not configured. Cannot send alert.")
        return

    try:
        # Format a rich message for Slack
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":warning: Anomaly Detected! :warning:",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Sensor ID:*\n`{anomaly_data['sensor_id']}`"},
                        {"type": "mrkdwn", "text": f"*Metric:*\n`{anomaly_data['metric_type']}`"},
                        {"type": "mrkdwn", "text": f"*Anomalous Value:*\n`{anomaly_data['value']}`"},
                        {"type": "mrkdwn", "text": f"*Z-Score:*\n`{anomaly_data['z_score']}`"},
                        {"type": "mrkdwn", "text": f"*Timestamp (UTC):*\n`{anomaly_data['timestamp']}`"}
                    ]
                },
                {
                    "type": "divider"
                }
            ]
        }
        
        response = requests.post(
            SLACK_WEBHOOK_URL, 
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status() # Raise an exception for HTTP errors
        print(f"Successfully sent Slack alert for sensor {anomaly_data['sensor_id']}.")

    except requests.exceptions.RequestException as e:
        print(f"Error sending Slack alert: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in send_slack_alert: {e}")