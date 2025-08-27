#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest-TkTT - 跨平台课程表悬浮窗应用
兼容 Windows, macOS, Linux 系统
"""

import sys
import os
import platform
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.mainwindow import DragWindow
    from ui.tray import TrayManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖已安装: pip install -r requirements.txt")
    sys.exit(1)

# 配置日志
from ui.logger_config import setup_logger
logger = setup_logger("TimeNest", level="INFO")

def get_platform_config():
    """获取平台特定配置"""
    system = platform.system().lower()
    configs = {
        'windows': {
            'default_x': 850,
            'default_y': 0,
            'alpha_min': 0.1,
            'alpha_max': 1.0
        },
        'darwin': {  # macOS
            'default_x': 100,
            'default_y': 100,
            'alpha_min': 0.3,
            'alpha_max': 1.0
        },
        'linux': {
            'default_x': 100,
            'default_y': 100,
            'alpha_min': 0.3,
            'alpha_max': 1.0
        }
    }
    return configs.get(system, configs['linux'])

def main():
    """主函数"""
    try:
        logger.info("启动 TimeNest-TkTT 应用")
        logger.info(f"运行平台: {platform.system()} {platform.release()}")
        
        # 获取平台配置
        config = get_platform_config()
        
        # 创建主窗口
        root = DragWindow()
        
        # 设置默认位置和大小
        root.geometry("250x120")
        # 位置设置已在load_window_position中处理
        
        # 创建系统托盘管理器
        tray_manager = TrayManager(root)
        
        logger.info("应用启动成功")
        
        # 运行主窗口
        try:
            root.mainloop()
        except KeyboardInterrupt:
            logger.info("程序被用户中断")
        except Exception as e:
            logger.error(f"程序运行出错: {e}", exc_info=True)
        finally:
            # 清理资源
            try:
                if tray_manager and hasattr(tray_manager, 'quit_window'):
                    tray_manager.quit_window(None, None)
            except Exception as e:
                logger.error(f"清理资源时出错: {e}")
                try:
                    root.destroy()
                except:
                    pass
                sys.exit(0)
                
    except Exception as e:
        logger.error(f"应用启动失败: {e}", exc_info=True)
        print(f"应用启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()