from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from models.subject import Subject  # type: ignore
from models.time_layout import TimeLayout, TimeLayoutItem


@dataclass
class ClassInfo:
    """课程信息模型，基于ClassIsland的ClassInfo类"""
    
    id: str = ""
    subject_id: str = ""
    index: int = 0
    is_changed_class: bool = False
    is_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "index": self.index,
            "is_changed_class": self.is_changed_class,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassInfo':
        """从字典创建课程信息"""
        class_info = cls()
        class_info.id = data.get("id", "")
        class_info.subject_id = data.get("subject_id", "")
        class_info.index = data.get("index", 0)
        class_info.is_changed_class = data.get("is_changed_class", False)
        class_info.is_enabled = data.get("is_enabled", True)
        
        # 处理时间戳
        created_at_str = data.get("created_at")
        if created_at_str:
            try:
                class_info.created_at = datetime.fromisoformat(created_at_str)
            except ValueError:
                class_info.created_at = datetime.now()
                
        updated_at_str = data.get("updated_at")
        if updated_at_str:
            try:
                class_info.updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                class_info.updated_at = datetime.now()
                
        return class_info
        
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class TimeRule:
    """时间规则模型，基于ClassIsland的TimeRule类"""
    
    week_day: int = 0  # 0=周日, 1=周一, ..., 6=周六
    week_count_div: int = 0  # 0=不轮换, n=第n周
    week_count_div_total: int = 2  # 总周数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "week_day": self.week_day,
            "week_count_div": self.week_count_div,
            "week_count_div_total": self.week_count_div_total
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeRule':
        """从字典创建时间规则"""
        rule = cls()
        rule.week_day = data.get("week_day", 0)
        rule.week_count_div = data.get("week_count_div", 0)
        rule.week_count_div_total = data.get("week_count_div_total", 2)
        return rule


@dataclass
class ClassPlanGroup:
    """课表群模型，基于ClassIsland的ClassPlanGroup类"""
    
    # 默认课表群 GUID
    DEFAULT_GROUP_GUID = "ACAF4EF0-E261-4262-B941-34EA93CB4369"
    
    # 全局课表群 GUID
    GLOBAL_GROUP_GUID = "00000000-0000-0000-0000-000000000000"
    
    id: str = ""
    name: str = "新课表群"
    is_global: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "is_global": self.is_global,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassPlanGroup':
        """从字典创建课表群"""
        group = cls()
        group.id = data.get("id", "")
        group.name = data.get("name", "新课表群")
        group.is_global = data.get("is_global", False)
        
        # 处理时间戳
        created_at_str = data.get("created_at")
        if created_at_str:
            try:
                group.created_at = datetime.fromisoformat(created_at_str)
            except ValueError:
                group.created_at = datetime.now()
                
        updated_at_str = data.get("updated_at")
        if updated_at_str:
            try:
                group.updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                group.updated_at = datetime.now()
                
        return group
        
    @classmethod
    def create_default_group(cls) -> 'ClassPlanGroup':
        """创建默认课表群"""
        return cls(
            id=cls.DEFAULT_GROUP_GUID,
            name="默认",
            is_global=False
        )
        
    @classmethod
    def create_global_group(cls) -> 'ClassPlanGroup':
        """创建全局课表群"""
        return cls(
            id=cls.GLOBAL_GROUP_GUID,
            name="全局课表群",
            is_global=True
        )


@dataclass
class ClassPlan:
    """课表模型，基于ClassIsland的ClassPlan类"""
    
    id: str = ""
    name: str = "新课表"
    time_layout_id: str = ""
    classes: List[ClassInfo] = field(default_factory=list)  # type: ignore
    time_rule: TimeRule = field(default_factory=TimeRule)
    is_activated: bool = False
    is_overlay: bool = False
    overlay_source_id: Optional[str] = None
    overlay_setup_time: datetime = field(default_factory=datetime.now)
    is_enabled: bool = True
    associated_group: str = ClassPlanGroup.DEFAULT_GROUP_GUID
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_valid_time_layout_items(self, time_layout: TimeLayout) -> List[TimeLayoutItem]:
        """获取有效的课程表时间点"""
        if not time_layout:
            return []
            
        # 获取时间布局中的有效时间点
        valid_items: List[TimeLayoutItem] = time_layout.get_valid_time_layout_items()
        
        # 获取课程映射
        time_layout_map: Dict[int, ClassInfo] = {class_info.index: class_info for class_info in self.classes}
        filtered_items: List[TimeLayoutItem] = []
        
        # 正向搜索过滤
        is_prev_enabled = True
        for item in valid_items:
            if item.time_type == 0:  # 上课时间点
                class_index = time_layout.get_class_index(item)
                if class_index in time_layout_map:
                    is_prev_enabled = time_layout_map[class_index].is_enabled
            if is_prev_enabled:
                filtered_items.append(item)
                
        # 反向搜索过滤
        is_prev_enabled = True
        final_items: List[TimeLayoutItem] = []
        for item in reversed(filtered_items):
            if item.time_type == 0:  # 上课时间点
                class_index = time_layout.get_class_index(item)
                if class_index in time_layout_map:
                    is_prev_enabled = time_layout_map[class_index].is_enabled
            if is_prev_enabled:
                final_items.append(item)
                
        return list(reversed(final_items))
        
    def refresh_classes_list(self, time_layout: TimeLayout):
        """刷新课程列表，使其与时间布局对齐"""
        if not time_layout:
            return
            
        # 获取上课时间点
        class_time_points: List[TimeLayoutItem] = time_layout.get_class_time_points()
        target_count = len(class_time_points)
        
        # 调整课程列表长度
        current_count = len(self.classes)
        if current_count < target_count:
            # 添加新课程
            for i in range(target_count - current_count):
                class_info = ClassInfo()
                class_info.index = current_count + i
                self.classes.append(class_info)
        elif current_count > target_count:
            # 移除多余课程
            self.classes = self.classes[:target_count]
            
        # 更新课程索引和时间布局引用
        for i, class_info in enumerate(self.classes):
            class_info.index = i
            
        self.updated_at = datetime.now()
        
    def refresh_is_changed_class(self, overlay_source_plan: Optional['ClassPlan'] = None):
        """刷新换课标记"""
        if not overlay_source_plan or len(self.classes) != len(overlay_source_plan.classes):
            # 清除所有换课标记
            for class_info in self.classes:
                class_info.is_changed_class = False
            return
            
        # 比较每个课程
        for i, class_info in enumerate(self.classes):
            if i < len(overlay_source_plan.classes):
                source_class_info = overlay_source_plan.classes[i]
                class_info.is_changed_class = (class_info.subject_id != source_class_info.subject_id)
            else:
                class_info.is_changed_class = False
                
        self.updated_at = datetime.now()
        
    def remove_time_point_safe(self, time_point: TimeLayoutItem, time_layout: TimeLayout):
        """安全地删除时间点"""
        # 移除对应的课程
        classes_to_remove: List[ClassInfo] = []
        for class_info in self.classes:
            if class_info.index < len(time_layout.layouts):
                layout_item = time_layout.layouts[class_info.index]
                if layout_item == time_point:
                    classes_to_remove.append(class_info)
                    
        for class_info in classes_to_remove:
            self.classes.remove(class_info)
            
        # 刷新课程列表
        self.refresh_classes_list(time_layout)
        self.updated_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "time_layout_id": self.time_layout_id,
            "classes": [class_info.to_dict() for class_info in self.classes],
            "time_rule": self.time_rule.to_dict(),
            "is_activated": self.is_activated,
            "is_overlay": self.is_overlay,
            "overlay_source_id": self.overlay_source_id,
            "overlay_setup_time": self.overlay_setup_time.isoformat() if self.overlay_setup_time else None,
            "is_enabled": self.is_enabled,
            "associated_group": self.associated_group,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassPlan':
        """从字典创建课表"""
        plan = cls()
        plan.id = data.get("id", "")
        plan.name = data.get("name", "新课表")
        plan.time_layout_id = data.get("time_layout_id", "")
        plan.is_activated = data.get("is_activated", False)
        plan.is_overlay = data.get("is_overlay", False)
        plan.overlay_source_id = data.get("overlay_source_id")
        plan.is_enabled = data.get("is_enabled", True)
        plan.associated_group = data.get("associated_group", ClassPlanGroup.DEFAULT_GROUP_GUID)
        
        # 处理时间规则
        time_rule_data = data.get("time_rule", {})
        plan.time_rule = TimeRule.from_dict(time_rule_data)
        
        # 处理课程列表
        classes_data = data.get("classes", [])
        plan.classes = [ClassInfo.from_dict(class_data) for class_data in classes_data]
        
        # 处理时间戳
        overlay_setup_time_str = data.get("overlay_setup_time")
        if overlay_setup_time_str:
            try:
                plan.overlay_setup_time = datetime.fromisoformat(overlay_setup_time_str)
            except ValueError:
                plan.overlay_setup_time = datetime.now()
                
        created_at_str = data.get("created_at")
        if created_at_str:
            try:
                plan.created_at = datetime.fromisoformat(created_at_str)
            except ValueError:
                plan.created_at = datetime.now()
                
        updated_at_str = data.get("updated_at")
        if updated_at_str:
            try:
                plan.updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                plan.updated_at = datetime.now()
                
        return plan
        
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.time_rule:
            self.time_rule = TimeRule()