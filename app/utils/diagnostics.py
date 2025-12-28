import time
import psutil
import logging
import platform
from functools import wraps
from pathlib import Path

# Setup unified logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / "slam.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SLAM_Core")

def profile_performance(func):
    """Decorator to measure execution time and memory usage."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        start_mem = psutil.Process().memory_info().rss / (1024 * 1024)
        
        result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        end_mem = psutil.Process().memory_info().rss / (1024 * 1024)
        
        logger.info(f"FUNC: {func.__name__} | TIME: {end_time-start_time:.4f}s | MEM: {end_mem-start_mem:+.2f}MB")
        return result
    return wrapper

class SystemHealth:
    @staticmethod
    def get_report():
        return {
            "os": platform.system(),
            "cpu_usage": psutil.cpu_percent(),
            "ram_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "threads": psutil.Process().num_threads()
        }
