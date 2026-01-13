# Postman Guide for Arabic Letters API

## What is Postman?

**Postman** is a popular tool for testing APIs (Application Programming Interfaces). It allows you to send HTTP requests to your server and see the responses without needing to write code or use a web browser.

Think of it as a **testing tool** that lets you:
- Send files, text, and data to your server
- See what your server sends back
- Save and organize your API tests
- Share API tests with team members

---

## Installation

### Option 1: Desktop App (Recommended)
1. Go to https://www.postman.com/downloads/
2. Download Postman for Windows
3. Install and open the application
4. Create a free account (optional but recommended)

### Option 2: Web Version
1. Go to https://www.postman.com/
2. Sign up for a free account
3. Use the web-based interface

---

## Your New API Endpoint

I've added a new endpoint called `/verify_letter` to your FastAPI server.

### Endpoint Details
- **URL**: `http://localhost:7860/verify_letter`
- **Method**: `POST`
- **Purpose**: Verify if an audio file matches a target Arabic letter

### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `audio` | File (WAV) | Yes | - | Audio file containing Arabic letter pronunciation |
| `target_letter` | Text | Yes | - | The expected letter (e.g., "Alif", "Ba", "Ta") |
| `threshold` | Number | No | 0.6 | Confidence threshold (0.6 = 60%) |
| `fixed_seconds` | Number | No | 1.0 | Audio processing window length |

### Response Format
```json
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
    "Alif": 0.9876,
    "Ba": 0.0045,
    "Ta": 0.0023,
    ...
  }
}
```

---

## Step-by-Step: Using Postman

### Step 1: Start Your Server

First, make sure your FastAPI server is running:

```bash
# In Git Bash or terminal
cd C:/Users/ansar/Desktop/Workstation/Kutuby/arabic-letters-realtime
bash scripts/run.sh
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:7860
```

### Step 2: Open Postman

1. Launch Postman application
2. Click on "New" or the "+" tab to create a new request

### Step 3: Configure the Request

1. **Set the Method**:
   - Change the dropdown from `GET` to `POST`

2. **Set the URL**:
   ```
   http://localhost:7860/verify_letter
   ```

3. **Configure the Body**:
   - Click on the "Body" tab (below the URL bar)
   - Select "form-data" (NOT "raw" or "binary")

4. **Add Parameters**:

   | Key | Type | Value |
   |-----|------|-------|
   | `audio` | File | (Select your WAV file) |
   | `target_letter` | Text | `Alif` |
   | `threshold` | Text | `0.6` (optional) |
   | `fixed_seconds` | Text | `1.0` (optional) |

   **How to add a file**:
   - In the "Key" column, type `audio`
   - Hover over the right side of the row, click the dropdown that says "Text"
   - Change it to "File"
   - Click "Select Files" and choose your WAV file

### Step 4: Send the Request

1. Click the blue "Send" button
2. Wait for the response (should take <1 second)

### Step 5: View the Response

Look at the "Response" section at the bottom:

**Success Example** (Correct prediction):
```json
{
  "result": true,
  "target_letter": "Alif",
  "target_probability": 0.9876,
  "predicted_letter": "Alif",
  "predicted_probability": 0.9876,
  "threshold": 0.6,
  "message": "✓ Success: 'Alif' detected with 98.76% confidence (threshold: 60%)"
}
```

**Failure Example** (Wrong prediction):
```json
{
  "result": false,
  "target_letter": "Alif",
  "target_probability": 0.1234,
  "predicted_letter": "Ba",
  "predicted_probability": 0.8765,
  "threshold": 0.6,
  "message": "✗ Failed: 'Alif' only has 12.34% confidence (threshold: 60%). Predicted: 'Ba' (87.65%)"
}
```

---

## Available Arabic Letters

Your model supports these 28 letters:

```
Aain, Alif, Ba, Dad, Dah, Dal, Fa, Ghain, Ha, Haa, Jeem, Kaf, Khaa, Laam,
Meem, Noon, Qaaf, Raa, Saa, Saud, Seen, Sheen, Ta, Taa, Thaa, Waw, Yaa, Zaa
```

**Important**: The letter names are case-sensitive! Use exact spelling:
- ✅ Correct: `Alif`
- ❌ Wrong: `alif`, `ALIF`, `Alef`

---

## Testing Scenarios

### Scenario 1: Perfect Match (>60% confidence)
```
Audio: alif_pronunciation.wav
Target: Alif
Expected Result: true
```

### Scenario 2: Close Match (<60% confidence)
```
Audio: unclear_audio.wav
Target: Alif
Expected Result: false (if confidence is below 60%)
```

### Scenario 3: Wrong Letter
```
Audio: ba_pronunciation.wav
Target: Alif
Expected Result: false (model predicts "Ba", not "Alif")
```

### Scenario 4: Custom Threshold (80%)
```
Audio: alif_pronunciation.wav
Target: Alif
Threshold: 0.8
Expected Result: true (only if confidence is >80%)
```

---

## Troubleshooting

### Error: "Could not read audio file"
- **Cause**: File is not in WAV format
- **Solution**: Convert your audio to WAV format using:
  - Audacity (free software)
  - Online converters (e.g., cloudconvert.com)
  - ffmpeg: `ffmpeg -i input.mp3 output.wav`

### Error: "Target letter 'X' not found"
- **Cause**: Letter name is misspelled or not supported
- **Solution**: Check the list of available letters above
- The response will include `available_letters` field with valid options

### Error: "Connection refused" or "Could not send request"
- **Cause**: Server is not running
- **Solution**: Start the server with `bash scripts/run.sh`

### Server is running but response is slow
- **Cause**: First request loads the model (can take 5-10 seconds)
- **Solution**: Wait for first request, subsequent requests will be fast (<1 second)

---

## Advanced: Using Python Instead of Postman

If you want to test the API with Python code instead of Postman:

```python
import requests

# Prepare the request
url = "http://localhost:7860/verify_letter"
files = {
    'audio': open('path/to/your/audio.wav', 'rb')
}
data = {
    'target_letter': 'Alif',
    'threshold': 0.6,
    'fixed_seconds': 1.0
}

# Send the request
response = requests.post(url, files=files, data=data)

# Parse the result
result = response.json()
print(f"Result: {result['result']}")
print(f"Message: {result['message']}")
```

---

## Advanced: Using cURL (Command Line)

You can also test with cURL in Git Bash:

```bash
curl -X POST http://localhost:7860/verify_letter \
  -F "audio=@path/to/your/audio.wav" \
  -F "target_letter=Alif" \
  -F "threshold=0.6" \
  -F "fixed_seconds=1.0"
```

---

## Next Steps

1. ✅ Start your server: `bash scripts/run.sh`
2. ✅ Open Postman
3. ✅ Configure a POST request to `http://localhost:7860/verify_letter`
4. ✅ Add your WAV file and target letter
5. ✅ Click "Send"
6. ✅ Check if `result` is `true` or `false`

---

## Questions?

Common questions:

**Q: Can I change the 60% threshold?**
A: Yes! Set the `threshold` parameter to any value between 0.0 and 1.0. For example, `0.8` = 80%.

**Q: Can I send MP3 or M4A files?**
A: No, only WAV files are supported. Convert your audio to WAV first.

**Q: What if my audio is longer than 2 seconds?**
A: The model will automatically trim or pad to the `fixed_seconds` parameter (default 1.0 second).

**Q: Can I test this from a different computer?**
A: Yes, but you need to either:
- Use your computer's IP address instead of `localhost`
- Use the `--share` flag to get a public ngrok URL

**Q: How do I see all the probabilities for all letters?**
A: Check the `all_probabilities` field in the response JSON.
