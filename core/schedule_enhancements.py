#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 课程表增强功能
在原有框架基础上新增细分功能
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date, time
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager


class TaskPriority(Enum):
    """任务优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class StudyTask:
    """学习任务"""
    id: str
    title: str
    description: str
    subject: str
    priority: TaskPriority
    status: TaskStatus
    due_date: datetime
    estimated_duration: int  # 分钟
    actual_duration: Optional[int] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tags is None:
            self.tags = []


@dataclass
class StudySession:
    """学习会话"""
    id: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: int  # 分钟
    notes: str = ""
    efficiency_rating: Optional[int] = None  # 1-5分


@dataclass
class ExamInfo:
    """考试信息"""
    id: str
    subject: str
    title: str
    exam_date: datetime
    duration: int  # 分钟
    location: str
    exam_type: str  # 期中、期末、随堂测验等
    preparation_tasks: List[str] = None  # 关联的准备任务ID
    
    def __post_init__(self):
        if self.preparation_tasks is None:
            self.preparation_tasks = []


class ScheduleEnhancementManager(BaseManager):
    """课程表增强功能管理器"""
    
    # 信号定义
    task_added = pyqtSignal(str)  # 任务ID
    task_updated = pyqtSignal(str)
    task_completed = pyqtSignal(str)
    exam_added = pyqtSignal(str)  # 考试ID
    study_session_started = pyqtSignal(str)  # 会话ID
    study_session_ended = pyqtSignal(str)
    
    def __init__(self, config_manager=None):
        super().__init__("ScheduleEnhancement", config_manager)
        
        # 数据存储
        self.tasks: Dict[str, StudyTask] = {}
        self.study_sessions: Dict[str, StudySession] = {}
        self.exams: Dict[str, ExamInfo] = {}
        
        # 当前活动会话
        self.active_session: Optional[StudySession] = None
        
        self.logger.info("课程表增强功能管理器初始化完成")
    
    def add_study_task(self, title: str, subject: str, due_date: datetime,
                      priority: TaskPriority = TaskPriority.NORMAL,
                      description: str = "", estimated_duration: int = 60,
                      tags: List[str] = None) -> str:
        """添加学习任务"""
        try:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            task = StudyTask(
                id=task_id,
                title=title,
                description=description,
                subject=subject,
                priority=priority,
                status=TaskStatus.PENDING,
                due_date=due_date,
                estimated_duration=estimated_duration,
                tags=tags or []
            )
            
            self.tasks[task_id] = task
            self.task_added.emit(task_id)
            
            self.logger.info(f"学习任务已添加: {title}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"添加学习任务失败: {e}")
            return ""
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """更新任务状态"""
        try:
            if task_id not in self.tasks:
                self.logger.error(f"任务不存在: {task_id}")
                return False
            
            task = self.tasks[task_id]
            old_status = task.status
            task.status = status
            
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
                self.task_completed.emit(task_id)
            
            self.task_updated.emit(task_id)
            self.logger.info(f"任务状态更新: {task.title} {old_status.value} -> {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新任务状态失败: {e}")
            return False
    
    def start_study_session(self, task_id: str) -> str:
        """开始学习会话"""
        try:
            if task_id not in self.tasks:
                self.logger.error(f"任务不存在: {task_id}")
                return ""
            
            # 结束当前活动会话
            if self.active_session:
                self.end_study_session(self.active_session.id)
            
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            session = StudySession(
                id=session_id,
                task_id=task_id,
                start_time=datetime.now(),
                end_time=None,
                duration=0
            )
            
            self.study_sessions[session_id] = session
            self.active_session = session
            
            # 更新任务状态
            if self.tasks[task_id].status == TaskStatus.PENDING:
                self.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            
            self.study_session_started.emit(session_id)
            self.logger.info(f"学习会话开始: {self.tasks[task_id].title}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"开始学习会话失败: {e}")
            return ""
    
    def end_study_session(self, session_id: str, notes: str = "", 
                         efficiency_rating: Optional[int] = None) -> bool:
        """结束学习会话"""
        try:
            if session_id not in self.study_sessions:
                self.logger.error(f"学习会话不存在: {session_id}")
                return False
            
            session = self.study_sessions[session_id]
            session.end_time = datetime.now()
            session.duration = int((session.end_time - session.start_time).total_seconds() / 60)
            session.notes = notes
            session.efficiency_rating = efficiency_rating
            
            # 更新任务的实际用时
            task = self.tasks[session.task_id]
            if task.actual_duration is None:
                task.actual_duration = session.duration
            else:
                task.actual_duration += session.duration
            
            if self.active_session and self.active_session.id == session_id:
                self.active_session = None
            
            self.study_session_ended.emit(session_id)
            self.logger.info(f"学习会话结束: {task.title}, 用时 {session.duration} 分钟")
            return True
            
        except Exception as e:
            self.logger.error(f"结束学习会话失败: {e}")
            return False
    
    def add_exam(self, subject: str, title: str, exam_date: datetime,
                duration: int, location: str = "", exam_type: str = "考试") -> str:
        """添加考试信息"""
        try:
            exam_id = f"exam_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            exam = ExamInfo(
                id=exam_id,
                subject=subject,
                title=title,
                exam_date=exam_date,
                duration=duration,
                location=location,
                exam_type=exam_type
            )
            
            self.exams[exam_id] = exam
            self.exam_added.emit(exam_id)
            
            self.logger.info(f"考试信息已添加: {title}")
            return exam_id
            
        except Exception as e:
            self.logger.error(f"添加考试信息失败: {e}")
            return ""
    
    def get_upcoming_tasks(self, days: int = 7) -> List[StudyTask]:
        """获取即将到期的任务"""
        try:
            cutoff_date = datetime.now() + timedelta(days=days)
            upcoming_tasks = []
            
            for task in self.tasks.values():
                if (task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS] and
                    task.due_date <= cutoff_date):
                    upcoming_tasks.append(task)
            
            # 按到期时间排序
            upcoming_tasks.sort(key=lambda t: t.due_date)
            return upcoming_tasks
            
        except Exception as e:
            self.logger.error(f"获取即将到期任务失败: {e}")
            return []
    
    def get_upcoming_exams(self, days: int = 14) -> List[ExamInfo]:
        """获取即将到来的考试"""
        try:
            cutoff_date = datetime.now() + timedelta(days=days)
            upcoming_exams = []
            
            for exam in self.exams.values():
                if exam.exam_date <= cutoff_date and exam.exam_date >= datetime.now():
                    upcoming_exams.append(exam)
            
            # 按考试时间排序
            upcoming_exams.sort(key=lambda e: e.exam_date)
            return upcoming_exams
            
        except Exception as e:
            self.logger.error(f"获取即将到来考试失败: {e}")
            return []
    
    def get_study_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取学习统计信息"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 统计最近的学习会话
            recent_sessions = [
                session for session in self.study_sessions.values()
                if session.start_time >= cutoff_date and session.end_time is not None
            ]
            
            # 按科目统计
            subject_stats = {}
            total_duration = 0
            
            for session in recent_sessions:
                task = self.tasks.get(session.task_id)
                if task:
                    subject = task.subject
                    if subject not in subject_stats:
                        subject_stats[subject] = {
                            'duration': 0,
                            'sessions': 0,
                            'avg_efficiency': 0
                        }
                    
                    subject_stats[subject]['duration'] += session.duration
                    subject_stats[subject]['sessions'] += 1
                    total_duration += session.duration
                    
                    if session.efficiency_rating:
                        current_avg = subject_stats[subject]['avg_efficiency']
                        sessions_count = subject_stats[subject]['sessions']
                        subject_stats[subject]['avg_efficiency'] = (
                            (current_avg * (sessions_count - 1) + session.efficiency_rating) / sessions_count
                        )
            
            # 完成的任务统计
            completed_tasks = [
                task for task in self.tasks.values()
                if (task.status == TaskStatus.COMPLETED and 
                    task.completed_at and task.completed_at >= cutoff_date)
            ]
            
            return {
                'total_study_time': total_duration,
                'total_sessions': len(recent_sessions),
                'completed_tasks': len(completed_tasks),
                'subject_breakdown': subject_stats,
                'avg_session_duration': total_duration / len(recent_sessions) if recent_sessions else 0
            }
            
        except Exception as e:
            self.logger.error(f"获取学习统计失败: {e}")
            return {}
    
    def get_task_by_id(self, task_id: str) -> Optional[StudyTask]:
        """根据ID获取任务"""
        return self.tasks.get(task_id)
    
    def get_exam_by_id(self, exam_id: str) -> Optional[ExamInfo]:
        """根据ID获取考试信息"""
        return self.exams.get(exam_id)
    
    def cleanup(self):
        """清理资源"""
        try:
            # 结束活动会话
            if self.active_session:
                self.end_study_session(self.active_session.id)
            
            super().cleanup()
            self.logger.info("课程表增强功能管理器已清理")
            
        except Exception as e:
            self.logger.error(f"清理课程表增强功能失败: {e}")
