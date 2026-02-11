FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir google-cloud-storage

# Copy application code
COPY Code/ ./Code/
COPY app.py .

# Create user for HF Spaces (runs as uid 1000) and writable dirs
RUN useradd -m -u 1000 user && \
    mkdir -p ./Models ./Results /tmp/matplotlib /tmp/huggingface /tmp/fontconfig /tmp/torch_cache && \
    chown -R user:user /app /tmp/matplotlib /tmp/huggingface /tmp/fontconfig /tmp/torch_cache

# Set environment variables
ENV PORT=7860
ENV HOME=/home/user
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/huggingface
ENV FONTCONFIG_PATH=/tmp/fontconfig
ENV TORCHINDUCTOR_CACHE_DIR=/tmp/torch_cache
EXPOSE 7860

USER 1000

# Run the application
CMD exec python app.py
