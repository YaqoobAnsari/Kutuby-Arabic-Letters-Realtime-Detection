#!/usr/bin/env python3
"""
Hugging Face Space entry point for Arabic Alphabet Pronunciation Trainer
Redirects to the main FastAPI server
"""

import sys
from pathlib import Path
import uvicorn


# Add Code directory to path
code_dir = Path(__file__).parent / "Code"
sys.path.insert(0, str(code_dir))

# Import and run the main FastAPI app
from serve_realtime_fastapi import app

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)