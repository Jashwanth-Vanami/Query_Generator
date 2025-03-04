import os
import logging
import mysql.connector
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class SchemaGenerator:
    """
    Generates a schema dictionary dynamically by extracting tables, columns,
    and their relationships (foreign keys) from a connected MySQL database.
    """
    def __init__(self):
        self.mysql_conn = None
        self.schema = {}
        self.relationships = {}
        self.logger = logger
        self.db_config = {
            "host": os.getenv("MYSQL_HOST"),
            "port": int(os.getenv("MYSQL_PORT", 3306)),
            "user": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
            "database": os.getenv("MYSQL_DATABASE"),
        }
        self.logger.info("SchemaGenerator initialized with DB config: %s", self.db_config)

    def connect_mysql(self):
        try:
            self.mysql_conn = mysql.connector.connect(**self.db_config)
            self.logger.info("Connected to MySQL database.")
        except Exception as e:
            self.logger.error("Failed to connect to MySQL: %s", str(e))
            raise

    def fetch_schema(self):
        if not self.mysql_conn:
            self.connect_mysql()
        try:
            cursor = self.mysql_conn.cursor()
            cursor.execute("SHOW TABLES;")
            tables = [table[0] for table in cursor.fetchall()]
            self.logger.info("Tables found: %s", tables)
            for table in tables:
                cursor.execute(f"DESCRIBE {table};")
                columns = [column[0] for column in cursor.fetchall()]
                self.schema[table] = {"columns": columns, "primary_key": None}
                cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY';")
                primary_keys = [row[4] for row in cursor.fetchall()]
                if primary_keys:
                    self.schema[table]["primary_key"] = primary_keys
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL;
            """)
            foreign_keys = cursor.fetchall()
            for row in foreign_keys:
                table_name, column_name, constraint_name, ref_table, ref_column = row
                if table_name not in self.relationships:
                    self.relationships[table_name] = []
                self.relationships[table_name].append({
                    "column": column_name,
                    "references": {"table": ref_table, "column": ref_column}
                })
            cursor.close()
            self.logger.info("Database schema and relationships successfully fetched.")
            return {"tables": self.schema, "relationships": self.relationships}
        except Exception as e:
            self.logger.error("Failed to fetch schema: %s", str(e))
            raise

    def get_schema(self):
        if not self.schema:
            return self.fetch_schema()
        return {"tables": self.schema, "relationships": self.relationships}