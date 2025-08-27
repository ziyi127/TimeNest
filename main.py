from ui.mainwindow import DragWindow
from ui.tray import TrayManager
import sys

root = DragWindow()
root.geometry("200x100")
root.set_display_postion(850, 0)

# 创建系统托盘管理器
tray_manager = TrayManager(root)

# 运行主窗口
try:
    root.mainloop()
except KeyboardInterrupt:
    print("程序被用户中断")
except Exception as e:
    print(f"程序运行出错: {e}")
finally:
    # 通过托盘管理器来退出程序
    try:
        tray_manager.quit_window(None, None)
    except Exception as e:
        print(f"通过托盘管理器退出时出错: {e}")
        # 如果托盘管理器退出失败，则直接销毁窗口
        try:
            root.destroy()
        except:
            pass
        sys.exit(0)