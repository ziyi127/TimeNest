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
TimeNest 智能学习助手
提供学习建议、进度跟踪和智能分析功能
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager


class StudyPattern(Enum):
    """学习模式"""
    MORNING_PERSON = "morning_person"
    NIGHT_OWL = "night_owl"
    BALANCED = "balanced"
    INTENSIVE = "intensive"
    DISTRIBUTED = "distributed"


class LearningStyle(Enum):
    """学习风格"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


@dataclass
class StudyRecommendation:
    """学习建议"""
    id: str
    title: str
    description: str
    priority: int  # 1-5
    category: str
    estimated_benefit: float  # 0-1
    difficulty: int  # 1-5
    time_required: int  # 分钟
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class LearningAnalytics:
    """学习分析数据"""
    total_study_time: int  # 分钟
    average_session_length: float
    most_productive_hours: List[int]
    subject_distribution: Dict[str, int]
    efficiency_trend: List[float]
    completion_rate: float
    streak_days: int


class StudyAssistantManager(BaseManager):
    """智能学习助手管理器"""
    
    # 信号定义
    recommendation_generated = pyqtSignal(str)  # 建议ID
    pattern_detected = pyqtSignal(str, str)  # 模式类型, 描述
    milestone_reached = pyqtSignal(str, str)  # 里程碑类型, 描述
    study_insight_available = pyqtSignal(str)  # 洞察内容
    
    def __init__(self, config_manager=None, schedule_enhancement=None):
        super().__init__("StudyAssistant", config_manager)
        
        self.schedule_enhancement = schedule_enhancement
        
        # 用户学习档案
        self.user_profile = {
            'study_pattern': StudyPattern.BALANCED,
            'learning_style': LearningStyle.VISUAL,
            'preferred_session_length': 45,  # 分钟
            'break_length': 10,  # 分钟
            'daily_study_goal': 180,  # 分钟
            'subjects': [],
            'difficulty_preference': 3  # 1-5
        }
        
        # 数据存储
        self.recommendations: Dict[str, StudyRecommendation] = {}
        self.analytics_cache: Optional[LearningAnalytics] = None
        self.last_analytics_update: Optional[datetime] = None
        
        # 学习模式检测
        self.pattern_detection_data = {
            'session_times': [],
            'productivity_scores': [],
            'subject_preferences': {}
        }
        
        self.logger.info("智能学习助手管理器初始化完成")
    
    def analyze_study_patterns(self) -> Dict[str, Any]:
        """分析学习模式"""
        try:
            if not self.schedule_enhancement:
                return {}
            
            # 获取最近的学习会话
            sessions = list(self.schedule_enhancement.study_sessions.values())
            if len(sessions) < 5:  # 需要足够的数据:
                return {'status': 'insufficient_data'}
            
            # 分析最佳学习时间
            productive_hours = self._analyze_productive_hours(sessions)
            
            # 分析学习持续时间偏好
            session_lengths = [s.duration for s in sessions if s.end_time]
            avg_session_length = sum(session_lengths) / len(session_lengths) if session_lengths else 0
            
            # 分析科目偏好
            subject_time = {}
            for session in sessions:
                task = self.schedule_enhancement.get_task_by_id(session.task_id)
                if task:
                    subject = task.subject
                    subject_time[subject] = subject_time.get(subject, 0) + session.duration
            
            # 检测学习模式
            detected_pattern = self._detect_study_pattern(productive_hours, avg_session_length)
            
            analysis = {
                'status': 'success',
                'productive_hours': productive_hours,
                'average_session_length': avg_session_length,
                'subject_distribution': subject_time,
                'detected_pattern': detected_pattern,
                'total_sessions': len(sessions)
            }
            
            # 更新用户档案
            if detected_pattern != self.user_profile.get('study_pattern'):
                self.user_profile['study_pattern'] = detected_pattern
                self.pattern_detected.emit(detected_pattern.value, f"检测到学习模式: {detected_pattern.value}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析学习模式失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _analyze_productive_hours(self, sessions: List) -> List[int]:
        """分析高效学习时间段"""
        try:
            hour_productivity = {}
            
            for session in sessions:
                if session.end_time and session.efficiency_rating:
                    hour = session.start_time.hour
                    if hour not in hour_productivity:
                        hour_productivity[hour] = []
                    hour_productivity[hour].append(session.efficiency_rating)
            
            # 计算每小时的平均效率
            hour_averages = {}
            for hour, ratings in hour_productivity.items():
                hour_averages[hour] = sum(ratings) / len(ratings)
            
            # 返回效率最高的时间段
            sorted_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)
            return [hour for hour, _ in sorted_hours[:3]]  # 返回前3个最佳时间段
            
        except Exception as e:
            self.logger.error(f"分析高效时间段失败: {e}")
            return []
    
    def _detect_study_pattern(self, productive_hours: List[int], avg_session_length: float) -> StudyPattern:
        """检测学习模式"""
        try:
            # 基于高效时间段判断
            if productive_hours:
                early_hours = [h for h in productive_hours if h < 12]
                late_hours = [h for h in productive_hours if h > 18]
                
                
                if len(early_hours) > len(late_hours):
                    return StudyPattern.MORNING_PERSON
                
                    return StudyPattern.MORNING_PERSON
                elif len(late_hours) > len(early_hours):
                    return StudyPattern.NIGHT_OWL
            
            # 基于学习时长判断
            if avg_session_length > 60:
                return StudyPattern.INTENSIVE
            elif avg_session_length < 30:
                return StudyPattern.DISTRIBUTED
            
            return StudyPattern.BALANCED
            
        except Exception as e:
            self.logger.error(f"检测学习模式失败: {e}")
            return StudyPattern.BALANCED
    
    def generate_study_recommendations(self) -> List[StudyRecommendation]:
        """生成学习建议"""
        try:
            recommendations = []
            
            # 分析当前状态
            analysis = self.analyze_study_patterns()
            if analysis.get('status') != 'success':
                return recommendations
            
            # 基于学习模式生成建议
            pattern = self.user_profile.get('study_pattern')
            
            
            if pattern == StudyPattern.MORNING_PERSON:
                recommendations.extend(self._generate_morning_recommendations())
            elif pattern == StudyPattern.NIGHT_OWL:
                recommendations.extend(self._generate_evening_recommendations())
            
            # 基于科目分布生成建议
            subject_dist = analysis.get('subject_distribution', {})
            if subject_dist and hasattr(self, "_generate_subject_balance_recommendations"):
                recommendations.extend(self._generate_subject_balance_recommendations(subject_dist))
            
            # 基于学习时长生成建议
            avg_length = analysis.get('average_session_length', 0)
            if avg_length > 0:
                recommendations.extend(self._generate_duration_recommendations(avg_length))
            
            # 存储建议
            for rec in recommendations:
                self.recommendations[rec.id] = rec
                self.recommendation_generated.emit(rec.id)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"生成学习建议失败: {e}")
            return []
    
    def _generate_morning_recommendations(self) -> List[StudyRecommendation]:
        """生成晨型人建议"""
        return [
            StudyRecommendation(
                id=f"morning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="充分利用晨间黄金时间",
                description="建议在6-9点安排最重要的学习任务，此时注意力最集中",
                priority=4,
                category="时间管理",
                estimated_benefit=0.8,
                difficulty=2,
                time_required=0,
                created_at=datetime.now()
            )
        ]
    
    def _generate_evening_recommendations(self) -> List[StudyRecommendation]:
        """生成夜型人建议"""
        return [
            StudyRecommendation(
                id=f"evening_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="优化夜间学习环境",
                description="建议在19-22点安排主要学习任务，注意保持良好的照明",
                priority=4,
                category="环境优化",
                estimated_benefit=0.7,
                difficulty=2,
                time_required=0,
                created_at=datetime.now()
            )
        ]
    
    def _generate_subject_balance_recommendations(self, subject_dist: Dict[str, int]) -> List[StudyRecommendation]:
        """生成科目平衡建议"""
        recommendations = []
        
        
        if not subject_dist:
            return recommendations
        
        total_time = sum(subject_dist.values())
        subjects = list(subject_dist.keys())
        
        # 检查是否有科目时间过少
        for subject, time_spent in subject_dist.items():
            percentage = time_spent / total_time
            if percentage < 0.15 and len(subjects) > 2:  # 少于15%且有多个科目:
                recommendations.append(
                    StudyRecommendation(
                        id=f"balance_{subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        title=f"增加{subject}学习时间",
                        description=f"{subject}的学习时间占比较低({percentage:.1%})，建议适当增加",
                        priority=3,
                        category="科目平衡",
                        estimated_benefit=0.6,
                        difficulty=2,
                        time_required=30,
                        created_at=datetime.now()
                    )
                )
        
        return recommendations
    
    def _generate_duration_recommendations(self, avg_length: float) -> List[StudyRecommendation]:
        """生成学习时长建议"""
        recommendations = []
        
        
        if avg_length < 20:
            recommendations.append(
                StudyRecommendation(
                    id=f"duration_short_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    title="延长学习会话时间",
                    description=f"当前平均学习时长{avg_length:.0f}分钟较短，建议延长至25-45分钟",
                    priority=3,
                    category="时间管理",
                    estimated_benefit=0.7,
                    difficulty=3,
                    time_required=0,
                    created_at=datetime.now()
                )
            )
        elif avg_length > 90:
            recommendations.append(
                StudyRecommendation(
                    id=f"duration_long_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    title="适当缩短学习会话",
                    description=f"当前平均学习时长{avg_length:.0f}分钟较长，建议分割为多个短会话",
                    priority=3,
                    category="效率优化",
                    estimated_benefit=0.6,
                    difficulty=2,
                    time_required=0,
                    created_at=datetime.now()
                )
            )
        
        return recommendations
    
    def get_learning_analytics(self, force_refresh: bool = False) -> Optional[LearningAnalytics]:
        """获取学习分析数据"""
        try:
            # 检查缓存
            if (not force_refresh and self.analytics_cache and
                self.last_analytics_update and
                datetime.now() - self.last_analytics_update < timedelta(hours=1)):
                return self.analytics_cache
            
            
            if not self.schedule_enhancement:
                return None
            
                return None
            
            # 计算分析数据
            sessions = list(self.schedule_enhancement.study_sessions.values())
            completed_sessions = [s for s in sessions if s.end_time]
            
            
            if not completed_sessions:
                return None
            
                return None
            
            # 总学习时间
            total_time = sum(s.duration for s in completed_sessions)
            
            # 平均会话长度
            avg_session = total_time / len(completed_sessions)
            
            # 最高效时间段
            productive_hours = self._analyze_productive_hours(completed_sessions)
            
            # 科目分布
            subject_dist = {}
            for session in completed_sessions:
                task = self.schedule_enhancement.get_task_by_id(session.task_id)
                if task:
                    subject = task.subject
                    subject_dist[subject] = subject_dist.get(subject, 0) + session.duration
            
            # 效率趋势（最近7天）
            recent_sessions = [
                s for s in completed_sessions
                if s.start_time >= datetime.now() - timedelta(days=7)
            ]
            efficiency_trend = [
                s.efficiency_rating or 3 for s in recent_sessions[-10:]  # 最近10次会话
            ]
            
            # 完成率
            all_tasks = list(self.schedule_enhancement.tasks.values())
            completed_tasks = [t for t in all_tasks if t.status.value == 'completed']
            completion_rate = len(completed_tasks) / len(all_tasks) if all_tasks else 0
            
            # 连续学习天数
            streak_days = self._calculate_study_streak(completed_sessions)
            
            analytics = LearningAnalytics(
                total_study_time=total_time,
                average_session_length=avg_session,
                most_productive_hours=productive_hours,
                subject_distribution=subject_dist,
                efficiency_trend=efficiency_trend,
                completion_rate=completion_rate,
                streak_days=streak_days
            )
            
            # 更新缓存
            self.analytics_cache = analytics
            self.last_analytics_update = datetime.now()
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"获取学习分析数据失败: {e}")
            return None
    
    def _calculate_study_streak(self, sessions: List) -> int:
        """计算连续学习天数"""
        try:
            if not sessions:
                return 0
            
            # 按日期分组
            study_dates = set()
            for session in sessions:
                study_dates.add(session.start_time.date())
            
            # 计算连续天数
            sorted_dates = sorted(study_dates, reverse=True)
            streak = 0
            current_date = datetime.now().date()
            
            for study_date in sorted_dates:
                if study_date == current_date or study_date == current_date - timedelta(days=streak):
                    streak += 1
                    current_date = study_date
                else:
                    break
            
            return streak
            
        except Exception as e:
            self.logger.error(f"计算学习连续天数失败: {e}")
            return 0
    
    def get_daily_study_summary(self, target_date: datetime = None) -> Dict[str, Any]:
        """获取每日学习总结"""
        try:
            if target_date is None:
                target_date = datetime.now()
            
            target_date = target_date.date()
            
            
            if not self.schedule_enhancement:
                return {}
            
                return {}
            
            # 获取当日会话
            daily_sessions = [
                s for s in self.schedule_enhancement.study_sessions.values()
                if s.start_time.date() == target_date and s.end_time
            ]
            
            # 获取当日任务
            daily_tasks = [
                t for t in self.schedule_enhancement.tasks.values()
                if (t.created_at.date() == target_date or
                    (t.completed_at and t.completed_at.date() == target_date))
            ]
            
            # 统计数据
            total_time = sum(s.duration for s in daily_sessions)
            completed_tasks = [t for t in daily_tasks if t.status.value == 'completed']
            avg_efficiency = (
                sum(s.efficiency_rating for s in daily_sessions if s.efficiency_rating) / 
                len([s for s in daily_sessions if s.efficiency_rating])
            ) if daily_sessions else 0
            
            return {
                'date': target_date,
                'total_study_time': total_time,
                'session_count': len(daily_sessions),
                'tasks_completed': len(completed_tasks),
                'tasks_total': len(daily_tasks),
                'average_efficiency': avg_efficiency,
                'goal_progress': min(total_time / self.user_profile.get('daily_study_goal'), 1.0)
            }
            
        except Exception as e:
            self.logger.error(f"获取每日学习总结失败: {e}")
            return {}
    
    def cleanup(self):
        """清理资源"""
        try:
            super().cleanup()
            self.logger.info("智能学习助手管理器已清理")
            
        except Exception as e:
            self.logger.error(f"清理智能学习助手失败: {e}")
