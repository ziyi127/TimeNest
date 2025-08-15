from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal


class SlideComponentSettings(QObject):
    """幻灯片组件设置类"""

    # 设置变更信号
    changed = Signal()

    def __init__(self):
        super().__init__()
        self._children: List[Any] = []  # 子组件列表
        self._auto_slide_enabled: bool = True  # 是否自动轮播
        self._slide_interval_seconds: int = 5  # 轮播间隔（秒）
        self._is_pause_on_rule_enabled: bool = False  # 是否根据规则暂停
        self._pause_rule: Dict[str, Any] = {}  # 暂停规则

    @property
    def children_list(self) -> List[Any]:
        """子组件列表"""
        return self._children

    @children_list.setter  # 修改属性名为 children_list 以避免与 QObject.children 冲突
    def children_list(self, value: List[Any]) -> None:
        if value != self._children:
            self._children = value
            self.changed.emit()

    @property
    def auto_slide_enabled(self) -> bool:
        """是否自动轮播"""
        return self._auto_slide_enabled

    @auto_slide_enabled.setter
    def auto_slide_enabled(self, value: bool) -> None:
        if value != self._auto_slide_enabled:
            self._auto_slide_enabled = value
            self.changed.emit()

    @property
    def slide_interval_seconds(self) -> int:
        """轮播间隔（秒）"""
        return self._slide_interval_seconds

    @slide_interval_seconds.setter
    def slide_interval_seconds(self, value: int) -> None:
        if value != self._slide_interval_seconds:
            self._slide_interval_seconds = value
            self.changed.emit()

    @property
    def is_pause_on_rule_enabled(self) -> bool:
        """是否根据规则暂停"""
        return self._is_pause_on_rule_enabled

    @is_pause_on_rule_enabled.setter
    def is_pause_on_rule_enabled(self, value: bool) -> None:
        if value != self._is_pause_on_rule_enabled:
            self._is_pause_on_rule_enabled = value
            self.changed.emit()

    @property
    def pause_rule(self) -> Dict[str, Any]:
        """暂停规则"""
        return self._pause_rule

    @pause_rule.setter
    def pause_rule(self, value: Dict[str, Any]) -> None:
        if value != self._pause_rule:
            self._pause_rule = value
            self.changed.emit()

    @property
    def interval(self) -> int:
        """轮播间隔（毫秒）"""
        return self._slide_interval_seconds * 1000
