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
COPY app.py .

# Create directories for models and results (will be downloaded at runtime from HF)
RUN mkdir -p ./Models ./Results

# Set environment variables
ENV PORT=7860
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/huggingface
EXPOSE 7860

# Run the application
CMD exec python app.py

