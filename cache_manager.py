import time
from collections import OrderedDict


class CacheManager:


    def __init__(self, cache_enabled: bool = True, max_entries: int = None):
        self.cache_enabled = cache_enabled
        self.max_entries = max_entries
        self.cache = OrderedDict()
        self.stats = {
            "TOTAL": 0,
            "AD_BLOCK": 0,
            "SANCTION": 0,
            "CACHE": 0,
            "UPSTREAM": 0,
            "ERRORS": 0
        }
    def _get_remaining_ttl(self, entry: dict) -> int:
        elapsed = int(time.time() - entry["timestamp"])
        remaining = entry["ttl"] - elapsed
        return remaining

    def get(self, domain: str):
        if not self.cache_enabled:
            return None

        if domain not in self.cache:
            return None
        entry = self.cache[domain]
        remaining_ttl = self._get_remaining_ttl(entry)
        if remaining_ttl >= 1:
            return entry["ip"], remaining_ttl
        else:
            del self.cache[domain]
            return None