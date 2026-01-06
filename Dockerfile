# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
# PYTHONDONTWRITEBYTECODE 1: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED 1: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei

# Install system dependencies
# gcc and other build tools might be needed for some python packages like pandas/numpy if wheels aren't found
# curl/wget for healthchecks if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user for security (optional but recommended for production)
# For simple personal NAS usage, running as root inside container simplifies permission mapping often,
# but let's stick to root for now unless user asks, or verify Synology behavior.
# Synology Docker often runs as root.

# Command to run the application
# We use a default command, but this can be overridden by docker-compose or cron
CMD ["python", "main.py"]
