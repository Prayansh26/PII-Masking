# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install botocore==1.29.128
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 80 to the world outside this container (optional, can be removed if not needed)
EXPOSE 80

# Run the script
ENTRYPOINT ["python", "etl.py"]