---
title: Arabic Pronunciation Trainer
emoji: 🔤
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Arabic Alphabet Realtime — wav2vec2-base

FastAPI demo for a fine-tuned **wav2vec2-base** model that classifies **Arabic letters** from short audio snippets (mic or file).
No Gradio, no ffmpeg—just vanilla HTML/JS in the browser and a FastAPI backend. Uses GPU if available.

**Model weights** are hosted on Hugging Face: [`yansari/arabic-letters-wav2vec2-base`](https://huggingface.co/yansari/arabic-letters-wav2vec2-base).  
The installer downloads them automatically into `Models/facebook__wav2vec2-base/`.

---

## Features

- 🎙️ In-browser mic recording (WAV encoded client-side)
- ⚡ FastAPI backend with torch/transformers (CUDA if present)
- 📈 Live probabilities, waveform plot, top-K table
- 🧪 Optional training diagnostics (confusion matrix, per-class report)
- 🌐 One-flag public sharing via ngrok (`--share`)
- 🔌 **NEW**: REST API endpoint for letter verification (perfect for Postman testing!)

---

## Quickstart

```bash
# 1) clone
git clone https://github.com/YaqoobAnsari/arabic-letters-realtime.git
cd arabic-letters-realtime

# 2) install (creates .venv, installs deps, downloads model from HF)
bash scripts/install.sh

# 3) run
bash scripts/run.sh
# open http://localhost:7860

# 4) (Optional) Test the API endpoint with Postman
# See POSTMAN_GUIDE.md for detailed instructions
```

---

## API Endpoints

### 1. Web Interface (Browser UI)
**URL**: `http://localhost:7860/`
**Method**: GET
**Description**: Interactive web interface with microphone recording and file upload

### 2. Letter Verification API (NEW!)
**URL**: `http://localhost:7860/verify_letter`
**Method**: POST
**Description**: Verify if an audio file matches a target Arabic letter

**Parameters**:
- `audio` (File, required): WAV audio file (1-2 seconds)
- `target_letter` (Text, required): Expected letter (e.g., "Alif", "Ba", "Ta")
- `threshold` (Number, optional): Confidence threshold (default: 0.6 = 60%)
- `fixed_seconds` (Number, optional): Audio window length (default: 1.0)

**Example Response**:
```json
{
  "result": true,
  "target_letter": "Alif",
  "target_probability": 0.9876,
  "predicted_letter": "Alif",
  "predicted_probability": 0.9876,
  "threshold": 0.6,
  "message": "✓ Success: 'Alif' detected with 98.76% confidence (threshold: 60%)",
  "latency_ms": 12.5
}
```

**Testing the API**:
- 📘 [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) - Complete Postman tutorial with step-by-step instructions
- 📗 [POSTMAN_VISUAL_GUIDE.md](POSTMAN_VISUAL_GUIDE.md) - Visual guide with UI examples and troubleshooting
- 📙 [API_EXAMPLES.md](API_EXAMPLES.md) - Code examples in Python, cURL, JavaScript, and more
- 🧪 [test_verify_endpoint.py](test_verify_endpoint.py) - Ready-to-use Python test script

**Available Letters**: Aain, Alif, Ba, Dad, Dah, Dal, Fa, Ghain, Ha, Haa, Jeem, Kaf, Khaa, Laam, Meem, Noon, Qaaf, Raa, Saa, Saud, Seen, Sheen, Ta, Taa, Thaa, Waw, Yaa, Zaa

---
