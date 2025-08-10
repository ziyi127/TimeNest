# TimeNest 🕐

智能课程表桌面应用 - 完整重构自ClassIsland的Python实现

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-GUI-red.svg)](https://www.qt.io/qt-for-python)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 项目概述

TimeNest是一个基于Python 3.12+和PySide6开发的智能课程表桌面应用程序，完整重构自ClassIsland的C#实现。它提供了现代化的悬浮窗界面，支持智能课程表管理、可视化课程安排、多样化提醒系统和个性化主题定制。

## 🌟 核心功能

### 📚 智能课程表管理
- 实时显示当前课程信息
- 支持今日/明日课表切换
- 智能冲突检测机制
- 灵活的课程配置

### ⏰ 可视化课程安排
- 直观的课程时间轴显示
- 实时倒计时功能
- 课程状态高亮显示
- 自动时间同步

### 🔔 多样化提醒系统
- 桌面通知提醒
- 浮窗提醒显示
- 链式提醒机制
- 自定义提醒时间

### 🎨 个性化主题定制
- 多主题支持（深色/浅色模式）
- 自定义颜色方案
- 灵活的界面布局
- 深度个性化配置

## 🚀 系统要求

- **Python**: 3.12+
- **操作系统**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+, Fedora 32+)
- **依赖库**: 
  - PySide6 >= 6.5.0
  - ntplib >= 0.4.0
  - python-dateutil >= 2.8.2
  - pyyaml >= 6.0

## 📦 安装说明

### 方法一：使用启动脚本（推荐）
```bash
# 克隆项目
git clone <repository-url>
cd TimeNest

# 运行启动脚本（自动创建虚拟环境并安装依赖）
chmod +x start.sh
./start.sh
```

### 方法二：手动安装
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行应用程序
python main.py
```

## 🖥️ 使用说明

### 启动应用程序
```bash
# 使用启动脚本
./start.sh

# 或直接运行
python main.py
```

### 系统托盘功能
TimeNest提供完整的系统托盘图标支持，功能与ClassIsland完全一致：

**托盘菜单项**：
- 📚 **帮助…** - 打开在线帮助文档
- 👁️ **显示主界面/隐藏主界面** - 动态切换主窗口可见性
- 🗑️ **清除全部提醒** - 清除所有活动通知
- 📁 **编辑档案…** - 打开档案编辑窗口
- ⚙️ **应用设置…** - 打开应用程序设置
- 📅 **加载临时课表…** - 加载临时课程表
- 🔄 **换课…** - 打开换课功能
- 🔄 **重启** - 完全重启应用程序
- 🚪 **退出** - 优雅关闭应用程序
- 🛠️ **dev_Debug** - 开发者调试功能

**交互方式**：
- **左键点击** - 切换主窗口显示/隐藏
- **右键点击** - 显示完整功能菜单
- **中键点击** - 快速访问设置功能

## 🏗️ 项目结构

```
TimeNest/
├── core/                    # 核心模块
│   ├── application.py      # 应用程序主类
│   ├── components/         # 组件系统
│   ├── models/            # 数据模型
│   ├── services/           # 服务层
│   ├── utils/              # 工具模块
│   │   └── performance_monitor.py  # 性能监控工具
│   └── main_window.py      # 主窗口
├── ui/                     # 用户界面
├── models/                 # 业务模型
├── assets/                 # 资源文件
├── docs/                   # 文档
│   └── ui_design_specification.md  # UI设计规范
├── main.py                # 应用程序入口
├── requirements.txt       # 依赖列表
└── start.sh              # 启动脚本
```

## 🔧 核心组件

### 课程表系统
- **数据模型**: Subject, TimeLayout, ClassPlan
- **服务层**: LessonsService, TimeService
- **UI组件**: ScheduleComponent

### 组件系统
- ⏰ **时钟组件** - 精确到秒的时间显示
- 📅 **日期组件** - 当前日期和星期显示
- 📚 **课程表组件** - 智能课程安排显示
- 📝 **文本组件** - 自定义文本显示
- ☀️ **天气组件** - 天气信息显示
- ⏳ **倒计时组件** - 倒计时功能
- 🎬 **滚动组件** - 滚动文本显示
- 📦 **分组组件** - 组件分组管理
- 🎠 **幻灯片组件** - 轮播显示功能
- 🔘 **分割线组件** - 视觉分隔元素

## 🎯 开发指南

### 组件开发
1. 继承 `BaseComponent` 类
2. 实现 `update_content()` 方法
3. 注册到组件注册表
4. 在主窗口中使用

### 服务开发
1. 创建服务类
2. 实现业务逻辑
3. 在应用程序中注册
4. 提供给组件使用

## 🌟 新增功能

### UI设计规范
- 完整的UI设计规范文档
- 统一的视觉设计标准
- 响应式设计支持
- 多平台适配

### 主题系统
- 深色/浅色主题切换
- 动态主题应用
- 平滑过渡动画
- 用户偏好保存

### 性能优化
- 组件性能监控
- 内存使用优化
- 渲染效率提升
- 错误处理增强

### 安全增强
- 输入验证机制
- 异常处理完善
- 资源管理优化
- 稳定性提升

### 交互优化
- 窗口管理改进
- 动画效果增强
- 用户体验优化
- 多平台支持

## 🧪 测试

```bash
# 运行组件测试
python test_components.py

# 运行课程表系统测试
python test_full_schedule_system.py

# 运行核心功能测试
python final_core_test.py
```

## 📁 配置文件

应用程序配置文件位于用户数据目录：
- **Windows**: `%APPDATA%\TimeNest\`
- **macOS**: `~/Library/Application Support/TimeNest/`
- **Linux**: `~/.config/TimeNest/`

## 📈 版本历史

### v1.0.2 (2025-08-09)
- ✅ **托盘菜单项功能增强** - 修复托盘菜单项点击后只显示提示但不执行实际功能的问题
- ✅ **用户体验提升** - 所有菜单项点击后都会立即给出视觉反馈并显示主窗口

### v1.0.1 (2025-08-09)
- ✅ **完整的系统托盘图标支持** - 实现与ClassIsland完全一致的托盘菜单功能
- ✅ **增强的托盘图标交互** - 左键点击切换主窗口显示/隐藏
- ✅ **仿ClassIsland的应用程序控制** - 重启、退出、帮助等功能完整实现

### v1.0.0 (2025-08-07)
- ✅ **核心功能完整实现** - 时钟、日期、课程表等核心组件
- ✅ **现代化UI设计** - 基于PySide6的现代化界面
- ✅ **完整的测试覆盖** - 单元测试和集成测试

## 🤝 贡献

欢迎提交Issue和Pull Request来改进TimeNest！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 原项目ClassIsland提供了优秀的架构设计灵感
- PySide6团队提供了强大的GUI框架支持

---

<p align="center">
  <strong>🕐 TimeNest - 让时间更有价值 🕐</strong>
</p>
