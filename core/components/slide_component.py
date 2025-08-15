import logging
from typing import Any, List, Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from core.models.component_settings.slide_component_settings import (
    SlideComponentSettings,
)


class SlideComponent(QWidget):
    """幻灯片组件 - 轮播显示多个组件，基于ClassIsland的SlideComponent实现"""

    def __init__(self, settings: Optional[SlideComponentSettings] = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # 设置组件
        self.settings: SlideComponentSettings = settings or SlideComponentSettings()

        # 幻灯片相关变量
        self.components: List[QWidget] = []
        self.current_slide_index = 0
        self.is_sliding = False

        # 初始化UI
        self.init_ui()

        # 初始化内容
        self.update_content()

        # 连接设置变更信号
        self.settings.changed.connect(self.update_content)  # type: ignore

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

    def update_content(self):
        """更新内容"""
        # 清空现有组件
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.setParent(None)  # type: ignore

        # 添加新组件
        # 类型检查：确保 settings.children_list 是 List[QWidget] 类型
        if hasattr(self.settings, "children_list"):
            self.components = self.settings.children_list.copy()
        else:
            self.components = []

        for component in self.components:
            self.stacked_widget.addWidget(component)

        # 设置当前显示的幻灯片
        if len(self.components) > 0:
            self.stacked_widget.setCurrentIndex(0)
            self.current_slide_index = 0
        else:
            self.current_slide_index = 0

    def next_slide(self):
        """切换到下一个幻灯片"""
        # 类型已明确为 List[QWidget]，通过类型注解和检查确保正确性
        if len(self.components) == 0:
            return

        self.current_slide_index = (self.current_slide_index + 1) % len(self.components)
        self.stacked_widget.setCurrentIndex(self.current_slide_index)

    def previous_slide(self):
        """切换到上一个幻灯片"""
        # 类型已明确为 List[QWidget]，通过类型注解和检查确保正确性
        if len(self.components) == 0:
            return

        self.current_slide_index = (self.current_slide_index - 1) % len(self.components)
        self.stacked_widget.setCurrentIndex(self.current_slide_index)

    def start_slideshow(self):
        """开始幻灯片播放"""
        if not hasattr(self, "slide_timer"):
            self.slide_timer = QTimer()
            self.slide_timer.timeout.connect(self.next_slide)

        interval = getattr(self.settings, "interval", 5000)  # 默认5秒
        self.slide_timer.start(interval)
        self.is_sliding = True

    def stop_slideshow(self):
        """停止幻灯片播放"""
        if hasattr(self, "slide_timer"):
            self.slide_timer.stop()
        self.is_sliding = False

    def update_settings(self, settings: Any):
        """更新设置"""
        self.settings = settings  # type: ignore
        self.update_content()

        # 重新启动幻灯片（如果正在播放）
        if self.is_sliding:
            self.stop_slideshow()
            self.start_slideshow()
