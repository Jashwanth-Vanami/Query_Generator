"""
Example usage of the AI Database Query Generator
"""

import os
from dotenv import load_dotenv
from ai_clients import OpenAIClient
from database_query import AIDatabaseQuery

# Load environment variables
load_dotenv()

def main():
    # Initialize AI client with API key from environment
    ai_client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))

    # Example schema configuration
    schema_config = {
        "users": ["id", "name", "email", "created_at"],
        "orders": ["id", "user_id", "total", "status", "created_at"],
        "products": ["id", "name", "price", "stock"],
        "order_items": ["id", "order_id", "product_id", "quantity", "price"]
    }

    # Initialize query generator
    query_gen = AIDatabaseQuery(
        mysql_conn_str=os.getenv("MYSQL_CONN_STR"),
        mssql_conn_str=os.getenv("MSSQL_CONN_STR"),
        ai_client=ai_client,
        schema_config=schema_config
    )

    # Example queries
    example_queries = [
        "Find all users who spent more than $1000 in total",
        "List the top 5 products by sales volume",
        "Get users who haven't made any orders in the last 30 days",
        "Calculate the average order value per user"
    ]

    # Generate queries for each example
    for user_input in example_queries:
        print(f"\nInput: {user_input}")
        try:
            query = query_gen.generate_query(
                user_input=user_input,
                db_type="mysql"
            )
            print(f"Generated Query:\n{query}\n")
        except Exception as e:
            print(f"Error generating query: {str(e)}\n")

if __name__ == "__main__":
    main()
