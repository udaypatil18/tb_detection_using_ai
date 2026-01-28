"""
Helper script to download LLaMA base weights locally using Hugging Face Hub.

Usage (PowerShell on Windows):

  # Activate your backend venv first
  # $env:HUGGING_FACE_HUB_TOKEN = "<your_hf_token>"  # if model is gated
  # $env:LLAMA_BASE_MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
  # $env:LLAMA_BASE_DIR = "backend/models/llama-3.2-1b-instruct"
  # python backend/scripts/download_llama_base.py

You can also pass arguments:
  python backend/scripts/download_llama_base.py --model-id meta-llama/Llama-3.2-1B-Instruct --out-dir backend/models/llama-3.2-1b-instruct

Requirements:
  pip install huggingface_hub

Notes:
- Ensure you have access to the gated model on Hugging Face.
- For large models, this may take a while and consume multiple GBs of storage.
"""
from __future__ import annotations

import os
import argparse
from huggingface_hub import snapshot_download, login


def main():
    parser = argparse.ArgumentParser(description="Download LLaMA base model weights locally")
    parser.add_argument(
        "--model-id",
        default=os.environ.get("LLAMA_BASE_MODEL_ID", "meta-llama/Llama-3.2-1B-Instruct"),
        help="Hugging Face model ID (default: env LLAMA_BASE_MODEL_ID or meta-llama/Llama-3.2-1B-Instruct)",
    )
    parser.add_argument(
        "--out-dir",
        default=os.environ.get("LLAMA_BASE_DIR", os.path.join("backend", "models", "llama-3.2-1b-instruct")),
        help="Local output directory (default: env LLAMA_BASE_DIR or backend/models/llama-3.2-1b-instruct)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("HUGGING_FACE_HUB_TOKEN"),
        help="Hugging Face token (default: env HUGGING_FACE_HUB_TOKEN)",
    )

    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Perform login only if a token is provided explicitly
    if args.token:
        try:
            login(token=args.token)
        except Exception as e:
            print(f"Warning: HF login failed: {e}. Continuing without explicit login...")

    print(f"Downloading model: {args.model_id}")
    print(f"Destination: {args.out_dir}")

    # snapshot_download saves a local snapshot of the repo files
    # local_dir_use_symlinks=False ensures physical copies (helpful on Windows)
    snapshot_download(
        repo_id=args.model_id,
        local_dir=args.out_dir,
        local_dir_use_symlinks=False,
        token=args.token,
        # You can set allow_patterns to limit files if needed
    )

    print("Download complete.")


if __name__ == "__main__":
    main()
