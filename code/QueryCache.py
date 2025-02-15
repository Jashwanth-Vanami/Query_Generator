


# -------------------- Cache Management --------------------
class QueryCache:
    """LRU cache for generated queries"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        
    def _generate_key(self, user_input: str, db_type: str) -> str:
        return hashlib.sha256(
            f"{user_input}-{db_type}".encode()
        ).hexdigest()
        
    def get(self, user_input: str, db_type: str) -> Optional[str]:
        key = self._generate_key(user_input, db_type)
        return self.cache.get(key)
        
    def set(self, user_input: str, db_type: str, query: str) -> None:
        key = self._generate_key(user_input, db_type)
        if len(self.cache) >= self.max_size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = query