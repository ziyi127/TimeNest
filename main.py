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
    # 确保程序完全退出
    try:
        root.destroy()
    except:
        pass
    sys.exit(0)