from PIL import Image, ImageDraw
import json
import os
import tkinter as tk
import platform

# Linux环境下不导入pystray以避免兼容性问题
if platform.system() != "Linux":
    try:
        import pystray
        from pystray import Menu, MenuItem
        PYSTRAY_AVAILABLE = True
    except ImportError:
        PYSTRAY_AVAILABLE = False
        print("无法导入pystray库")
else:
    PYSTRAY_AVAILABLE = False
    print("Linux环境下禁用系统托盘功能")

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
        self.create_icon()
        
        # UI设置窗口实例
        self.ui_settings = None
    
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
        # Linux环境下不创建系统托盘图标
        if not PYSTRAY_AVAILABLE:
            print("系统托盘功能不可用")
            return
        
        # 使用项目目录下的图标文件
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TKtimetable.ico')
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            # 如果图标文件不存在，使用生成的图像
            image = self.create_image()
        
        # 添加允许拖拽的状态变量，默认为关闭状态
        self.allow_drag = tk.BooleanVar(value=False)
        
        menu = Menu(
            MenuItem('允许编辑悬浮窗', self.toggle_drag, checked=lambda item: self.allow_drag.get()),
            MenuItem('UI设置', self.open_ui_settings),
            MenuItem('退出', self.quit_window)
        )
        
        self.icon = pystray.Icon("test_icon", image, menu=menu)
        self.icon.run_detached()
    
    def toggle_drag(self, icon, item):
        # 切换允许拖拽状态
        self.allow_drag.set(not self.allow_drag.get())
        # 应用新的拖拽状态到主窗口
        self.root_window.set_draggable(self.allow_drag.get())
        print(f"允许拖拽状态: {self.allow_drag.get()}")
    

    
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
            if self.ui_settings:
                try:
                    self.ui_settings.window.destroy()
                except:
                    pass
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
    
    def run(self):
        if self.icon:
            self.icon.run()