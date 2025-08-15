from typing import Any, Dict, List

from PySide6.QtCore import Signal

from core.components.base_component import ComponentSettings


class RollingComponentSettings(ComponentSettings):
    """滚动组件设置类"""

    # 设置变更信号
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._children_list: List[Any] = []  # 子组件列表
        self._speed_pixel_per_second: float = 40.0
        self._is_pause_enabled: bool = True
        self._pause_offset_x: float = 0.0
        self._pause_seconds: float = 10.0
        self._pause_on_rule: bool = False
        self._stop_on_rule: bool = False
        self._pause_rule: Dict[str, Any] = {}  # 规则设置
        self._stop_rule: Dict[str, Any] = {}  # 停止规则设置
        self._scroll_texts: List[str] = []  # 滚动文本列表
        self._scroll_interval: int = 2  # 滚动间隔（秒）

    @property
    def children_list(self) -> List[Any]:
        """子组件列表"""
        return self._children_list

    @children_list.setter
    def children_list(self, value: List[Any]) -> None:
        if value != self._children_list:
            self._children_list = value
            self.changed.emit()

    @property
    def speed_pixel_per_second(self) -> float:
        """滚动速度(像素/秒)"""
        return self._speed_pixel_per_second

    @speed_pixel_per_second.setter
    def speed_pixel_per_second(self, value: float) -> None:
        if value != self._speed_pixel_per_second:
            self._speed_pixel_per_second = value
            self.changed.emit()

    @property
    def is_pause_enabled(self) -> bool:
        """是否启用暂停"""
        return self._is_pause_enabled

    @is_pause_enabled.setter
    def is_pause_enabled(self, value: bool) -> None:
        if value != self._is_pause_enabled:
            self._is_pause_enabled = value
            self.changed.emit()

    @property
    def pause_offset_x(self) -> float:
        """暂停偏移量X"""
        return self._pause_offset_x

    @pause_offset_x.setter
    def pause_offset_x(self, value: float) -> None:
        if value != self._pause_offset_x:
            self._pause_offset_x = value
            self.changed.emit()

    @property
    def pause_seconds(self) -> float:
        """暂停秒数"""
        return self._pause_seconds

    @pause_seconds.setter
    def pause_seconds(self, value: float) -> None:
        if value != self._pause_seconds:
            self._pause_seconds = value
            self.changed.emit()

    @property
    def pause_on_rule(self) -> bool:
        """是否根据规则暂停"""
        return self._pause_on_rule

    @pause_on_rule.setter
    def pause_on_rule(self, value: bool) -> None:
        if value != self._pause_on_rule:
            self._pause_on_rule = value
            self.changed.emit()

    @property
    def stop_on_rule(self) -> bool:
        """是否根据规则停止"""
        return self._stop_on_rule

    @stop_on_rule.setter
    def stop_on_rule(self, value: bool) -> None:
        if value != self._stop_on_rule:
            self._stop_on_rule = value
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
    def stop_rule(self) -> Dict[str, Any]:
        """停止规则"""
        return self._stop_rule

    @stop_rule.setter
    def stop_rule(self, value: Dict[str, Any]) -> None:
        if value != self._stop_rule:
            self._stop_rule = value
            self.changed.emit()

    @property
    def scroll_texts(self) -> List[str]:
        """滚动文本列表"""
        return self._scroll_texts

    @scroll_texts.setter
    def scroll_texts(self, value: List[str]) -> None:
        if value != self._scroll_texts:
            self._scroll_texts = value
            self.changed.emit()

    @property
    def scroll_interval(self) -> int:
        """滚动间隔（秒）"""
        return self._scroll_interval

    @scroll_interval.setter
    def scroll_interval(self, value: int) -> None:
        if value != self._scroll_interval:
            self._scroll_interval = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建设置对象
    settings = RollingComponentSettings()

    # 测试属性
    print(f"Speed pixel per second: {settings.speed_pixel_per_second}")
    print(f"Is pause enabled: {settings.is_pause_enabled}")
    print(f"Pause seconds: {settings.pause_seconds}")
    print(f"Pause on rule: {settings.pause_on_rule}")
    print(f"Stop on rule: {settings.stop_on_rule}")

    # 测试设置变更
    settings.speed_pixel_per_second = 50.0
    print(
        f"After setting speed_pixel_per_second=50.0: {settings.speed_pixel_per_second}"
    )

    settings.is_pause_enabled = False
    print(f"After setting is_pause_enabled=False: {settings.is_pause_enabled}")
