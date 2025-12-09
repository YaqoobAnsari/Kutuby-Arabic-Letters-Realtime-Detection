FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libsndfile1 ffmpeg git && rm -rf /var/lib/apt/lists/*

# Set matplotlib cache directory
ENV MPLCONFIGDIR=/tmp/matplotlib

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Download the model from Hugging Face
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='yansari/arabic-letters-wav2vec2-base', local_dir='Models/facebook__wav2vec2-base')"

EXPOSE 7860

CMD ["python", "app.py"]
