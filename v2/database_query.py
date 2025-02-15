"""
Main module for AI-powered database query generation
"""

import logging
from typing import Dict, List, Optional
import pyodbc

from .ai_clients import AIClient
from .query_cache import QueryCache
from .rate_limiter import RateLimiter
from .schema_manager import SchemaManager
from .query_optimizer import QueryOptimizer

logger = logging.getLogger(__name__)

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
        """
        Initialize the database query class
        
        Parameters:
        mysql_conn_str (str): MySQL connection string
        mssql_conn_str (str): SQL Server connection string
        ai_client (AIClient): AI service client for generating queries
        schema_config (Dict[str, List[str]]): Schema configuration for the database
        cache_size (int): Maximum size of the query cache
        rate_limit (int): Rate limit for AI API calls
        """
        self.mysql_conn_str = mysql_conn_str
        self.mssql_conn_str = mssql_conn_str
        self.ai_client = ai_client
        self.schema_manager = SchemaManager(schema_config)
        self.query_cache = QueryCache(cache_size)
        self.rate_limiter = RateLimiter(rate_limit)
        self.optimizer = QueryOptimizer()
        
        self.mysql_conn = None
        self.mssql_conn = None

    @RateLimiter(30)
    def generate_query(
        self,
        user_input: str,
        db_type: str,
        max_tokens: int = 150
    ) -> str:
        """
        Generate SQL query with caching and rate limiting
        
        Parameters:
        user_input (str): Natural language query description
        db_type (str): Database type ('mysql' or 'mssql')
        max_tokens (int): Maximum tokens to use for AI response
        
        Returns:
        str: Generated SQL query string
        """
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
