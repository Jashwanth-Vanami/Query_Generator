"""
A module for generating and executing SQL queries using AI models with proper error handling,
logging, and multi-database support.
"""

import logging
import json
import pyodbc
import openai
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIDatabaseQuery:
    """
    A class to generate and execute SQL queries using AI models for MySQL and SQL Server databases.
    
    Attributes:
        mysql_conn_str (str): MySQL connection string
        mssql_conn_str (str): SQL Server connection string
        ai_provider (str): AI service to use ('openai', 'deepsea', 'qwen')
        ai_config (dict): Configuration for AI service
    """
    
    def __init__(
        self,
        mysql_conn_str: str,
        mssql_conn_str: str,
        ai_provider: str = 'openai',
        ai_config: Optional[Dict[str, Any]] = None
    ):
        self.mysql_conn_str = mysql_conn_str
        self.mssql_conn_str = mssql_conn_str
        self.ai_provider = ai_provider
        self.ai_config = ai_config or {}
        self._validate_ai_config()
        
        self.mysql_conn = None
        self.mssql_conn = None

    def _validate_ai_config(self) -> None:
        """Validate AI configuration parameters."""
        if self.ai_provider == 'openai' and not self.ai_config.get('api_key'):
            raise ValueError("OpenAI requires an API key in ai_config")
        # Add validations for other AI providers here

    def connect_mysql(self) -> None:
        """Establish MySQL database connection with error handling."""
        try:
            self.mysql_conn = pyodbc.connect(self.mysql_conn_str)
            logger.info("Successfully connected to MySQL database")
        except pyodbc.Error as e:
            logger.error(f"MySQL connection failed: {str(e)}")
            raise

    def connect_mssql(self) -> None:
        """Establish Microsoft SQL Server database connection with error handling."""
        try:
            self.mssql_conn = pyodbc.connect(self.mssql_conn_str)
            logger.info("Successfully connected to MS SQL Server database")
        except pyodbc.Error as e:
            logger.error(f"MS SQL Server connection failed: {str(e)}")
            raise

    def generate_query(
        self,
        user_input: str,
        db_type: str,
        schema_context: str = "",
        max_tokens: int = 150
    ) -> str:
        """
        Generate SQL query using AI model with token optimization.
        
        Args:
            user_input: Natural language query description
            db_type: Database type ('mysql' or 'mssql')
            schema_context: Relevant schema information (optimized for tokens)
            max_tokens: Maximum tokens to use for AI response
            
        Returns:
            Generated SQL query string
        """
        prompt = f"""
        Generate a {db_type.upper()} SQL query for: {user_input}
        Schema Context: {schema_context}
        Respond ONLY with the SQL query, no explanations.
        Use standard syntax and best practices.
        """
        
        try:
            if self.ai_provider == 'openai':
                openai.api_key = self.ai_config['api_key']
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a SQL expert assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens
                )
                return response.choices[0].message['content'].strip()
            # Add implementations for other AI providers here
        except Exception as e:
            logger.error(f"AI query generation failed: {str(e)}")
            raise

    def execute_query(
        self,
        query: str,
        db_type: str
    ) -> str:
        """
        Execute SQL query and return results as JSON.
        
        Args:
            query: SQL query to execute
            db_type: Database type ('mysql' or 'mssql')
            
        Returns:
            JSON string of query results
        """
        conn = self.mysql_conn if db_type == 'mysql' else self.mssql_conn
        if not conn:
            raise ConnectionError(f"{db_type.upper()} connection not established")
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
                # Convert to JSON format
                columns = [column[0] for column in cursor.description]
                json_result = json.dumps(
                    [dict(zip(columns, row)) for row in results],
                    default=str
                )
                return json_result
        except pyodbc.Error as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON conversion failed: {str(e)}")
            raise

    def close_connections(self) -> None:
        """Close all database connections."""
        for conn in [self.mysql_conn, self.mssql_conn]:
            if conn:
                conn.close()
        logger.info("All database connections closed")



