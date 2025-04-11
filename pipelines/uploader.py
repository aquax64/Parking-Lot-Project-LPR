# =============================
# pipelines/uploader.py
# =============================
import json
import queue
import threading
import time

import requests


class Uploader(threading.Thread):
    def __init__(self, api_url: str, batch_size: int = 10, flush_sec: int = 5):
        super().__init__(daemon=True)
        self.api_url = api_url
        self.batch_size = batch_size
        self.flush_sec = flush_sec
        self.q: "queue.Queue[dict]" = queue.Queue()

    def enqueue(self, event: dict):
        self.q.put(event)

    def run(self):
        buffer: list[dict] = []
        last_flush = time.time()
        while True:
            try:
                item = self.q.get(timeout=1)
                buffer.append(item)
            except queue.Empty:
                pass
            if buffer and (len(buffer) >= self.batch_size or time.time() - last_flush >= self.flush_sec):
                try:
                    requests.post(self.api_url, json=buffer, timeout=3)
                    buffer.clear()
                    last_flush = time.time()
                except requests.RequestException as exc:
                    print(f"Upload failed: {exc}")