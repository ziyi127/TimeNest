from PIL import Image, ImageDraw
import pystray
from pystray import Menu, MenuItem
import json
import os
import tkinter as tk

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
        self.create_icon()
        
        # 课程表设置窗口实例
        self.timetable_settings = None
        
        # UI设置窗口实例
        self.ui_settings = None
        
        # 初始化时设置窗口的可拖动状态
        if hasattr(self.root_window, 'set_draggable'):
            self.root_window.set_draggable(self.allow_drag.get())
    
    def create_image(self):
        # 创建一个简单的图标
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2 - 10, height // 2 - 10, width // 2 + 10, height // 2 + 10),
            fill=(0, 0, 0))
        return image
    
    def create_icon(self):
        # 使用项目目录下的图标文件
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TKtimetable.ico')
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            # 如果图标文件不存在，使用生成的图像
            image = self.create_image()
        
        menu = Menu(
            MenuItem('允许编辑悬浮窗', self.toggle_drag, checked=lambda item: self.allow_drag.get()),
            MenuItem('课程表设置', self.open_timetable_settings),
            MenuItem('UI设置', self.open_ui_settings),
            MenuItem('退出', self.quit_window)
        )
        
        self.icon = pystray.Icon("test_icon", image, menu=menu)
        self.icon.run_detached()
    
    def toggle_drag(self, icon, item):
        self.allow_drag.set(not self.allow_drag.get())
        print(f"切换拖动状态: {self.allow_drag.get()}")
        # 更新悬浮窗的可拖动状态
        if hasattr(self.root_window, 'set_draggable'):
            self.root_window.set_draggable(self.allow_drag.get())
    
    def open_timetable_settings(self, icon, item):
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
        # 退出程序
        try:
            # 清理资源
            if self.timetable_settings:
                try:
                    self.timetable_settings.window.destroy()
                except:
                    pass
                self.timetable_settings = None
            
            if self.ui_settings:
                try:
                    self.ui_settings.window.destroy()
                except:
                    pass
                self.ui_settings = None
            
            # 确保所有Tkinter事件都被处理
            try:
                self.root_window.update_idletasks()
                self.root_window.update()
            except:
                pass  # 窗口可能已经被销毁
            
            # 调用窗口的关闭方法以保存位置
            if hasattr(self.root_window, 'on_closing'):
                try:
                    self.root_window.on_closing()
                except Exception as e:
                    print(f"调用窗口关闭方法时出错: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                try:
                    self.root_window.destroy()
                except Exception as e:
                    print(f"销毁窗口时出错: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 停止托盘图标
            if self.icon:
                try:
                    # 停止托盘图标
                    self.icon.stop()
                except Exception as e:
                    print(f"停止托盘图标时出错: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    self.icon = None
        except Exception as e:
            print(f"退出程序时出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 使用Tkinter的quit方法优雅退出
            try:
                if hasattr(self.root_window, 'quit'):
                    self.root_window.quit()
            except:
                pass
            
            # 确保所有线程都被终止
            import threading
            import time
            for thread in threading.enumerate():
                if thread != threading.current_thread() and thread.is_alive():
                    try:
                        thread.join(timeout=1.0)
                    except:
                        pass
            
            # 延迟确保所有资源都被释放
            time.sleep(0.5)
            
            # 最终强制退出
            import os
            import sys
            # 先尝试正常退出
            try:
                # 直接调用主窗口的quit方法
                if hasattr(self.root_window, 'quit'):
                    self.root_window.quit()
            except:
                pass
            
            # 再尝试sys.exit
            try:
                sys.exit(0)
            except:
                # 如果sys.exit失败，使用os._exit强制退出
                os._exit(0)
    
    def run(self):
        if self.icon:
            self.icon.run()