# Push Model to Hugging Face Hub

This guide explains how to push your fine-tuned Arabic letters model to Hugging Face Hub.

## Prerequisites

1. **Install dependencies** (if not already installed):
   ```bash
   pip install huggingface_hub
   ```

2. **Authenticate with Hugging Face**:
   ```bash
   huggingface-cli login
   ```
   You'll need your Hugging Face token. Get it from: https://huggingface.co/settings/tokens

## Quick Start

### Option 1: Push model only (recommended)

```bash
python Code/push_to_huggingface.py
```

This will push your model from `Models/facebook__wav2vec2-base/` to `yansari/arabic-letters-wav2vec2-base`.

### Option 2: Push model with README (model card)

```bash
python Code/push_to_huggingface.py --create-readme
```

This will also create and upload a README.md with training metrics and usage examples.

### Option 3: Custom repository name

```bash
python Code/push_to_huggingface.py --repo-id your-username/your-model-name
```

## What Gets Pushed

The script uploads all files from `Models/facebook__wav2vec2-base/`:
- `config.json` - Model configuration
- `model.safetensors` - Model weights
- `preprocessor_config.json` - Preprocessor configuration
- `tokenizer_config.json` - Tokenizer configuration
- `vocab.json` - Vocabulary
- `special_tokens_map.json` - Special tokens mapping
- `README.md` - Model card (if `--create-readme` is used)

## Verify Upload

After pushing, visit your model page:
```
https://huggingface.co/yansari/arabic-letters-wav2vec2-base
```

## Troubleshooting

### Authentication Error
If you see authentication errors:
```bash
huggingface-cli login
```
Enter your token when prompted.

### Repository Already Exists
If the repository already exists, the script will update it with new files. This is normal and expected.

### Model Directory Not Found
Make sure you've trained the model first:
```bash
python Code/finetune_eval.py
```

## Advanced Usage

### Push to a different repository
```bash
python Code/push_to_huggingface.py --repo-id your-org/arabic-letters-model
```

### Specify custom paths
```bash
python Code/push_to_huggingface.py \
    --model-dir path/to/model \
    --results-dir path/to/results \
    --create-readme
```

## Next Steps

After pushing to Hugging Face:
1. Your model will be publicly available (unless you set it to private)
2. Others can use it with:
   ```python
   from transformers import AutoProcessor, AutoModelForAudioClassification
   processor = AutoProcessor.from_pretrained("yansari/arabic-letters-wav2vec2-base")
   model = AutoModelForAudioClassification.from_pretrained("yansari/arabic-letters-wav2vec2-base")
   ```
3. Update your README.md to reference the Hugging Face model

