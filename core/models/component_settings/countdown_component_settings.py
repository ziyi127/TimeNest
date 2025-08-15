from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor

from core.components.base_component import ComponentSettings


class CountDownComponentSettings(ComponentSettings):
    """倒计时组件设置类"""

    # 设置变更信号
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._count_down_name: str = "倒计时"
        self._over_time: datetime = datetime.now()
        self._days_left: int = 0
        self._font_color: QColor = QColor(255, 0, 0)  # 红色
        self._font_size: int = 16
        self._is_compact_mode_enabled: bool = False
        self._count_down_connector: str = "还有"

    @property
    def count_down_name(self) -> str:
        """倒计时名称"""
        return self._count_down_name

    @count_down_name.setter
    def count_down_name(self, value: str) -> None:
        if value != self._count_down_name:
            self._count_down_name = value
            self.changed.emit()

    @property
    def over_time(self) -> datetime:
        """结束时间"""
        return self._over_time

    @over_time.setter
    def over_time(self, value: datetime) -> None:
        if value != self._over_time:
            self._over_time = value
            self.changed.emit()

    @property
    def days_left(self) -> int:
        """剩余天数"""
        return self._days_left

    @days_left.setter
    def days_left(self, value: int) -> None:
        if value != self._days_left:
            self._days_left = max(0, value)  # 确保不为负数
            self.changed.emit()

    @property
    def font_color(self) -> QColor:
        """字体颜色"""
        return self._font_color

    @font_color.setter
    def font_color(self, value: QColor) -> None:
        if value != self._font_color:
            self._font_color = value
            self.changed.emit()

    @property
    def font_size(self) -> int:
        """字体大小"""
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        if value != self._font_size:
            self._font_size = value
            self.changed.emit()

    @property
    def is_compact_mode_enabled(self) -> bool:
        """是否启用紧凑模式"""
        return self._is_compact_mode_enabled

    @is_compact_mode_enabled.setter
    def is_compact_mode_enabled(self, value: bool) -> None:
        if value != self._is_compact_mode_enabled:
            self._is_compact_mode_enabled = value
            self.changed.emit()

    @property
    def count_down_connector(self) -> str:
        """倒计时连接符"""
        return self._count_down_connector

    @count_down_connector.setter
    def count_down_connector(self, value: str) -> None:
        if value != self._count_down_connector:
            self._count_down_connector = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建设置对象
    settings = CountDownComponentSettings()

    # 测试属性
    print(f"Count down name: {settings.count_down_name}")
    print(f"Over time: {settings.over_time}")
    print(f"Days left: {settings.days_left}")
    print(f"Font color: {settings.font_color}")
    print(f"Font size: {settings.font_size}")
    print(f"Is compact mode enabled: {settings.is_compact_mode_enabled}")
    print(f"Count down connector: {settings.count_down_connector}")

    # 测试设置变更
    settings.count_down_name = "考试倒计时"
    print(f"After setting count_down_name='考试倒计时': {settings.count_down_name}")

    settings.font_color = QColor(0, 255, 0)
    print(f"After setting font_color=green: {settings.font_color}")
