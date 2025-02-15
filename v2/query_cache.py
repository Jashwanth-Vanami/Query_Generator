"""
Module for caching generated SQL queries
"""

import hashlib
from typing import Optional

class QueryCache:
    """LRU cache for generated queries"""
    
    def __init__(self, max_size: int = 100):
        """
        Initialize the query cache
        
        Parameters:
        max_size (int): Maximum number of queries to cache
        """
        self.cache = {}
        self.max_size = max_size
        
    def _generate_key(self, user_input: str, db_type: str) -> str:
        """
        Generate a unique key for the cache
        
        Parameters:
        user_input (str): Natural language query description
        db_type (str): Database type
        
        Returns:
        str: Hash key for the cache
        """
        return hashlib.sha256(
            f"{user_input}-{db_type}".encode()
        ).hexdigest()
        
    def get(self, user_input: str, db_type: str) -> Optional[str]:
        """
        Get a cached query if it exists
        
        Parameters:
        user_input (str): Natural language query description
        db_type (str): Database type
        
        Returns:
        Optional[str]: Cached query if it exists, None otherwise
        """
        key = self._generate_key(user_input, db_type)
        return self.cache.get(key)
        
    def set(self, user_input: str, db_type: str, query: str) -> None:
        """
        Cache a query
        
        Parameters:
        user_input (str): Natural language query description
        db_type (str): Database type
        query (str): SQL query to cache
        """
        key = self._generate_key(user_input, db_type)
        if len(self.cache) >= self.max_size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = query
