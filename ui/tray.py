from PIL import Image, ImageDraw
import pystray
from pystray import Menu, MenuItem
import json
import os
import tkinter as tk
import platform
import sys

# 导入课程表设置界面
try:
    from ui.timetable_settings import TimetableSettings
    TIMETABLE_AVAILABLE = True
except ImportError:
    TIMETABLE_AVAILABLE = False
    print("无法导入课程表设置模块")

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
        self.timetable_settings = None
        self.ui_settings = None
        
        self.create_icon()
        
        # 初始化时设置窗口的可拖动状态
        if hasattr(self.root_window, 'set_draggable'):
            self.root_window.set_draggable(self.allow_drag.get())
    
    def create_image(self):
        """创建一个简单的托盘图标"""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        # 绘制一个简单的时钟图标
        dc.ellipse((10, 10, 54, 54), outline=(0, 0, 0), width=2)
        dc.line((32, 32, 32, 15), fill=(0, 0, 0), width=2)  # 时针
        dc.line((32, 32, 45, 32), fill=(0, 0, 0), width=2)  # 分针
        return image
    
    def create_icon(self):
        """创建系统托盘图标"""
        try:
            # 检查图标文件路径
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TKtimetable.ico')
            
            if os.path.exists(icon_path):
                try:
                    image = Image.open(icon_path)
                except Exception as e:
                    print(f"加载图标文件失败: {e}")
                    # 如果图标文件加载失败，使用生成的图像
                    image = self.create_image()
            else:
                # 如果图标文件不存在，使用生成的图像
                image = self.create_image()
            
            # 创建菜单 - 使用英文菜单项避免编码问题
            menu = Menu(
                MenuItem('Allow Edit Window', self.toggle_drag, checked=lambda item: self.allow_drag.get()),
                MenuItem('Timetable Settings', self.open_timetable_settings),
                MenuItem('UI Settings', self.open_ui_settings),
                MenuItem('Exit', self.quit_window)
            )
            
            # 创建托盘图标（使用英文标题避免编码问题）
            self.icon = pystray.Icon("Timetable", image, "Timetable", menu)
            
            # 启动托盘图标 - 使用更简单的方式
            try:
                # 直接运行托盘图标，不尝试detached模式
                import threading
                def run_icon():
                    try:
                        self.icon.run()
                        print("托盘图标运行中...")
                    except Exception as e:
                        print(f"托盘图标运行失败: {e}")
                
                # 在守护线程中运行托盘图标
                icon_thread = threading.Thread(target=run_icon, daemon=True)
                icon_thread.start()
                print("托盘图标已启动")
                
                # 添加延迟确保托盘图标有时间初始化
                import time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"启动托盘图标时出错: {e}")
                print("托盘图标启动失败，但程序将继续运行")
            
        except Exception as e:
            print(f"创建托盘图标时出错: {e}")
            # 即使托盘图标创建失败，程序也应该继续运行
            print("托盘图标创建失败，但程序将继续运行")
    
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
    
    def open_timetable_settings(self, icon, item):
        """打开课程表设置界面"""
        # 打开课程表设置界面
        if TIMETABLE_AVAILABLE:
            # 如果窗口已存在，将其带到前台
            if self.timetable_settings and self.timetable_settings.window.winfo_exists():
                self.timetable_settings.window.lift()
                self.timetable_settings.window.focus_force()
            else:
                # 创建新窗口
                self.timetable_settings = TimetableSettings(self.root_window)
        else:
            print("课程表设置功能不可用")
    
    def open_ui_settings(self, icon, item):
        """打开UI设置界面"""
        # 打开UI设置界面
        if UI_SETTINGS_AVAILABLE:
            # 如果窗口已存在，将其带到前台
            if self.ui_settings and self.ui_settings.window.winfo_exists():
                self.ui_settings.window.lift()
                self.ui_settings.window.focus_force()
            else:
                # 创建新窗口
                self.ui_settings = UISettings(self.root_window, self.root_window)
        else:
            print("UI设置功能不可用")
    
    def quit_window(self, icon, item):
        """退出程序"""
        # 退出程序
        try:
            # 清理资源
            if self.timetable_settings:
                try:
                    self.timetable_settings.window.destroy()
                except Exception as e:
                    print(f"销毁课程表设置窗口时出错: {e}")
                self.timetable_settings = None
            
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