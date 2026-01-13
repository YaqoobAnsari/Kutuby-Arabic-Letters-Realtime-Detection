# API Examples: Different Ways to Test the Endpoint

This document shows multiple ways to test the `/verify_letter` endpoint without Postman.

---

## 1. Using Python (requests library)

### Install requests (if needed)
```bash
pip install requests
```

### Simple Example
```python
import requests

# Prepare the request
url = "http://localhost:7860/verify_letter"
files = {'audio': open('path/to/audio.wav', 'rb')}
data = {
    'target_letter': 'Alif',
    'threshold': 0.6
}

# Send the request
response = requests.post(url, files=files, data=data)
result = response.json()

# Check result
if result['result']:
    print(f"✅ SUCCESS: {result['message']}")
else:
    print(f"❌ FAILED: {result['message']}")
```

### Complete Example with Error Handling
```python
import requests
from pathlib import Path

def verify_arabic_letter(audio_path: str, target_letter: str, threshold: float = 0.6):
    """
    Verify if an audio file matches a target Arabic letter.

    Args:
        audio_path: Path to WAV file
        target_letter: Expected letter (e.g., "Alif")
        threshold: Confidence threshold (0.0-1.0)

    Returns:
        dict: API response with result, probabilities, etc.
    """
    url = "http://localhost:7860/verify_letter"

    # Check if file exists
    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Prepare the request
    with open(audio_path, 'rb') as audio_file:
        files = {'audio': (Path(audio_path).name, audio_file, 'audio/wav')}
        data = {
            'target_letter': target_letter,
            'threshold': str(threshold),
            'fixed_seconds': '1.0'
        }

        # Send request
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Could not connect to server. Is it running?")
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out. Server might be overloaded.")

    # Parse response
    result = response.json()

    # Display results
    print(f"\n{'='*60}")
    print(f"VERIFICATION RESULT")
    print(f"{'='*60}")
    print(f"Result: {'✅ PASS' if result['result'] else '❌ FAIL'}")
    print(f"Message: {result['message']}")
    print(f"\nDetails:")
    print(f"  Target Letter:         {result['target_letter']}")
    print(f"  Target Probability:    {result['target_probability']*100:.2f}%")
    print(f"  Predicted Letter:      {result['predicted_letter']}")
    print(f"  Predicted Probability: {result['predicted_probability']*100:.2f}%")
    print(f"  Threshold:             {result['threshold']*100:.0f}%")
    print(f"  Inference Time:        {result['latency_ms']:.2f} ms")
    print(f"{'='*60}\n")

    return result

# Example usage
if __name__ == "__main__":
    result = verify_arabic_letter(
        audio_path="test_audio.wav",
        target_letter="Alif",
        threshold=0.6
    )

    # Access individual fields
    if result['result']:
        print(f"Confidence: {result['target_probability']*100:.2f}%")
    else:
        print(f"Expected '{result['target_letter']}' but got '{result['predicted_letter']}'")
```

### Batch Processing Example
```python
import requests
from pathlib import Path

def batch_verify(audio_files: list, target_letter: str, threshold: float = 0.6):
    """
    Verify multiple audio files against the same target letter.

    Args:
        audio_files: List of audio file paths
        target_letter: Expected letter
        threshold: Confidence threshold

    Returns:
        dict: Summary statistics
    """
    url = "http://localhost:7860/verify_letter"
    results = []

    for audio_path in audio_files:
        print(f"Testing {Path(audio_path).name}...")

        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            data = {'target_letter': target_letter, 'threshold': str(threshold)}
            response = requests.post(url, files=files, data=data)
            result = response.json()
            results.append({
                'file': Path(audio_path).name,
                'passed': result['result'],
                'probability': result['target_probability']
            })

    # Summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"\n{'='*60}")
    print(f"BATCH RESULTS: {passed}/{total} passed ({passed/total*100:.1f}%)")
    print(f"{'='*60}")
    for r in results:
        status = "✅" if r['passed'] else "❌"
        print(f"{status} {r['file']:30s} {r['probability']*100:6.2f}%")

    return results

# Example usage
audio_files = [
    "recordings/alif_1.wav",
    "recordings/alif_2.wav",
    "recordings/alif_3.wav",
]
batch_verify(audio_files, target_letter="Alif", threshold=0.7)
```

---

## 2. Using cURL (Command Line)

### Basic Example
```bash
curl -X POST http://localhost:7860/verify_letter \
  -F "audio=@path/to/audio.wav" \
  -F "target_letter=Alif" \
  -F "threshold=0.6"
```

### With Pretty JSON Output (using jq)
```bash
curl -X POST http://localhost:7860/verify_letter \
  -F "audio=@audio.wav" \
  -F "target_letter=Alif" \
  -F "threshold=0.6" \
  | jq '.'
```

### Extract Only the Result
```bash
curl -s -X POST http://localhost:7860/verify_letter \
  -F "audio=@audio.wav" \
  -F "target_letter=Alif" \
  | jq -r '.result'
```
Output: `true` or `false`

### Extract the Message
```bash
curl -s -X POST http://localhost:7860/verify_letter \
  -F "audio=@audio.wav" \
  -F "target_letter=Alif" \
  | jq -r '.message'
```
Output: `✓ Success: 'Alif' detected with 98.76% confidence (threshold: 60%)`

### Bash Script for Testing
```bash
#!/bin/bash
# test_letter.sh - Test audio file against target letter

AUDIO_FILE="$1"
TARGET_LETTER="$2"
THRESHOLD="${3:-0.6}"

if [ -z "$AUDIO_FILE" ] || [ -z "$TARGET_LETTER" ]; then
    echo "Usage: $0 <audio.wav> <target_letter> [threshold]"
    exit 1
fi

echo "Testing $AUDIO_FILE for letter: $TARGET_LETTER"
echo "Threshold: $THRESHOLD"
echo "─────────────────────────────────────"

RESPONSE=$(curl -s -X POST http://localhost:7860/verify_letter \
    -F "audio=@$AUDIO_FILE" \
    -F "target_letter=$TARGET_LETTER" \
    -F "threshold=$THRESHOLD")

RESULT=$(echo "$RESPONSE" | jq -r '.result')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')

if [ "$RESULT" = "true" ]; then
    echo "✅ PASSED"
else
    echo "❌ FAILED"
fi

echo "$MESSAGE"
```

Usage:
```bash
bash test_letter.sh recordings/alif.wav Alif 0.6
```

---

## 3. Using JavaScript (Node.js)

### Install dependencies
```bash
npm install form-data node-fetch
```

### Example Code
```javascript
const fs = require('fs');
const FormData = require('form-data');
const fetch = require('node-fetch');

async function verifyLetter(audioPath, targetLetter, threshold = 0.6) {
    const url = 'http://localhost:7860/verify_letter';

    // Create form data
    const form = new FormData();
    form.append('audio', fs.createReadStream(audioPath));
    form.append('target_letter', targetLetter);
    form.append('threshold', threshold.toString());
    form.append('fixed_seconds', '1.0');

    // Send request
    const response = await fetch(url, {
        method: 'POST',
        body: form
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    // Display results
    console.log('\n' + '='.repeat(60));
    console.log('VERIFICATION RESULT');
    console.log('='.repeat(60));
    console.log(`Result: ${result.result ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Message: ${result.message}`);
    console.log(`\nTarget Probability: ${(result.target_probability * 100).toFixed(2)}%`);
    console.log(`Predicted Letter: ${result.predicted_letter}`);
    console.log('='.repeat(60) + '\n');

    return result;
}

// Example usage
verifyLetter('test_audio.wav', 'Alif', 0.6)
    .then(result => {
        if (result.result) {
            console.log('Success!');
        } else {
            console.log('Failed verification');
        }
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
```

---

## 4. Using JavaScript (Browser)

### HTML Form Example
```html
<!DOCTYPE html>
<html>
<head>
    <title>Arabic Letter Verification</title>
</head>
<body>
    <h1>Verify Arabic Letter Pronunciation</h1>

    <form id="verifyForm">
        <div>
            <label>Audio File (WAV):</label>
            <input type="file" id="audioFile" accept=".wav" required>
        </div>

        <div>
            <label>Target Letter:</label>
            <select id="targetLetter" required>
                <option value="Alif">Alif</option>
                <option value="Ba">Ba</option>
                <option value="Ta">Ta</option>
                <!-- Add all 28 letters -->
            </select>
        </div>

        <div>
            <label>Threshold (%):</label>
            <input type="number" id="threshold" value="60" min="0" max="100">
        </div>

        <button type="submit">Verify</button>
    </form>

    <div id="result" style="margin-top: 20px;"></div>

    <script>
        document.getElementById('verifyForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const audioFile = document.getElementById('audioFile').files[0];
            const targetLetter = document.getElementById('targetLetter').value;
            const threshold = document.getElementById('threshold').value / 100;

            // Create form data
            const formData = new FormData();
            formData.append('audio', audioFile);
            formData.append('target_letter', targetLetter);
            formData.append('threshold', threshold.toString());

            // Send request
            try {
                const response = await fetch('http://localhost:7860/verify_letter', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                // Display result
                const resultDiv = document.getElementById('result');
                if (result.result) {
                    resultDiv.innerHTML = `
                        <div style="color: green; font-weight: bold;">
                            ✅ PASSED
                        </div>
                        <p>${result.message}</p>
                        <p>Confidence: ${(result.target_probability * 100).toFixed(2)}%</p>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div style="color: red; font-weight: bold;">
                            ❌ FAILED
                        </div>
                        <p>${result.message}</p>
                        <p>Target Confidence: ${(result.target_probability * 100).toFixed(2)}%</p>
                        <p>Predicted: ${result.predicted_letter} (${(result.predicted_probability * 100).toFixed(2)}%)</p>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <div style="color: red;">Error: ${error.message}</div>
                `;
            }
        });
    </script>
</body>
</html>
```

---

## 5. Using PowerShell (Windows)

```powershell
# test_letter.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$AudioFile,

    [Parameter(Mandatory=$true)]
    [string]$TargetLetter,

    [Parameter(Mandatory=$false)]
    [double]$Threshold = 0.6
)

$url = "http://localhost:7860/verify_letter"

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$fileBytes = [System.IO.File]::ReadAllBytes($AudioFile)
$fileName = [System.IO.Path]::GetFileName($AudioFile)

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"audio`"; filename=`"$fileName`"",
    "Content-Type: audio/wav",
    "",
    [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes),
    "--$boundary",
    "Content-Disposition: form-data; name=`"target_letter`"",
    "",
    $TargetLetter,
    "--$boundary",
    "Content-Disposition: form-data; name=`"threshold`"",
    "",
    $Threshold.ToString(),
    "--$boundary--"
)

$body = $bodyLines -join "`r`n"

# Send request
$response = Invoke-RestMethod -Uri $url -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $body

# Display result
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "VERIFICATION RESULT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($response.result) {
    Write-Host "✅ PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ FAILED" -ForegroundColor Red
}

Write-Host "`nMessage: $($response.message)"
Write-Host "Target Probability: $([math]::Round($response.target_probability * 100, 2))%"
Write-Host "Predicted Letter: $($response.predicted_letter)"
Write-Host "========================================`n" -ForegroundColor Cyan
```

Usage:
```powershell
.\test_letter.ps1 -AudioFile "test.wav" -TargetLetter "Alif" -Threshold 0.6
```

---

## 6. Test Script Provided

I've already created a Python test script for you: `test_verify_endpoint.py`

### Usage:
```bash
# Basic test
python test_verify_endpoint.py path/to/audio.wav Alif

# With custom threshold
python test_verify_endpoint.py path/to/audio.wav Alif 0.8

# Test with a file from your dataset
python test_verify_endpoint.py Dataset/Alif/sample1.wav Alif
```

### Output Example:
```
============================================================
Testing /verify_letter endpoint
============================================================
Audio file: Dataset/Alif/sample1.wav
Target letter: Alif
Threshold: 60%
============================================================

Sending request...

============================================================
RESULTS
============================================================
✅ VERIFICATION PASSED

Message: ✓ Success: 'Alif' detected with 98.76% confidence (threshold: 60%)

Details:
  Target Letter:        Alif
  Target Probability:   98.76%
  Predicted Letter:     Alif
  Predicted Probability: 98.76%
  Threshold:            60%
  Latency:              12.50 ms

Top 5 Predictions:
  1. Alif       98.76% ←
  2. Ba          0.45%
  3. Ta          0.23%
  4. Jeem        0.15%
  5. Meem        0.12%
============================================================
```

---

## Summary: Which Method to Use?

| Method | Best For | Difficulty |
|--------|----------|-----------|
| **Postman** | Manual testing, learning APIs | ⭐ Easy |
| **Python (requests)** | Automation, batch processing | ⭐⭐ Medium |
| **cURL** | Quick command-line tests | ⭐⭐ Medium |
| **JavaScript (Node.js)** | Backend integration | ⭐⭐⭐ Hard |
| **JavaScript (Browser)** | Web app integration | ⭐⭐⭐ Hard |
| **PowerShell** | Windows automation | ⭐⭐ Medium |
| **test_verify_endpoint.py** | Quick testing | ⭐ Easy |

**Recommendation for beginners**: Start with **Postman** or the provided **test_verify_endpoint.py** script.

---

## All Available Letters

Remember, letter names are **case-sensitive**:

```
Aain, Alif, Ba, Dad, Dah, Dal, Fa, Ghain, Ha, Haa, Jeem, Kaf, Khaa, Laam,
Meem, Noon, Qaaf, Raa, Saa, Saud, Seen, Sheen, Ta, Taa, Thaa, Waw, Yaa, Zaa
```

Use exact spelling in your requests!
