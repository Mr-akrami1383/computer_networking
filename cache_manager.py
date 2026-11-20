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
        if not self.cache_enabled or ttl <= 0:
            return

        if self.max_entries is not None and self.max_entries <= 0:
            raise ValueError("max_entries must be positive")

        self._purge_expired()

        if domain in self.cache:
            del self.cache[domain]

        if self.max_entries is not None:
            while len(self.cache) >= self.max_entries:
                self.cache.popitem(last=False)

        self.cache[domain] = {
            "ip": ip,
            "ttl": ttl,
            "timestamp": time.time()
        }

    def format_cache_contents(self) -> str:
            if not self.cache_enabled:
                return "Cache is empty."

            self._purge_expired()

            if not self.cache:
                return "Cache is empty."

            lines = []
            for domain, entry in self.cache.items():
                rem_ttl = self._get_remaining_ttl(entry)
                if rem_ttl >= 1:
                    lines.append(f"{domain} | {entry['ip']} | {rem_ttl}")

            return "\n".join(lines) if lines else "Cache is empty."

    def record_decision(self, source: str, status: str):
            self.stats["TOTAL"] += 1

            if status in ("INVALID_INPUT", "SERVER_ERROR"):
                self.stats["ERRORS"] += 1
            elif source == "AD_BLOCK":
                self.stats["AD_BLOCK"] += 1
            elif source == "SANCTION":
                self.stats["SANCTION"] += 1
            elif source == "CACHE":
                self.stats["CACHE"] += 1
            elif source == "UPSTREAM":
                self.stats["UPSTREAM"] += 1

    def format_stats(self) -> str:
            s = self.stats
            return (
                f"Total: {s['TOTAL']} | AD_BLOCK: {s['AD_BLOCK']} |"
                f" SANCTION: {s['SANCTION']} | CACHE: {s['CACHE']} |"
                f" UPSTREAM: {s['UPSTREAM']} | ERRORS: {s['ERRORS']}"
            )