import hashlib
import logging
from typing import Optional
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class QueryCache:
    """LRU cache for generated queries"""

    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        logger.info("QueryCache initialized with max_size %d", max_size)

    def _generate_key(self, user_input: str, db_type: str) -> str:
        key = hashlib.sha256(f"{user_input}-{db_type}".encode()).hexdigest()
        logger.debug(f"Generated cache key: {key} for input: {user_input} and db_type: {db_type}")
        return key

    def get(self, user_input: str, db_type: str) -> Optional[str]:
        key = self._generate_key(user_input, db_type)
        result = self.cache.get(key)
        logger.info("Cache get for key %s: %s", key, result)
        return result

    def set(self, user_input: str, db_type: str, query: str) -> None:
        key = self._generate_key(user_input, db_type)
        if len(self.cache) >= self.max_size:
            evicted_key = next(iter(self.cache))
            logger.warning("Cache max size reached. Evicting key: %s", evicted_key)
            self.cache.pop(evicted_key)
        self.cache[key] = query
        logger.info("Cache set for key %s with query: %s", key, query)