# Build stage
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    linux-headers \
    unzip \
    curl \
    nodejs \
    npm \
    git

# Set working directory
WORKDIR /build

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize Reflex app
RUN reflex init

# Production stage
FROM python:3.12-alpine

# Install runtime dependencies
RUN apk add --no-cache \
    nodejs \
    npm \
    linux-headers

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/reflex /usr/local/bin/reflex

# Copy application from builder
COPY --from=builder /build /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 3000

# Run the application
CMD ["reflex", "run"]