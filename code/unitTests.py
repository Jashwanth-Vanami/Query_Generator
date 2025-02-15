
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
            ai_client=OpenAIClient(api_key="test"),
            schema_config=schema_config
        )
        
        # First request (cold cache)
        query1 = db.generate_query("Get active users", "mysql")
        
        # Second request (cached)
        query2 = db.generate_query("Get active users", "mysql")
        self.assertEqual(query1, query2)
        
        # Test query validation
        with self.assertRaises(ValueError):
            db.generate_query("Delete all users", "mysql")

if __name__ == "__main__":
    unittest.main()