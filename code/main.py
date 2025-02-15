# Example initialization with Qwen AI
qwen_client = QwenClient(api_key="qwen_api_key")
db = AIDatabaseQuery(
    mysql_conn_str="...",
    mssql_conn_str="...",
    ai_client=qwen_client,
    schema_config=your_schema
)