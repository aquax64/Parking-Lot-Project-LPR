# =============================
# lpr_engine/yolo_paddle_engine.py (placeholder for future)
# =============================
from typing import Any, Dict, List

import numpy as np  # type: ignore

from .base import BaseEngine


class YoloPaddleEngine(BaseEngine):
    """Placeholder – implement when ready."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("YOLO + PaddleOCR engine not yet implemented.")

    def recognize(self, frame: np.ndarray) -> List[Dict[str, Any]]:  # noqa: D401
        return []
