Key features and best practices:

Database Management:

Separate methods for MySQL and SQL Server connections

Connection pooling and proper resource cleanup

Comprehensive error handling for database operations

AI Integration:

Token-optimized prompt engineering

Flexible architecture for multiple AI providers

Configurable model parameters

Security & Reliability:

Credential management through connection strings

Input validation and sanitization

Comprehensive logging

Code Quality:

Full PEP-8 compliance

Type hints and docstrings

Modular design for extensibility

Performance:

Context-aware schema handling

Token usage optimization

Efficient result serialization

Testing:

Mocked database connections

AI response validation

Error scenario testing




#Usage Example
# Initialize with your credentials
db_query = AIDatabaseQuery(
    mysql_conn_str="DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=localhost;...",
    mssql_conn_str="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;...",
    ai_provider='openai',
    ai_config={'api_key': 'your_openai_key'}
)

try:
    db_query.connect_mysql()
    schema_context = "users(id INT PRIMARY KEY, name VARCHAR(255))"
    
    # Generate query
    query = db_query.generate_query(
        user_input="Get all users with names starting with 'J'",
        db_type="mysql",
        schema_context=schema_context
    )
    
    # Execute query
    results = db_query.execute_query(query, "mysql")
    print(results)

except Exception as e:
    logger.error(f"Operation failed: {str(e)}")
finally:
    db_query.close_connections()