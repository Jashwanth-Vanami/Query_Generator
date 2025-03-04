from dotenv import load_dotenv
import mysql.connector
# Load environment variables from .env file
load_dotenv()
import openai
import json
import time
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from functools import lru_cache
import logging  # ✅ Ensure logging is imported at the top

import os
from ai_clients import OpenAIClient
from database_query import AIDatabaseQuery
from SchemaGenerator import SchemaGenerator
import unittest
import logging
import unittest
from dotenv import load_dotenv
from ai_clients import OpenAIClient
from database_query import AIDatabaseQuery
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

class TestSystem(unittest.TestCase):
    """End-to-end test cases."""
    def test_full_flow(self):
        db = AIDatabaseQuery(
            mysql_conn_str="...",  # Placeholder connection string
            mssql_conn_str="...",  # Placeholder connection string
            ai_client=OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
        )
        try:
            sql_query = db.generate_query("Give me total online sales amount count", "mysql")
            print(f"Generated Query: {sql_query}")
            db.execute_mysql_query(sql_query)
        except Exception as e:
            print("Error occurred during query generation.")
            logger.error("MySQL Query Execution Failed: %s", e)
            self.fail("Test failed due to exception.")

if __name__ == "__main__":
    unittest.main()