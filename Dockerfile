# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy wait script
COPY wait_for_services.sh /wait_for_services.sh
RUN chmod +x /wait_for_services.sh

# Run the wait script followed by the main script
ENTRYPOINT ["/wait_for_services.sh", "python", "etl.py"]
