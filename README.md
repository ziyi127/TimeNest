# TimeNest for instructional all-in-one PC 课程表大屏应用

<div align="center">

<img src="https://github.com/ziyi127/TimeNest/tree/TkTT/TKtimetable.ico" style="width:64%; max-width:500px; display:block; margin:auto;" alt="TimeNest Logo">

**一个简洁的课程表显示工具**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ziyi127/TimeNest.svg)](https://github.com/ziyi127/TimeNest/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/ziyi127/TimeNest.svg)](https://github.com/ziyi127/TimeNest/issues)

[🌐 官方网站](https://timenest.qzz.io) | [📖 文档](https://timenest.qzz.io/docs) | [🐞 问题反馈](https://github.com/ziyi127/TimeNest/issues) | [💬 讨论](https://github.com/ziyi127/TimeNest/discussions)
[🐧QQ群](https://qun.qq.com/universal-share/share?ac=1&authKey=EEu9RUAgQSCdOaeoQHVAubu1PZF4f7LnE6zXGhu1bitT4exPdY%2Fgx5c5RK9z6Jen&busi_data=eyJncm91cENvZGUiOiI3MTk5Mzc1ODYiLCJ0b2tlbiI6IjU0cmxuZlJMaWFnNmtzS3E4cFN0bGZRckZkZnp6SDhEcjM3bG50Y0lKRTZFaWxWRFBiZ0craGdjV1ZkKzNyWm8iLCJ1aW4iOiIzMjQ5MTk2OTk2In0%3D&data=cylTd1VkYAIVgm4wHNRQGp58TXGOdcF5LnvhD-d0joV5GnI2PG8IJ3wvDuw6E3fhUfWL4iitXT4Nx8sXOLnwfQ&svctype=4&tempid=h5_group_info)
</div>

TimeNest 是一个简洁美观的桌面课程表应用。它以悬浮窗的形式显示在桌面上，可以随时查看当前和下一节课的信息。

## 功能特点

- **桌面悬浮窗**: 课程表以半透明悬浮窗形式显示在桌面上
- **实时课程信息**: 显示当前时间和日期，以及当前和下一节课的详细信息
- **系统托盘管理**: 最小化到系统托盘，支持快速操作
- **课程表设置**: 可自定义一周五天（周一至周五）的课程安排
- **UI个性化**: 支持背景颜色、文字颜色、透明度等界面设置
- **拖拽移动**: 可以拖拽窗口到任意位置
- **鼠标穿透**: 可设置鼠标穿透功能，避免误操作(此功能由于tkinter本身限制正在开发)

## 课表显示逻辑

程序会根据当前时间和课表数据动态显示课程信息：

1. **正在上课**: 如果当前时间在某节课的时间段内，会显示"正在上课: 课程名 (开始时间-结束时间)"
2. **课间休息**: 如果当前时间不在任何课程时间段内，但当天还有未开始的课程，会显示"课间休息: 距离下一节课还有X分钟"
3. **周末**: 周六和周日如果没有课程安排，会显示"今天休息，无课程安排"
4. **放学后**: 如果当天课程已结束，会显示"今天课程已结束"
5. **无课程安排**: 如果当天没有任何课程，会显示"今天没有课程安排"
6. **第一节课前**: 如果当天有课程但还没到第一节课时间，会显示"今天没有课程进行中"

程序还会显示下一节课的信息，包括课程名称和距离开始的时间。

## 源码编辑说明

1. 确保系统已安装 Python 3.6 或更高版本
2. 下载或克隆本项目到本地
3. 安装requirements.txt中所写依赖包（可以使用`pip install -r requirements.txt`命令）
4. 若您使用的是Linux发行版，请您查看"Linux桌面环境适配说明"来安装依赖

### Linux桌面环境适配说明

对于Linux用户，特别是使用KDE或GNOME桌面环境的用户，可能需要手动安装额外的依赖包以确保程序正常运行：

**Ubuntu/Debian及UOS，deepin，kylin等信创系统**:
```bash
# 安装基本依赖
sudo apt-get update
sudo apt-get install python3-pil python3-pil.imagetk python3-tk
pip3 install pystray

# 基于GNOME的桌面环境额外需要
sudo apt-get install gnome-shell-extension-appindicator

# 基于KDE的桌面环境可能需要
sudo apt-get install libappindicator3-1
```

**请注意，Fedora系统需要安装这些依赖**:
```bash
# 安装基本依赖
sudo dnf install python3-pillow python3-pillow-tk python3-tkinter
pip3 install pystray
```

**注意事项**:
- 在某些Linux发行版中，当依赖完成安装后，可能需要重启桌面环境或系统才能使系统托盘正常显示
- 如果系统托盘无法正常显示，请检查桌面环境是否支持系统托盘功能
- KDE和GNOME环境下推荐使用不同的窗口类型以获得最佳显示效果
- 如果遇到"Failed to dock icon"错误，请确保已安装系统托盘支持组件，如Ubuntu/Debian系统中的`gnome-shell-extension-appindicator`或Fedora系统中的相应组件
- 在Linux环境下，程序会自动尝试保持窗口置顶，如果发现窗口被其他应用遮挡，可以尝试重启程序
- 在Linux环境中若托盘菜单无法显示，可以直接右键点击悬浮窗来打开托盘菜单

## 文件结构

- `main.py`: 程序入口文件
- `timetable.json`: 课程表数据文件
- `timetable_ui_settings.json`: UI设置数据文件
- `ui/`: UI相关模块目录
  - `mainwindow.py`: 主窗口实现
  - `tray.py`: 系统托盘实现
  - `ui_settings.py`: UI设置窗口
  - `temp_class_change.py`: 临时调课设置窗口
  - `timetable_wizard.py`: 课程表向导窗口
  - `classtable_wizard.py`: 课表设置窗口

## 开发说明

本程序部分由AI开发，请仔细甄别，使用Python和Tkinter，Pystray，PIL库实现。

## 🏆 致谢

### 核心贡献者

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/hujinming0722ispassword">
        <img src="https://github.com/hujinming0722ispassword.png" width="100" alt="hujinming0722ispassword" />
        <br />
        <sub><b>hujinming0722ispassword</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/ziyi127">
        <img src="https://github.com/ziyi127.png" width="100" alt="ziyi127" />
        <br />
        <sub><b>ziyi127</b></sub>
      </a>
    </td>
    <!-- 我们一直在等第三个人，加入我们的团队，一起完善这个项目！ -->

</table>

## 许可证

Apache-2.0 license
