# =============================
# lpr_engine/__init__.py
# =============================
"""Factory for plate‑recognition engines."""
from .hyperlpr3_engine import HyperLPREngine

try:
    from .yolo_paddle_engine import YoloPaddleEngine  # optional
except ModuleNotFoundError:
    YoloPaddleEngine = None  # noqa: N816

def get_engine(name: str, **kwargs):
    engines = {
        "hyperlpr3": HyperLPREngine,
        "yolo_paddle": YoloPaddleEngine,
    }
    if name not in engines or engines[name] is None:
        raise ValueError(f"LPR engine '{name}' is not available.")
    return engines[name](**kwargs)