#!/usr/bin/env python3
"""
Quick test script for the /verify_letter endpoint.

Usage:
1. Start the server: bash scripts/run.sh
2. Run this script: python test_verify_endpoint.py path/to/audio.wav Alif
"""

import sys
import requests
from pathlib import Path

def test_verify_letter(audio_path: str, target_letter: str, threshold: float = 0.6):
    """
    Test the /verify_letter endpoint with a WAV file.

    Args:
        audio_path: Path to WAV file
        target_letter: Expected Arabic letter (e.g., "Alif", "Ba")
        threshold: Confidence threshold (default 0.6 = 60%)
    """
    # API endpoint
    url = "http://localhost:7860/verify_letter"

    # Check if file exists
    audio_file = Path(audio_path)
    if not audio_file.exists():
        print(f"❌ Error: File not found: {audio_path}")
        return

    # Prepare the request
    print(f"\n{'='*60}")
    print(f"Testing /verify_letter endpoint")
    print(f"{'='*60}")
    print(f"Audio file: {audio_path}")
    print(f"Target letter: {target_letter}")
    print(f"Threshold: {threshold*100:.0f}%")
    print(f"{'='*60}\n")

    try:
        # Open file and send request
        with open(audio_file, 'rb') as f:
            files = {'audio': (audio_file.name, f, 'audio/wav')}
            data = {
                'target_letter': target_letter,
                'threshold': str(threshold),
                'fixed_seconds': '1.0'
            }

            print("Sending request...")
            response = requests.post(url, files=files, data=data)

        # Check if request was successful
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return

        # Parse JSON response
        result = response.json()

        # Display results
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)

        if result.get('result'):
            print("✅ VERIFICATION PASSED")
        else:
            print("❌ VERIFICATION FAILED")

        print(f"\nMessage: {result.get('message', 'N/A')}")
        print(f"\nDetails:")
        print(f"  Target Letter:        {result.get('target_letter', 'N/A')}")
        print(f"  Target Probability:   {result.get('target_probability', 0)*100:.2f}%")
        print(f"  Predicted Letter:     {result.get('predicted_letter', 'N/A')}")
        print(f"  Predicted Probability: {result.get('predicted_probability', 0)*100:.2f}%")
        print(f"  Threshold:            {result.get('threshold', 0)*100:.0f}%")
        print(f"  Latency:              {result.get('latency_ms', 0):.2f} ms")

        # Show top 5 predictions
        if 'all_probabilities' in result:
            print(f"\nTop 5 Predictions:")
            probs = result['all_probabilities']
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            for i, (letter, prob) in enumerate(sorted_probs[:5], 1):
                marker = "←" if letter == target_letter else ""
                print(f"  {i}. {letter:10s} {prob*100:6.2f}% {marker}")

        print("="*60 + "\n")

        return result

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("   Make sure the server is running:")
        print("   bash scripts/run.sh")
        return
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return


def show_usage():
    """Display usage instructions."""
    print("\nUsage:")
    print("  python test_verify_endpoint.py <audio_file.wav> <target_letter> [threshold]")
    print("\nExamples:")
    print("  python test_verify_endpoint.py audio.wav Alif")
    print("  python test_verify_endpoint.py audio.wav Ba 0.8")
    print("\nAvailable letters:")
    letters = [
        "Aain", "Alif", "Ba", "Dad", "Dah", "Dal", "Fa", "Ghain", "Ha", "Haa",
        "Jeem", "Kaf", "Khaa", "Laam", "Meem", "Noon", "Qaaf", "Raa", "Saa",
        "Saud", "Seen", "Sheen", "Ta", "Taa", "Thaa", "Waw", "Yaa", "Zaa"
    ]
    print("  " + ", ".join(letters))
    print()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Error: Missing required arguments")
        show_usage()
        sys.exit(1)

    audio_path = sys.argv[1]
    target_letter = sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6

    test_verify_letter(audio_path, target_letter, threshold)
