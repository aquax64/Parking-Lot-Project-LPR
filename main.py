# =============================
# main.py
# =============================
"""Entry point for the Smart Parking Pi node."""
import logging.config
from pathlib import Path

import yaml

from capture.camera import Camera
from capture.motion_detector import MotionDetector
from lpr_engine import get_engine
from pipelines.occupancy_counter import OccupancyCounter
from pipelines.uploader import Uploader

CONFIG_PATH = Path(__file__).parent / "config" / "settings.yaml"
LOG_CFG_PATH = Path(__file__).parent / "config" / "logging.yaml"

logging.config.dictConfig(yaml.safe_load(LOG_CFG_PATH.read_text()))
logger = logging.getLogger("smartparking")

cfg = yaml.safe_load(CONFIG_PATH.read_text())

camera = Camera(cfg["camera"])
motion = MotionDetector(cfg["motion"])
lpr = get_engine(cfg["lpr"]["engine"], **cfg["lpr"]["params"])
counter = OccupancyCounter(cfg["lots"])
up_cfg = cfg["uploader"]
uploader = Uploader(**up_cfg)
uploader.start()

for frame in camera.stream():
    if not motion.is_triggered(frame):
        continue
    plates = lpr.recognize(frame)
    events = counter.filter_new_events(plates)
    for ev in events:
        uploader.enqueue(ev)