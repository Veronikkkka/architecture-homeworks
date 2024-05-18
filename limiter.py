import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.fill_rate = 3 # Tokens per second
        self.capacity = 5  # Maximum tokens in the bucket
        self.tokens = defaultdict(lambda: 5)  # Dictionary to store tokens for each API key
        self.last_update_time = defaultdict(time.time)  # Dictionary to store last update time for each API key

    def allow_request(self, api_key):
        # Calculate the time elapsed since the last update for the specific API key
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time[api_key]

        # Add tokens to the bucket for the specific API key based on the fill rate and elapsed time
        self.tokens[api_key] += elapsed_time * self.fill_rate
        self.tokens[api_key] = min(self.tokens[api_key], self.capacity)  # Ensure tokens don't exceed capacity

        # Check if there are enough tokens for the request for the specific API key
        if self.tokens[api_key] >= 1:
            self.tokens[api_key] -= 1  # Consume one token
            self.last_update_time[api_key] = current_time  # Update the last update time for the specific API key
            return True  # Request is allowed
        else:
            return False  # Request is rejected due to lack of tokens for the specific API key
