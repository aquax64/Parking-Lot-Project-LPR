import datetime
import logging
import os
import re
import time

import cv2
import numpy as np
from openalpr import Alpr
from picamera2 import Picamera2

# =============================
# CONFIGURATION
# =============================
SAVE_DIR = "captured_frames"
LOG_FILE = "detected_plates.txt"
MOTION_AREA_THRESHOLD = 50000
FRAME_DELAY = 2

# =============================
# SETUP
# =============================
os.makedirs(SAVE_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("session.log"),
        logging.StreamHandler()
    ]
)

# Initialize OpenALPR
alpr = Alpr("us", "openalpr.conf", "runtime_data")
if not alpr.is_loaded():
    logging.error("Failed to load OpenALPR. Check your config paths.")
    exit(1)
logging.info("OpenALPR loaded.")

# Initialize Picamera2
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (4608, 2592)})
picam2.configure(camera_config)
picam2.start()
time.sleep(FRAME_DELAY)
logging.info("Camera started.")

# =============================
# FUNCTIONS
# =============================
def detect_motion(prev_gray, current_frame):
    gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_gray is None:
        return gray, False

    frame_delta = cv2.absdiff(prev_gray, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > MOTION_AREA_THRESHOLD:
            logging.debug(f"Motion detected! Contour area: {area}")
            return gray, True

    return gray, False


def process_alpr(frame, timestamp):
    ret, encoded_image = cv2.imencode(".jpg", frame)
    if not ret:
        logging.error("Failed to encode image for ALPR.")
        return

    results = alpr.recognize_array(encoded_image.tobytes())
    if "results" in results and results["results"]:
        logging.info("License plates detected:")
        with open(LOG_FILE, "a") as log:
            for plate in results["results"]:
                clean_plate_text = clean_plate(plate["plate"])
                confidence = plate["confidence"]
                log_entry = f"{timestamp} - {clean_plate_text} ({confidence:.2f}%)\n"
                logging.info(f"  - {log_entry.strip()}")
                log.write(log_entry)
    else:
        logging.info("No license plates detected in this frame.")

def clean_plate(plate_text):
    # Remove spaces to simplify
    plate_text = plate_text.replace(" ", "")

    # Format 1: ABC1234 → Letters first
    pattern1 = r"^[A-Z0-9]{3}[0-9]{4}$"
    # Format 2: 123ABCD → Numbers first
    pattern2 = r"^[0-9]{3}[A-Z0-9]{4}$"

    if re.match(pattern1, plate_text):
        # Fix first 3 letters (change 0 to O)
        cleaned = ''.join(['O' if c == '0' else c for c in plate_text[:3]]) + plate_text[3:]
        return cleaned

    elif re.match(pattern2, plate_text):
        # Fix last 4 letters (change 0 to O)
        cleaned = plate_text[:3] + ''.join(['O' if c == '0' else c for c in plate_text[3:]])
        return cleaned

    else:
        # If it doesn't match, return as-is
        return plate_text



# =============================
# MAIN LOOP
# =============================
prev_gray = None
frame_count = 0
motion_event_count = 0

try:
    while True:
        frame = picam2.capture_array()
        prev_gray, motion_detected = detect_motion(prev_gray, frame)

        if motion_detected:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"{SAVE_DIR}/motion_{timestamp}.jpg"
            cv2.imwrite(image_path, frame)
            logging.info(f"Saved frame to {image_path}")

            process_alpr(frame, timestamp)
            motion_event_count += 1
        else:
            logging.debug(f"No motion. Frame #{frame_count}")

        frame_count += 1

except KeyboardInterrupt:
    logging.info("Stopping due to keyboard interrupt...")

except Exception as e:
    logging.error(f"Unexpected error: {e}")

finally:
    alpr.unload()
    picam2.stop()
    logging.info(f"Session ended. Total frames: {frame_count}, Motion events: {motion_event_count}")