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
TimeNest 智能学习计划生成器
基于个人习惯、课程安排和目标自动生成学习计划
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, time, date
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager


class PlanType(Enum):
    """计划类型"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    EXAM_PREP = "exam_prep"
    CUSTOM = "custom"


class TaskType(Enum):
    """任务类型"""
    REVIEW = "review"
    PREVIEW = "preview"
    PRACTICE = "practice"
    MEMORIZATION = "memorization"
    READING = "reading"
    WRITING = "writing"
    RESEARCH = "research"


class Difficulty(Enum):
    """难度级别"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4


@dataclass
class StudyGoal:
    """学习目标"""
    id: str
    title: str
    description: str
    subject: str
    target_date: datetime
    priority: int  # 1-5
    estimated_hours: float
    current_progress: float = 0.0  # 0-1
    milestones: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StudyBlock:
    """学习块"""
    id: str
    title: str
    subject: str
    task_type: TaskType
    difficulty: Difficulty
    start_time: datetime
    duration: int  # 分钟
    description: str = ""
    prerequisites: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    expected_outcome: str = ""


@dataclass
class StudyPlan:
    """学习计划"""
    id: str
    name: str
    plan_type: PlanType
    start_date: date
    end_date: date
    goals: List[StudyGoal]
    study_blocks: List[StudyBlock]
    total_hours: float
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    completion_rate: float = 0.0


class StudyPlannerManager(BaseManager):
    """智能学习计划生成器"""
    
    # 信号定义
    plan_generated = pyqtSignal(str)  # 计划ID
    plan_updated = pyqtSignal(str)
    goal_achieved = pyqtSignal(str)  # 目标ID
    milestone_reached = pyqtSignal(str, str)  # 目标ID, 里程碑
    plan_optimization_suggested = pyqtSignal(str, str)  # 计划ID, 建议
    
    def __init__(self, config_manager=None, schedule_enhancement=None, study_assistant=None):
        super().__init__(config_manager, "StudyPlanner")
        
        self.schedule_enhancement = schedule_enhancement
        self.study_assistant = study_assistant
        
        # 数据存储
        self.study_plans: Dict[str, StudyPlan] = {}
        self.study_goals: Dict[str, StudyGoal] = {}
        
        # 计划生成参数
        self.planning_preferences = {
            'preferred_session_length': 45,  # 分钟
            'max_daily_hours': 8,
            'break_between_sessions': 15,  # 分钟
            'difficulty_progression': True,
            'subject_rotation': True,
            'avoid_late_night': True,
            'weekend_lighter_load': True
        }
        
        # 学科难度权重
        self.subject_difficulty_weights = {
            '数学': 1.2,
            '物理': 1.1,
            '化学': 1.0,
            '英语': 0.9,
            '语文': 0.8,
            '历史': 0.7,
            '地理': 0.7
        }
        
        self.logger.info("智能学习计划生成器初始化完成")

    def initialize(self) -> bool:
        """
        初始化智能学习计划生成器

        Returns:
            bool: 初始化是否成功
        """
        try:
            with self._lock:
                if self._initialized:
                    return True

                # 加载计划配置
                self._load_planning_preferences()

                # 加载历史计划
                self._load_study_plans()

                # 加载学习目标
                self._load_study_goals()

                # 初始化学科权重
                self._init_subject_weights()

                self._initialized = True
                self._running = True
                self.manager_initialized.emit()

                self.logger.info("智能学习计划生成器初始化成功")
                return True

        except Exception as e:
            self.logger.error(f"智能学习计划生成器初始化失败: {e}")
            self.manager_error.emit("initialization_failed", str(e))
            return False

    def _load_planning_preferences(self):
        """加载计划偏好设置"""
        try:
            if self.config_manager:
                planner_config = self.config_manager.get_config('study_planner', {})
                preferences = planner_config.get('planning_preferences', {})

                # 更新计划偏好
                for key, value in preferences.items():
                    if key in self.planning_preferences:
                        self.planning_preferences[key] = value

                self.logger.info("计划偏好设置加载完成")
        except Exception as e:
            self.logger.error(f"加载计划偏好设置失败: {e}")

    def _load_study_plans(self):
        """加载历史学习计划"""
        try:
            if self.config_manager:
                planner_config = self.config_manager.get_config('study_planner', {})
                plans_data = planner_config.get('study_plans', {})

                # 重建学习计划
                for plan_id, plan_data in plans_data.items():
                    try:
                        # 这里可以添加计划数据的反序列化逻辑
                        # 暂时只记录日志
                        pass
                    except Exception as e:
                        self.logger.warning(f"加载计划 {plan_id} 失败: {e}")

                self.logger.info("历史学习计划加载完成")
        except Exception as e:
            self.logger.error(f"加载历史学习计划失败: {e}")

    def _load_study_goals(self):
        """加载学习目标"""
        try:
            if self.config_manager:
                planner_config = self.config_manager.get_config('study_planner', {})
                goals_data = planner_config.get('study_goals', {})

                # 重建学习目标
                for goal_id, goal_data in goals_data.items():
                    try:
                        # 这里可以添加目标数据的反序列化逻辑
                        # 暂时只记录日志
                        pass
                    except Exception as e:
                        self.logger.warning(f"加载目标 {goal_id} 失败: {e}")

                self.logger.info("学习目标加载完成")
        except Exception as e:
            self.logger.error(f"加载学习目标失败: {e}")

    def _init_subject_weights(self):
        """初始化学科权重"""
        try:
            if self.config_manager:
                planner_config = self.config_manager.get_config('study_planner', {})
                weights = planner_config.get('subject_difficulty_weights', {})

                # 更新学科权重
                for subject, weight in weights.items():
                    self.subject_difficulty_weights[subject] = weight

                self.logger.info("学科权重初始化完成")
        except Exception as e:
            self.logger.error(f"初始化学科权重失败: {e}")

    def create_study_goal(self, title: str, subject: str, target_date: datetime,
                         estimated_hours: float, description: str = "",
                         priority: int = 3, milestones: List[str] = None) -> str:
        """创建学习目标"""
        try:
            goal_id = f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            goal = StudyGoal(
                id=goal_id,
                title=title,
                description=description,
                subject=subject,
                target_date=target_date,
                priority=priority,
                estimated_hours=estimated_hours,
                milestones=milestones or []
            )
            
            self.study_goals[goal_id] = goal
            self.logger.info(f"学习目标已创建: {title}")
            return goal_id
            
        except Exception as e:
            self.logger.error(f"创建学习目标失败: {e}")
            return ""
    
    def generate_study_plan(self, plan_name: str, plan_type: PlanType,
                          start_date: date, end_date: date,
                          goal_ids: List[str] = None) -> str:
        """生成学习计划"""
        try:
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 获取目标
            goals = []
            if goal_ids:
                goals = [self.study_goals[gid] for gid in goal_ids if gid in self.study_goals]
            
            # 分析用户习惯
            user_patterns = self._analyze_user_patterns()
            
            # 生成学习块
            study_blocks = self._generate_study_blocks(goals, start_date, end_date, user_patterns)
            
            # 计算总时长
            total_hours = sum(block.duration for block in study_blocks) / 60.0
            
            # 创建计划
            plan = StudyPlan(
                id=plan_id,
                name=plan_name,
                plan_type=plan_type,
                start_date=start_date,
                end_date=end_date,
                goals=goals,
                study_blocks=study_blocks,
                total_hours=total_hours
            )
            
            self.study_plans[plan_id] = plan
            self.plan_generated.emit(plan_id)
            
            self.logger.info(f"学习计划已生成: {plan_name}, 包含 {len(study_blocks)} 个学习块")
            return plan_id
            
        except Exception as e:
            self.logger.error(f"生成学习计划失败: {e}")
            return ""
    
    def _analyze_user_patterns(self) -> Dict[str, Any]:
        """分析用户学习模式"""
        try:
            patterns = {
                'productive_hours': [9, 10, 14, 15, 19, 20],  # 默认高效时间
                'preferred_session_length': 45,
                'break_duration': 15,
                'subject_preferences': {},
                'difficulty_tolerance': 0.7
            }
            
            # 如果有学习助手数据，使用实际分析结果
            if self.study_assistant:
                analytics = self.study_assistant.get_learning_analytics()
                if analytics:
                    patterns['productive_hours'] = analytics.most_productive_hours
                    patterns['preferred_session_length'] = analytics.average_session_length
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"分析用户模式失败: {e}")
            return {}
    
    def _generate_study_blocks(self, goals: List[StudyGoal], start_date: date,
                             end_date: date, user_patterns: Dict[str, Any]) -> List[StudyBlock]:
        """生成学习块"""
        try:
            study_blocks = []
            current_date = start_date
            
            # 计算可用天数
            total_days = (end_date - start_date).days + 1
            
            # 为每个目标分配时间
            for goal in goals:
                goal_blocks = self._generate_goal_blocks(goal, current_date, end_date, user_patterns)
                study_blocks.extend(goal_blocks)
            
            # 按时间排序
            study_blocks.sort(key=lambda b: b.start_time)
            
            # 优化时间安排
            optimized_blocks = self._optimize_schedule(study_blocks, user_patterns)
            
            return optimized_blocks
            
        except Exception as e:
            self.logger.error(f"生成学习块失败: {e}")
            return []
    
    def _generate_goal_blocks(self, goal: StudyGoal, start_date: date,
                            end_date: date, user_patterns: Dict[str, Any]) -> List[StudyBlock]:
        """为单个目标生成学习块"""
        try:
            blocks = []
            
            # 计算可用时间
            available_days = (end_date - start_date).days + 1
            daily_hours = goal.estimated_hours / available_days
            
            # 限制每日最大学习时间
            max_daily_hours = self.planning_preferences.get('max_daily_hours')
            if daily_hours > max_daily_hours:
                daily_hours = max_daily_hours
                available_days = goal.estimated_hours / daily_hours
            
            # 生成每日学习块
            current_date = start_date
            remaining_hours = goal.estimated_hours
            
            while remaining_hours > 0 and current_date <= end_date:
                # 计算当日学习时间
                today_hours = min(daily_hours, remaining_hours)
                
                # 分割为多个会话
                sessions = self._split_into_sessions(today_hours, user_patterns)
                
                # 为每个会话创建学习块
                for i, session_duration in enumerate(sessions):
                    # 选择时间段
                    start_time = self._select_time_slot(current_date, i, user_patterns)
                    
                    block = StudyBlock(
                        id=f"{goal.id}_block_{current_date.strftime('%Y%m%d')}_{i}",
                        title=f"{goal.title} - 第{i+1}节",
                        subject=goal.subject,
                        task_type=self._determine_task_type(goal, i),
                        difficulty=self._determine_difficulty(goal, i),
                        start_time=start_time,
                        duration=session_duration,
                        description=goal.description,
                        expected_outcome=f"完成 {goal.title} 的部分内容"
                    )
                    
                    blocks.append(block)
                
                remaining_hours -= today_hours
                current_date += timedelta(days=1)
            
            return blocks
            
        except Exception as e:
            self.logger.error(f"为目标生成学习块失败: {e}")
            return []
    
    def _split_into_sessions(self, total_hours: float, user_patterns: Dict[str, Any]) -> List[int]:
        """将学习时间分割为多个会话"""
        try:
            session_length = user_patterns.get('preferred_session_length', 45)
            total_minutes = int(total_hours * 60)
            
            sessions = []
            remaining_minutes = total_minutes
            
            while remaining_minutes > 0:
                if remaining_minutes >= session_length:
                    sessions.append(session_length)
                    remaining_minutes -= session_length
                else:
                    # 最后一个会话，如果太短则合并到前一个会话
                    if remaining_minutes >= 15:
                        sessions.append(remaining_minutes)
                    elif sessions:
                        sessions[-1] += remaining_minutes
                    remaining_minutes = 0
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"分割学习会话失败: {e}")
            return [45]  # 默认45分钟
    
    def _select_time_slot(self, study_date: date, session_index: int,
                         user_patterns: Dict[str, Any]) -> datetime:
        """选择时间段"""
        try:
            productive_hours = user_patterns.get('productive_hours', [9, 14, 19])
            
            # 根据会话索引选择时间
            if session_index < len(productive_hours):
                hour = productive_hours[session_index]
            else:
                # 如果会话数超过高效时间段，使用默认时间
                hour = 9 + session_index * 2
            
            # 确保时间在合理范围内
            hour = max(8, min(22, hour))
            
            return datetime.combine(study_date, time(hour, 0))
            
        except Exception as e:
            self.logger.error(f"选择时间段失败: {e}")
            return datetime.combine(study_date, time(9, 0))
    
    def _determine_task_type(self, goal: StudyGoal, session_index: int) -> TaskType:
        """确定任务类型"""
        try:
            # 根据会话索引和目标类型确定任务类型
            task_cycle = [TaskType.PREVIEW, TaskType.PRACTICE, TaskType.REVIEW]
            return task_cycle[session_index % len(task_cycle)]
            
        except Exception as e:
            self.logger.error(f"确定任务类型失败: {e}")
            return TaskType.PRACTICE
    
    def _determine_difficulty(self, goal: StudyGoal, session_index: int) -> Difficulty:
        """确定难度级别"""
        try:
            # 根据科目和会话进度确定难度
            subject_weight = self.subject_difficulty_weights.get(goal.subject, 1.0)
            
            # 逐渐增加难度
            if session_index == 0:
                base_difficulty = Difficulty.EASY
            elif session_index < 3:
                base_difficulty = Difficulty.MEDIUM
            else:
                base_difficulty = Difficulty.HARD
            
            # 根据科目权重调整
            if subject_weight > 1.1:
                return Difficulty(min(4, base_difficulty.value + 1))
            elif subject_weight < 0.8:
                return Difficulty(max(1, base_difficulty.value - 1))
            
            return base_difficulty
            
        except Exception as e:
            self.logger.error(f"确定难度级别失败: {e}")
            return Difficulty.MEDIUM
    
    def _optimize_schedule(self, blocks: List[StudyBlock],
                          user_patterns: Dict[str, Any]) -> List[StudyBlock]:
        """优化时间安排"""
        try:
            optimized_blocks = blocks.copy()
            
            # 避免时间冲突
            optimized_blocks = self._resolve_time_conflicts(optimized_blocks)
            
            # 平衡科目分布
            optimized_blocks = self._balance_subjects(optimized_blocks)
            
            # 调整难度分布
            optimized_blocks = self._adjust_difficulty_distribution(optimized_blocks)
            
            return optimized_blocks
            
        except Exception as e:
            self.logger.error(f"优化时间安排失败: {e}")
            return blocks
    
    def _resolve_time_conflicts(self, blocks: List[StudyBlock]) -> List[StudyBlock]:
        """解决时间冲突"""
        try:
            # 按时间排序
            blocks.sort(key=lambda b: b.start_time)
            
            for i in range(1, len(blocks)):
                current_block = blocks[i]
                previous_block = blocks[i-1]
                
                # 检查是否有时间重叠
                prev_end = previous_block.start_time + timedelta(minutes=previous_block.duration)
                if current_block.start_time < prev_end:
                    # 调整当前块的开始时间:
                    # 调整当前块的开始时间
                    current_block.start_time = prev_end + timedelta(minutes=15)  # 15分钟休息
            
            return blocks
            
        except Exception as e:
            self.logger.error(f"解决时间冲突失败: {e}")
            return blocks
    
    def _balance_subjects(self, blocks: List[StudyBlock]) -> List[StudyBlock]:
        """平衡科目分布"""
        try:
            # 统计每个科目的时间分布
            subject_time = {}
            for block in blocks:
                subject = block.subject
                subject_time[subject] = subject_time.get(subject, 0) + block.duration
            
            # 这里可以添加科目平衡逻辑
            # 例如：重新排列块的顺序以避免同一科目连续出现
            
            return blocks
            
        except Exception as e:
            self.logger.error(f"平衡科目分布失败: {e}")
            return blocks
    
    def _adjust_difficulty_distribution(self, blocks: List[StudyBlock]) -> List[StudyBlock]:
        """调整难度分布"""
        try:
            # 确保难度逐渐递增，避免连续高难度任务
            for i in range(1, len(blocks)):
                current_block = blocks[i]
                previous_block = blocks[i-1]
                
                # 如果连续两个都是高难度，调整当前块的难度
                if (previous_block.difficulty == Difficulty.HARD and
                    current_block.difficulty == Difficulty.HARD):
                    current_block.difficulty = Difficulty.MEDIUM
            
            return blocks
            
        except Exception as e:
            self.logger.error(f"调整难度分布失败: {e}")
            return blocks
    
    def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """更新目标进度"""
        try:
            if goal_id not in self.study_goals:
                return False
            
            goal = self.study_goals[goal_id]
            old_progress = goal.current_progress
            goal.current_progress = min(1.0, max(0.0, progress))
            
            # 检查里程碑
            self._check_milestones(goal, old_progress)
            
            # 检查目标完成
            if goal.current_progress >= 1.0:
                self.goal_achieved.emit(goal_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新目标进度失败: {e}")
            return False
    
    def _check_milestones(self, goal: StudyGoal, old_progress: float):
        """检查里程碑"""
        try:
            milestone_thresholds = [0.25, 0.5, 0.75]
            
            for i, threshold in enumerate(milestone_thresholds):
                if old_progress < threshold <= goal.current_progress:
                    if i < len(goal.milestones):
                        milestone = goal.milestones[i]
                        self.milestone_reached.emit(goal.id, milestone)
                    else:
                        self.milestone_reached.emit(goal.id, f"完成 {threshold:.0%}")
                        
        except Exception as e:
            self.logger.error(f"检查里程碑失败: {e}")
    
    def get_plan_summary(self, plan_id: str) -> Dict[str, Any]:
        """获取计划总结"""
        try:
            if plan_id not in self.study_plans:
                return {'status': 'not_found'}
            
            plan = self.study_plans[plan_id]
            
            # 统计信息
            total_blocks = len(plan.study_blocks)
            completed_blocks = sum(1 for block in plan.study_blocks
                                 if block.start_time < datetime.now())
            
            # 科目分布
            subject_distribution = {}
            for block in plan.study_blocks:
                subject = block.subject
                subject_distribution[subject] = subject_distribution.get(subject, 0) + block.duration
            
            # 难度分布
            difficulty_distribution = {}
            for block in plan.study_blocks:
                diff = block.difficulty.name
                difficulty_distribution[diff] = difficulty_distribution.get(diff, 0) + 1
            
            return {
                'status': 'success',
                'plan_name': plan.name,
                'plan_type': plan.plan_type.value,
                'total_hours': plan.total_hours,
                'total_blocks': total_blocks,
                'completed_blocks': completed_blocks,
                'completion_rate': completed_blocks / total_blocks if total_blocks > 0 else 0,
                'subject_distribution': subject_distribution,
                'difficulty_distribution': difficulty_distribution,
                'goals_count': len(plan.goals),
                'start_date': plan.start_date,
                'end_date': plan.end_date
            }
            
        except Exception as e:
            self.logger.error(f"获取计划总结失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def cleanup(self):
        """清理资源"""
        try:
            super().cleanup()
            self.logger.info("智能学习计划生成器已清理")
            
        except Exception as e:
            self.logger.error(f"清理智能学习计划生成器失败: {e}")
