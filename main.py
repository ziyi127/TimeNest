from ui.mainwindow import DragWindow
from ui.tray import TrayManager

root = DragWindow()
root.geometry("200x100")
root.set_display_postion(850, 0)

# 创建系统托盘管理器
tray_manager = TrayManager(root)

# 运行主窗口
root.mainloop()