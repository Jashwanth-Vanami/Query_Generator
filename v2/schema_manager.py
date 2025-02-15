"""
Module for managing database schema context
"""

from typing import Dict, List

class SchemaManager:
    """Manages schema context efficiently"""
    
    def __init__(self, full_schema: Dict[str, List[str]]):
        """
        Initialize the schema manager
        
        Parameters:
        full_schema (Dict[str, List[str]]): Dictionary mapping table names to column lists
        """
        self.full_schema = full_schema
        self.usage_stats = {table: 0 for table in full_schema}
        
    def get_context(self, user_input: str) -> str:
        """
        Extract relevant schema parts based on input
        
        Parameters:
        user_input (str): Natural language query description
        
        Returns:
        str: Relevant schema context as a string
        """
        # Simple keyword matching - can be enhanced with NLP
        relevant_tables = [
            table for table, columns in self.full_schema.items()
            if any(word.lower() in table.lower() 
                   for word in user_input.split())
        ]
        
        context = []
        for table in relevant_tables[:3]:  # Limit to 3 tables
            context.append(f"{table}({', '.join(self.full_schema[table])})")
            self.usage_stats[table] += 1
            
        return ' '.join(context)
