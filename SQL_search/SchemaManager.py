from typing import Dict, List 
import logging  

class SchemaManager:
    """Manages schema context efficiently"""
    
    def __init__(self, full_schema: Dict[str, List[str]]):
        self.full_schema = full_schema
        self.usage_stats = {table: 0 for table in full_schema}
        
    def get_context(self, user_input: str) -> str:
        """Extract relevant schema parts based on input"""
        
        relevant_tables = [
            table for table, columns in self.full_schema.items()
            if any(word.lower() in table.lower() for word in user_input.split())
        ]
        
        context = []
        for table in relevant_tables[:3]:  # Limit to 3 tables
            context.append(f"{table}({', '.join(self.full_schema[table])})")
            self.usage_stats[table] += 1
            
        return ' '.join(context)