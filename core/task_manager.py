#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务管理器
管理用户的任务和待办事项
"""

import logging
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tasks_file = Path.home() / '.timenest' / 'tasks.json'
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """加载任务数据"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                self.logger.info(f"加载了 {len(self.tasks)} 个任务")
            else:
                self.tasks = self._get_default_tasks()
                self.save_tasks()
        except Exception as e:
            self.logger.error(f"加载任务失败: {e}")
            self.tasks = self._get_default_tasks()
    
    def save_tasks(self):
        """保存任务数据"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            self.logger.info("任务数据已保存")
        except Exception as e:
            self.logger.error(f"保存任务失败: {e}")
    
    def _get_default_tasks(self) -> List[Dict[str, Any]]:
        """获取默认任务数据"""
        today = date.today().isoformat()
        tasks_data = [
            ('完成数学作业', '第三章习题1-20题', '高', '进行中', '2025-01-16'),
            ('准备英语演讲', '主题：我的大学生活', '中', '进行中', '2025-01-18'),
            ('实验报告', '数据结构实验三', '高', '进行中', '2025-01-20'),
            ('复习计算机网络', '第1-5章内容', '中', '已完成', '2025-01-15'),
            ('购买教材', '下学期课程教材', '低', '已完成', '2025-01-10')
        ]

        return [
            {
                'id': i + 1,
                'title': title,
                'description': desc,
                'priority': priority,
                'status': status,
                'due_date': due_date,
                'created_date': today
            }
            for i, (title, desc, priority, status, due_date) in enumerate(tasks_data)
        ]
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务"""
        return self.tasks.copy()
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.get('id') == task_id:
                return task.copy()
        return None
    
    def add_task(self, task_data: Dict[str, Any]) -> bool:
        """添加新任务"""
        try:
            # 生成新的ID
            max_id = max([task.get('id', 0) for task in self.tasks], default=0)
            new_id = max_id + 1
            
            # 创建新任务
            new_task = {
                'id': new_id,
                'title': task_data.get('title', ''),
                'description': task_data.get('description', ''),
                'priority': task_data.get('priority', '中'),
                'status': task_data.get('status', '进行中'),
                'due_date': task_data.get('due_date', ''),
                'created_date': date.today().isoformat()
            }
            
            self.tasks.append(new_task)
            self.save_tasks()
            self.logger.info(f"添加任务: {new_task['title']}")
            return True
        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return False

    def add_simple_task(self, title: str, description: str = "", priority: str = "medium", due_date: str = "") -> bool:
        """添加新任务（简化接口）"""
        try:
            # 转换优先级
            priority_map = {
                "low": "低",
                "medium": "中",
                "high": "高",
                "urgent": "紧急"
            }

            task_data = {
                'title': title,
                'description': description,
                'priority': priority_map.get(priority, "中"),
                'due_date': due_date,
                'status': '进行中'
            }

            return self.add_task(task_data)
        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        try:
            original_count = len(self.tasks)
            self.tasks = [task for task in self.tasks if task.get('id') != task_id]

            if len(self.tasks) < original_count:
                self.save_tasks()
                self.logger.info(f"删除任务: ID {task_id}")
                return True

            self.logger.warning(f"未找到要删除的任务: ID {task_id}")
            return False
        except Exception as e:
            self.logger.error(f"删除任务失败: {e}")
            return False

    def update_task_status(self, task_id: int, status: str) -> bool:
        """更新任务状态"""
        try:
            for task in self.tasks:
                if task.get('id') == task_id:
                    task['status'] = status
                    self.save_tasks()
                    self.logger.info(f"更新任务状态: ID {task_id} -> {status}")
                    return True

            self.logger.warning(f"未找到要更新的任务: ID {task_id}")
            return False
        except Exception as e:
            self.logger.error(f"更新任务状态失败: {e}")
            return False

    def toggle_task_complete(self, task_id: int) -> bool:
        """切换任务完成状态"""
        try:
            for task in self.tasks:
                if task.get('id') == task_id:
                    current_status = task.get('status', '进行中')
                    new_status = '已完成' if current_status != '已完成' else '进行中'
                    task['status'] = new_status
                    self.save_tasks()
                    self.logger.info(f"切换任务状态: ID {task_id} -> {new_status}")
                    return True

            self.logger.warning(f"未找到要切换的任务: ID {task_id}")
            return False
        except Exception as e:
            self.logger.error(f"切换任务状态失败: {e}")
            return False

    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> bool:
        """更新任务信息"""
        try:
            for task in self.tasks:
                if task.get('id') == task_id:
                    # 更新允许的字段
                    updatable_fields = ['title', 'description', 'priority', 'status', 'due_date']
                    for field in updatable_fields:
                        if field in task_data:
                            task[field] = task_data[field]

                    self.save_tasks()
                    self.logger.info(f"更新任务: ID {task_id}")
                    return True

            self.logger.warning(f"未找到要更新的任务: ID {task_id}")
            return False
        except Exception as e:
            self.logger.error(f"更新任务失败: {e}")
            return False

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取任务"""
        try:
            for task in self.tasks:
                if task.get('id') == task_id:
                    return task.copy()
            return None
        except Exception as e:
            self.logger.error(f"获取任务失败: {e}")
            return None

    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """根据状态获取任务"""
        try:
            return [task.copy() for task in self.tasks if task.get('status') == status]
        except Exception as e:
            self.logger.error(f"获取任务失败: {e}")
            return []

    def get_tasks_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """根据优先级获取任务"""
        try:
            return [task.copy() for task in self.tasks if task.get('priority') == priority]
        except Exception as e:
            self.logger.error(f"获取任务失败: {e}")
            return []

    def clear_completed_tasks(self) -> bool:
        """清除已完成的任务"""
        try:
            original_count = len(self.tasks)
            self.tasks = [task for task in self.tasks if task.get('status') != '已完成']

            if len(self.tasks) < original_count:
                self.save_tasks()
                cleared_count = original_count - len(self.tasks)
                self.logger.info(f"清除了 {cleared_count} 个已完成任务")
                return True
            else:
                self.logger.info("没有已完成的任务需要清除")
                return False
        except Exception as e:
            self.logger.error(f"清除已完成任务失败: {e}")
            return False

    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> bool:
        """更新任务"""
        try:
            for i, task in enumerate(self.tasks):
                if task.get('id') == task_id:
                    # 更新任务数据
                    self.tasks[i].update(task_data)
                    self.save_tasks()
                    self.logger.info(f"更新任务: {task_id}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"更新任务失败: {e}")
            return False
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """更新任务状态"""
        return self.update_task(task_id, {'status': status})
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        try:
            for i, task in enumerate(self.tasks):
                if task.get('id') == task_id:
                    deleted_task = self.tasks.pop(i)
                    self.save_tasks()
                    self.logger.info(f"删除任务: {deleted_task['title']}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"删除任务失败: {e}")
            return False
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """根据状态获取任务"""
        return [task for task in self.tasks if task.get('status') == status]
    
    def get_tasks_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """根据优先级获取任务"""
        return [task for task in self.tasks if task.get('priority') == priority]
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """获取逾期任务"""
        today = date.today().isoformat()
        overdue_tasks = []
        
        for task in self.tasks:
            if (task.get('status') != '已完成' and 
                task.get('due_date') and 
                task.get('due_date') < today):
                overdue_tasks.append(task)
        
        return overdue_tasks
    
    def get_task_statistics(self) -> Dict[str, int]:
        """获取任务统计信息"""
        stats = {
            'total': len(self.tasks),
            'in_progress': len(self.get_tasks_by_status('进行中')),
            'completed': len(self.get_tasks_by_status('已完成')),
            'overdue': len(self.get_overdue_tasks())
        }
        return stats
