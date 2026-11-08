"""Zero-shot galaxy classification with Galaxy-CLIP, read from the local folder models/galaxy-clip-finetuned/.

Galaxy-CLIP (juppy44/galaxy-clip-finetuned on Hugging Face) is OpenAI's CLIP (ViT-B/32) tuned on galaxy pictures
paired with written descriptions. CLIP turns a picture into a list of numbers and a sentence into a list of the same
length, so that a picture and a sentence about the same thing point the same way. For a picture a and labels b_i:

    similarity  s_i = cos(a, b_i)                        between -1 and 1; the labels are ranked by it
    match       p_i = exp(k s_i) / sum_j exp(k s_j)      k is the model's learned scale; adds up to 100% over the labels

Nothing is trained or fine-tuned here and nothing is downloaded: the files must already be in MODEL_DIR. Only the
safetensors weights are read, and no code from the model folder is run. torch and transformers are imported when the
model is first used, so the rest of the app works without them.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = Path(os.environ.get("GALAXY_CLIP_DIR") or ROOT / "models" / "galaxy-clip-finetuned")
HF_NAME = "juppy44/galaxy-clip-finetuned"
REVISION = "111c09edb0aa5ea0898288fbc9d5a4cce972db5e"   # the version downloaded on 2026-11-08
DOWNLOAD = f"hf download {HF_NAME} --local-dir models/galaxy-clip-finetuned"
FILES = ("config.json", "model.safetensors", "processor_config.json", "tokenizer.json", "tokenizer_config.json")
PICTURE_TYPES = ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tif", "tiff"]

# The ten classes of Galaxy10 DECaLS (Leung and Bovy 2019; labels from Galaxy Zoo DECaLS, Walmsley et al. 2022),
# in their usual order. Any other short descriptions work too: the model only compares the picture with the words.
DEFAULT_LABELS = [
    "disturbed galaxy",
    "merging galaxies",
    "round smooth galaxy",
    "in-between round smooth galaxy",
    "cigar-shaped smooth galaxy",
    "barred spiral galaxy",
    "unbarred tight spiral galaxy",
    "unbarred loose spiral galaxy",
    "edge-on galaxy without bulge",
    "edge-on galaxy with bulge",
]


def packages_missing() -> list[str]:
    return [f"the Python package `{mod}`: `.venv/bin/pip install {pip}`"
            for mod, pip in (("torch", "torch --index-url https://download.pytorch.org/whl/cpu"),
                             ("transformers", "transformers"), ("PIL", "pillow"))
            if importlib.util.find_spec(mod) is None]


def files_missing() -> list[str]:
    return [f for f in FILES if not (MODEL_DIR / f).is_file()]


def missing() -> list[str]:
    """What still has to be installed or downloaded before the model can run; empty when it is ready."""
    out = packages_missing()
    gone = files_missing()
    if gone:
        out.append(f"the model files in `{MODEL_DIR}` ({', '.join(gone)}): `{DOWNLOAD}`")
    return out


def fetch() -> None:
    """Download the model files once, pinned to REVISION, for a copy of the app that does not have them (such as
    the hosted one). A computer that already has the folder never calls this. Only the safetensors weights and the
    config and tokenizer files are fetched; no code."""
    global MODEL_DIR
    from huggingface_hub import snapshot_download

    for target in (MODEL_DIR, Path(tempfile.gettempdir()) / "galaxy-clip-finetuned"):
        try:
            snapshot_download(HF_NAME, revision=REVISION, local_dir=target, allow_patterns=list(FILES))
        except OSError:                                  # the app folder is read-only: use the temp folder
            continue
        MODEL_DIR = target
        info.cache_clear()
        return


def ready() -> bool:
    return not missing()


@lru_cache(maxsize=1)
def load():
    """(model, processor), from MODEL_DIR only."""
    from transformers import CLIPModel, CLIPProcessor
    from transformers.utils import logging

    logging.disable_progress_bar()
    model = CLIPModel.from_pretrained(MODEL_DIR, local_files_only=True, use_safetensors=True)
    processor = CLIPProcessor.from_pretrained(MODEL_DIR, local_files_only=True)
    return model.eval(), processor


@lru_cache(maxsize=1)
def info() -> dict:
    """Plain facts about the model, read from its config file (no need to load it)."""
    cfg = json.loads((MODEL_DIR / "config.json").read_text())
    v = cfg["vision_config"]
    side = v["image_size"] // v["patch_size"]
    return {"image_px": v["image_size"], "patch_px": v["patch_size"], "patches_side": side, "patches": side * side,
            "embed_dim": cfg["projection_dim"], "text_tokens": cfg["text_config"]["max_position_embeddings"],
            "weights_mb": (MODEL_DIR / "model.safetensors").stat().st_size / 1e6}


def scale() -> float:
    """k, the learned number the similarities are multiplied by before the softmax."""
    return float(load()[0].logit_scale.detach().exp())


def n_params() -> int:
    return sum(p.numel() for p in load()[0].parameters())


def clean_labels(labels) -> list[str]:
    """The labels as given, with spaces tidied, without blanks or repeats, in order."""
    out, seen = [], set()
    for lab in labels or []:
        lab = " ".join(str(lab).split())
        if lab and lab.lower() not in seen:
            out.append(lab)
            seen.add(lab.lower())
    return out


def open_image(src):
    """A picture as RGB, from a file path, bytes or a file object (the first frame of an animated one)."""
    from PIL import Image, ImageOps

    img = Image.open(io.BytesIO(src) if isinstance(src, (bytes, bytearray)) else src)
    img = ImageOps.exif_transpose(img)                  # phone pictures: turn them the right way up
    if img.mode in ("I", "I;16", "I;16B", "I;16L", "F"):  # 16-bit or float pictures (from telescope software)
        import numpy as np
        a = np.asarray(img, dtype="float32")
        lo, hi = np.nanpercentile(a, [1, 99.5])
        img = Image.fromarray((np.clip((a - lo) / ((hi - lo) or 1), 0, 1) * 255).astype("uint8"))
    return img.convert("RGB")


def classify(image, labels=None) -> pd.DataFrame:
    """Rank the labels for one picture: rank, label, match_pct (adds up to 100 over the labels), similarity."""
    import torch

    labels = clean_labels(labels) or list(DEFAULT_LABELS)
    model, processor = load()
    inputs = processor(text=labels, images=image, return_tensors="pt", padding=True, truncation=True)
    with torch.inference_mode():
        out = model(**inputs)
    sim = (out.image_embeds @ out.text_embeds.T)[0]          # both are unit length, so this is the cosine
    match = out.logits_per_image.softmax(dim=-1)[0]          # k times the cosine, then softmax
    table = pd.DataFrame({"label": labels, "match_pct": 100 * match.double().numpy(),
                          "similarity": sim.double().numpy()})
    table = table.sort_values("similarity", ascending=False, kind="stable").reset_index(drop=True)
    table.insert(0, "rank", range(1, len(table) + 1))
    return table
