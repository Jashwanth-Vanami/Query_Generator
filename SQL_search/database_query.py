import os
import re
import json
import logging
import mysql.connector
from ai_clients import AIClient
from RateLimiter import RateLimiter
from SchemaGenerator import SchemaGenerator
from QueryCache import QueryCache
from QueryOptimizer import QueryOptimizer
from prompttemplate import MySQLPromptTemplate, MSSQLPromptTemplate, PostgreSQLPromptTemplate
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class AIDatabaseQuery:
    """
    Main class handling SQL generation and execution.
    """
    def __init__(self, mysql_conn_str: str, mssql_conn_str: str, ai_client: AIClient,
                 cache_size: int = 100, rate_limit: int = 30):
        self.mysql_conn_str = mysql_conn_str
        self.mssql_conn_str = mssql_conn_str
        self.ai_client = ai_client
        self.query_cache = QueryCache(cache_size)
        self.rate_limiter = RateLimiter(rate_limit)
        self.optimizer = QueryOptimizer()
        self.mysql_conn = None
        self.mssql_conn = None
        logger.info("AIDatabaseQuery initialized.")

    def connect_mysql(self):
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
            logger.error("Failed to connect to MySQL: %s", str(e))
            raise

    def execute_mysql_query(self, query: str):
        """
        Executes a query on the MySQL database.
        Extracts SQL from a markdown code block if present.
        """
        if not self.mysql_conn:
            self.connect_mysql()
        try:
            match = re.search(r"```sql\s*(.*?)\s*```", query, re.DOTALL | re.IGNORECASE)
            if match:
                sql_code = match.group(1).strip()
            else:
                sql_code = query.strip()
            logger.info("Executing SQL query: %s", sql_code)
            cursor = self.mysql_conn.cursor()
            cursor.execute(sql_code)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            cursor.close()
        except Exception as e:
            logger.error("Failed to execute MySQL query: %s", str(e))
            raise

    @RateLimiter(30)
    def generate_query(self, user_input: str, db_type: str, max_tokens: int = 150) -> dict:
        """
        Generates a query with caching and rate limiting.
        Returns a dictionary with keys:
          - "query": the optimized SQL query (str)
          - "latency": latency in seconds (float)
          - "usage": token usage details (dict)
        """
        schema_generator = SchemaGenerator()
        schema_config = schema_generator.get_schema()
        #schema_str = json.dumps(schema_config, indent=2)
        #logger.info("Schema Config: %s", schema_str)
        if cached_query := self.query_cache.get(user_input, db_type):
            logger.info("Returning cached query")
            # For simplicity, assume cached queries have no latency/usage metrics.
            return {"query": cached_query, "latency": None, "usage": None}
        if db_type.lower() == "mysql":
            prompt_template = MySQLPromptTemplate()
        elif db_type.lower() == "mssql":
            prompt_template = MSSQLPromptTemplate()
        elif db_type.lower() == "postgresql":
            prompt_template = PostgreSQLPromptTemplate()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        system_msg = prompt_template.system_prompt()
        user_msg = prompt_template.user_prompt(user_input, schema_config)
        try:
            result = self.ai_client.generate_query(user_msg, max_tokens, system_prompt=system_msg)
            generated_query = result["query"]
            latency = result["latency"]
            usage = result["usage"]
            optimized_query = self.optimizer.optimize(generated_query, db_type)
            if not self.optimizer.validate(optimized_query):
                raise ValueError("Query validation failed")
            self.query_cache.set(user_input, db_type, optimized_query)
            logger.info("Generated and optimized query: %s", optimized_query)
            return {"query": optimized_query, "latency": latency, "usage": usage}
        except Exception as e:
            logger.error("Query generation failed: %s", str(e))
            raise