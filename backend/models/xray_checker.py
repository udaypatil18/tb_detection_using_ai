"""
TorchXrayVision-based X-ray checker aligned with training pipeline.

Contract:
- check_xray(filepath: str) -> bool
  Returns True if image is an X-ray (prob <= 0.5), False otherwise.

Model setup:
- DenseNet with weights="all"
- Replace classifier with nn.Linear(in_features, 1)
- model.op_threshs = None
- Load state dict from xray_classifier.pth

Preprocessing:
- Resize(224, 224), Grayscale(1), ToTensor(), Normalize(mean=[0.485], std=[0.229])
"""

import os
from typing import Optional
import warnings

_model = None
_device = None
_error: Optional[str] = None

# Configurable gate behavior
_THRESH = float(os.environ.get("XRAY_THRESHOLD", "0.5"))
_DIR = os.environ.get("XRAY_DIRECTION", "less").strip().lower()  # 'less' or 'greater'
if _DIR not in ("less", "greater"):
    _DIR = "less"


def _get_transform():
    from torchvision import transforms
    # Match the exact transforms used during training
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485], std=[0.229]),  # Added normalization to match training
    ])


def _load_model():
    global _model, _device, _error
    if _model is not None:
        return _model
    try:
        # Suppress the heuristic normalization warning from TorchXRayVision
        # Use a broad filter without category to catch any warning class
        warnings.filterwarnings(
            "ignore",
            message=r".*does not appear to be normalized correctly.*",
        )
        import torch
        import torch.nn as nn
        import torchxrayvision as xrv

        # Match the exact model setup from training
        base = xrv.models.DenseNet(weights="all")
        in_feats = base.classifier.in_features
        base.classifier = nn.Linear(in_feats, 1)
        base.op_threshs = None  # Set op_threshs to None before loading state_dict

        weights_path = os.path.join(os.path.dirname(__file__), 'xray_classifier.pth')
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Weights not found at {weights_path}")

        # Load state dict exactly as in training
        state_dict = torch.load(weights_path, map_location='cpu')
        
        # Handle different state dict formats
        if isinstance(state_dict, dict) and 'state_dict' in state_dict:
            state_dict = state_dict['state_dict']
        
        # Clean possible prefixes if present
        if isinstance(state_dict, dict):
            cleaned_state_dict = {}
            for k, v in state_dict.items():
                # Remove common prefixes
                clean_key = k.replace('module.', '').replace('model.', '')
                cleaned_state_dict[clean_key] = v
            state_dict = cleaned_state_dict

        base.load_state_dict(state_dict, strict=False)

        _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        base.to(_device)
        base.eval()
        _model = base
        _error = None
        return _model
    except Exception as e:
        _error = str(e)
        _model = None
        return None


def check_xray(filepath: str) -> bool:
    """Return True if image is an X-ray (prob <= 0.5), else False.

    Raises no exceptions; returns False on any failure so caller can reject.
    """
    model = _load_model()
    if model is None:
        return False
    try:
        from PIL import Image
        import io
        import contextlib
        import torch
        transform = _get_transform()

        img = Image.open(filepath).convert('L')
        # Ensure warning suppression also covers the transform call path
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r".*does not appear to be normalized correctly.*")
            tensor = transform(img).unsqueeze(0).to(_device)  # [1,1,224,224]
        # Suppress any stdout/stderr warning prints from underlying libs during forward pass
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r".*does not appear to be normalized correctly.*")
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                with torch.no_grad():
                    logits = model(tensor)
                    prob = torch.sigmoid(logits).squeeze().item()
        # Debug log to help diagnose false negatives/positives
        try:
            print(f"[XRayGate] prob={prob:.4f} direction={_DIR} threshold={_THRESH}")
        except Exception:
            pass
        if _DIR == "less":
            is_xray = prob <= _THRESH
        else:
            is_xray = prob >= _THRESH
        return is_xray
    except Exception:
        return False


def is_ready() -> bool:
    """Return True if the TorchXRayVision model is loaded or can be loaded."""
    return _load_model() is not None


def last_error() -> Optional[str]:
    """Return the last error string encountered while loading the model, if any."""
    return _error
