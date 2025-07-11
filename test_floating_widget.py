#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试浮窗功能
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def test_floating_widget():
    """测试浮窗功能"""
    logger = setup_logging()
    logger.info("开始测试浮窗功能...")
    
    try:
        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName('TimeNest Floating Widget Test')
        app.setQuitOnLastWindowClosed(False)
        
        # 创建模拟的应用管理器
        class MockAppManager:
            def __init__(self):
                self.config_manager = MockConfigManager()
                self.theme_manager = MockThemeManager()
        
        class MockConfigManager:
            def get_config(self, key, default=None, section=None):
                # 返回默认的浮窗配置
                if key == 'floating_widget':
                    return {
                        'width': 400,
                        'height': 60,
                        'opacity': 0.9,
                        'border_radius': 30,
                        'mouse_transparent': False,  # 禁用鼠标穿透以便测试
                        'fixed_position': True,
                        'auto_rotate_content': False,  # 禁用轮播以便看到所有内容
                        'rotation_interval': 5000,
                        'modules': {
                            'time': {'enabled': True, 'order': 0},
                            'schedule': {'enabled': True, 'order': 1}
                        }
                    }
                return default
            
            def set_config(self, key, value, section=None):
                pass
        
        class MockThemeManager:
            def get_current_theme(self):
                class MockTheme:
                    def __init__(self):
                        self.name = 'light'
                        self.type = MockThemeType()
                
                class MockThemeType:
                    def __init__(self):
                        self.value = 'light'
                
                return MockTheme()
        
        # 创建模拟应用管理器
        app_manager = MockAppManager()
        
        # 导入并创建浮窗
        from ui.floating_widget.smart_floating_widget import SmartFloatingWidget
        logger.info("✓ 浮窗类导入成功")
        
        # 创建浮窗
        floating_widget = SmartFloatingWidget(app_manager)
        logger.info("✓ 浮窗创建成功")
        
        # 显示浮窗
        floating_widget.show()
        logger.info("✓ 浮窗显示成功")
        
        # 设置定时器来检查浮窗状态
        def check_status():
            logger.info(f"浮窗状态检查:")
            logger.info(f"  - 可见: {floating_widget.isVisible()}")
            logger.info(f"  - 位置: ({floating_widget.x()}, {floating_widget.y()})")
            logger.info(f"  - 大小: {floating_widget.width()}x{floating_widget.height()}")
            logger.info(f"  - 模块数量: {len(floating_widget.modules)}")
            logger.info(f"  - 启用模块: {floating_widget.enabled_modules}")
            logger.info(f"  - 当前文本: '{floating_widget.content_label.text()}'")
            
            # 手动触发更新
            floating_widget.update_display()
        
        # 立即检查一次，然后每5秒检查一次
        QTimer.singleShot(1000, check_status)
        status_timer = QTimer()
        status_timer.timeout.connect(check_status)
        status_timer.start(5000)
        
        # 显示测试信息
        QMessageBox.information(
            None, 
            "浮窗测试", 
            "浮窗测试启动成功！\n\n"
            "浮窗应该显示在屏幕顶部中央。\n"
            "如果只显示'TimeNest 智能浮窗'，请检查控制台日志。\n\n"
            "点击确定开始测试..."
        )
        
        logger.info("浮窗测试运行中...")
        
        # 运行应用
        return app.exec()
        
    except Exception as e:
        logger.error(f"浮窗测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            QMessageBox.critical(
                None,
                "测试失败",
                f"浮窗测试失败:\n\n{str(e)}"
            )
        except:
            print(f"测试失败: {e}")
        
        return 1

if __name__ == '__main__':
    sys.exit(test_floating_widget())
