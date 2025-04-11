# =============================
# capture/motion_detector.py
# =============================
import cv2
import numpy as np  # type: ignore


class MotionDetector:
    def __init__(self, cfg: dict):
        self.prev_gray = None
        self.area_threshold = cfg.get("area_threshold", 50000)

    def is_triggered(self, frame: np.ndarray) -> bool:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if self.prev_gray is None:
            self.prev_gray = gray
            return False
        delta = cv2.absdiff(self.prev_gray, gray)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.prev_gray = gray
        return any(cv2.contourArea(c) > self.area_threshold for c in contours)