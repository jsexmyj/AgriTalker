import time
import functools
from typing import Callable

def timeit_logger(logger):
    def decorator(func:Callable):
        """装饰器：用于计算函数运行时间"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()  # 记录开始时间
            result = func(*args, **kwargs)  # 执行函数
            end_time = time.time()  # 记录结束时间
            duration = end_time - start_time
            logger.info(f"函数 '{func.__name__}' 运行时间: {duration:.4f} 秒")
            return result
        return wrapper
    return decorator
