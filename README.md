# =============================
# README.md
# =============================
# Smart Parking Pi Node

Minimal, swappable plate‑recognition node for the TTU Smart Parking System.

## Quick start

```bash
# 1. clone repo & cd
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. (Optional) install system deps
# sudo apt-get install libopencv-dev libopenblas-dev

# 3. edit config/settings.yaml as needed

# 4. run
python main.py
```

### Switching LPR engines

```yaml
lpr:
  engine: "yolo_paddle"  # <- change here
  params:
    detector_path: "models/yolov8n.onnx"
    ocr_model_path: "models/paddleocr_lite.onnx"
```

Provide an implementation in `lpr_engine/yolo_paddle_engine.py`, then restart.

### Directory notes
* `capture/` – camera + motion sensing
* `lpr_engine/` – drop‑in plate recognizers
* `pipelines/` – occupancy logic & data upload
* `config/` – YAML for runtime config & logging

### Next steps
1. Collect 2 k images from the pilot lot and fine‑tune HyperLPR 3.
2. Flesh out entry/exit logic in `OccupancyCounter`.
3. Add RotatingFileHandler to logging config.
4. Implement OTA update script in `scripts/`.