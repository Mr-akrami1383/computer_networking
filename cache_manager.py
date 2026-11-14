import time
from collections import OrderedDict


class CacheManager:


    def __init__(self, cache_enabled: bool = True, max_entries: int = None):
        self.cache_enabled = cache_enabled
        self.max_entries = max_entries
        self.cache = OrderedDict()