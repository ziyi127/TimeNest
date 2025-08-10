# TimeNest 档案模型
# 完整重构自Classisland的Profile类

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class TimeNestProfile(QObject):
    """TimeNest档案模型类"""
    
    # 档案变更信号
    profile_changed = Signal()
    
    def __init__(self, name: str = "Default"):
        """
        初始化档案模型
        
        Args:
            name: 档案名称
        """
        super().__init__()
        
        self.name = name
        self.id = "default-profile-id"
        self.time_layouts = {}
        self.class_plans = {}
        self.subjects = {}
        self.class_plan_groups = {}
        
        # 初始化默认数据
        self._initialize_default_data()
        
        logger.info(f"TimeNest档案模型已初始化: {name}")
    
    def _initialize_default_data(self):
        """初始化默认数据"""
        # 初始化课表群
        self.class_plan_groups = {
            "default-group": {
                "id": "default-group",
                "name": "默认",
                "is_global": False
            },
            "global-group": {
                "id": "global-group",
                "name": "全局课表群",
                "is_global": True
            }
        }
        
        logger.debug("默认数据已初始化")
    
    def load_from_file(self, file_path: Path) -> bool:
        """
        从文件加载档案数据
        
        Args:
            file_path: 档案文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 更新档案数据
                self._update_from_dict(data)
                logger.info(f"档案已从文件加载: {file_path}")
                return True
            else:
                logger.warning(f"档案文件不存在: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"加载档案文件时出错: {e}")
            return False
    
    def save_to_file(self, file_path: Path) -> bool:
        """
        保存档案数据到文件
        
        Args:
            file_path: 档案文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 准备保存数据
            data = self._to_dict()
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"档案已保存到文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存档案文件时出错: {e}")
            return False
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """从字典更新数据"""
        self.name = data.get('name', self.name)
        self.id = data.get('id', self.id)
        self.time_layouts = data.get('time_layouts', self.time_layouts)
        self.class_plans = data.get('class_plans', self.class_plans)
        self.subjects = data.get('subjects', self.subjects)
        self.class_plan_groups = data.get('class_plan_groups', self.class_plan_groups)
        
        # 发送变更信号
        self.profile_changed.emit()
    
    def _to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'id': self.id,
            'time_layouts': self.time_layouts,
            'class_plans': self.class_plans,
            'subjects': self.subjects,
            'class_plan_groups': self.class_plan_groups
        }
    
    def get_time_layout(self, layout_id: str) -> Optional[Dict[str, Any]]:
        """
        获取时间表
        
        Args:
            layout_id: 时间表ID
            
        Returns:
            时间表数据或None
        """
        return self.time_layouts.get(layout_id)
    
    def add_time_layout(self, layout_id: str, layout_data: Dict[str, Any]):
        """
        添加时间表
        
        Args:
            layout_id: 时间表ID
            layout_data: 时间表数据
        """
        self.time_layouts[layout_id] = layout_data
        self.profile_changed.emit()
    
    def get_class_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        获取课表
        
        Args:
            plan_id: 课表ID
            
        Returns:
            课表数据或None
        """
        return self.class_plans.get(plan_id)
    
    def add_class_plan(self, plan_id: str, plan_data: Dict[str, Any]):
        """
        添加课表
        
        Args:
            plan_id: 课表ID
            plan_data: 课表数据
        """
        self.class_plans[plan_id] = plan_data
        self.profile_changed.emit()
    
    def get_subject(self, subject_id: str) -> Optional[Dict[str, Any]]:
        """
        获取科目
        
        Args:
            subject_id: 科目ID
            
        Returns:
            科目数据或None
        """
        return self.subjects.get(subject_id)
    
    def add_subject(self, subject_id: str, subject_data: Dict[str, Any]):
        """
        添加科目
        
        Args:
            subject_id: 科目ID
            subject_data: 科目数据
        """
        self.subjects[subject_id] = subject_data
        self.profile_changed.emit()
    
    def get_class_plan_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        获取课表群
        
        Args:
            group_id: 课表群ID
            
        Returns:
            课表群数据或None
        """
        return self.class_plan_groups.get(group_id)
    
    def add_class_plan_group(self, group_id: str, group_data: Dict[str, Any]):
        """
        添加课表群
        
        Args:
            group_id: 课表群ID
            group_data: 课表群数据
        """
        self.class_plan_groups[group_id] = group_data
        self.profile_changed.emit()
    
    def get_all_time_layouts(self) -> Dict[str, Any]:
        """获取所有时间表"""
        return self.time_layouts.copy()
    
    def get_all_class_plans(self) -> Dict[str, Any]:
        """获取所有课表"""
        return self.class_plans.copy()
    
    def get_all_subjects(self) -> Dict[str, Any]:
        """获取所有科目"""
        return self.subjects.copy()
    
    def get_all_class_plan_groups(self) -> Dict[str, Any]:
        """获取所有课表群"""
        return self.class_plan_groups.copy()
    
    def clear(self):
        """清空所有数据"""
        self.time_layouts.clear()
        self.class_plans.clear()
        self.subjects.clear()
        self.class_plan_groups.clear()
        self.profile_changed.emit()
        logger.debug("档案数据已清空")
    
    def is_empty(self) -> bool:
        """检查档案是否为空"""
        return (len(self.time_layouts) == 0 and 
                len(self.class_plans) == 0 and 
                len(self.subjects) == 0 and 
                len(self.class_plan_groups) == 0)
