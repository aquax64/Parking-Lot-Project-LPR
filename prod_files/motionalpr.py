import time
import cv2
import datetime
import os
import numpy as np
from picamera2 import Picamera2
from openalpr import Alpr

# Setup directories
SAVE_DIR = "captured_frames"
LOG_FILE = "detected_plates.txt"
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize OpenALPR
alpr = Alpr("us", "openalpr.conf", "runtime_data")
if not alpr.is_loaded():
    print("[ERROR] Failed to load OpenALPR. Check your config paths.")
    exit(1)
print("[INFO] OpenALPR loaded.")

# Initialize Picamera2
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (4608, 2592)})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
print("[INFO] Camera started.")

# Initialize motion detection
prev_gray = None
frame_count = 0
motion_event_count = 0

try:
    while True:
        # Capture current frame
        frame = picam2.capture_array()

        # Convert to grayscale & blur for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Set up initial previous frame
        if prev_gray is None:
            prev_gray = gray
            print("[INFO] Motion detection primed.")
            continue

        # Compute difference
        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours (motion regions)
        _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_detected = False

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 50000:
                print(f"[DEBUG] Motion detected! Contour area: {area}")
                motion_detected = True
                break

        if motion_detected:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"{SAVE_DIR}/motion_{timestamp}.jpg"
            cv2.imwrite(image_path, frame)
            print(f"[INFO] Saved frame to {image_path}")

            # Encode and pass to ALPR
            ret, encoded_image = cv2.imencode(".jpg", frame)
            if not ret:
                print("[ERROR] Failed to encode image for ALPR.")
                continue

            results = alpr.recognize_array(encoded_image.tobytes())
            if "results" in results and results["results"]:
                print("[INFO] License plates detected:")
                with open(LOG_FILE, "a") as log:
                    for plate in results["results"]:
                        plate_text = plate["plate"]
                        confidence = plate["confidence"]
                        log_entry = f"{timestamp} - {plate_text} ({confidence:.2f}%)\n"
                        print(f"  - {log_entry.strip()}")
                        log.write(log_entry)
            else:
                print("[INFO] No license plates detected in this frame.")

            motion_event_count += 1
        else:
            print(f"[DEBUG] No motion. Frame #{frame_count}")

        prev_gray = gray
        frame_count += 1

except KeyboardInterrupt:
    print("\n[INFO] Stopping...")

# Cleanup
alpr.unload()
picam2.stop()
print(f"[INFO] Session ended. Total frames: {frame_count}, Motion events: {motion_event_count}")
