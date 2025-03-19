import time
import threading
import cv2
import numpy as np
from picamera2 import Picamera2
from openalpr import Alpr

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

# Global variables
latest_frame = None
lock = threading.Lock()

# ---- NEW: We'll keep a rolling buffer of the last 5 frames' detections
FRAME_BUFFER_SIZE = 5
last_frames = []           # will store a list of lists, each sub-list is [(plate_text, confidence), ...]
already_logged = set()     # keeps track of plates we’ve already done a “consensus log” for

def process_frames():
    """Thread that continuously runs ALPR on the latest frame and logs results with multi-frame consensus."""
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

        # Recognize plates in this single frame
        results = alpr.recognize_array(encoded_image.tobytes())

        # Build a list of (plate_text, confidence) for this frame
        frame_detections = []
        if "results" in results and results["results"]:
            for plate in results["results"]:
                plate_text = plate["plate"]
                confidence = plate["confidence"]
                frame_detections.append((plate_text, confidence))

        # Store in rolling buffer
        last_frames.append(frame_detections)
        if len(last_frames) > FRAME_BUFFER_SIZE:
            last_frames.pop(0)

        # ----------------------------------------
        #  MULTI-FRAME CONSENSUS LOGIC
        # ----------------------------------------
        # Flatten all the plate detections in the last N frames
        combined_plates = []
        for fd_list in last_frames:
            combined_plates.extend(fd_list)  # fd_list is a list of (plate_text, confidence)

        # Count how many times each plate appears
        plate_counts = {}
        for (p_text, conf) in combined_plates:
            plate_counts[p_text] = plate_counts.get(p_text, 0) + 1

        # Check if a plate appears >= 3 times; if so, compute average confidence
        for p_text, count in plate_counts.items():
            if count >= 3 and p_text not in already_logged:
                # Calculate average confidence for this plate
                matching_confs = [conf for (pt, conf) in combined_plates if pt == p_text]
                avg_conf = sum(matching_confs) / len(matching_confs)

                # If above a threshold, log it as a "consensus" detection
                if avg_conf > 80:
                    log_entry = f"Consensus Plate: {p_text} (Avg Confidence: {avg_conf:.2f}%)\n"
                    print(log_entry.strip())
                    with open(log_file_path, "a") as log_file:
                        log_file.write(log_entry)

                    # Mark as logged so we don't spam if it keeps showing up
                    already_logged.add(p_text)

# Start the background processing thread
threading.Thread(target=process_frames, daemon=True).start()

try:
    while True:
        start_time = time.perf_counter()

        # Capture latest frame
        with lock:
            latest_frame = picam2.capture_array()

        # Print FPS (optional)
        end_time = time.perf_counter()
        fps = 1.0 / (end_time - start_time)
        print(f"Camera FPS: {fps:.2f}")

except KeyboardInterrupt:
    print("\nStopping...")
    alpr.unload()
    picam2.stop()
