#!/usr/bin/env python3

import time
import threading
import cv2
import numpy as np
from picamera2 import Picamera2
from openalpr import Alpr
import LPR

# File to store detected license plates
log_file_path = "detected_plates.txt"

# Initialize OpenALPR
alpr = Alpr("us", "openalpr.conf", "runtime_data")
if not alpr.is_loaded():
    print("Error loading OpenALPR. Check your configuration paths.")
    exit(1)

# Initialize Picamera2
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (1920, 1080)})  # Balanced resolution
picam2.configure(camera_config)
picam2.start()

time.sleep(1)  # Allow camera to stabilize

print("Camera started. Press Ctrl+C to stop.")

# Global variable for latest frame
latest_frame = None
lock = threading.Lock()

def process_frames():
    """Thread that continuously runs ALPR on the latest frame and logs results."""
    global latest_frame
    while True:
        with lock:
            if latest_frame is None:
                continue
            frame_copy = latest_frame.copy()  # Process a copy to avoid locking camera

        # Convert to JPEG in memory
        ret, encoded_image = cv2.imencode(".jpg", frame_copy)
        if not ret:
            print("Error encoding image!")
            continue
        
        # Ensure it's contiguous for safe memory passing
        encoded_image = np.ascontiguousarray(encoded_image, dtype=np.uint8)
        
        # Recognize plates
        result = LPR.testAlpr(encoded_image)
        log_entry = f"Detected Plate: {result.characters} (Confidence: {result.overall_confidence:.2f}%)\n"

        print('Test finished')

        # Print to console
        print(log_entry.strip())

        # Append to log file
        with open(log_file_path, "a") as log_file:
           log_file.write(log_entry)
           print('Written to file')

# Start processing thread
threading.Thread(target=process_frames, daemon=True).start()

try:
    while True:
        start_time = time.perf_counter()

        # Capture latest frame
        with lock:
            latest_frame = picam2.capture_array()

        # Print FPS
        end_time = time.perf_counter()
        fps = 1.0 / (end_time - start_time)
        # print(f"Camera FPS: {fps:.2f}")

except KeyboardInterrupt:
    print("\nStopping...")
    alpr.unload()
    picam2.stop()
