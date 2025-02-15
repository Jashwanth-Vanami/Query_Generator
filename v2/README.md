# AI-Powered Database Query Generator

This package provides an AI-powered solution for generating optimized SQL queries from natural language descriptions. It supports multiple AI providers (OpenAI, DeepSea, Qwen) and different database types (MySQL, MSSQL).

## Features

- Natural language to SQL query generation
- Query optimization and validation
- Schema-aware query generation
- Query result caching
- Rate limiting for API calls
- Support for multiple AI providers
- Support for MySQL and MSSQL databases

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Here's a basic example of how to use the package:

```python
from v2.database_query import AIDatabaseQuery
from v2.ai_clients import OpenAIClient

# Initialize AI client
ai_client = OpenAIClient(api_key="your-api-key")

# Define your database schema
schema_config = {
    "users": ["id", "name", "email", "created_at"],
    "orders": ["id", "user_id", "total", "status", "created_at"],
}

# Initialize the query generator
query_gen = AIDatabaseQuery(
    mysql_conn_str="your-mysql-connection-string",
    mssql_conn_str="your-mssql-connection-string",
    ai_client=ai_client,
    schema_config=schema_config
)

# Generate a query
query = query_gen.generate_query(
    user_input="Find all users who made orders in the last 7 days",
    db_type="mysql"
)
print(query)
```

## Configuration

The package can be configured through environment variables:

```env
OPENAI_API_KEY=your-openai-api-key
DEEPSEA_API_KEY=your-deepsea-api-key
QWEN_API_KEY=your-qwen-api-key
MYSQL_CONN_STR=your-mysql-connection-string
MSSQL_CONN_STR=your-mssql-connection-string
```

## Module Structure

- `ai_clients.py`: AI provider implementations
- `database_query.py`: Main query generation class
- `query_optimizer.py`: Query optimization and validation
- `schema_manager.py`: Database schema management
- `query_cache.py`: Query caching functionality
- `rate_limiter.py`: API rate limiting

## Contributing

Feel free to submit issues and enhancement requests!
