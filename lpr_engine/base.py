# =============================
# lpr_engine/base.py
# =============================

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import numpy as np  # type: ignore


class BaseEngine(ABC):
    """Abstract base class for all LPR engines."""

    @abstractmethod
    def recognize(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Return a list of plate dictionaries.

        Each dict contains:
        - plate: str
        - confidence: float (0‑1)
        - bbox: Tuple[int, int, int, int] (x1, y1, x2, y2)
        """