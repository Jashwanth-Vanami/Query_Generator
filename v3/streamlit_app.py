import streamlit as st
import os
import re
import json
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# Import your modules
from ai_clients import OpenAIClient
from database_query import AIDatabaseQuery

st.title("SQL Query Generator and Executor")

# User prompt input
user_prompt_text = st.text_area("Enter your query prompt:")

if st.button("Generate and Execute Query"):
    try:
        st.info("Generating SQL query...")
        # Create an instance of your database query class.
        db = AIDatabaseQuery(
            mysql_conn_str="...", 
            mssql_conn_str="...", 
            ai_client=OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
        )
        
        # Generate the query and retrieve metrics (for MySQL in this example)
        result = db.generate_query(user_prompt_text, "mysql")
        generated_query = result["query"]
        latency = result["latency"]
        usage = result["usage"]
        
        st.subheader("Generated SQL Query:")
        st.code(generated_query, language="sql")
        
        # Display latency and token usage with cost information.
        if usage and "total_tokens" in usage:
            tokens = usage["total_tokens"]
            cost = tokens / 1000 * 0.002  # Example cost: $0.002 per 1,000 tokens
            st.write(f"**Latency:** {latency:.2f} seconds, **Cost:** ${cost:.5f} ({tokens} tokens)")
        else:
            st.write(f"**Latency:** {latency:.2f} seconds")
        
        st.info("Executing the query on the database...")
        if not db.mysql_conn:
            db.connect_mysql()
        
        # Extract SQL code from markdown if present.
        match = re.search(r"```sql\s*(.*?)\s*```", generated_query, re.DOTALL | re.IGNORECASE)
        if match:
            sql_code = match.group(1).strip()
        else:
            sql_code = generated_query.strip()
        
        # Execute the query and fetch results.
        cursor = db.mysql_conn.cursor()
        cursor.execute(sql_code)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        cursor.close()
        
        st.subheader("Query Results:")
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            # If there's only one column but multiple rows, transpose the DataFrame.
            if df.shape[1] == 1 and df.shape[0] > 1:
                df = df.T
            # Optionally, parse the table name from the SQL query.
            table_name_match = re.search(r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql_code, re.IGNORECASE)
            table_name = table_name_match.group(1) if table_name_match else "Query Results"
            st.write(f"**Table:** {table_name}")
            # Convert DataFrame to HTML without the index.
            html_table = df.to_html(index=False)
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.info("The query executed successfully but returned no results.")
    except Exception as e:
        st.error(f"An error occurred: {e}")