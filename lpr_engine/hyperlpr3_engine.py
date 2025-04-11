# =============================
# lpr_engine/hyperlpr3_engine.py
# =============================
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np  # type: ignore

from .base import BaseEngine
from .utils import clean_plate_text

try:
    from hyperlpr import HyperLPR3
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ImportError("hyperlpr3 is not installed. Add it to requirements.txt.") from exc

class HyperLPREngine(BaseEngine):
    def __init__(self, model_path: str | None = None):
        model_dir = Path(model_path) if model_path else None
        self.recognizer = HyperLPR3(model_dir=model_dir)

    def recognize(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        results = self.recognizer.recognize(frame)
        parsed: List[Dict[str, Any]] = []
        for plate, confidence, bbox in results:
            parsed.append(
                {
                    "plate": clean_plate_text(plate),
                    "confidence": confidence / 100.0,  # convert to 0‑1
                    "bbox": tuple(int(x) for x in bbox),
                }
            )
        return parsed