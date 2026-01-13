#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
push_to_huggingface.py — Push fine-tuned model to Hugging Face Hub.

Usage:
    python Code/push_to_huggingface.py
    
    # Or specify custom repository name:
    python Code/push_to_huggingface.py --repo-id yansari/arabic-letters-wav2vec2-base
    
    # Push with README:
    python Code/push_to_huggingface.py --create-readme

Requirements:
    pip install huggingface_hub
    huggingface-cli login  # Authenticate first
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

try:
    from huggingface_hub import HfApi, create_repo, upload_folder
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
    exit(1)


def resolve_repo_paths() -> dict[str, Path]:
    """Resolve paths relative to this script."""
    code_dir = Path(__file__).resolve().parent
    root = code_dir.parent
    return {
        "root": root,
        "code": code_dir,
        "models": root / "Models",
        "results": root / "Results",
    }


def create_model_readme(model_dir: Path, results_dir: Path, repo_id: str) -> str:
    """Create a README.md for the model card."""
    summary_path = results_dir / "summary.json"
    
    # Read summary if available
    summary = {}
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
    
    # Extract metrics
    test_metrics = summary.get("metrics", {}).get("test", {})
    val_metrics = summary.get("metrics", {}).get("val", {})
    
    readme = f"""---
license: mit
tags:
- audio
- audio-classification
- wav2vec2
- arabic
- speech-recognition
- pytorch
datasets:
- custom
metrics:
- accuracy
- f1
- balanced_accuracy
- mcc
model-index:
- name: {repo_id.split('/')[-1]}
  results:
  - task:
      type: audio-classification
      name: Arabic Letter Classification
    dataset:
      name: Custom Arabic Letters Dataset
      type: custom
    metrics:
"""
    
    if test_metrics:
        readme += f"""      - type: accuracy
        value: {test_metrics.get('eval_accuracy', 0):.4f}
      - type: macro_f1
        value: {test_metrics.get('eval_macro_f1', 0):.4f}
      - type: weighted_f1
        value: {test_metrics.get('eval_weighted_f1', 0):.4f}
      - type: balanced_accuracy
        value: {test_metrics.get('eval_balanced_accuracy', 0):.4f}
      - type: mcc
        value: {test_metrics.get('eval_mcc', 0):.4f}
"""
    
    readme += f"""
---

# {repo_id.split('/')[-1]}

Fine-tuned **wav2vec2-base** model for Arabic alphabet letter classification (28 classes).

## Model Details

- **Base Model**: facebook/wav2vec2-base
- **Task**: Audio Classification
- **Number of Classes**: {summary.get('num_labels', 28)}
- **Model Size**: {summary.get('model_size_mb', 0):.2f} MB

## Training Details

"""
    
    training = summary.get("training", {})
    if training:
        readme += f"""- **Epochs**: {training.get('num_epochs', 'N/A')}
- **Batch Size**: {training.get('batch_size', 'N/A')}
- **Learning Rate**: {training.get('lr', 'N/A')}
- **Weight Decay**: {training.get('weight_decay', 'N/A')}
- **Warmup Ratio**: {training.get('warmup_ratio', 'N/A')}
- **FP16**: {training.get('fp16', False)}
- **Gradient Accumulation Steps**: {training.get('gradient_accumulation_steps', 'N/A')}

"""
    
    readme += """## Performance

### Test Set Metrics

"""
    
    if test_metrics:
        readme += f"""- **Accuracy**: {test_metrics.get('eval_accuracy', 0)*100:.2f}%
- **Macro F1**: {test_metrics.get('eval_macro_f1', 0):.4f}
- **Weighted F1**: {test_metrics.get('eval_weighted_f1', 0):.4f}
- **Balanced Accuracy**: {test_metrics.get('eval_balanced_accuracy', 0)*100:.2f}%
- **Matthews Correlation Coefficient**: {test_metrics.get('eval_mcc', 0):.4f}

"""
    
    readme += """### Validation Set Metrics

"""
    
    if val_metrics:
        readme += f"""- **Accuracy**: {val_metrics.get('eval_accuracy', 0)*100:.2f}%
- **Macro F1**: {val_metrics.get('eval_macro_f1', 0):.4f}
- **Weighted F1**: {val_metrics.get('eval_weighted_f1', 0):.4f}
- **Balanced Accuracy**: {val_metrics.get('eval_balanced_accuracy', 0)*100:.2f}%
- **Matthews Correlation Coefficient**: {val_metrics.get('eval_mcc', 0):.4f}

"""
    
    readme += """## Classes

The model classifies 28 Arabic letters:

"""
    
    labels = summary.get("labels", [])
    if labels:
        readme += ", ".join(labels)
        readme += "\n\n"
    
    readme += f"""## Usage

```python
from transformers import AutoProcessor, AutoModelForAudioClassification
import torchaudio

processor = AutoProcessor.from_pretrained("{repo_id}")
model = AutoModelForAudioClassification.from_pretrained("{repo_id}")

# Load audio
audio, sr = torchaudio.load("path/to/audio.wav")
inputs = processor(audio, sampling_rate=sr, return_tensors="pt")

# Predict
with torch.no_grad():
    logits = model(**inputs).logits
    predicted_class_id = logits.argmax(-1).item()
    predicted_class = model.config.id2label[predicted_class_id]
    print(f"Predicted: {{predicted_class}}")
```

## Citation

If you use this model, please cite:

```bibtex
@misc{{{repo_id.replace('/', '_').replace('-', '_')},
  title={{Arabic Letters Classification with wav2vec2}},
  author={{Yansari}},
  year={{2025}},
  publisher={{Hugging Face}},
  howpublished={{\\url{{https://huggingface.co/{repo_id}}}}}
}}
```

## License

MIT
"""
    
    return readme


def push_model_to_hub(
    model_dir: Path,
    repo_id: str,
    create_readme: bool = False,
    results_dir: Path | None = None
) -> None:
    """Push model files to Hugging Face Hub."""
    api = HfApi()
    
    print(f"[INFO] Pushing model to: {repo_id}")
    print(f"[INFO] Model directory: {model_dir}")
    
    # Check if model directory exists
    if not model_dir.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")
    
    # Check if config.json exists
    config_path = model_dir / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"config.json not found in {model_dir}")
    
    # Create repository if it doesn't exist
    try:
        create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
        print(f"[INFO] Repository '{repo_id}' is ready")
    except HfHubHTTPError as e:
        if "already exists" in str(e).lower():
            print(f"[INFO] Repository '{repo_id}' already exists")
        else:
            raise
    
    # Upload model files
    print(f"[INFO] Uploading model files...")
    upload_folder(
        folder_path=str(model_dir),
        repo_id=repo_id,
        repo_type="model",
        ignore_patterns=[".git*", "__pycache__", "*.pyc"]
    )
    print(f"[INFO] ✓ Model files uploaded successfully")
    
    # Create and upload README if requested
    if create_readme:
        if results_dir and results_dir.exists():
            readme_content = create_model_readme(model_dir, results_dir, repo_id)
            readme_path = model_dir / "README.md"
            readme_path.write_text(readme_content, encoding="utf-8")
            print(f"[INFO] Created README.md")
            
            # Upload README
            api.upload_file(
                path_or_fileobj=str(readme_path),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="model"
            )
            print(f"[INFO] ✓ README.md uploaded successfully")
        else:
            print(f"[WARN] Results directory not found, skipping README creation")


def main():
    parser = argparse.ArgumentParser(
        description="Push fine-tuned model to Hugging Face Hub"
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="yansari/arabic-letters-wav2vec2-base",
        help="Hugging Face repository ID (default: yansari/arabic-letters-wav2vec2-base)"
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default=None,
        help="Path to model directory (default: Models/facebook__wav2vec2-base)"
    )
    parser.add_argument(
        "--create-readme",
        action="store_true",
        help="Create and upload README.md model card"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default=None,
        help="Path to results directory for README (default: Results/facebook__wav2vec2-base)"
    )
    
    args = parser.parse_args()
    
    paths = resolve_repo_paths()
    
    # Determine model directory
    if args.model_dir:
        model_dir = Path(args.model_dir)
    else:
        model_dir = paths["models"] / "facebook__wav2vec2-base"
    
    # Determine results directory
    if args.results_dir:
        results_dir = Path(args.results_dir)
    else:
        results_dir = paths["results"] / "facebook__wav2vec2-base"
    
    # Verify authentication
    try:
        api = HfApi()
        user = api.whoami()
        print(f"[INFO] Authenticated as: {user.get('name', 'Unknown')}")
    except Exception as e:
        print(f"[ERROR] Authentication failed. Please run: huggingface-cli login")
        print(f"Error: {e}")
        exit(1)
    
    # Push model
    try:
        push_model_to_hub(
            model_dir=model_dir,
            repo_id=args.repo_id,
            create_readme=args.create_readme,
            results_dir=results_dir if args.create_readme else None
        )
        print(f"\n[SUCCESS] Model pushed to: https://huggingface.co/{args.repo_id}")
    except Exception as e:
        print(f"\n[ERROR] Failed to push model: {e}")
        exit(1)


if __name__ == "__main__":
    main()

