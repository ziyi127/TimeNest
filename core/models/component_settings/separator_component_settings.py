from PySide6.QtCore import QObject, Signal


class SeparatorComponentSettings(QObject):
    """分割线组件设置类"""

    # 设置变更信号
    changed = Signal()

    def __init__(self):
        super().__init__()
        self._is_vertical: bool = False  # 是否为垂直分割线
        self._line_width: int = 1  # 线宽

    @property
    def is_vertical(self) -> bool:
        """是否为垂直分割线"""
        return self._is_vertical

    @is_vertical.setter
    def is_vertical(self, value: bool) -> None:
        if value != self._is_vertical:
            self._is_vertical = value
            self.changed.emit()

    @property
    def line_width(self) -> int:
        """线宽"""
        return self._line_width

    @line_width.setter
    def line_width(self, value: int) -> None:
        if value != self._line_width:
            self._line_width = max(1, value)  # 确保线宽至少为1
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建设置对象
    settings = SeparatorComponentSettings()

    # 测试属性
    print(f"Is vertical: {settings.is_vertical}")
    print(f"Line width: {settings.line_width}")

    # 测试设置变更
    settings.is_vertical = True
    print(f"After setting is_vertical=True: {settings.is_vertical}")

    settings.line_width = 3
    print(f"After setting line_width=3: {settings.line_width}")
