#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 学习环境优化器
提供学习环境监控、优化建议、专注模式等功能
"""

import logging
import psutil
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.base_manager import BaseManager


class EnvironmentStatus(Enum):
    """环境状态"""
    OPTIMAL = "optimal"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class OptimizationType(Enum):
    """优化类型"""
    PERFORMANCE = "performance"
    DISTRACTION = "distraction"
    RESOURCE = "resource"
    FOCUS = "focus"
    HEALTH = "health"


@dataclass
class EnvironmentMetrics:
    """环境指标"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_activity: float
    running_processes: int
    active_windows: int
    noise_level: Optional[float] = None
    brightness_level: Optional[float] = None
    timestamp: datetime = None


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    id: str
    type: OptimizationType
    title: str
    description: str
    priority: int  # 1-5
    estimated_impact: float  # 0-1
    action_required: bool
    auto_applicable: bool
    created_at: datetime


@dataclass
class FocusSession:
    """专注会话"""
    id: str
    start_time: datetime
    planned_duration: int  # 分钟
    actual_duration: Optional[int] = None
    interruptions: int = 0
    productivity_score: Optional[float] = None
    end_time: Optional[datetime] = None
    notes: str = ""


class EnvironmentOptimizer(BaseManager):
    """学习环境优化器"""
    
    # 信号定义
    environment_status_changed = pyqtSignal(str)  # 状态
    optimization_suggested = pyqtSignal(str)  # 建议ID
    focus_session_started = pyqtSignal(str)  # 会话ID
    focus_session_ended = pyqtSignal(str, float)  # 会话ID, 生产力分数
    distraction_detected = pyqtSignal(str, str)  # 类型, 描述
    performance_warning = pyqtSignal(str, float)  # 指标名称, 值
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager, "EnvironmentOptimizer")
        
        # 数据存储
        self.current_metrics: Optional[EnvironmentMetrics] = None
        self.metrics_history: List[EnvironmentMetrics] = []
        self.optimization_suggestions: Dict[str, OptimizationSuggestion] = {}
        self.focus_sessions: Dict[str, FocusSession] = {}
        
        # 当前状态
        self.current_status = EnvironmentStatus.GOOD
        self.focus_mode_active = False
        self.current_focus_session: Optional[FocusSession] = None
        
        # 定时器
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self._collect_metrics)
        
        # 配置参数
        self.optimizer_settings = {
            'monitoring_interval': 30,  # 秒
            'metrics_history_limit': 1000,
            'cpu_warning_threshold': 80.0,
            'memory_warning_threshold': 85.0,
            'disk_warning_threshold': 90.0,
            'auto_optimization': True,
            'focus_mode_strict': False
        }
        
        # 阈值设置
        self.status_thresholds = {
            EnvironmentStatus.OPTIMAL: {'cpu': 30, 'memory': 50, 'disk': 70},
            EnvironmentStatus.GOOD: {'cpu': 50, 'memory': 70, 'disk': 80},
            EnvironmentStatus.FAIR: {'cpu': 70, 'memory': 80, 'disk': 85},
            EnvironmentStatus.POOR: {'cpu': 85, 'memory': 90, 'disk': 95},
            EnvironmentStatus.CRITICAL: {'cpu': 95, 'memory': 95, 'disk': 98}
        }
        
        self.logger.info("学习环境优化器初始化完成")
    
    def initialize(self) -> bool:
        """
        初始化学习环境优化器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            with self._lock:
                if self._initialized:
                    return True
                
                # 加载配置
                self._load_optimizer_settings()
                
                # 初始化系统监控
                self._init_system_monitoring()
                
                # 加载历史数据
                self._load_metrics_history()
                
                # 启动监控
                self._start_monitoring()
                
                # 初始环境评估
                self._initial_environment_assessment()
                
                self._initialized = True
                self._running = True
                self.manager_initialized.emit()
                
                self.logger.info("学习环境优化器初始化成功")
                return True
                
        except Exception as e:
            self.logger.error(f"学习环境优化器初始化失败: {e}")
            self.manager_error.emit("initialization_failed", str(e))
            return False
    
    def _load_optimizer_settings(self):
        """加载优化器设置"""
        try:
            if self.config_manager:
                optimizer_config = self.config_manager.get_config('environment_optimizer', {})
                settings = optimizer_config.get('optimizer_settings', {})
                
                # 更新设置
                for key, value in settings.items():
                    if key in self.optimizer_settings:
                        self.optimizer_settings[key] = value
                        
                self.logger.info("优化器设置加载完成")
        except Exception as e:
            self.logger.error(f"加载优化器设置失败: {e}")
    
    def _init_system_monitoring(self):
        """初始化系统监控"""
        try:
            # 检查系统监控能力
            try:
                psutil.cpu_percent()
                psutil.virtual_memory()
                psutil.disk_usage('/')
                self.logger.info("系统监控能力检查通过")
            except Exception as e:
                self.logger.warning(f"系统监控能力受限: {e}")
                
        except Exception as e:
            self.logger.error(f"初始化系统监控失败: {e}")
    
    def _load_metrics_history(self):
        """加载指标历史"""
        try:
            if self.config_manager:
                optimizer_config = self.config_manager.get_config('environment_optimizer', {})
                history_data = optimizer_config.get('metrics_history', [])
                
                # 重建指标历史
                for metrics_data in history_data:
                    try:
                        # 这里可以添加指标数据的反序列化逻辑
                        pass
                    except Exception as e:
                        self.logger.warning(f"加载指标数据失败: {e}")
                        
                self.logger.info("指标历史加载完成")
        except Exception as e:
            self.logger.error(f"加载指标历史失败: {e}")
    
    def _start_monitoring(self):
        """启动监控"""
        try:
            interval = self.optimizer_settings.get('monitoring_interval', 30) * 1000  # 转换为毫秒
            self.monitoring_timer.start(interval)
            self.logger.info("环境监控已启动")
        except Exception as e:
            self.logger.error(f"启动监控失败: {e}")
    
    def _initial_environment_assessment(self):
        """初始环境评估"""
        try:
            # 收集初始指标
            self._collect_metrics()
            
            # 生成初始建议
            self._generate_optimization_suggestions()
            
            self.logger.info("初始环境评估完成")
        except Exception as e:
            self.logger.error(f"初始环境评估失败: {e}")
    
    def _collect_metrics(self):
        """收集环境指标"""
        try:
            # 收集系统指标
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 网络活动（简化版）
            network_activity = 0.0
            try:
                net_io = psutil.net_io_counters()
                network_activity = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            except:
                pass
            
            # 运行进程数
            running_processes = len(psutil.pids())
            
            # 活动窗口数（简化版）
            active_windows = 1  # 暂时固定值
            
            # 创建指标对象
            metrics = EnvironmentMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_activity=network_activity,
                running_processes=running_processes,
                active_windows=active_windows,
                timestamp=datetime.now()
            )
            
            self.current_metrics = metrics
            self.metrics_history.append(metrics)
            
            # 限制历史记录数量
            limit = self.optimizer_settings.get('metrics_history_limit', 1000)
            if len(self.metrics_history) > limit:
                self.metrics_history = self.metrics_history[-limit:]
            
            # 评估环境状态
            self._evaluate_environment_status(metrics)
            
            # 检查警告阈值
            self._check_warning_thresholds(metrics)
            
        except Exception as e:
            self.logger.error(f"收集环境指标失败: {e}")
    
    def _evaluate_environment_status(self, metrics: EnvironmentMetrics):
        """评估环境状态"""
        try:
            # 根据指标确定状态
            for status, thresholds in self.status_thresholds.items():
                if (metrics.cpu_usage <= thresholds['cpu'] and
                    metrics.memory_usage <= thresholds['memory'] and
                    metrics.disk_usage <= thresholds['disk']):
                    if self.current_status != status:
                        self.current_status = status
                        self.environment_status_changed.emit(status.value)
                        self.logger.info(f"环境状态变更: {status.value}")
                    break
                    
        except Exception as e:
            self.logger.error(f"评估环境状态失败: {e}")
    
    def _check_warning_thresholds(self, metrics: EnvironmentMetrics):
        """检查警告阈值"""
        try:
            cpu_threshold = self.optimizer_settings.get('cpu_warning_threshold', 80.0)
            memory_threshold = self.optimizer_settings.get('memory_warning_threshold', 85.0)
            disk_threshold = self.optimizer_settings.get('disk_warning_threshold', 90.0)
            
            if metrics.cpu_usage > cpu_threshold:
                self.performance_warning.emit("CPU使用率", metrics.cpu_usage)
            
            if metrics.memory_usage > memory_threshold:
                self.performance_warning.emit("内存使用率", metrics.memory_usage)
            
            if metrics.disk_usage > disk_threshold:
                self.performance_warning.emit("磁盘使用率", metrics.disk_usage)
                
        except Exception as e:
            self.logger.error(f"检查警告阈值失败: {e}")
    
    def _generate_optimization_suggestions(self):
        """生成优化建议"""
        try:
            if not self.current_metrics:
                return
            
            suggestions = []
            
            # CPU优化建议
            if self.current_metrics.cpu_usage > 70:
                suggestion = OptimizationSuggestion(
                    id=f"cpu_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type=OptimizationType.PERFORMANCE,
                    title="CPU使用率过高",
                    description="建议关闭不必要的程序以降低CPU使用率",
                    priority=3,
                    estimated_impact=0.3,
                    action_required=True,
                    auto_applicable=False,
                    created_at=datetime.now()
                )
                suggestions.append(suggestion)
            
            # 内存优化建议
            if self.current_metrics.memory_usage > 80:
                suggestion = OptimizationSuggestion(
                    id=f"mem_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type=OptimizationType.PERFORMANCE,
                    title="内存使用率过高",
                    description="建议清理内存或关闭占用内存较多的程序",
                    priority=4,
                    estimated_impact=0.4,
                    action_required=True,
                    auto_applicable=False,
                    created_at=datetime.now()
                )
                suggestions.append(suggestion)
            
            # 添加建议到存储
            for suggestion in suggestions:
                self.optimization_suggestions[suggestion.id] = suggestion
                self.optimization_suggested.emit(suggestion.id)
                
            if suggestions:
                self.logger.info(f"生成了 {len(suggestions)} 个优化建议")
                
        except Exception as e:
            self.logger.error(f"生成优化建议失败: {e}")
    
    def start_focus_session(self, planned_duration: int) -> str:
        """开始专注会话"""
        try:
            if self.focus_mode_active:
                raise ValueError("专注会话已在进行中")
            
            session_id = f"focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            session = FocusSession(
                id=session_id,
                start_time=datetime.now(),
                planned_duration=planned_duration
            )
            
            self.focus_sessions[session_id] = session
            self.current_focus_session = session
            self.focus_mode_active = True
            
            self.focus_session_started.emit(session_id)
            self.logger.info(f"专注会话已开始: {planned_duration} 分钟")
            return session_id
            
        except Exception as e:
            self.logger.error(f"开始专注会话失败: {e}")
            return ""
    
    def end_focus_session(self) -> Optional[float]:
        """结束专注会话"""
        try:
            if not self.focus_mode_active or not self.current_focus_session:
                raise ValueError("没有活动的专注会话")
            
            session = self.current_focus_session
            session.end_time = datetime.now()
            session.actual_duration = int((session.end_time - session.start_time).total_seconds() / 60)
            
            # 计算生产力分数（简化版）
            planned_ratio = session.actual_duration / session.planned_duration if session.planned_duration > 0 else 0
            interruption_penalty = max(0, 1 - (session.interruptions * 0.1))
            session.productivity_score = min(1.0, planned_ratio * interruption_penalty)
            
            self.focus_mode_active = False
            self.current_focus_session = None
            
            self.focus_session_ended.emit(session.id, session.productivity_score)
            self.logger.info(f"专注会话已结束，生产力分数: {session.productivity_score:.2f}")
            return session.productivity_score
            
        except Exception as e:
            self.logger.error(f"结束专注会话失败: {e}")
            return None
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.monitoring_timer.isActive():
                self.monitoring_timer.stop()
            
            super().cleanup()
            self.logger.info("学习环境优化器已清理")
        except Exception as e:
            self.logger.error(f"清理学习环境优化器失败: {e}")
