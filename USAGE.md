# TimeNest 课程表桌面应用使用说明

## 运行环境准备

1. 确保系统已安装 Python 3.6 或更高版本
2. 安装 Tk 库（在 Arch Linux 上使用 `sudo pacman -S tk`）
3. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```
4. 激活虚拟环境：
   ```bash
   source venv/bin/activate
   ```
5. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

## 运行程序

```bash
source venv/bin/activate && python main.py
```

## 使用方法

1. 程序启动后会在桌面显示课程表悬浮窗
2. 悬浮窗默认处于鼠标穿透状态，不会影响其他应用程序的操作
3. 右键点击系统托盘图标可打开菜单
4. 通过托盘菜单可以：
   - 切换拖拽状态（允许编辑悬浮窗位置）
   - 打开课程表设置
   - 打开UI设置
   - 退出程序

## 功能说明

- **桌面悬浮窗**: 课程表以半透明悬浮窗形式显示在桌面上
- **实时课程信息**: 显示当前时间和日期，以及当前和下一节课的详细信息
- **系统托盘管理**: 最小化到系统托盘，支持快速操作
- **UI个性化**: 支持背景颜色、文字颜色、透明度等界面设置
- **拖拽移动**: 可以拖拽窗口到任意位置
- **鼠标穿透**: 可设置鼠标穿透功能，避免误操作

## 配置文件

- `timetable.json`: 课程表数据文件
- `timetable_ui_settings.json`: UI设置数据文件
- `timetable_window_position.json`: 窗口位置数据文件