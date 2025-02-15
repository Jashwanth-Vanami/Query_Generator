"""
Module for AI-powered SQL query generation with MySQL database integration
"""
from dotenv import load_dotenv
import mysql.connector
import os

# Load environment variables from .env file
load_dotenv()

import openai
import logging
import unittest
import json
import time
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from functools import lru_cache
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------- AI Client Interfaces --------------------
class AIClient(ABC):
    """Abstract base class for AI clients"""
    
    @abstractmethod
    def generate_query(self, prompt: str, max_tokens: int) -> str: 
        pass

class OpenAIClient(AIClient):
    """OpenAI API implementation"""
    
    def __init__(self, api_key: str = None):
        import openai
        # Prioritize environment variable, fallback to passed key
        openai.api_key = os.getenv("OPENAI_API_KEY", api_key)
        if not openai.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env or pass as an argument.")
        print(f"OpenAI API Key loaded: {openai.api_key[:5]}...")  # Debug print
    
    def generate_query(self, prompt: str, max_tokens: int) -> str:
        """Generate SQL query using OpenAI API"""
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise   

# -------------------- Query Optimization --------------------
class QueryOptimizer:
    """Handles query optimization and validation"""
    
    def __init__(self):
        self.prohibited_patterns = [
            'DROP', 'DELETE', 'TRUNCATE', 
            'GRANT', 'REVOKE', 'ALTER'
        ]
        
    def optimize(self, query: str, db_type: str) -> str:
        """Basic query optimization"""
        return query.strip(';') + ';'  # Ensure proper termination
        
    def validate(self, query: str) -> bool:
        """Check for prohibited patterns"""
        return not any(
            pattern in query.upper() 
            for pattern in self.prohibited_patterns
        )

# -------------------- Schema Management --------------------
class SchemaManager:
    """Manages schema context efficiently"""
    
    def __init__(self, full_schema: Dict[str, List[str]]):
        self.full_schema = full_schema
        self.usage_stats = {table: 0 for table in full_schema}
        
    def get_context(self, user_input: str) -> str:
        """Extract relevant schema parts based on input"""
        relevant_tables = [
            table for table, columns in self.full_schema.items()
            if any(word.lower() in table.lower() for word in user_input.split())
        ]
        
        context = []
        for table in relevant_tables[:3]:  # Limit to 3 tables
            context.append(f"{table}({', '.join(self.full_schema[table])})")
            self.usage_stats[table] += 1
            
        return ' '.join(context)

# -------------------- Cache Management --------------------
class QueryCache:
    """LRU cache for generated queries"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        
    def _generate_key(self, user_input: str, db_type: str) -> str:
        return hashlib.sha256(f"{user_input}-{db_type}".encode()).hexdigest()
        
    def get(self, user_input: str, db_type: str) -> Optional[str]:
        key = self._generate_key(user_input, db_type)
        return self.cache.get(key)
        
    def set(self, user_input: str, db_type: str, query: str) -> None:
        key = self._generate_key(user_input, db_type)
        if len(self.cache) >= self.max_size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = query

# -------------------- Rate Limiting --------------------
class RateLimiter:
    """Enforces rate limits for API calls"""
    
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.timestamps = []
        
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            current_time = time.time()
            self.timestamps = [t for t in self.timestamps if t > current_time - 60]
            
            if len(self.timestamps) >= self.calls_per_minute:
                sleep_time = 60 - (current_time - self.timestamps[0])
                time.sleep(sleep_time)
                
            self.timestamps.append(current_time)
            return func(*args, **kwargs)
        return wrapper

# -------------------- Main Database Class --------------------
class AIDatabaseQuery:
    """Main class handling SQL generation and execution"""
    
    def __init__(
        self,
        mysql_conn_str: str,
        mssql_conn_str: str,
        ai_client: AIClient,
        schema_config: Dict[str, List[str]],
        cache_size: int = 100,
        rate_limit: int = 30
    ):
        load_dotenv()  # Load .env file
        self.mysql_conn_str = mysql_conn_str
        self.mssql_conn_str = mssql_conn_str
        self.ai_client = ai_client
        self.schema_manager = SchemaManager(schema_config)
        self.query_cache = QueryCache(cache_size)
        self.rate_limiter = RateLimiter(rate_limit)
        self.optimizer = QueryOptimizer()
        
        self.mysql_conn = None
        self.mssql_conn = None

    def connect_mysql(self):
        """Establish a connection to the MySQL database using .env variables."""
        try:
            self.mysql_conn = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST'),
                port=os.getenv('MYSQL_PORT'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=os.getenv('MYSQL_DATABASE')
            )
            logger.info("Connected to MySQL database.")
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {str(e)}")
            raise

    def execute_mysql_query(self, query: str):
        """Execute a query on the MySQL database."""
        if not self.mysql_conn:
            self.connect_mysql()
        try:
            # Remove Markdown-style code block delimiters (e.g., ```sql ... ```)
            query = query.replace("```sql", "").replace("```", "").strip()

            cursor = self.mysql_conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            cursor.close()
        except Exception as e:
            logger.error(f"Failed to execute MySQL query: {str(e)}")
            raise

    @RateLimiter(30)
    def generate_query(self, user_input: str, db_type: str, max_tokens: int = 150) -> str:
        """Generate SQL query with caching and rate limiting"""
        if cached_query := self.query_cache.get(user_input, db_type):
            logger.info("Returning cached query")
            return cached_query
            
        schema_context = self.schema_manager.get_context(user_input)
        prompt = f"""
        Generate {db_type.upper()} query for: {user_input}
        Schema: {schema_context}
        Respond ONLY with valid SQL, no explanations.
        Use proper indexing and optimization.
        """
        
        try:
            query = self.ai_client.generate_query(prompt, max_tokens)
            optimized_query = self.optimizer.optimize(query, db_type)
            
            if not self.optimizer.validate(optimized_query):
                raise ValueError("Query validation failed")
                
            self.query_cache.set(user_input, db_type, optimized_query)
            return optimized_query
            
        except Exception as e:
            logger.error(f"Query generation failed: {str(e)}")
            raise

# -------------------- Testing --------------------
class TestSystem(unittest.TestCase):
    """End-to-end test cases"""
    
    def test_full_flow(self):
        schema_config = {
            "users": ["id", "name", "email"],
            "orders": ["order_id", "user_id", "amount"]
        }
        
        db = AIDatabaseQuery(
            mysql_conn_str="...",
            mssql_conn_str="...",
            ai_client=OpenAIClient(api_key=os.getenv("OPENAI_API_KEY")),
            schema_config=schema_config
        )
        
        try:
            sql_query = db.generate_query("Get top 5 users by email", "mysql")a
            print(f"Generated Query: {sql_query}")
            db.execute_mysql_query(sql_query)
        except Exception as e:
            logger.error(f"MySQL Query Execution Failed: {e}")

if __name__ == "__main__":
    unittest.main()