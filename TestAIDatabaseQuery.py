# Test cases
import unittest
from unittest.mock import patch, MagicMock

class TestAIDatabaseQuery(unittest.TestCase):
    """Unit tests for AIDatabaseQuery class"""
    
    def setUp(self):
        self.mock_ai_config = {'api_key': 'test_key'}
        self.db = AIDatabaseQuery(
            mysql_conn_str="DRIVER={MySQL};...",
            mssql_conn_str="DRIVER={SQL Server};...",
            ai_provider='openai',
            ai_config=self.mock_ai_config
        )
        
    @patch('pyodbc.connect')
    def test_mysql_connection(self, mock_connect):
        mock_connect.return_value = MagicMock()
        self.db.connect_mysql()
        self.assertIsNotNone(self.db.mysql_conn)
        
    @patch('openai.ChatCompletion.create')
    def test_query_generation(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message={'content': 'SELECT * FROM users'})]
        mock_openai.return_value = mock_response
        
        query = self.db.generate_query(
            user_input="Get all users",
            db_type="mysql",
            schema_context="users(id, name, email)"
        )
        self.assertEqual(query, "SELECT * FROM users")
        
    @patch('pyodbc.Cursor')
    def test_query_execution(self, mock_cursor):
        mock_conn = MagicMock()
        self.db.mysql_conn = mock_conn
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'John'), (2, 'Jane')]
        
        results = self.db.execute_query("SELECT * FROM users", "mysql")
        expected = '[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]'
        self.assertEqual(json.loads(results), json.loads(expected))
        
    def tearDown(self):
        self.db.close_connections()

if __name__ == "__main__":
    unittest.main()