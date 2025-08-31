from PIL import Image, ImageDraw
import json
import os
import tkinter as tk
import platform

# 尝试导入pystray，Linux环境下也可以使用
try:
    import pystray
    from pystray import Menu, MenuItem
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    print("无法导入pystray库")

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
        
        # 添加托盘可用性检查
        self.root_window.after(1000, self._check_tray_availability)
    
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
        # 尝试创建系统托盘图标
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
            MenuItem('允许编辑悬浮窗位置', self.toggle_drag, checked=lambda item: self.allow_drag.get()),
            MenuItem('UI设置', self.open_ui_settings),
            MenuItem('退出', self.quit_window)
        )
        
        try:
            self.icon = pystray.Icon("test_icon", image, menu=menu)
            # 在Linux环境下，尝试使用不同的方法创建托盘图标
            if platform.system() == "Linux":
                # 先尝试运行图标
                try:
                    self.icon.run_detached()
                except Exception as e:
                    print(f"首次创建系统托盘图标失败: {e}")
                    # 如果失败，等待一段时间后重试
                    import time
                    time.sleep(0.5)
                    try:
                        self.icon.run_detached()
                    except Exception as e2:
                        print(f"重试创建系统托盘图标失败: {e2}")
                        print("系统托盘功能在当前Linux环境中不可用")
                        self.icon = None
            else:
                self.icon.run_detached()
        except Exception as e:
            print(f"创建系统托盘图标失败: {e}")
            print("系统托盘功能在当前环境中不可用")
            self.icon = None
    
    def toggle_drag(self, icon, item):
        # 切换允许拖拽状态
        self.allow_drag.set(not self.allow_drag.get())
        # 应用新的拖拽状态到主窗口
        self.root_window.set_draggable(self.allow_drag.get())
        print(f"允许拖拽状态: {self.allow_drag.get()}")
        
        # 更新菜单项文本
        self._update_menu_text()
    
    def _update_menu_text(self):
        """更新菜单项文本"""
        # 在Linux环境下，更新右键菜单的文本
        import platform
        if platform.system() == "Linux" and hasattr(self.root_window, 'context_menu') and self.root_window.context_menu:
            # 获取当前菜单项
            menu = self.root_window.context_menu
            
            # 根据当前状态更新菜单项文本
            if self.allow_drag.get():
                menu.entryconfig(0, label="不允许编辑悬浮窗位置")
            else:
                menu.entryconfig(0, label="允许编辑悬浮窗位置")
    

    
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
            try:
                self.icon.run()
            except Exception as e:
                print(f"运行系统托盘时出错: {e}")
                print("系统托盘功能在当前环境中不可用")
    
    def _check_tray_availability(self):
        """检查系统托盘是否可用，如果不可用则尝试重新创建"""
        if PYSTRAY_AVAILABLE and not self.icon:
            print("尝试重新创建系统托盘图标...")
            self.create_icon()
            # 如果重新创建成功，绑定右键菜单事件到主窗口
            if self.icon:
                print("系统托盘图标重新创建成功")
            else:
                # 如果仍然失败，继续定期检查
                self.root_window.after(5000, self._check_tray_availability)