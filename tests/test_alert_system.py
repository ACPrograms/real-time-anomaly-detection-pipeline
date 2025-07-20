import pytest
from pipeline import alert_system

def test_send_slack_alert_success(requests_mock):
    """Test that a Slack alert is sent correctly on a 200 OK response."""
    webhook_url = "https://hooks.slack.com/services/fake/webhook"
    requests_mock.post(webhook_url, text="ok", status_code=200)
    
    # Temporarily set the webhook URL for the test
    alert_system.SLACK_WEBHOOK_URL = webhook_url
    
    anomaly_data = {'sensor_id': 's1', 'metric_type': 'temp', 'value': 100, 'z_score': 5.0, 'timestamp': 'now'}
    
    # This should run without raising an exception
    alert_system.send_slack_alert(anomaly_data)
    
    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json()['blocks'][0]['text']['text'] == ":warning: Anomaly Detected! :warning:"

def test_send_slack_alert_failure(requests_mock, capsys):
    """Test that an error is printed on a non-200 response."""
    webhook_url = "https://hooks.slack.com/services/fake/webhook"
    requests_mock.post(webhook_url, text="error", status_code=500)
    
    alert_system.SLACK_WEBHOOK_URL = webhook_url
    anomaly_data = {'sensor_id': 's1'}
    
    alert_system.send_slack_alert(anomaly_data)
    
    # Check that an error message was printed to stdout/stderr
    captured = capsys.readouterr()
    assert "Error sending Slack alert" in captured.out

def test_no_alert_if_url_not_configured(capsys, monkeypatch):
    """Test that no alert is sent if the webhook URL is not set."""
    # Use monkeypatch to temporarily remove the environment variable
    monkeypatch.setattr(alert_system, "SLACK_WEBHOOK_URL", None)
    
    anomaly_data = {'sensor_id': 's1'}
    alert_system.send_slack_alert(anomaly_data)
    
    captured = capsys.readouterr()
    assert "SLACK_WEBHOOK_URL not configured" in captured.out