from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, time
import json


@dataclass
class TimeLayoutItem:
    """时间布局项模型，基于ClassIsland的TimeLayoutItem类"""
    
    id: str = ""
    start_time: str = "00:00"  # HH:MM格式
    end_time: str = "00:00"    # HH:MM格式
    time_type: int = 0  # 0=上课, 1=课间, 2=分割线, 3=行动
    is_hide_default: bool = False
    default_class_id: str = ""
    break_name: str = ""
    action_set: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def break_name_text(self) -> str:
        """获取课间名称文本"""
        return self.break_name if self.break_name else "课间休息"
        
    @property
    def last(self) -> int:
        """获取持续时间（分钟）"""
        try:
            start = datetime.strptime(self.start_time, "%H:%M")
            end = datetime.strptime(self.end_time, "%H:%M")
            duration = end - start
            return int(duration.total_seconds() / 60)
        except ValueError:
            return 0
            
    @property
    def time_type_text(self) -> str:
        """获取时间类型文本"""
        type_map = {
            0: "上课",
            1: "课间休息",
            2: "分割线",
            3: "行动"
        }
        return type_map.get(self.time_type, "未知")
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "time_type": self.time_type,
            "is_hide_default": self.is_hide_default,
            "default_class_id": self.default_class_id,
            "break_name": self.break_name,
            "action_set": self.action_set,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeLayoutItem':
        """从字典创建时间布局项"""
        item = cls()
        item.id = data.get("id", "")
        item.start_time = data.get("start_time", "00:00")
        item.end_time = data.get("end_time", "00:00")
        item.time_type = data.get("time_type", 0)
        item.is_hide_default = data.get("is_hide_default", False)
        item.default_class_id = data.get("default_class_id", "")
        item.break_name = data.get("break_name", "")
        item.action_set = data.get("action_set")
        
        # 处理时间戳
        created_at_str = data.get("created_at")
        if created_at_str:
            try:
                item.created_at = datetime.fromisoformat(created_at_str)
            except ValueError:
                item.created_at = datetime.now()
                
        updated_at_str = data.get("updated_at")
        if updated_at_str:
            try:
                item.updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                item.updated_at = datetime.now()
                
        return item
        
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.time_type_text} {self.start_time}-{self.end_time}"


@dataclass
class TimeLayout:
    """时间布局模型，基于ClassIsland的TimeLayout类"""
    
    id: str = ""
    name: str = "新时间表"
    layouts: List[TimeLayoutItem] = field(default_factory=list)
    is_activated: bool = False
    is_activated_manually: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_valid_time_layout_items(self) -> List[TimeLayoutItem]:
        """获取有效的课程表时间点（上课、课间、分割线）"""
        return [item for item in self.layouts if item.time_type in [0, 1, 2]]
        
    def get_class_time_points(self) -> List[TimeLayoutItem]:
        """获取所有上课时间点"""
        return [item for item in self.layouts if item.time_type == 0]
        
    def get_break_time_points(self) -> List[TimeLayoutItem]:
        """获取所有课间时间点"""
        return [item for item in self.layouts if item.time_type == 1]
        
    def insert_time_point(self, index: int, item: TimeLayoutItem):
        """在指定索引处插入时间点"""
        self.layouts.insert(index, item)
        self.updated_at = datetime.now()
        
    def remove_time_point(self, item: TimeLayoutItem):
        """删除指定的时间点"""
        if item in self.layouts:
            self.layouts.remove(item)
            self.updated_at = datetime.now()
            
    def get_class_index(self, time_layout_item: TimeLayoutItem) -> int:
        """获取时间点在上课时间点中的索引"""
        class_time_points = self.get_class_time_points()
        try:
            return class_time_points.index(time_layout_item)
        except ValueError:
            return -1
            
    def sort_layouts(self):
        """对时间布局项进行排序"""
        try:
            self.layouts.sort(key=lambda x: datetime.strptime(x.start_time, "%H:%M"))
            self.updated_at = datetime.now()
        except ValueError:
            pass  # 如果时间格式不正确，不进行排序
            
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "layouts": [item.to_dict() for item in self.layouts],
            "is_activated": self.is_activated,
            "is_activated_manually": self.is_activated_manually,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeLayout':
        """从字典创建时间布局"""
        layout = cls()
        layout.id = data.get("id", "")
        layout.name = data.get("name", "新时间表")
        layout.is_activated = data.get("is_activated", False)
        layout.is_activated_manually = data.get("is_activated_manually", False)
        
        # 处理时间布局项
        layouts_data = data.get("layouts", [])
        layout.layouts = [TimeLayoutItem.from_dict(item_data) for item_data in layouts_data]
        
        # 处理时间戳
        created_at_str = data.get("created_at")
        if created_at_str:
            try:
                layout.created_at = datetime.fromisoformat(created_at_str)
            except ValueError:
                layout.created_at = datetime.now()
                
        updated_at_str = data.get("updated_at")
        if updated_at_str:
            try:
                layout.updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                layout.updated_at = datetime.now()
                
        return layout
        
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = str(datetime.now().timestamp())
