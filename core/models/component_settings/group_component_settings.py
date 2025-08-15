from typing import List, Optional

from PySide6.QtCore import QObject, Signal


class GroupComponentSettings(QObject):
    """分组组件设置类"""

    # 设置变更信号
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._children: List[str] = []  # 子组件列表
        self._show_border: bool = True  # 是否显示边框
        self._border_color: Optional[str] = None  # 边框颜色
        self._title: str = ""  # 分组标题

    @property
    def children(self) -> List[str]:
        """子组件列表"""
        return self._children

    @children.setter
    def children(self, value: List[str]) -> None:
        if value != self._children:
            self._children = value
            self.changed.emit()

    @property
    def show_border(self) -> bool:
        """是否显示边框"""
        return self._show_border

    @show_border.setter
    def show_border(self, value: bool) -> None:
        if value != self._show_border:
            self._show_border = value
            self.changed.emit()

    @property
    def border_color(self) -> Optional[str]:
        """边框颜色"""
        return self._border_color

    @border_color.setter
    def border_color(self, value: Optional[str]) -> None:
        if value != self._border_color:
            self._border_color = value
            self.changed.emit()

    @property
    def title(self) -> str:
        """分组标题"""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if value != self._title:
            self._title = value
            self.changed.emit()


# 测试代码
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建设置对象
    settings = GroupComponentSettings()

    # 测试属性
    print(f"Children: {settings.children}")

    # 测试设置变更
    settings.children = ["时钟", "日期", "天气"]
    print(f"After setting children=['时钟', '日期', '天气']: {settings.children}")
