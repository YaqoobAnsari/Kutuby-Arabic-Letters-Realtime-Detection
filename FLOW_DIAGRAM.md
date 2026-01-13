# API Flow Diagram

## How the `/verify_letter` Endpoint Works

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         POSTMAN (or any client)                  │
│                                                                  │
│  User fills in:                                                  │
│  • Audio file: alif_pronunciation.wav                           │
│  • Target letter: "Alif"                                        │
│  • Threshold: 0.6 (optional)                                    │
│                                                                  │
│  [Send Button] ──────────────────────────────────────────────► │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST Request
                                    │ multipart/form-data
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR FASTAPI SERVER                          │
│                    (localhost:7860)                              │
│                                                                  │
│  Endpoint: POST /verify_letter                                  │
│                                                                  │
│  Step 1: Receive Parameters                                     │
│  ├─ audio: binary WAV data                                      │
│  ├─ target_letter: "Alif"                                       │
│  └─ threshold: 0.6                                              │
│                                                                  │
│  Step 2: Load Audio File                                        │
│  ├─ Read WAV with soundfile library                             │
│  ├─ Convert to mono if stereo                                   │
│  └─ Validate format (must be WAV)                               │
│          │                                                       │
│          │ ✅ Valid                                             │
│          ▼                                                       │
│  Step 3: Preprocess Audio                                       │
│  ├─ Resample to 16kHz if needed                                 │
│  ├─ Pad or trim to 1 second (16,000 samples)                    │
│  └─ Normalize audio                                             │
│          │                                                       │
│          ▼                                                       │
│  Step 4: Run AI Model (wav2vec2-base)                           │
│  ├─ Extract features from audio                                 │
│  ├─ Forward pass through neural network                         │
│  └─ Get probability for all 28 letters                          │
│          │                                                       │
│          │ Output: [Alif: 0.98, Ba: 0.01, Ta: 0.003, ...]       │
│          ▼                                                       │
│  Step 5: Verification Logic                                     │
│  ├─ Find probability for target letter ("Alif")                 │
│  │   target_prob = 0.98                                         │
│  │                                                               │
│  ├─ Check threshold                                             │
│  │   IF target_prob >= threshold (0.98 >= 0.6)                  │
│  │   THEN result = True                                         │
│  │   ELSE result = False                                        │
│  │                                                               │
│  └─ Generate message                                            │
│      "✓ Success: 'Alif' detected with 98.00% confidence"        │
│                                                                  │
│  Step 6: Build Response                                         │
│  └─ Create JSON with all details                                │
│                                                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ HTTP 200 OK Response
                               │ Content-Type: application/json
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         POSTMAN (or any client)                  │
│                                                                  │
│  Receives JSON Response:                                        │
│  {                                                               │
│    "result": true,                                              │
│    "target_letter": "Alif",                                     │
│    "target_probability": 0.98,                                  │
│    "predicted_letter": "Alif",                                  │
│    "predicted_probability": 0.98,                               │
│    "threshold": 0.6,                                            │
│    "message": "✓ Success: 'Alif' detected...",                 │
│    "latency_ms": 12.5,                                          │
│    "all_probabilities": {...}                                   │
│  }                                                               │
│                                                                  │
│  User sees: ✅ Result = true                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Example Scenarios

### Scenario 1: Perfect Match ✅

```
INPUT:
┌─────────────────────────┐
│ Audio: Clear "Alif"     │
│ Target: "Alif"          │
│ Threshold: 0.6 (60%)    │
└─────────────────────────┘
              │
              ▼
        [AI MODEL]
              │
              ▼
┌─────────────────────────────────┐
│ Model Predictions:              │
│ • Alif:  0.987 (98.7%) ← TOP   │
│ • Ba:    0.008 (0.8%)          │
│ • Ta:    0.003 (0.3%)          │
│ • Others: < 0.1%               │
└─────────────────────────────────┘
              │
              ▼
        [VERIFICATION]
        0.987 >= 0.6?
        YES! ✅
              │
              ▼
OUTPUT:
┌─────────────────────────────────┐
│ result: true                    │
│ target_probability: 0.987       │
│ message: "✓ Success..."         │
└─────────────────────────────────┘
```

---

### Scenario 2: Wrong Letter ❌

```
INPUT:
┌─────────────────────────┐
│ Audio: Clear "Ba"       │
│ Target: "Alif"          │
│ Threshold: 0.6 (60%)    │
└─────────────────────────┘
              │
              ▼
        [AI MODEL]
              │
              ▼
┌─────────────────────────────────┐
│ Model Predictions:              │
│ • Ba:    0.952 (95.2%) ← TOP   │
│ • Ta:    0.023 (2.3%)          │
│ • Alif:  0.015 (1.5%)          │
│ • Others: < 1%                 │
└─────────────────────────────────┘
              │
              ▼
        [VERIFICATION]
        0.015 >= 0.6?
        NO! ❌
              │
              ▼
OUTPUT:
┌─────────────────────────────────┐
│ result: false                   │
│ target_probability: 0.015       │
│ predicted_letter: "Ba"          │
│ message: "✗ Failed: 'Alif'     │
│   only has 1.5% confidence...   │
│   Predicted: 'Ba' (95.2%)"      │
└─────────────────────────────────┘
```

---

### Scenario 3: Close but Not Enough ⚠️

```
INPUT:
┌─────────────────────────┐
│ Audio: Unclear "Alif"   │
│ Target: "Alif"          │
│ Threshold: 0.6 (60%)    │
└─────────────────────────┘
              │
              ▼
        [AI MODEL]
              │
              ▼
┌─────────────────────────────────┐
│ Model Predictions:              │
│ • Alif:  0.543 (54.3%) ← TOP   │
│ • Ba:    0.321 (32.1%)         │
│ • Ta:    0.089 (8.9%)          │
│ • Others: < 5%                 │
└─────────────────────────────────┘
              │
              ▼
        [VERIFICATION]
        0.543 >= 0.6?
        NO! ❌
              │
              ▼
OUTPUT:
┌─────────────────────────────────┐
│ result: false                   │
│ target_probability: 0.543       │
│ predicted_letter: "Alif"        │
│ message: "✗ Failed: 'Alif'     │
│   only has 54.3% confidence     │
│   (threshold: 60%)"             │
└─────────────────────────────────┘
```

---

## Decision Logic (Pseudocode)

```python
def verify_letter(audio_file, target_letter, threshold=0.6):
    # 1. Load and preprocess audio
    audio = load_wav(audio_file)
    audio = resample(audio, target_sr=16000)
    audio = pad_or_trim(audio, length=1.0)

    # 2. Run AI model
    probabilities = model.predict(audio)
    # Returns: {"Alif": 0.98, "Ba": 0.01, "Ta": 0.003, ...}

    # 3. Get target probability
    target_prob = probabilities[target_letter]

    # 4. Verify
    if target_prob >= threshold:
        result = True
        message = f"✓ Success: '{target_letter}' detected with {target_prob*100}% confidence"
    else:
        predicted = max(probabilities, key=probabilities.get)
        predicted_prob = probabilities[predicted]
        result = False
        message = f"✗ Failed: '{target_letter}' only has {target_prob*100}% confidence. Predicted: '{predicted}' ({predicted_prob*100}%)"

    # 5. Return response
    return {
        "result": result,
        "target_letter": target_letter,
        "target_probability": target_prob,
        "predicted_letter": predicted,
        "predicted_probability": predicted_prob,
        "threshold": threshold,
        "message": message,
        "all_probabilities": probabilities
    }
```

---

## Component Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                      YOUR SYSTEM                              │
│                                                               │
│  ┌─────────────────┐                                         │
│  │   Postman       │  HTTP Request                           │
│  │   (Client)      │─────────────────┐                       │
│  └─────────────────┘                 │                       │
│                                       ▼                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Server                          │   │
│  │                                                       │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Route Handler: /verify_letter                 │  │   │
│  │  │  • Receives audio + target_letter + threshold  │  │   │
│  │  │  • Validates inputs                            │  │   │
│  │  │  • Calls model wrapper                         │  │   │
│  │  │  • Formats response                            │  │   │
│  │  └────────────────┬───────────────────────────────┘  │   │
│  │                   │                                   │   │
│  │                   ▼                                   │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Wav2Vec2Classifier (Model Wrapper)           │  │   │
│  │  │  • Audio preprocessing                         │  │   │
│  │  │  • Feature extraction                          │  │   │
│  │  │  • Model inference                             │  │   │
│  │  │  • Post-processing                             │  │   │
│  │  └────────────────┬───────────────────────────────┘  │   │
│  │                   │                                   │   │
│  │                   ▼                                   │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  PyTorch + Transformers                        │  │   │
│  │  │  • wav2vec2-base pre-trained model            │  │   │
│  │  │  • Fine-tuned on 28 Arabic letters            │  │   │
│  │  │  • GPU-accelerated (if available)             │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Model Files (Models/facebook__wav2vec2-base/)        │ │
│  │  • config.json                                         │ │
│  │  • pytorch_model.bin (360 MB)                         │ │
│  │  • preprocessor_config.json                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Data Format Examples

### Request (Postman sends)
```http
POST /verify_letter HTTP/1.1
Host: localhost:7860
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="audio"; filename="test.wav"
Content-Type: audio/wav

[binary WAV data]
------WebKitFormBoundary
Content-Disposition: form-data; name="target_letter"

Alif
------WebKitFormBoundary
Content-Disposition: form-data; name="threshold"

0.6
------WebKitFormBoundary--
```

### Response (Server sends back)
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 456

{
  "result": true,
  "target_letter": "Alif",
  "target_probability": 0.9876,
  "predicted_letter": "Alif",
  "predicted_probability": 0.9876,
  "threshold": 0.6,
  "message": "✓ Success: 'Alif' detected with 98.76% confidence (threshold: 60%)",
  "latency_ms": 12.5,
  "all_probabilities": {
    "Aain": 0.0001,
    "Alif": 0.9876,
    "Ba": 0.0045,
    "Dad": 0.0008,
    ...
  }
}
```

---

## Timeline of a Request

```
Time  Event
─────────────────────────────────────────────────────────────
0 ms  User clicks "Send" in Postman
      ↓
1 ms  HTTP POST request sent over network
      ↓
2 ms  FastAPI receives request
      ↓
3 ms  Read audio file from request body
      ↓
5 ms  Validate audio format (soundfile)
      ↓
7 ms  Resample audio to 16kHz
      ↓
8 ms  Pad/trim to 1 second (16,000 samples)
      ↓
10 ms Extract features (wav2vec2 processor)
      ↓
11 ms Run neural network inference (GPU)
      ↓
23 ms Compute softmax probabilities
      ↓
24 ms Get target letter probability
      ↓
25 ms Compare with threshold (0.6)
      ↓
26 ms Generate message string
      ↓
27 ms Build JSON response
      ↓
28 ms Send HTTP 200 OK response
      ↓
29 ms Postman displays result
      ↓
30 ms User sees: "result": true ✅
```

---

## Error Handling Flow

```
┌─────────────────────────┐
│  Request Received       │
└────────┬────────────────┘
         │
         ▼
    ┌────────────────┐
    │ Valid WAV?     │
    └───┬────────┬───┘
        │ NO     │ YES
        ▼        │
   [400 Error]   │
   "Could not    │
    read audio"  │
                 ▼
        ┌────────────────┐
        │ Letter exists? │
        └───┬────────┬───┘
            │ NO     │ YES
            ▼        │
       [400 Error]   │
       "Target       │
        letter not   │
        found"       │
                     ▼
            ┌────────────────┐
            │ Model loaded?  │
            └───┬────────┬───┘
                │ NO     │ YES
                ▼        │
           [500 Error]   │
           "Server       │
            error"       │
                         ▼
                ┌────────────────┐
                │ Run inference  │
                │ ✅ Success     │
                └────────────────┘
```

---

## Summary

The flow is straightforward:

1. **Postman** sends audio + target letter → Server
2. **Server** processes audio → AI model
3. **AI Model** predicts letter probabilities
4. **Verification** checks if target ≥ threshold
5. **Server** sends True/False ← Postman

**Key Point**: The `result` field in the JSON response is what you care about most - it tells you if the audio matches the target letter with enough confidence!
