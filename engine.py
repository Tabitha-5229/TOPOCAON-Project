"""Model loading and prediction. No Streamlit code in here, so it can be tested on its own."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np
from PIL import Image, ImageOps

MODEL_DIR = Path(__file__).parent / "models"
CROPS = ["Potato", "Tomato", "Cassava", "Onion"]

# Scores below LOW are treated as "no clear result"; between LOW and HIGH the result is shown with a warning.
LOW = 0.35
HIGH = 0.60
MIN_CONF = 0.10  # lowest detection score kept, so that runner up classes can be listed


def model_path(crop: str) -> Path:
    return MODEL_DIR / f"{crop.lower()}.pt"


def model_available(crop: str) -> bool:
    return model_path(crop).exists()


_loaded: Dict[str, object] = {}


def load_model(crop: str):
    """Load (and keep in memory) the YOLO model for one crop."""
    if crop not in _loaded:
        from ultralytics import YOLO  # imported here so the rest of the app starts fast

        _loaded[crop] = YOLO(str(model_path(crop)))
    return _loaded[crop]


@dataclass
class Prediction:
    class_name: str
    score: float


@dataclass
class Result:
    ranked: List[Prediction]            # best score per class, highest first
    verdict: str                        # "confident", "uncertain" or "none"
    annotated: Optional[np.ndarray]     # RGB image with the detection box drawn
    inference_ms: float


def rank_classes(names: Dict[int, str], class_ids: Sequence[int], scores: Sequence[float]) -> List[Prediction]:
    """Keep the best score for each class and sort from highest to lowest."""
    best: Dict[int, float] = {}
    for c, s in zip(class_ids, scores):
        c = int(c)
        best[c] = max(best.get(c, 0.0), float(s))
    ranked = [Prediction(names[c], s) for c, s in best.items()]
    ranked.sort(key=lambda p: p.score, reverse=True)
    return ranked


def verdict_for(ranked: List[Prediction]) -> str:
    if not ranked or ranked[0].score < LOW:
        return "none"
    if ranked[0].score < HIGH:
        return "uncertain"
    return "confident"


def prepare_image(image: Image.Image) -> Image.Image:
    """Fix phone rotation and make sure the image is plain RGB."""
    return ImageOps.exif_transpose(image).convert("RGB")


def predict(crop: str, image: Image.Image, draw_box: bool = True) -> Result:
    model = load_model(crop)
    img = prepare_image(image)
    out = model.predict(img, conf=MIN_CONF, iou=0.5, imgsz=640, verbose=False)[0]

    ranked: List[Prediction] = []
    if out.boxes is not None and len(out.boxes) > 0:
        ranked = rank_classes(out.names, out.boxes.cls.cpu().numpy(), out.boxes.conf.cpu().numpy())

    annotated = None
    if draw_box and ranked:
        annotated = out.plot()[:, :, ::-1]  # Ultralytics draws in BGR, the page needs RGB

    return Result(
        ranked=ranked,
        verdict=verdict_for(ranked),
        annotated=annotated,
        inference_ms=float(out.speed.get("inference", 0.0)),
    )
