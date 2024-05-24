import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, redis):
        self.fill_rate = 3 # Tokens per second
        self.capacity = 5  # Maximum tokens in the bucket        
        self.last_update_time = defaultdict(time.time)  
        self.redis = redis

    def allow_request(self, api_key):
        # Calculate the time elapsed since the last update for the specific API key
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time[api_key]

        tokens = self.redis.get(api_key)
        tokens += elapsed_time * self.fill_rate
        tokens = min(tokens, self.capacity)

        # Check if there are enough tokens for the request for the specific API key
        if tokens >= 1:
            tokens -= 1  # Consume one token
            self.redis.set(api_key, tokens)
            self.last_update_time[api_key] = current_time
            return True  
        else:
            return False
