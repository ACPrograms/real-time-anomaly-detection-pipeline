import numpy as np
from collections import deque

class AnomalyDetector:
    """
    A class to detect anomalies in sensor data using a rolling Z-score.
    
    This detector maintains a separate history (a deque) for each sensor metric
    to calculate the rolling mean and standard deviation.
    """
    def __init__(self, window_size=30, z_score_threshold=3.0):
        """
        Initializes the AnomalyDetector.
        
        Args:
            window_size (int): The number of recent data points to consider for the rolling average.
            z_score_threshold (float): The number of standard deviations from the mean to be considered an anomaly.
        """
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.data_history = {}

    def check(self, data_point):
        """
        Checks a new data point for anomalies and updates the history.
        
        Args:
            data_point (dict): A dictionary representing a single sensor reading.
                               Must contain 'sensor_id', 'metric_type', and 'value'.
                               
        Returns:
            dict: The original data_point dictionary, augmented with an 'is_anomaly' boolean
                  and a 'z_score' float if calculable.
        """
        sensor_id = data_point['sensor_id']
        metric_type = data_point['metric_type']
        value = data_point['value']
        
        history_key = (sensor_id, metric_type)
        
        if history_key not in self.data_history:
            self.data_history[history_key] = deque(maxlen=self.window_size)
            
        history = self.data_history[history_key]
        
        data_point['is_anomaly'] = False
        data_point['z_score'] = None
        
        if len(history) > 1:
            mean = np.mean(history)
            std_dev = np.std(history)
            
            if std_dev > 0:
                z_score = abs((value - mean) / std_dev)
                
                data_point['z_score'] = float(round(z_score, 2))
                
                if z_score > self.z_score_threshold:
                    data_point['is_anomaly'] = True
        
        history.append(value)
        
        return data_point