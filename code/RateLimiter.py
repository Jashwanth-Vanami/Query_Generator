

# -------------------- Rate Limiting --------------------
class RateLimiter:
    """Enforces rate limits for API calls"""
    
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.timestamps = []
        
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            current_time = time.time()
            self.timestamps = [
                t for t in self.timestamps 
                if t > current_time - 60
            ]
            
            if len(self.timestamps) >= self.calls_per_minute:
                sleep_time = 60 - (current_time - self.timestamps[0])
                time.sleep(sleep_time)
                
            self.timestamps.append(current_time)
            return func(*args, **kwargs)
        return wrapper
