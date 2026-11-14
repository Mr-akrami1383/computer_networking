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

    def _purge_expired(self):
        expired_domains = [
            domain for domain, entry in self.cache.items()
            if self._get_remaining_ttl(entry) < 1
        ]
        for domain in expired_domains:
            del self.cache[domain]

    def get(self, domain: str):
        if not self.cache_enabled:
            return None

        if domain not in self.cache:
            return None

        entry = self.cache[domain]
        remaining_ttl = self._get_remaining_ttl(entry)
        if remaining_ttl >= 1:
            return entry["ip"], remaining_ttl
        del self.cache[domain]
        return None

    def put(self, domain: str, ip: str, ttl: int):
        if not self.cache_enabled:
            return
        if ttl <= 0:
            return
        if domain in self.cache:
            del self.cache[domain]

            if self.max_entries is not None and self.max_entries > 0:
                self._purge_expired()
                while len(self.cache) >= self.max_entries:
                    self.cache.popitem(last=False)

        self.cache[domain] = {
            "ip": ip,
            "ttl": ttl,
            "timestamp": time.time()
        }

