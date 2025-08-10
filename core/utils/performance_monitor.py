import logging
import time
from functools import wraps
from typing import Callable, Any


class PerformanceMonitor:
    """性能监控器 - 监控应用性能和组件执行时间"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_data = {}
        
    def monitor_function(self, func_name: str = None):
        """装饰器：监控函数执行时间"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    func_name_used = func_name or func.__name__
                    
                    # 记录性能数据
                    if func_name_used not in self.performance_data:
                        self.performance_data[func_name_used] = []
                    self.performance_data[func_name_used].append(execution_time)
                    
                    # 如果执行时间过长，记录警告
                    if execution_time > 0.1:  # 超过100ms记录警告
                        self.logger.warning(
                            f"函数 {func_name_used} 执行时间过长: {execution_time:.4f}s"
                        )
                    elif execution_time > 0.01:  # 超过10ms记录信息
                        self.logger.info(
                            f"函数 {func_name_used} 执行时间: {execution_time:.4f}s"
                        )
            return wrapper
        return decorator
    
    def get_performance_stats(self) -> dict:
        """获取性能统计信息"""
        stats = {}
        for func_name, times in self.performance_data.items():
            stats[func_name] = {
                'count': len(times),
                'total_time': sum(times),
                'avg_time': sum(times) / len(times) if times else 0,
                'max_time': max(times) if times else 0,
                'min_time': min(times) if times else 0
            }
        return stats
    
    def reset_performance_data(self):
        """重置性能数据"""
        self.performance_data.clear()
    
    def log_performance_summary(self):
        """记录性能摘要"""
        stats = self.get_performance_stats()
        if stats:
            self.logger.info("=== 性能监控摘要 ===")
            for func_name, data in stats.items():
                self.logger.info(
                    f"{func_name}: "
                    f"平均{data['avg_time']:.4f}s, "
                    f"总计{data['total_time']:.4f}s, "
                    f"次数{data['count']}"
                )


# 创建全局性能监控实例
performance_monitor = PerformanceMonitor()
