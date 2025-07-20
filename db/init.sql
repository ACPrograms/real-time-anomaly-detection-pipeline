-- This db script will be executed when the Docker container starts for the first time

-- Create a table to store all incoming sensor data
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL
);

-- Create a table to store only the detected anomalies
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    z_score FLOAT,
    timestamp TIMESTAMPTZ NOT NULL
);

-- This is optional but to create indexes for faster queries on columns that will be frequently filtered
CREATE INDEX idx_sensor_data_timestamp ON sensor_data (timestamp);
CREATE INDEX idx_sensor_data_sensor_id ON sensor_data (sensor_id);
CREATE INDEX idx_anomalies_timestamp ON anomalies (timestamp);