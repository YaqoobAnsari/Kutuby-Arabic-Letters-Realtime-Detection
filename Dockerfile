FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir google-cloud-storage

# Copy application code
COPY Code/ ./Code/
COPY Models/ ./Models/
COPY Results/ ./Results/

# Set port (Cloud Run uses PORT env var)
ENV PORT=8080
EXPOSE 8080

# Run the application
CMD exec python Code/serve_realtime_fastapi.py --host 0.0.0.0 --port ${PORT}

