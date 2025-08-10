from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Subject:
    """科目模型，基于ClassIsland的Subject类"""
    
    id: str = ""
    name: str = ""
    initial: str = ""
    teacher_name: str = ""
    is_outdoor: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create_empty(cls) -> 'Subject':
        """创建空科目"""
        return cls(
            id="empty",
            name="???",
            initial="?",
            teacher_name=""
        )
        
    @classmethod
    def create_breaking(cls) -> 'Subject':
        """创建课间休息科目"""
        return cls(
            id="breaking",
            name="课间休息",
            initial="休",
            teacher_name=""
        )
        
    def get_first_name(self) -> str:
        """获取教师姓名的姓氏"""
        if not self.teacher_name.strip():
            return ""
            
        # 判断是否包含中文字符
        contains_chinese = any('\u4e00' <= char <= '\u9fff' for char in self.teacher_name)
        
        if contains_chinese:
            # 中文姓名处理
            common_compound_surnames = {
                "万俟", "司马", "上官", "欧阳", "夏侯", "诸葛", "闻人", "东方", "赫连", "皇甫",
                "尉迟", "公羊", "澹台", "公冶", "宗政", "濮阳", "淳于", "单于", "太叔", "申屠",
                "公孙", "仲孙", "轩辕", "令狐", "钟离", "宇文", "长孙", "慕容", "鲜于", "闾丘",
                "司徒", "司空", "亓官", "司寇", "子车", "颛孙", "端木", "巫马", "公西", "漆雕",
                "乐正", "壤驷", "公良", "拓跋", "夹谷", "宰父", "谷梁", "段干", "百里", "东郭",
                "南门", "呼延", "羊舌", "微生", "梁丘", "左丘", "东门", "西门", "南宫", "第五"
            }
            
            # 处理复姓
            if len(self.teacher_name) >= 2:
                surname = self.teacher_name[:2]
                if surname in common_compound_surnames:
                    return surname
                    
            # 单姓
            if len(self.teacher_name) >= 1:
                return self.teacher_name[0]
        else:
            # 英文姓名处理
            name_parts = self.teacher_name.split()
            if len(name_parts) > 1:
                return name_parts[-1]  # 返回姓氏（最后一个单词）
            elif len(name_parts) == 1:
                return self.teacher_name
                
        return ""
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "initial": self.initial,
            "teacher_name": self.teacher_name,
            "is_outdoor": self.is_outdoor,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subject':
        """从字典创建科目"""
        subject = cls()
        subject.id = data.get("id", "")
        subject.name = data.get("name", "")
        subject.initial = data.get("initial", "")
        subject.teacher_name = data.get("teacher_name", "")
        subject.is_outdoor = data.get("is_outdoor", False)
        
        # 处理时间戳
        created_at_str = data.get("created_at")
        if created_at_str:
            try:
                subject.created_at = datetime.fromisoformat(created_at_str)
            except ValueError:
                subject.created_at = datetime.now()
                
        updated_at_str = data.get("updated_at")
        if updated_at_str:
            try:
                subject.updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                subject.updated_at = datetime.now()
                
        return subject
        
    def __post_init__(self):
        """初始化后处理"""
        if not self.initial and self.name:
            self.initial = self.name[0] if self.name else ""
