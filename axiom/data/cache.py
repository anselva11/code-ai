"""Disk caching layer with timestamping, TTL, and hash-based keys."""
import os
import json
import time
import hashlib
from typing import Any, Optional

class DiskCache:
    def __init__(self, cache_dir: str = "data/cache", default_ttl_hours: float = 24.0):
        self.cache_dir = cache_dir
        self.default_ttl_hours = default_ttl_hours
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        hashed = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        safe_key = "".join(c for c in key if c.isalnum() or c in ("-", "_")).rstrip()[:24]
        filename = f"{safe_key}_{hashed}.json"
        return os.path.join(self.cache_dir, filename)

    def get(self, key: str, max_age_hours: Optional[float] = None) -> Optional[Any]:
        filepath = self._get_path(key)
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                payload = json.load(f)
            
            cached_at = payload.get("_cached_at", 0)
            ttl = max_age_hours if max_age_hours is not None else self.default_ttl_hours
            if (time.time() - cached_at) > (ttl * 3600):
                return None  # Expired
            
            return payload.get("data")
        except Exception:
            return None

    def set(self, key: str, data: Any) -> None:
        filepath = self._get_path(key)
        payload = {
            "_cached_at": time.time(),
            "_key": key,
            "data": data
        }
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
        except Exception:
            pass

    def clear(self) -> None:
        if os.path.exists(self.cache_dir):
            for fname in os.listdir(self.cache_dir):
                if fname.endswith(".json"):
                    try:
                        os.remove(os.path.join(self.cache_dir, fname))
                    except Exception:
                        pass
