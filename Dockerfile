# Use Python 3.10 instead of 3.9
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory in the container
WORKDIR /app

# Copy the requirements first to leverage Docker cache
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    unzip \
    curl \
    nodejs \
    npm && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY . .

# Initialize and build the Reflex application
RUN reflex init


ENV API_URL=${API_URL}

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["reflex", "run"]