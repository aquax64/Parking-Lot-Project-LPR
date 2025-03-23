import cv2
import datetime
import os
from openalpr import Alpr

# Setup
SAVE_DIR = "captured_frames"
LOG_FILE = "detected_plates.txt"
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize OpenALPR
alpr = Alpr("us", "openalpr.conf", "runtime_data")
if not alpr.is_loaded():
    print("[ERROR] Failed to load OpenALPR. Check your config.")
    exit(1)

print("[INFO] OpenALPR loaded.")

# Initialize camera
print("[INFO] Starting camera...")
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 4608)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 2592)

ret, prev_frame = camera.read()
if not ret:
    print("[ERROR] Failed to read from camera.")
    camera.release()
    alpr.unload()
    exit(1)

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

print("[INFO] Camera warmed up. Watching for motion...")

frame_count = 0
motion_event_count = 0

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 50000:  # You can adjust this threshold
                print(f"[DEBUG] Motion detected. Contour area: {area}")
                motion_detected = True
                break

        if motion_detected:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"{SAVE_DIR}/motion_{timestamp}.jpg"
            cv2.imwrite(image_path, frame)
            print(f"[INFO] Motion frame saved: {image_path}")
            motion_event_count += 1

            # Run ALPR on saved image
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

        else:
            print(f"[DEBUG] No motion. Frame #{frame_count}")

        prev_gray = gray
        frame_count += 1

except KeyboardInterrupt:
    print("\n[INFO] Stopping...")

# Cleanup
camera.release()
alpr.unload()
cv2.destroyAllWindows()
print(f"[INFO] Session ended. Total frames: {frame_count}, Motion events: {motion_event_count}")
