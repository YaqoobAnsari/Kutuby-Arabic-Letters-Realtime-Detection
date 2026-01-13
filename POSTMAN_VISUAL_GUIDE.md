# Visual Guide: Using Postman with Your API

## Quick Start Checklist

- [ ] Server is running (`bash scripts/run.sh`)
- [ ] Postman is installed and open
- [ ] You have a WAV file ready for testing
- [ ] You know which letter to test (e.g., "Alif")

---

## Visual Step-by-Step Guide

### Step 1: Create a New Request in Postman

When you open Postman, you'll see:

```
┌─────────────────────────────────────────────────────┐
│  [+] New Tab                                        │
│                                                     │
│  [GET ▼]  [Enter request URL]          [Send]      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Actions**:
1. Click the [+] or "New" button to create a new request
2. You'll see an empty request tab

---

### Step 2: Configure the Request Method and URL

```
┌─────────────────────────────────────────────────────┐
│  [POST ▼]  http://localhost:7860/verify_letter     │
│                                                     │
│  Params  Authorization  Headers  Body  ...         │
└─────────────────────────────────────────────────────┘
```

**Actions**:
1. Change `GET` dropdown to `POST`
2. Type in the URL: `http://localhost:7860/verify_letter`

---

### Step 3: Configure the Body

Click on the **Body** tab:

```
┌─────────────────────────────────────────────────────┐
│  Params  Authorization  Headers  Body  Pre-request  │
│                                                     │
│  ⚪ none                                            │
│  ⚪ form-data  ← SELECT THIS                       │
│  ⚪ x-www-form-urlencoded                          │
│  ⚪ raw                                             │
│  ⚪ binary                                          │
│  ⚪ GraphQL                                         │
└─────────────────────────────────────────────────────┘
```

**Action**: Select the **form-data** radio button

---

### Step 4: Add Parameters (form-data)

After selecting form-data, you'll see a table:

```
┌──────────────────────────────────────────────────────────┐
│  KEY              TYPE      VALUE                        │
├──────────────────────────────────────────────────────────┤
│  audio            File      [Select Files]               │
│  target_letter    Text      Alif                         │
│  threshold        Text      0.6                          │
│  fixed_seconds    Text      1.0                          │
└──────────────────────────────────────────────────────────┘
```

**How to add each row**:

#### Row 1: Audio File (Required)
1. Type `audio` in KEY column
2. Hover over the row, click dropdown next to KEY (says "Text")
3. Change to **File**
4. Click **Select Files** in VALUE column
5. Browse and select your `.wav` file

#### Row 2: Target Letter (Required)
1. Type `target_letter` in KEY column
2. Keep TYPE as **Text**
3. Type letter name in VALUE (e.g., `Alif`, `Ba`, `Ta`)
   - **Important**: Case-sensitive! Use exact spelling

#### Row 3: Threshold (Optional)
1. Type `threshold` in KEY column
2. Keep TYPE as **Text**
3. Type `0.6` in VALUE (or any number between 0.0 and 1.0)
   - `0.6` = 60% confidence required
   - `0.8` = 80% confidence required

#### Row 4: Fixed Seconds (Optional)
1. Type `fixed_seconds` in KEY column
2. Keep TYPE as **Text**
3. Type `1.0` in VALUE (processing window length in seconds)

---

### Step 5: Send the Request

```
┌─────────────────────────────────────────────────────┐
│  [POST ▼]  http://localhost:7860/verify_letter     │
│                                           [Send] ←  │
└─────────────────────────────────────────────────────┘
```

**Action**: Click the blue **Send** button on the right

**What happens**:
- Postman sends your WAV file and parameters to the server
- Server processes the audio with the AI model
- Server sends back a JSON response

---

### Step 6: View the Response

After clicking Send, scroll down to see the response section:

```
┌─────────────────────────────────────────────────────┐
│  Body   Cookies   Headers   Test Results   Status  │
│                                                     │
│  Pretty   Raw   Preview   Visualize                │
│                                                     │
│  {                                                  │
│    "result": true,                                  │
│    "target_letter": "Alif",                         │
│    "target_probability": 0.9876,                    │
│    "predicted_letter": "Alif",                      │
│    "predicted_probability": 0.9876,                 │
│    "threshold": 0.6,                                │
│    "message": "✓ Success: 'Alif' detected...",     │
│    "latency_ms": 12.5,                              │
│    "all_probabilities": { ... }                     │
│  }                                                  │
└─────────────────────────────────────────────────────┘
```

---

## Understanding the Response

### Key Fields to Check

#### 1. `result` (boolean)
- **`true`**: ✅ Audio matches target letter (confidence ≥ threshold)
- **`false`**: ❌ Audio does NOT match target letter

```json
"result": true   ← This is what you care about most!
```

#### 2. `message` (string)
Human-readable explanation:

**Success example**:
```json
"message": "✓ Success: 'Alif' detected with 98.76% confidence (threshold: 60%)"
```

**Failure example**:
```json
"message": "✗ Failed: 'Alif' only has 12.34% confidence (threshold: 60%). Predicted: 'Ba' (87.65%)"
```

#### 3. `target_probability` (number)
The probability (0.0 to 1.0) that the model assigned to your target letter:

```json
"target_probability": 0.9876  ← 98.76% confidence
```

#### 4. `predicted_letter` (string)
The letter the model thinks it heard:

```json
"predicted_letter": "Alif"  ← Model's top prediction
```

#### 5. `all_probabilities` (object)
Probabilities for ALL 28 letters:

```json
"all_probabilities": {
  "Alif": 0.9876,  ← Highest
  "Ba": 0.0045,
  "Ta": 0.0023,
  "Jeem": 0.0015,
  ...
}
```

---

## Response Status Codes

### 200 OK (Success)
```
Status: 200 OK
Time: 124 ms
Size: 1.2 KB
```
✅ Request was successful, check the `result` field

### 400 Bad Request (Error)
```
Status: 400 Bad Request
Time: 45 ms
Size: 245 B
```
❌ Something was wrong with your request:
- Invalid audio file format (not WAV)
- Unknown target letter name
- Missing required parameters

**Example error response**:
```json
{
  "error": "Target letter 'Alef' not found in model vocabulary.",
  "available_letters": "Aain, Alif, Ba, Dad, ...",
  "result": false
}
```

### 500 Internal Server Error
```
Status: 500 Internal Server Error
```
❌ Server crashed (rare). Check server logs.

---

## Example Test Cases

### Test Case 1: Perfect Match
```
Input:
  audio: alif_clear.wav (clear pronunciation)
  target_letter: Alif
  threshold: 0.6

Expected Output:
  result: true
  target_probability: > 0.85
  message: "✓ Success..."
```

### Test Case 2: Wrong Letter
```
Input:
  audio: ba_pronunciation.wav (says "Ba")
  target_letter: Alif
  threshold: 0.6

Expected Output:
  result: false
  predicted_letter: "Ba"
  message: "✗ Failed... Predicted: 'Ba' (...)"
```

### Test Case 3: Low Confidence
```
Input:
  audio: noisy_audio.wav (unclear)
  target_letter: Alif
  threshold: 0.6

Expected Output:
  result: false (if confidence < 60%)
  target_probability: < 0.6
  message: "✗ Failed... only has X% confidence"
```

### Test Case 4: High Threshold
```
Input:
  audio: alif_good.wav
  target_letter: Alif
  threshold: 0.95 (95% required!)

Expected Output:
  result: false (unless pronunciation is perfect)
  message: "✗ Failed... only has 87% confidence (threshold: 95%)"
```

---

## Troubleshooting Visuals

### Problem: Can't click Send button

**Symptom**:
```
[Send] button is grayed out
```

**Solution**: Make sure you've set the request method to POST

---

### Problem: "Audio file not selected"

**Symptom**:
```
KEY         TYPE      VALUE
audio       File      [No file selected]
```

**Solution**:
1. Click [Select Files]
2. Make sure you're selecting a `.wav` file
3. Make sure the file exists on your computer

---

### Problem: "Target letter not found"

**Symptom**:
```json
{
  "error": "Target letter 'alif' not found..."
}
```

**Solution**: Letter names are **case-sensitive**!
- ✅ Correct: `Alif`
- ❌ Wrong: `alif`, `ALIF`, `Alef`

---

### Problem: Connection refused

**Symptom**:
```
Error: connect ECONNREFUSED 127.0.0.1:7860
Could not send request
```

**Solution**: Server is not running!
```bash
# In Git Bash
cd C:/Users/ansar/Desktop/Workstation/Kutuby/arabic-letters-realtime
bash scripts/run.sh
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:7860
```

---

## Saving Your Request in Postman

To save your request for future use:

1. Click **Save** button (top right)
2. Give it a name: "Verify Arabic Letter"
3. Create a new collection: "Arabic Letters API"
4. Click **Save**

Now you can:
- Re-use the request later (just change the audio file)
- Duplicate it to create variations
- Share with team members

---

## Advanced: Collections

You can create a **Collection** with multiple saved requests:

```
📁 Arabic Letters API
  ├── Verify Alif (threshold 60%)
  ├── Verify Alif (threshold 80%)
  ├── Verify Ba (threshold 60%)
  └── Full Inference (original endpoint)
```

**Benefits**:
- Organize related requests
- Run all tests in sequence
- Export/import collections
- Share with teammates

---

## Quick Reference Card

```
┌─────────────────────────────────────────────┐
│ POSTMAN QUICK REFERENCE                     │
├─────────────────────────────────────────────┤
│ Method:    POST                             │
│ URL:       http://localhost:7860/verify_letter
│                                             │
│ Body Type: form-data                        │
│                                             │
│ Required Parameters:                        │
│   • audio          (File)                   │
│   • target_letter  (Text)                   │
│                                             │
│ Optional Parameters:                        │
│   • threshold      (Text, default: 0.6)     │
│   • fixed_seconds  (Text, default: 1.0)     │
│                                             │
│ Response:                                   │
│   • result: true/false                      │
│   • message: explanation                    │
│   • target_probability: 0.0-1.0             │
│                                             │
│ Available Letters:                          │
│   Aain, Alif, Ba, Dad, Dah, Dal, Fa,       │
│   Ghain, Ha, Haa, Jeem, Kaf, Khaa, Laam,   │
│   Meem, Noon, Qaaf, Raa, Saa, Saud, Seen,  │
│   Sheen, Ta, Taa, Thaa, Waw, Yaa, Zaa      │
└─────────────────────────────────────────────┘
```

---

## Next Steps

1. ✅ Read this guide
2. ✅ Start your server
3. ✅ Open Postman
4. ✅ Create a POST request to `/verify_letter`
5. ✅ Add audio file and target letter
6. ✅ Click Send
7. ✅ Check the `result` field in response

**You're ready to go!** 🚀
