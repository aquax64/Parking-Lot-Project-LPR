#!/usr/bin/env python3
import sys
import time
import threading
# sys.path.append("/usr/local/lib")
import cv2
import numpy as np
# from picamera2 import Picamera2
# from openalpr import Alpr
import LPR

# File to store detected license plates
log_file_path = "detected_plates.txt"

encoded_image = cv2.imread("us-1.jpg")
        
# Ensure it's contiguous for safe memory passing
# encoded_image = np.ascontiguousarray(encoded_image, dtype=np.uint8)
        
# Recognize plates
result = LPR.testAlpr(encoded_image)
# log_entry = f"Detected Plate: {result.characters} (Confidence: {result.overall_confidence:.2f}%)\n"
log_entry = f"Detected Plate: {result.character} (Confidence: {result.confidence:.2f}%)\n"

print('Test finished')

# Print to console
print(log_entry.strip())

# Append to log file
with open(log_file_path, "a") as log_file:
    log_file.write(log_entry)
    print('Written to file')