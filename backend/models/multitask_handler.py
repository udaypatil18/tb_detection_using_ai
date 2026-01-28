import os
from datetime import datetime
import cv2
import json
import base64
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union

# Defaults matching training
IMG_SIZE = 384
_input_size: int = IMG_SIZE

_model = None
_loaded = False
_last_error: Optional[str] = None

_mc_labels: List[str] = ["benign", "malignant", "other_tumor", "normal"]
_pathology_labels: List[str] = []

# Tumor subtypes (9 specific categories)
TUMOR_SUBTYPES = [
    "osteochondroma",
    "multiple osteochondromas", 
    "simple bone cyst",
    "giant cell tumor",
    "osteofibroma",
    "synovial osteochondroma",
    "other bt",
    "osteosarcoma",
    "other mt"
]


def is_ready() -> bool:
    return _loaded and _model is not None


def last_error() -> Optional[str]:
    return _last_error


def _models_dir() -> str:
    return os.path.dirname(__file__)


def _find_model_path() -> Optional[str]:
    # Check for SavedModel directory first (preferred)
    savedmodel_dir = os.path.join(_models_dir(), 'savedmodel')
    if os.path.exists(savedmodel_dir) and os.path.isdir(savedmodel_dir):
        return savedmodel_dir
    
    # Fallback to single file formats
    candidates = [
        os.path.join(_models_dir(), 'multitask_bonetumor_savedmodel.keras'),
        os.path.join(_models_dir(), 'multitask_bonetumor_model.keras'),
        os.path.join(_models_dir(), 'multitask_model_keras.keras'),
        os.path.join(_models_dir(), 'multitask_model_keras.h5'),
        os.path.join(_models_dir(), 'best_multitask_tf.keras'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _load_labels() -> None:
    global _mc_labels, _pathology_labels
    try:
        mc_path = os.path.join(_models_dir(), 'multiclass_labels.json')
        if os.path.exists(mc_path):
            with open(mc_path, 'r', encoding='utf-8') as f:
                arr = json.load(f)
            if isinstance(arr, list) and all(isinstance(x, str) for x in arr):
                _mc_labels = arr
    except Exception:
        pass
    try:
        path_path = os.path.join(_models_dir(), 'pathology_columns.json')
        if os.path.exists(path_path):
            with open(path_path, 'r', encoding='utf-8') as f:
                arr = json.load(f)
            if isinstance(arr, list) and all(isinstance(x, str) for x in arr):
                _pathology_labels = arr
    except Exception:
        pass


def load_model_if_needed() -> None:
    global _model, _loaded, _last_error
    if _model is not None and _loaded:
        return
    try:
        import tensorflow as tf
        model_path = _find_model_path()
        if not model_path:
            _last_error = 'No multitask model file found in models directory.'
            _loaded = False
            _model = None
            return
        _load_labels()
        
        # Check if it's a SavedModel directory
        if os.path.isdir(model_path):
            # Load SavedModel format
            _model = tf.saved_model.load(model_path)
            print(f"✅ SavedModel loaded from {model_path}")
            
            # Get the inference function
            if hasattr(_model, 'signatures') and 'serving_default' in _model.signatures:
                _model = _model.signatures['serving_default']
            else:
                _last_error = 'SavedModel does not have serving_default signature'
                _loaded = False
                _model = None
                return
        else:
            # Load single file format (Keras)
            try:
                _model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
            except TypeError:
                _model = tf.keras.models.load_model(model_path, compile=False)
        
        _loaded = True
        _last_error = None
    except Exception as e:
        _last_error = str(e)
        _loaded = False
        _model = None


def _to_data_url(img_bgr: np.ndarray) -> str:
    ok, buf = cv2.imencode('.png', img_bgr)
    if not ok:
        return ''
    b64 = base64.b64encode(buf.tobytes()).decode('ascii')
    return f"data:image/png;base64,{b64}"


def preprocess(image_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load as 3-channel RGB, resize to input size, normalize to [-1,1].
    Returns (batched_input[NHWC], orig_resized_rgb[HWC])."""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    size = int(_input_size) if isinstance(_input_size, int) and _input_size > 0 else IMG_SIZE
    orig_resized = cv2.resize(img, (size, size)).astype(np.float32)
    inp = (orig_resized / 127.5) - 1.0
    inp = np.expand_dims(inp, 0)
    return inp, orig_resized

def _read_as_rgb(image: Union[str, Any]) -> np.ndarray:
    # Fallback for file-like inputs; keep behavior consistent with training
    if isinstance(image, str):
        # Prefer main preprocess for paths
        batched, orig = preprocess(image)
        # Return de-batched normalized image for compatibility
        return batched[0]
    else:
        if hasattr(image, 'seek'):
            try:
                image.seek(0)
            except Exception:
                pass
        data = np.frombuffer(image.read(), np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError('Could not read image')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)).astype(np.float32)
        img = (img / 127.5) - 1.0
        return img


def _predict(batch: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not is_ready():
        raise RuntimeError(f'Model not loaded: {last_error()}')
    
    import tensorflow as tf
    
    # Check if it's a SavedModel signature function
    if hasattr(_model, 'structured_input_signature'):
        # SavedModel format
        input_names = list(_model.structured_input_signature[1].keys())
        input_name = input_names[0] if input_names else 'input_1'
        
        # Convert to TensorFlow tensor
        inp_tensor = tf.constant(batch, dtype=tf.float32)
        predictions = _model(**{input_name: inp_tensor})
        
        # Map outputs based on shapes (following user's approach)
        mc_p = None
        path_p = None
        seg_p = None
        
        for key, value in predictions.items():
            shape = value.shape
            if len(shape) == 2 and shape[1] <= 5:  # Multiclass (batch, 3-5)
                mc_p = value.numpy()
            elif len(shape) == 2 and shape[1] >= 20:  # Pathology (batch, many)
                path_p = value.numpy()
            elif len(shape) == 4 and shape[1] == IMG_SIZE:  # Segmentation (batch, H, W, 1)
                seg_p = value.numpy()
        
        if mc_p is None or path_p is None or seg_p is None:
            raise RuntimeError('Could not identify all SavedModel outputs correctly')
            
        return mc_p, path_p, seg_p
    else:
        # Keras model format
        preds = _model.predict(batch, verbose=0)
        if isinstance(preds, (list, tuple)) and len(preds) >= 3:
            mc, path, seg = preds[0], preds[1], preds[2]
        else:
            raise RuntimeError('Unexpected model outputs')
        return mc, path, seg


def analyze_to_view(image: Union[str, Any]) -> Dict[str, Any]:
    import tensorflow as tf  # for Grad-CAM checks
    load_model_if_needed()
    if not is_ready():
        raise RuntimeError(f'Model not available: {last_error()}')

    # Use requested preprocess when a path is provided; fallback for file-like
    if isinstance(image, str):
        batch, orig_resized = preprocess(image)
    else:
        rgb = _read_as_rgb(image)
        batch = np.expand_dims(rgb, 0)
        # Reconstruct display RGB in [0,255] from normalized
        orig_resized = ((rgb + 1.0) * 127.5).clip(0, 255).astype(np.uint8)

    mc_p, path_p, seg_p = _predict(batch)

    # Multiclass top-1 only (highest confidence)
    mc_vec = mc_p[0]
    top_idx = int(np.argmax(mc_vec))
    top_conf = float(mc_vec[top_idx])
    mc_label = _mc_labels[top_idx] if top_idx < len(_mc_labels) else f'class_{top_idx}'
    
    # Single prediction with highest confidence only
    pred_list = [
        { 'class': mc_label, 'confidence': top_conf }
    ]

    # Pathologies with confidence above 0.5 (50%)
    path_pairs: List[Tuple[str, float]] = []
    path_scores: List[Dict[str, float]] = []
    
    # Tumor subtype analysis (only for benign/malignant with segmentation)
    tumor_subtype = None
    tumor_subtype_confidence = None
    has_segmentation = seg_p is not None and seg_p.size > 0 and np.any(seg_p[0] >= 0.5)
    is_tumor = mc_label in ["benign", "malignant"]
    
    if path_p is not None and path_p.size > 0:
        pv = path_p[0]
        
        # Separate tumor subtypes from pathology characteristics
        tumor_scores = []
        pathology_scores_filtered = []
        
        for i, p in enumerate(pv):
            name = _pathology_labels[i] if i < len(_pathology_labels) else f'pathology_{i}'
            confidence = float(p)
            
            if name in TUMOR_SUBTYPES:
                # This is a tumor subtype
                tumor_scores.append((name, confidence))
            else:
                # This is a pathology characteristic (location)
                pathology_scores_filtered.append({ 'name': name, 'prob': confidence })
                if confidence > 0.5:
                    path_pairs.append((name, confidence))
        
        # Find highest confidence tumor subtype if conditions are met
        if is_tumor and has_segmentation and tumor_scores:
            tumor_scores.sort(key=lambda x: x[1], reverse=True)
            tumor_subtype = tumor_scores[0][0]
            tumor_subtype_confidence = tumor_scores[0][1]
        
        # Use filtered pathology scores (excluding tumor subtypes)
        path_scores = pathology_scores_filtered
        path_pairs.sort(key=lambda x: x[1], reverse=True)
        path_pairs = path_pairs[:5]

    # Segmentation overlay
    seg = seg_p[0]
    if seg.ndim == 3 and seg.shape[-1] == 1:
        seg = seg[..., 0]
    seg_mask = (seg >= 0.5).astype(np.uint8)

    base_bgr = cv2.cvtColor(orig_resized.astype(np.uint8), cv2.COLOR_RGB2BGR)

    seg_bgr = base_bgr.copy()
    red = np.zeros_like(seg_bgr)
    red[seg_mask.astype(bool)] = [0, 0, 255]
    seg_bgr = cv2.addWeighted(base_bgr, 0.6, red, 0.4, 0)

    # Grad-CAM using segmentation-based attention (following user's approach)
    grad_bgr = base_bgr.copy()
    try:
        # Use segmentation output as attention map (simpler approach for SavedModel)
        attention_map = seg_p[0, :, :, 0] if seg_p.ndim == 4 else seg_p[0]
        
        # Normalize attention map
        heatmap = attention_map.copy()
        heatmap = np.maximum(heatmap, 0)
        if heatmap.max() > 0:
            heatmap /= heatmap.max()

        heatmap_resized = cv2.resize(heatmap, (IMG_SIZE, IMG_SIZE))
        
        # Create colormap overlay
        gradcam_heatmap = cv2.applyColorMap(cv2.convertScaleAbs(heatmap_resized * 255), cv2.COLORMAP_JET)
        gradcam_heatmap = cv2.cvtColor(gradcam_heatmap, cv2.COLOR_BGR2RGB)
        grad_bgr_rgb = cv2.cvtColor(base_bgr, cv2.COLOR_BGR2RGB)
        overlay_gradcam = cv2.addWeighted(grad_bgr_rgb, 0.5, gradcam_heatmap, 0.5, 0)
        grad_bgr = cv2.cvtColor(overlay_gradcam, cv2.COLOR_RGB2BGR)
        
    except Exception as e:
        print(f"Grad-CAM generation failed: {e}")
        pass

    # Save segmentation and gradcam images to static/heatmaps so backend can reference them
    try:
        heatmaps_dir = os.path.abspath(os.path.join(_models_dir(), '..', 'static', 'heatmaps'))
        os.makedirs(heatmaps_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        seg_filename = f"segmentation_{timestamp}.png"
        grad_filename = f"gradcam_{timestamp}.png"
        seg_path = os.path.join(heatmaps_dir, seg_filename)
        grad_path = os.path.join(heatmaps_dir, grad_filename)
        # Debug: report shapes and existence
        try:
            print(f"[multitask] Saving heatmaps to {heatmaps_dir}")
            print(f"[multitask] seg_bgr shape: {getattr(seg_bgr, 'shape', 'N/A')}")
            print(f"[multitask] grad_bgr shape: {getattr(grad_bgr, 'shape', 'N/A')}")
            ok_seg = cv2.imwrite(seg_path, seg_bgr)
            print(f"[multitask] cv2.imwrite(seg) => {ok_seg} (path={seg_path})")
            ok_grad = cv2.imwrite(grad_path, grad_bgr)
            print(f"[multitask] cv2.imwrite(grad) => {ok_grad} (path={grad_path})")
            if not ok_seg:
                print(f"[multitask] Warning: failed to write segmentation image to {seg_path}")
            if not ok_grad:
                print(f"[multitask] Warning: failed to write gradcam image to {grad_path}")
        except Exception as inner_e:
            import traceback
            print(f"[multitask] Exception while saving heatmaps: {inner_e}")
            traceback.print_exc()
    except Exception as e:
        import traceback
        print(f"Failed to prepare heatmaps directory or filenames: {e}")
        traceback.print_exc()
        seg_filename = None
        grad_filename = None

    return {
        'multiclass_label': mc_label,
        'multiclass_confidence': top_conf,
        'predictions': pred_list,
        'pathologies': path_pairs,  # list of (name, prob>0.1) - location characteristics only
        'pathology_scores': path_scores,  # all pathology scores - location characteristics only
        'tumor_subtype': tumor_subtype,  # highest confidence tumor subtype if conditions met
        'tumor_subtype_confidence': tumor_subtype_confidence,
        'segmentation_url': _to_data_url(seg_bgr),
        'gradcam_url': _to_data_url(grad_bgr),
        'segmentation_filename': seg_filename,
        'gradcam_filename': grad_filename,
    }
