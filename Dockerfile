FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (keep your existing ones + add curl for health checks)
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set matplotlib cache directory
ENV MPLCONFIGDIR=/tmp/matplotlib

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download the model from Hugging Face (keep your existing model download)
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='yansari/arabic-letters-wav2vec2-base', local_dir='Models/facebook__wav2vec2-base', local_dir_use_symlinks=False)"

# Cloud Run uses PORT environment variable (not fixed 7860)
ENV PORT=8080
EXPOSE 8080

# Run with environment variable PORT
CMD exec python app.py