import time
import logging
from functools import wraps

logger = logging.getLogger("myapp")

def timing(text=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            display_text = text if text else func.__name__
            logger.info(f"{display_text} execution time: {elapsed_time:.6f} seconds")
            return result
        return wrapper
    return decorator