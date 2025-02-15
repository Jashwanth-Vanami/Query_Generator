

# -------------------- Query Optimization --------------------
class QueryOptimizer:
    """Handles query optimization and validation"""
    
    def __init__(self):
        self.prohibited_patterns = [
            'DROP', 'DELETE', 'TRUNCATE', 
            'GRANT', 'REVOKE', 'ALTER'
        ]
        
    def optimize(self, query: str, db_type: str) -> str:
        """Basic query optimization"""
        # Add database-specific optimizations
        return query.strip(';') + ';'  # Ensure proper termination
        
    def validate(self, query: str) -> bool:
        """Check for prohibited patterns"""
        return not any(
            pattern in query.upper() 
            for pattern in self.prohibited_patterns
        )