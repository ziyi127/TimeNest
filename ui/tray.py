from PIL import Image, ImageDraw
import pystray
from pystray import Menu, MenuItem
import json
import os
import tkinter as tk
import platform
import sys
import logging
import threading
import time
from pathlib import Path

# 课程表设置界面已删除

# 导入UI设置界面
try:
    from ui.ui_settings import UISettings
    UI_SETTINGS_AVAILABLE = True
except ImportError:
    UI_SETTINGS_AVAILABLE = False
    print("无法导入UI设置模块")

class TrayManager:
    def __init__(self, root_window):
        self.root_window = root_window
        self.icon = None
        self.allow_drag = tk.BooleanVar(value=False)
        self.ui_settings = None
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        
        self.create_icon()
        
        # 初始化时设置窗口的可拖动状态
        if hasattr(self.root_window, 'set_draggable'):
            self.root_window.set_draggable(self.allow_drag.get())
    
    def create_image(self):
        """创建一个简单的托盘图标（跨平台兼容）"""
        width = 64
        height = 64
        
        # 根据平台选择合适的图标颜色
        if self.platform == "darwin":  # macOS
            bg_color = (0, 0, 0, 0)  # 透明背景
            icon_color = (0, 122, 255)  # macOS系统蓝色
        elif self.platform == "linux":
            bg_color = (255, 255, 255)  # 白色背景
            icon_color = (53, 132, 228)  # Linux系统蓝色
        else:  # Windows
            bg_color = (255, 255, 255)  # 白色背景
            icon_color = (0, 0, 0)  # 黑色
            
        image = Image.new('RGBA', (width, height), bg_color)
        dc = ImageDraw.Draw(image)
        
        # 绘制时钟图标
        dc.ellipse((8, 8, 56, 56), outline=icon_color, width=3)
        dc.line((32, 32, 32, 16), fill=icon_color, width=3)  # 时针
        dc.line((32, 32, 48, 32), fill=icon_color, width=2)  # 分针
        dc.ellipse((30, 30, 34, 34), fill=icon_color)  # 中心点
        
        return image
    
    def create_icon(self):
        """创建系统托盘图标（跨平台兼容）"""
        try:
            # 获取图标文件路径（使用pathlib处理跨平台路径）
            base_path = Path(__file__).parent.parent
            
            # 平台特定的图标文件
            icon_files = {
                'windows': 'TKtimetable.ico',
                'darwin': 'TKtimetable.icns',  # macOS
                'linux': 'TKtimetable.png'   # Linux
            }
            
            icon_filename = icon_files.get(self.platform, 'TKtimetable.ico')
            icon_path = base_path / icon_filename
            
            image = None
            
            # 尝试加载平台特定图标
            if icon_path.exists():
                try:
                    image = Image.open(icon_path)
                    self.logger.info(f"加载平台特定图标: {icon_path}")
                except Exception as e:
                    self.logger.warning(f"加载图标文件失败: {e}")
            
            # 如果加载失败，使用生成的图标
            if image is None:
                image = self.create_image()
                self.logger.info("使用生成的图标")
            
            # 创建菜单 - 使用英文菜单项避免编码问题
            menu = Menu(
                MenuItem('Allow Edit Window', self.toggle_drag, checked=lambda item: self.allow_drag.get()),
                MenuItem('UI Settings', self.open_ui_settings),
                MenuItem('Exit', self.quit_window)
            )
            
            # 创建托盘图标（使用英文标题避免编码问题）
            self.icon = pystray.Icon("Timetable", image, "Timetable", menu)
            
            # 启动托盘图标（跨平台兼容）
            self._start_icon_platform_specific()
            
        except Exception as e:
            self.logger.error(f"创建托盘图标时出错: {e}")
            # 即使托盘图标创建失败，程序也应该继续运行
            print("托盘图标创建失败，但程序将继续运行")
    
    def _start_icon_platform_specific(self):
        """平台特定的托盘图标启动方式"""
        try:
            # 根据平台选择合适的启动方式
            if self.platform == "darwin":  # macOS
                self._start_icon_macos()
            elif self.platform == "linux":
                self._start_icon_linux()
            else:  # Windows
                self._start_icon_windows()
        except Exception as e:
            self.logger.error(f"平台特定启动失败: {e}")
            self._start_icon_fallback()
    
    def _start_icon_windows(self):
        """Windows平台托盘图标启动"""
        try:
            # Windows使用标准方式
            def run_icon():
                try:
                    self.icon.run()
                    self.logger.info("Windows托盘图标运行中...")
                except Exception as e:
                    self.logger.error(f"Windows托盘图标运行失败: {e}")
            
            icon_thread = threading.Thread(target=run_icon, daemon=True)
            icon_thread.start()
            self.logger.info("Windows托盘图标已启动")
            
        except Exception as e:
            self.logger.error(f"Windows托盘启动失败: {e}")
            raise
    
    def _start_icon_macos(self):
        """macOS平台托盘图标启动"""
        try:
            # macOS使用标准方式
            def run_icon():
                try:
                    self.icon.run()
                    self.logger.info("macOS托盘图标运行中...")
                except Exception as e:
                    self.logger.error(f"macOS托盘图标运行失败: {e}")
            
            icon_thread = threading.Thread(target=run_icon, daemon=True)
            icon_thread.start()
            self.logger.info("macOS托盘图标已启动")
            
        except Exception as e:
            self.logger.error(f"macOS托盘启动失败: {e}")
            raise
    
    def _start_icon_linux(self):
        """Linux平台托盘图标启动"""
        try:
            # Linux使用标准方式
            def run_icon():
                try:
                    self.icon.run()
                    self.logger.info("Linux托盘图标运行中...")
                except Exception as e:
                    self.logger.error(f"Linux托盘图标运行失败: {e}")
            
            icon_thread = threading.Thread(target=run_icon, daemon=True)
            icon_thread.start()
            self.logger.info("Linux托盘图标已启动")
            
        except Exception as e:
            self.logger.error(f"Linux托盘启动失败: {e}")
            raise
    
    def _start_icon_fallback(self):
        """托盘图标启动的备用方案"""
        try:
            # 通用的备用启动方式
            def run_icon():
                try:
                    self.icon.run()
                    self.logger.info("托盘图标备用启动方式运行中...")
                except Exception as e:
                    self.logger.error(f"托盘图标备用启动失败: {e}")
            
            icon_thread = threading.Thread(target=run_icon, daemon=True)
            icon_thread.start()
            self.logger.info("托盘图标备用启动方式已启动")
            
        except Exception as e:
            self.logger.error(f"托盘图标所有启动方式均失败: {e}")
    
    def _start_icon(self):
        """启动托盘图标，适配不同平台"""
        try:
            # 首先尝试detached模式（推荐方式）
            self.icon.run_detached()
        except Exception as e:
            print(f"detached模式启动失败: {e}")
            
            try:
                # 如果detached模式失败，尝试在线程中运行
                import threading
                def run_icon():
                    try:
                        self.icon.run()
                    except Exception as e2:
                        print(f"线程模式启动失败: {e2}")
                
                # 在守护线程中运行托盘图标
                icon_thread = threading.Thread(target=run_icon, daemon=True)
                icon_thread.start()
            except Exception as e2:
                print(f"线程启动失败: {e2}")
                print("托盘图标启动失败，但程序将继续运行")
    
    def toggle_drag(self, icon, item):
        """切换悬浮窗的可拖动状态"""
        current_value = self.allow_drag.get()
        new_value = not current_value
        self.allow_drag.set(new_value)
        # 更新悬浮窗的可拖动状态
        if hasattr(self.root_window, 'set_draggable'):
            self.root_window.set_draggable(new_value)
    

    
    def open_ui_settings(self, icon, item):
        """打开UI设置界面"""
        # 打开UI设置界面
        if UI_SETTINGS_AVAILABLE:
            # 如果窗口已存在，将其带到前台
            if self.ui_settings and hasattr(self.ui_settings, 'window') and self.ui_settings.window.winfo_exists():
                self.ui_settings.window.lift()
                self.ui_settings.window.focus_force()
            else:
                # 创建新窗口，传递悬浮窗实例
                self.ui_settings = UISettings(self.root_window, self.root_window)
        else:
            print("UI设置功能不可用")
    
    def quit_window(self, icon, item):
        """退出程序"""
        # 退出程序
        try:
            # 清理资源
            if self.ui_settings:
                try:
                    self.ui_settings.window.destroy()
                except Exception as e:
                    print(f"销毁UI设置窗口时出错: {e}")
                self.ui_settings = None
            
            # 调用窗口的关闭方法以保存位置
            if hasattr(self.root_window, 'on_closing'):
                try:
                    self.root_window.on_closing()
                except Exception as e:
                    print(f"调用窗口关闭方法时出错: {e}")
            else:
                try:
                    self.root_window.destroy()
                except Exception as e:
                    print(f"销毁窗口时出错: {e}")
            
            # 停止托盘图标
            if self.icon:
                try:
                    self.icon.stop()
                except Exception as e:
                    print(f"停止托盘图标时出错: {e}")
                finally:
                    self.icon = None
        except Exception as e:
            print(f"退出程序时出错: {e}")
        finally:
            # 使用sys.exit优雅退出
            import sys
            try:
                sys.exit(0)
            except:
                # 如果sys.exit失败，使用os._exit强制退出
                import os
                os._exit(0)