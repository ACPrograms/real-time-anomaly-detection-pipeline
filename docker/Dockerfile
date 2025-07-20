# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
# This includes the 'pipeline', 'data_generator', etc. folders.
COPY . .

# Command to run when the container starts
# We run the consumer as it's the main long-running process
# Using '-m' ensures Python paths work correctly
CMD ["python3", "-m", "pipeline.kafka_consumer"]