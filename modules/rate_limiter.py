import time
import threading
from collections import deque


# ============================================================
# Gemini Rate Limiter
# ============================================================

MAX_REQUESTS = 5
TIME_WINDOW = 60


class GeminiRateLimiter:
    """
    Global in-memory rate limiter for Gemini API requests.

    Allows a maximum of 5 requests within a rolling
    60-second window.
    """

    def __init__(
        self,
        max_requests=MAX_REQUESTS,
        time_window=TIME_WINDOW
    ):

        self.max_requests = max_requests
        self.time_window = time_window

        self.request_times = deque()

        self.lock = threading.Lock()

    def allow_request(self):
        """
        Check whether a new Gemini request is allowed.

        Returns:
            (True, remaining_requests)
            (False, 0)
        """

        current_time = time.time()

        with self.lock:

            # Remove requests older than 60 seconds
            while self.request_times:

                oldest_request = self.request_times[0]

                if (
                    current_time - oldest_request
                    >= self.time_window
                ):
                    self.request_times.popleft()

                else:
                    break

            # Rate limit reached
            if len(self.request_times) >= self.max_requests:

                return False, 0

            # Register this request
            self.request_times.append(current_time)

            remaining_requests = (
                self.max_requests
                - len(self.request_times)
            )

            return True, remaining_requests


# One shared limiter for the entire application
gemini_rate_limiter = GeminiRateLimiter()