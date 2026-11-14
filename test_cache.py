import time
from cache_manager import CacheManager


def run_tests():
    cm = CacheManager(cache_enabled=True, max_entries=2)
    cm.put("normal.example.net", "198.51.100.7", 3)
    res = cm.get("normal.example.net")
    assert res is not None and res[0] == "198.51.100.7", "Cache Hit failed!"
    print("Test Hit & B3:\n", cm.format_cache_contents())

    cm.put("site2.example.net", "1.1.1.1", 10)
    cm.put("site3.example.net", "2.2.2.2", 10)
    assert cm.get("normal.example.net") is None, "FIFO eviction failed!"

    cm_exp = CacheManager(cache_enabled=True)
    cm_exp.put("short.example.net", "9.9.9.9", 1)
    time.sleep(1.2)
    assert cm_exp.get("short.example.net") is None, "TTL expiration failed!"

    cm.record_decision("AD_BLOCK", "OK")
    cm.record_decision("UPSTREAM", "OK")
    cm.record_decision("NONE", "INVALID_INPUT")
    print("Test Stats (B1):\n", cm.format_stats())
    print("All cache module tests passed successfully!")


if __name__ == "__main__":
    run_tests()