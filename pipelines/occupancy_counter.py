# =============================
# pipelines/occupancy_counter.py
# =============================
import time
from collections import defaultdict
from typing import Dict, List


class OccupancyCounter:
    """Deduplicate plates and emit clean events for the backend.

    The Pi *does not* maintain a local running count—aggregation happens
    server‑side.  We only ensure that the same plate isn’t sent twice within
    a short window to avoid double‑counting when a car inches forward.
    """

    def __init__(self, lots_cfg: dict):
        self.cache: Dict[str, float] = defaultdict(float)  # plate → last_seen_ts
        self.dedup_sec = lots_cfg.get("dedup_seconds", 3)
        self.lot_id = lots_cfg.get("lot_id", "lot‑1")

    def filter_new_events(self, plates: List[dict]) -> List[dict]:
        """Return a list of *new* plate events that should be uploaded."""
        now = time.time()
        new_events: List[dict] = []
        for p in plates:
            plate = p["plate"]
            if now - self.cache[plate] < self.dedup_sec:
                continue  # duplicate within debounce window
            self.cache[plate] = now
            new_events.append({
                "lot": self.lot_id,
                "plate": plate,
                "ts": int(now),
                "conf": p["confidence"],
            })
        return new_events
import time
# =============================
from collections import defaultdict
from typing import Dict, List


class OccupancyCounter:
    """Simple dedup + increment/decrement logic."""

    def __init__(self, lots_cfg: dict):
        self.cache: Dict[str, float] = defaultdict(float)  # plate -> last_seen_ts
        self.dedup_sec = lots_cfg.get("dedup_seconds", 3)
        self.lot_id = lots_cfg.get("lot_id", "lot‑1")
        self.count = 0

    def update(self, plates: List[dict]):
        now = time.time()
        for p in plates:
            plate = p["plate"]
            if now - self.cache[plate] < self.dedup_sec:
                continue  # skip duplicate
            self.cache[plate] = now
            self.count += 1  # naive increment; add entry/exit logic later
            print(f"[{self.lot_id}] Count => {self.count} (plate {plate})")