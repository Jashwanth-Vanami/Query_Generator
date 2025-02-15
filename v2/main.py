# Initialize enhanced system
schema_versions = SchemaVersioning()
schema_versions.add_version("1.0", {"users": ["id", "name"]})
schema_versions.add_version("2.0", {"users": ["id", "name", "email"]})

db = EnhancedAIDatabaseQuery(
    mysql_conn_str="...",
    mssql_conn_str="...",
    ai_client=EnhancedOpenAIClient("openai_key"),
    schema_config=schema_versions.get_current_schema()
)

# Generate and explain query
query = db.generate_query("Get users with Gmail addresses", "mysql")
explanation = db.explain_query(query)

# Check costs
print(f"Total cost: ${CostTracker().get_cost('openai')}")

# Analyze complexity
analysis = db.complexity_analyzer.analyze(query)
print(f"Query risk level: {analysis['risk_level']}")