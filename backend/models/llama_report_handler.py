"""
LLaMA LoRA-based report generator handler (refactored with robust base/adapter loading).

- Ensures dependencies are present (installs if missing, dev only).
- Downloads base model from HF Hub if not found locally (needs HF token in env).
- Attaches saved LoRA adapter and exposes `generate_report()` for Flask backend.
"""

import os, sys, subprocess, threading, json
from typing import Any, Dict, List, Optional, Tuple

_lock = threading.Lock()
_loaded = False
_last_error: Optional[str] = None
_tokenizer = None
_model = None

# Force model + adapter to load from the same directory as this file
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL_PATH = os.path.join(_THIS_DIR, "llama3_base_model")
ADAPTER_PATH   = os.path.join(_THIS_DIR, "llama3_bone_lora_adapter")

# Ensure deps
_pkgs = ["transformers", "accelerate", "peft", "bitsandbytes", "huggingface_hub"]
for p in _pkgs:
    try:
        __import__(p)
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", p])

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from huggingface_hub import snapshot_download


# ================= Loader =================

def _download_base_if_needed():
    if not os.path.isdir(BASE_MODEL_PATH):
        hf_token = (os.environ.get("HUGGINGFACEHUB_API_TOKEN")
                    or os.environ.get("HF_TOKEN")
                    or os.environ.get("HUGGINGFACE_TOKEN"))
        if not hf_token:
            raise RuntimeError("Base model not found and no HF token set. "
                               "Set HUGGINGFACEHUB_API_TOKEN to download.")
        MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
        print("Downloading base model (first run may take long)...")
        snapshot_download(repo_id=MODEL_ID, local_dir=BASE_MODEL_PATH, token=hf_token)


def load_if_needed() -> None:
    global _loaded, _last_error, _tokenizer, _model
    if _loaded and _model is not None:
        return
    with _lock:
        if _loaded and _model is not None:
            return
        try:
            _download_base_if_needed()

            # Device detection
            device = torch.device("cpu")
            use_4bit = False
            bnb_config = None
            if torch.cuda.is_available():
                try:
                    import bitsandbytes as _bnb  # noqa
                    from transformers import BitsAndBytesConfig
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16,
                    )
                    use_4bit = True
                    device = torch.device("cuda")
                    print("CUDA + bitsandbytes available: using 4-bit load")
                except Exception:
                    device = torch.device("cuda")
                    print("CUDA available but bitsandbytes failed, using fp16")

            # Tokenizer
            _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, use_fast=False)
            if _tokenizer.pad_token is None:
                _tokenizer.add_special_tokens({"pad_token": _tokenizer.eos_token})

            # Base model
            if use_4bit and bnb_config:
                base = AutoModelForCausalLM.from_pretrained(
                    BASE_MODEL_PATH, quantization_config=bnb_config,
                    device_map="auto", trust_remote_code=True
                )
            else:
                dtype = torch.float16 if device.type == "cuda" else torch.float32
                base = AutoModelForCausalLM.from_pretrained(
                    BASE_MODEL_PATH, dtype=dtype,
                    device_map="auto" if device.type == "cuda" else None,
                    trust_remote_code=True,
                )

            # Adapter
            if not os.path.isdir(ADAPTER_PATH):
                raise FileNotFoundError(f"Adapter folder not found at {ADAPTER_PATH}")
            model = PeftModel.from_pretrained(base, ADAPTER_PATH)
            try:
                model = model.merge_and_unload()
            except Exception:
                pass
            model.to(device)
            model.eval()

            _model = model
            _loaded, _last_error = True, None
        except Exception as e:
            _loaded, _tokenizer, _model = False, None, None
            _last_error = str(e)


def is_ready() -> bool:
    return _loaded and _model is not None and _tokenizer is not None


def last_error() -> Optional[str]:
    return _last_error


# ========== Prompting & Report ==========

TUMOR_CLASSES = [
    "osteochondroma", "multiple osteochondromas", "simple bone cyst",
    "giant cell tumor", "osteofibroma", "synovial osteochondroma",
    "other bt", "osteosarcoma", "other mt"
]


def extract_tumor_and_locations(top_labels: List[str]) -> Tuple[Optional[str], List[str]]:
    tumor_type, locs = None, []
    for lbl in (top_labels or []):
        if lbl and lbl.lower() in TUMOR_CLASSES:
            tumor_type = lbl
        elif lbl:
            locs.append(lbl)
    return tumor_type, locs


def _default_template() -> str:
    return (
        "1. Key Findings\n"
        "Tumor Type: {tumor_type} ({malignancy})\n"
        "Confidence: {confidence}\n"
        "Tumor Locations: {locations}\n"
        "Additional Observations: {observations}\n"
        "Malignancy Status: {risk_level}\n\n"
        "2. Patient-Friendly Explanation\n<Explanation>\n\n"
        "3. Recommended Treatment Plan\n<Treatment steps>"
    )


def build_prompt_from_input_struct(inp: Dict[str, Any]) -> str:
    tumor, locs = extract_tumor_and_locations(inp.get("top_pathology_labels", []))
    instr = f"Generate a full report for a {tumor} case" if tumor else "Generate a full report for a normal case"
    input_text = "\n".join([
        f"Multiclass Label: {inp.get('multiclass_label','')}",
        f"Tumor Type: {tumor or 'None'}",
        f"Confidence: {inp.get('confidence','')}",
        f"Pathology Locations: {', '.join(locs)}"
    ])
    return f"### Instruction:\n{instr}\n\n### Input:\n{input_text}\n\n### Response Format Example:\n{_default_template()}\n\n### Response:\n "


# ========= Helpers for strict formatting =========

def _format_confidence(conf_value: Any) -> Tuple[float, str]:
    """
    Normalizes confidence to float in [0,1] if possible and returns (raw_float, display_string).
    If input looks like 0.0–1.0, treat as prob; if >1, treat as percentage.
    """
    try:
        c = float(conf_value)
    except Exception:
        return 0.0, "Undetermined"

    if c > 1.0:
        # assume already in percent like 85.0
        return c / 100.0, f"{c:.1f}%"
    else:
        # assume probability 0–1
        return c, f"{c * 100.0:.1f}%"

def _build_normal_report(conf_display: str) -> str:
    """
    Deterministic report for multiclass_label == 'normal'.
    Absolutely no tumor locations or malignancy.
    """
    if not conf_display or conf_display == "Undetermined":
        conf_display = "Not available"

    lines = [
        "1. Key Findings",
        "Tumor Type: None",
        f"Confidence: {conf_display}",
        "Tumor Locations: None",
        "Additional Observations: No tumor or abnormal growth is detected in the evaluated bone structures.",
        "Malignancy Status: None",
        "",
        "2. Patient-Friendly Explanation",
        "Based on the analysis of your imaging, there is no evidence of a bone tumor or abnormal growth. "
        "The overall appearance of the scanned region is within normal limits. "
        "No tumor-related treatment is required at this time.",
        "",
        "3. Recommended Treatment Plan",
        "1. No active tumor-specific treatment is required.",
        "2. Continue routine clinical check-ups as advised by your doctor.",
        "3. Seek medical review if you develop new pain, swelling, or other concerning symptoms."
    ]
    return "\n".join(lines)


# ========== Main generation function (UPDATED) ==========

def generate_report(
    inp: Dict[str, Any],
    max_new_tokens: int = 512,
    instruction_override: str = None
) -> Dict[str, Any]:
    """
    Generate a report from input using the LLaMA model + strict normal/tumor handling.

    - If multiclass_label == "normal" (case-insensitive): we bypass LLaMA and
      return a deterministic, safe normal report with:
        Tumor Type: None
        Tumor Locations: None
        Malignancy Status: None
    - Otherwise: use LLaMA with a strict prompt that enforces the 3-section format.
    """
    load_if_needed()
    if not is_ready():
        raise RuntimeError(f"LLaMA not ready: {last_error()}")

    device = next(_model.parameters()).device

    multiclass = (inp.get("multiclass_label") or "").strip()
    multiclass_lower = multiclass.lower()

    # Normalize confidence
    raw_conf, conf_display = _format_confidence(inp.get("confidence"))

    # === HARD OVERRIDE: NORMAL CASE HANDLED WITHOUT LLM ===
    if multiclass_lower == "normal":
        report_text = _build_normal_report(conf_display)
        return {"report": report_text}

    # === TUMOR / ABNORMAL CASES → USE LLaMA WITH STRICT PROMPT ===
    tumor, locs = extract_tumor_and_locations(inp.get("top_pathology_labels", []))
    tumor_display = tumor or inp.get("predicted_tumor_type") or "Unknown"

    # Basic malignancy heuristic (you can tune based on your labels)
    lower_combo = (multiclass + " " + tumor_display).lower()
    is_malignant = any(k in lower_combo for k in ["malignant", "sarcoma", "other mt"])
    malignancy = "Malignant" if is_malignant else "Benign"

    # Risk level based on malignancy + confidence
    risk_level = "High" if is_malignant or raw_conf >= 0.8 else "Low"

    locations = ", ".join(locs) if locs else "Not specified"

    # Observations summary for model context
    observations = []
    if raw_conf >= 0.8:
        observations.append("High confidence in tumor classification.")
    if is_malignant:
        observations.append("Findings are consistent with a malignant bone tumor.")
    if locs:
        observations.append(f"Tumor appears concentrated in {locations}.")
    observations_text = " ".join(observations) if observations else "No additional specific observations provided."

    # === STRICT PROMPT FOR TUMOR CASES ===
    # This enforces your format & prevents extra hallucinations.
    prompt = f"""You are an AI medical report generator for bone tumor analysis.
You must strictly follow the classifier output below and MUST NOT invent new tumor types, locations, or treatments.

--- CLASSIFIER OUTPUT ---
Multiclass Label: {multiclass}
Tumor Type: {tumor_display}
Tumor Present: yes
Classification (Benign/Malignant): {malignancy}
Confidence: {conf_display}
Tumor Locations: {locations}
Risk Level: {risk_level}
Key Observations: {observations_text}
--------------------------

STRICT RULES:
1. Treat this as a TUMOR/ABNORMAL case (tumor present = "yes").
   - Use the same tumor type given above.
   - Use the same locations given above. Do NOT add new body parts or regions.
   - Do NOT guess additional locations, symptoms, or diseases.
2. Only use information from the classifier output and general medical knowledge.
3. The report MUST follow EXACTLY this 3-part structure and heading text:

1. Key Findings
Tumor Type: ...
Confidence: ...
Tumor Locations: ...
Additional Observations: ...
Malignancy Status: ...

2. Patient-Friendly Explanation
...

3. Recommended Treatment Plan
...

4. Do NOT use any placeholders like <Tumor Type> or <Explanation>. Write complete, final text.

Now generate the report in this exact format:
1. Key Findings
Tumor Type: (state tumor type and whether it is benign or malignant in brackets)
Confidence: (use the confidence above)
Tumor Locations: (list the locations from classifier or 'Not specified')
Additional Observations: (use the key observations in concise form)
Malignancy Status: (High or Low based on the risk level)

2. Patient-Friendly Explanation
(Explain the findings in 2–4 simple sentences a patient can understand.)

3. Recommended Treatment Plan
(Provide 3–4 numbered steps, including specialist consultation, imaging or follow-up as appropriate.)

### Response:
"""

    # Allow custom override if passed (kept for flexibility)
    if instruction_override:
        prompt = instruction_override + "\n\n" + prompt

    # === Tokenize & generate ===
    inputs = _tokenizer(prompt, return_tensors="pt", padding=True).to(device)

    with torch.inference_mode():
        params = {
            "max_new_tokens": max_new_tokens,
            "do_sample": False,
            "num_beams": 3,
            "early_stopping": True,
            "length_penalty": 1.0,
            "repetition_penalty": 1.15,
            "no_repeat_ngram_size": 5,
            "eos_token_id": _tokenizer.eos_token_id,
            "pad_token_id": _tokenizer.pad_token_id,
        }

        # Allow mild sampling when GPU is available (nicer text but still controlled)
        if torch.cuda.is_available():
            params.update({
                "do_sample": True,
                "temperature": 0.6,
                "top_p": 0.85,
                "top_k": 50,
            })

        out = _model.generate(**inputs, **params)

    text = _tokenizer.decode(out[0], skip_special_tokens=True).strip()

    # Try to isolate the answer after "### Response:" if present
    if "### Response:" in text:
        text = text.split("### Response:", 1)[1].strip()

    # === SAFETY NET: if model format is wrong, fall back to deterministic template ===
    if not text.startswith("1. Key Findings"):
        fallback_lines = [
            "1. Key Findings",
            f"Tumor Type: {tumor_display} ({malignancy})",
            f"Confidence: {conf_display}",
            f"Tumor Locations: {locations}",
            f"Additional Observations: {observations_text}",
            f"Malignancy Status: {risk_level}",
            "",
            "2. Patient-Friendly Explanation",
            "Based on our analysis of your X-ray images, we have identified a "
            f"{tumor_display.lower()} which is classified as {malignancy.lower()}. "
            f"The confidence in this diagnosis is {conf_display}. "
            + (f"The tumor is primarily located in the {locations}. " if locations != "Not specified" else "")
            + f"Given these findings, we assess this as a {risk_level.lower()} risk case.",
            "",
            "3. Recommended Treatment Plan",
            "1. Schedule a consultation with an orthopedic oncologist.",
            "2. Conduct additional imaging studies (MRI/CT) for detailed assessment.",
            "3. Plan for appropriate treatment based on the specialist's evaluation.",
            "4. Maintain regular follow-up appointments to monitor response and progression."
        ]
        text = "\n".join(fallback_lines)

    return {"report": text}


def build_input_from_multitask(mt: Dict[str, Any]) -> Dict[str, Any]:
    top_labels = []
    if mt.get("tumor_subtype"):
        top_labels.append(str(mt["tumor_subtype"]))
    names_scores = []
    if isinstance(mt.get("pathology_scores"), list):
        for itm in mt["pathology_scores"]:
            try:
                names_scores.append((str(itm["name"]), float(itm.get("prob", 0.0))))
            except Exception:
                pass
    elif isinstance(mt.get("pathologies"), list):
        for name, prob in mt["pathologies"]:
            try:
                names_scores.append((str(name), float(prob)))
            except Exception:
                pass
    names_scores.sort(key=lambda x: x[1], reverse=True)
    for name, _ in names_scores[:5]:
        if name not in top_labels:
            top_labels.append(name)
    return {
        "multiclass_label": mt.get("multiclass_label") or mt.get("prediction"),
        "top_pathology_labels": top_labels,
        "predicted_tumor_type": mt.get("tumor_subtype"),
        "confidence": mt.get("multiclass_confidence") or mt.get("confidence"),
    }
