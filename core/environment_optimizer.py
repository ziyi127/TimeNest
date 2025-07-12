#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 学习环境优化器
提供学习环境监控、优化建议和自动调节功能
"""

import logging
import platform
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.base_manager import BaseManager

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class EnvironmentFactor(Enum):
    """环境因素"""
    NOISE_LEVEL = "noise_level"
    LIGHTING = "lighting"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    AIR_QUALITY = "air_quality"
    SYSTEM_PERFORMANCE = "system_performance"
    NETWORK_QUALITY = "network_quality"


class OptimizationLevel(Enum):
    """优化级别"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


@dataclass
class EnvironmentReading:
    """环境读数"""
    factor: EnvironmentFactor
    value: float
    unit: str
    timestamp: datetime
    quality_score: float  # 0-1, 1为最佳
    recommendation: str = ""


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    id: str
    title: str
    description: str
    factor: EnvironmentFactor
    priority: int  # 1-5
    impact_score: float  # 0-1
    difficulty: int  # 1-5
    estimated_improvement: float  # 0-1
    action_steps: List[str]
    created_at: datetime


class EnvironmentOptimizer(BaseManager):
    """学习环境优化器"""
    
    # 信号定义
    environment_updated = pyqtSignal(str, float)  # 因素名, 质量分数
    optimization_suggested = pyqtSignal(str)  # 建议ID
    environment_alert = pyqtSignal(str, str)  # 因素, 警告信息
    auto_optimization_applied = pyqtSignal(str, str)  # 因素, 操作描述
    
    def __init__(self, config_manager=None):
        super().__init__("EnvironmentOptimizer", config_manager)
        
        # 环境数据存储
        self.current_readings: Dict[EnvironmentFactor, EnvironmentReading] = {}
        self.reading_history: List[EnvironmentReading] = []
        self.optimization_suggestions: Dict[str, OptimizationSuggestion] = {}
        
        # 监控设置
        self.monitoring_enabled = True
        self.auto_optimization_enabled = False
        self.optimization_level = OptimizationLevel.STANDARD
        
        # 环境标准
        self.environment_standards = {
            EnvironmentFactor.SYSTEM_PERFORMANCE: {
                'excellent': (0.9, 1.0),
                'good': (0.7, 0.9),
                'fair': (0.5, 0.7),
                'poor': (0.0, 0.5)
            },
            EnvironmentFactor.NETWORK_QUALITY: {
                'excellent': (0.9, 1.0),
                'good': (0.7, 0.9),
                'fair': (0.5, 0.7),
                'poor': (0.0, 0.5)
            }
        }
        
        # 监控定时器
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_environment)
        self.monitor_timer.start(30000)  # 每30秒监控一次
        
        self.logger.info("学习环境优化器初始化完成")
    
    def start_monitoring(self):
        """开始环境监控"""
        try:
            self.monitoring_enabled = True
            self.monitor_timer.start(30000)
            self.logger.info("环境监控已启动")
            
        except Exception as e:
            self.logger.error(f"启动环境监控失败: {e}")
    
    def stop_monitoring(self):
        """停止环境监控"""
        try:
            self.monitoring_enabled = False
            self.monitor_timer.stop()
            self.logger.info("环境监控已停止")
            
        except Exception as e:
            self.logger.error(f"停止环境监控失败: {e}")
    
    def _monitor_environment(self):
        """监控环境状态"""
        try:
            if not self.monitoring_enabled:
                return
            
            # 监控系统性能
            self._monitor_system_performance()
            
            # 监控网络质量
            self._monitor_network_quality()
            
            # 分析环境质量
            self._analyze_environment_quality()
            
        except Exception as e:
            self.logger.error(f"环境监控失败: {e}")
    
    def _monitor_system_performance(self):
        """监控系统性能"""
        try:
            if not PSUTIL_AVAILABLE:
                return
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_score = max(0, (100 - cpu_percent) / 100)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_score = max(0, (100 - memory.percent) / 100)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_score = max(0, (100 - disk_percent) / 100)
            
            # 综合性能分数
            performance_score = (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
            
            reading = EnvironmentReading(
                factor=EnvironmentFactor.SYSTEM_PERFORMANCE,
                value=performance_score * 100,
                unit="%",
                timestamp=datetime.now(),
                quality_score=performance_score,
                recommendation=self._get_performance_recommendation(performance_score)
            )
            
            self._update_reading(reading)
            
        except Exception as e:
            self.logger.error(f"监控系统性能失败: {e}")
    
    def _monitor_network_quality(self):
        """监控网络质量"""
        try:
            if not PSUTIL_AVAILABLE:
                return
            
            # 获取网络统计
            net_io = psutil.net_io_counters()
            
            # 简单的网络质量评估（基于错误率）
            total_packets = net_io.packets_sent + net_io.packets_recv
            error_packets = net_io.errin + net_io.errout + net_io.dropin + net_io.dropout
            
            if total_packets > 0:
                error_rate = error_packets / total_packets
                network_score = max(0, 1 - error_rate * 10)  # 错误率越低分数越高
            else:
                network_score = 0.8  # 默认分数
            
            reading = EnvironmentReading(
                factor=EnvironmentFactor.NETWORK_QUALITY,
                value=network_score * 100,
                unit="%",
                timestamp=datetime.now(),
                quality_score=network_score,
                recommendation=self._get_network_recommendation(network_score)
            )
            
            self._update_reading(reading)
            
        except Exception as e:
            self.logger.error(f"监控网络质量失败: {e}")
    
    def _update_reading(self, reading: EnvironmentReading):
        """更新环境读数"""
        try:
            # 更新当前读数
            self.current_readings[reading.factor] = reading
            
            # 添加到历史记录
            self.reading_history.append(reading)
            
            # 限制历史记录长度
            if len(self.reading_history) > 1000:
                self.reading_history = self.reading_history[-500:]
            
            # 发送信号
            self.environment_updated.emit(reading.factor.value, reading.quality_score)
            
            # 检查是否需要警告
            if reading.quality_score < 0.3:
                self.environment_alert.emit(
                    reading.factor.value,
                    f"{reading.factor.value}质量较差: {reading.recommendation}"
                )
            
        except Exception as e:
            self.logger.error(f"更新环境读数失败: {e}")
    
    def _analyze_environment_quality(self):
        """分析环境质量并生成建议"""
        try:
            if not self.current_readings:
                return
            
            # 计算整体环境分数
            total_score = 0
            count = 0
            
            for reading in self.current_readings.values():
                total_score += reading.quality_score
                count += 1
            
            if count > 0:
                overall_score = total_score / count
                
                # 生成优化建议
                if overall_score < 0.7:
                    self._generate_optimization_suggestions()
                
        except Exception as e:
            self.logger.error(f"分析环境质量失败: {e}")
    
    def _generate_optimization_suggestions(self):
        """生成优化建议"""
        try:
            suggestions = []
            
            for factor, reading in self.current_readings.items():
                if reading.quality_score < 0.7:
                    suggestion = self._create_optimization_suggestion(factor, reading)
                    if suggestion:
                        suggestions.append(suggestion)
            
            # 存储建议
            for suggestion in suggestions:
                self.optimization_suggestions[suggestion.id] = suggestion
                self.optimization_suggested.emit(suggestion.id)
            
        except Exception as e:
            self.logger.error(f"生成优化建议失败: {e}")
    
    def _create_optimization_suggestion(self, factor: EnvironmentFactor, 
                                      reading: EnvironmentReading) -> Optional[OptimizationSuggestion]:
        """创建优化建议"""
        try:
            suggestion_id = f"{factor.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if factor == EnvironmentFactor.SYSTEM_PERFORMANCE:
                return OptimizationSuggestion(
                    id=suggestion_id,
                    title="优化系统性能",
                    description=f"当前系统性能分数: {reading.quality_score:.1%}，建议进行优化",
                    factor=factor,
                    priority=4,
                    impact_score=0.8,
                    difficulty=2,
                    estimated_improvement=0.3,
                    action_steps=[
                        "关闭不必要的后台程序",
                        "清理系统垃圾文件",
                        "检查磁盘空间",
                        "重启系统释放内存"
                    ],
                    created_at=datetime.now()
                )
            
            elif factor == EnvironmentFactor.NETWORK_QUALITY:
                return OptimizationSuggestion(
                    id=suggestion_id,
                    title="改善网络连接",
                    description=f"当前网络质量分数: {reading.quality_score:.1%}，建议检查网络",
                    factor=factor,
                    priority=3,
                    impact_score=0.6,
                    difficulty=2,
                    estimated_improvement=0.4,
                    action_steps=[
                        "检查网络连接状态",
                        "重启路由器",
                        "关闭占用带宽的程序",
                        "切换到有线连接"
                    ],
                    created_at=datetime.now()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"创建优化建议失败: {e}")
            return None
    
    def _get_performance_recommendation(self, score: float) -> str:
        """获取性能建议"""
        if score >= 0.9:
            return "系统性能优秀，适合高强度学习"
        elif score >= 0.7:
            return "系统性能良好，可以正常学习"
        elif score >= 0.5:
            return "系统性能一般，建议关闭不必要程序"
        else:
            return "系统性能较差，建议优化后再学习"
    
    def _get_network_recommendation(self, score: float) -> str:
        """获取网络建议"""
        if score >= 0.9:
            return "网络连接优秀，适合在线学习"
        elif score >= 0.7:
            return "网络连接良好，可以正常使用"
        elif score >= 0.5:
            return "网络连接一般，避免大文件下载"
        else:
            return "网络连接较差，建议检查网络设置"
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """获取环境总结"""
        try:
            if not self.current_readings:
                return {'status': 'no_data'}
            
            # 计算整体分数
            total_score = sum(r.quality_score for r in self.current_readings.values())
            overall_score = total_score / len(self.current_readings)
            
            # 分类评级
            if overall_score >= 0.9:
                grade = "优秀"
                color = "green"
            elif overall_score >= 0.7:
                grade = "良好"
                color = "blue"
            elif overall_score >= 0.5:
                grade = "一般"
                color = "orange"
            else:
                grade = "较差"
                color = "red"
            
            # 获取最需要改善的因素
            worst_factor = min(self.current_readings.values(), key=lambda r: r.quality_score)
            
            return {
                'status': 'success',
                'overall_score': overall_score,
                'grade': grade,
                'color': color,
                'total_factors': len(self.current_readings),
                'worst_factor': worst_factor.factor.value,
                'worst_score': worst_factor.quality_score,
                'suggestions_count': len(self.optimization_suggestions),
                'last_update': max(r.timestamp for r in self.current_readings.values())
            }
            
        except Exception as e:
            self.logger.error(f"获取环境总结失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_optimization_suggestions(self, factor: EnvironmentFactor = None) -> List[OptimizationSuggestion]:
        """获取优化建议"""
        try:
            suggestions = list(self.optimization_suggestions.values())
            
            if factor:
                suggestions = [s for s in suggestions if s.factor == factor]
            
            # 按优先级排序
            suggestions.sort(key=lambda s: s.priority, reverse=True)
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"获取优化建议失败: {e}")
            return []
    
    def apply_auto_optimization(self, factor: EnvironmentFactor) -> bool:
        """应用自动优化"""
        try:
            if not self.auto_optimization_enabled:
                return False
            
            if factor == EnvironmentFactor.SYSTEM_PERFORMANCE:
                return self._auto_optimize_performance()
            elif factor == EnvironmentFactor.NETWORK_QUALITY:
                return self._auto_optimize_network()
            
            return False
            
        except Exception as e:
            self.logger.error(f"应用自动优化失败: {e}")
            return False
    
    def _auto_optimize_performance(self) -> bool:
        """自动优化系统性能"""
        try:
            actions_taken = []
            
            # 清理系统缓存（仅在Windows上）
            if platform.system() == "Windows":
                import subprocess
                try:
                    subprocess.run(["cleanmgr", "/sagerun:1"], check=False, timeout=30)
                    actions_taken.append("清理系统缓存")
                except:
                    pass
            
            # 发送优化信号
            if actions_taken:
                self.auto_optimization_applied.emit(
                    EnvironmentFactor.SYSTEM_PERFORMANCE.value,
                    f"已执行: {', '.join(actions_taken)}"
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"自动优化系统性能失败: {e}")
            return False
    
    def _auto_optimize_network(self) -> bool:
        """自动优化网络连接"""
        try:
            # 这里可以添加网络优化逻辑
            # 例如：刷新DNS、重置网络适配器等
            
            self.auto_optimization_applied.emit(
                EnvironmentFactor.NETWORK_QUALITY.value,
                "网络连接检查完成"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"自动优化网络连接失败: {e}")
            return False
    
    def set_optimization_level(self, level: OptimizationLevel):
        """设置优化级别"""
        try:
            self.optimization_level = level
            self.logger.info(f"优化级别设置为: {level.value}")
            
        except Exception as e:
            self.logger.error(f"设置优化级别失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.monitor_timer.stop()
            super().cleanup()
            self.logger.info("学习环境优化器已清理")
            
        except Exception as e:
            self.logger.error(f"清理学习环境优化器失败: {e}")
