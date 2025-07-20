import pytest
from pipeline.anomaly_detector import AnomalyDetector

@pytest.fixture
def detector():
    """Returns a default AnomalyDetector instance for testing."""
    return AnomalyDetector(window_size=10, z_score_threshold=3.0)

def test_initial_data_points_not_anomalies(detector):
    """Test that the first few data points are not flagged as anomalies."""
    data_point1 = {"sensor_id": "s1", "metric_type": "temp", "value": 20.0}
    result = detector.check(data_point1)
    assert not result['is_anomaly']

    data_point2 = {"sensor_id": "s1", "metric_type": "temp", "value": 21.0}
    result = detector.check(data_point2)
    assert not result['is_anomaly']

def test_normal_data_point_after_warmup(detector):
    """Test that a normal data point is not flagged after the history is populated."""
    for i in range(10):
        detector.check({"sensor_id": "s1", "metric_type": "temp", "value": 20.0 + i * 0.1})
    
    normal_point = {"sensor_id": "s1", "metric_type": "temp", "value": 21.0}
    result = detector.check(normal_point)
    assert not result['is_anomaly']
    assert result['z_score'] is not None

def test_anomaly_is_detected_correctly(detector):
    """Test that a clear anomaly is flagged."""
    for _ in range(10):
        detector.check({"sensor_id": "s1", "metric_type": "temp", "value": 20.0})
    
    anomaly_point = {"sensor_id": "s1", "metric_type": "temp", "value": 100.0}
    result = detector.check(anomaly_point)
    assert result['is_anomaly']
    assert result['z_score'] > detector.z_score_threshold

def test_state_is_maintained_per_sensor_metric(detector):
    """Test that the detector maintains separate history for different sensors/metrics."""
    # Populate history for sensor s1/temp
    for _ in range(10):
        detector.check({"sensor_id": "s1", "metric_type": "temp", "value": 20.0})

    # This should not be an anomaly, as there's no history for s2/humidity
    first_point_s2 = {"sensor_id": "s2", "metric_type": "humidity", "value": 99.0}
    result = detector.check(first_point_s2)
    assert not result['is_anomaly']import pytest
from pipeline.anomaly_detector import AnomalyDetector

@pytest.fixture
def detector():
    """Returns a default AnomalyDetector instance for testing."""
    return AnomalyDetector(window_size=10, z_score_threshold=3.0)

def test_initial_data_points_not_anomalies(detector):
    """Test that the first few data points are not flagged as anomalies."""
    data_point1 = {"sensor_id": "s1", "metric_type": "temp", "value": 20.0}
    result = detector.check(data_point1)
    assert not result['is_anomaly']

    data_point2 = {"sensor_id": "s1", "metric_type": "temp", "value": 21.0}
    result = detector.check(data_point2)
    assert not result['is_anomaly']

def test_normal_data_point_after_warmup(detector):
    """Test that a normal data point is not flagged after the history is populated."""
    for i in range(10):
        detector.check({"sensor_id": "s1", "metric_type": "temp", "value": 20.0 + i * 0.1})
    
    normal_point = {"sensor_id": "s1", "metric_type": "temp", "value": 21.0}
    result = detector.check(normal_point)
    assert not result['is_anomaly']
    assert result['z_score'] is not None

def test_anomaly_is_detected_correctly(detector):
    """Test that a clear anomaly is flagged."""
    for _ in range(10):
        detector.check({"sensor_id": "s1", "metric_type": "temp", "value": 20.0})
    
    anomaly_point = {"sensor_id": "s1", "metric_type": "temp", "value": 100.0}
    result = detector.check(anomaly_point)
    assert result['is_anomaly']
    assert result['z_score'] > detector.z_score_threshold

def test_state_is_maintained_per_sensor_metric(detector):
    """Test that the detector maintains separate history for different sensors/metrics."""
    # Populate history for sensor s1/temp
    for _ in range(10):
        detector.check({"sensor_id": "s1", "metric_type": "temp", "value": 20.0})

    # This should not be an anomaly, as there's no history for s2/humidity
    first_point_s2 = {"sensor_id": "s2", "metric_type": "humidity", "value": 99.0}
    result = detector.check(first_point_s2)
    assert not result['is_anomaly']