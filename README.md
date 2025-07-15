# TimeNest 2.0.0 Preview

<div align="center">

<img src="https://github.com/ziyi127/TimeNest/blob/main/resources/icons/app_icon.png" style="width:64%; max-width:500px; display:block; margin:auto;" alt="TimeNest Logo">

**一个功能强大的跨平台课程表管理工具 - RinUI版本**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![RinUI](https://img.shields.io/badge/RinUI-0.1.5+-blue.svg)](https://github.com/RinLit-233-shiroko/Rin-UI)
[![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ziyi127/TimeNest.svg)](https://github.com/ziyi127/TimeNest/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/ziyi127/TimeNest.svg)](https://github.com/ziyi127/TimeNest/issues)

[🌐 官方网站](https://ziyi127.github.io/TimeNest-Website) | [📖 文档](https://ziyi127.github.io/TimeNest-Website/docs) | [🐛 问题反馈](https://github.com/ziyi127/TimeNest/issues) | [💬 讨论](https://github.com/ziyi127/TimeNest/discussions)

</div>

---

## 📖 项目简介

TimeNest 2.0.0 Preview 是一个基于 Python、RinUI 和 PySide6 开发的现代化课程表管理工具，专为学生、教师和教育工作者设计。本版本完全采用 RinUI 框架重构，提供了全新的现代化用户界面、强大的功能和跨平台支持，让时间管理变得简单高效。

### 🎯 设计理念

- **简洁高效**：直观的用户界面，简化复杂操作
- **功能全面**：涵盖课程管理的各个方面
- **跨平台**：支持 Windows、macOS、Linux
- **可扩展**：模块化设计，支持插件扩展
- **现代化**：采用最新技术栈，持续更新


## 🔄 架构升级

TimeNest 2.0.0 Preview 完全基于 RinUI 现代化架构构建：

- **当前架构**: RinUI + QML 声明式UI
- **旧版架构**: PySide6 Widgets (已完全移除)
- **性能提升**: 更快的渲染速度和更低的内存占用
- **界面优化**: 全新的现代化设计语言

### 启动方式

```bash
# 主要启动方式
python main.py

# 或使用启动脚本（包含依赖检查）
python run_rinui.py
```

## 🚀 快速开始

### 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **操作系统** | Windows 10 / macOS 10.14 / Linux | Windows 11 / macOS 12+ / Ubuntu 20.04+ |
| **Python** | 3.8+ | 3.11+ |
| **内存** | 2GB | 4GB+ |
| **存储空间** | 500MB | 1GB+ |
| **显示器** | 1024x768 | 1920x1080+ |

### 快速安装

```bash
# 克隆项目
git clone https://github.com/ziyi127/TimeNest.git
cd TimeNest

# 自动安装脚本（推荐）
python install.py

# 或手动安装
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py  # RinUI版本
# 或使用启动脚本
python run_rinui.py
```

### 验证安装

```bash
# 运行应用
python main.py  # RinUI版本
# 或使用启动脚本
python run_rinui.py
```

## ✨ 核心功能

### 📅 智能课程表管理

<table>
<tr>
<td width="50%">

**📊 动态显示**
- 实时课程状态更新
- 当前课程高亮显示
- 课程进度可视化
- 智能时间轴

**📝 灵活编辑**
- 拖拽式课程调整
- 批量操作支持
- 模板快速创建
- 历史版本管理

</td>
<td width="50%">

**📁 多格式支持**
- JSON/YAML 配置文件
- Excel 表格导入导出
- CSV 数据交换
- ClassIsland 兼容

**🔄 数据同步**
- 云端备份同步
- 多设备数据共享
- 自动备份恢复
- 增量同步机制

</td>
</tr>
</table>

### ⏰ 智能提醒系统

<table>
<tr>
<td width="50%">

**🔔 多样化提醒**
- 系统通知弹窗
- 自定义音效播放
- 语音播报功能
- 邮件提醒推送

**⚙️ 智能配置**
- 提前提醒时间设置
- 免打扰模式
- 条件触发规则
- 优先级管理

</td>
<td width="50%">

**🎵 个性化定制**
- 自定义提醒音效
- 语音合成设置
- 通知样式主题
- 提醒内容模板

**📱 跨平台通知**
- Windows 原生通知
- macOS 通知中心
- Linux 桌面通知
- 移动端推送（规划中）

</td>
</tr>
</table>

### 🎨 现代化界面

<table>
<tr>
<td width="50%">

**🖥️ 智能浮窗**
- 仿苹果灵动岛设计
- 实时信息显示
- 自适应透明度
- 磁性吸附定位

**🎭 主题系统**
- 明暗主题切换
- 自定义配色方案
- 主题市场下载
- 实时预览效果

</td>
<td width="50%">

**🧩 模块化组件**
- 可拖拽组件布局
- 自定义组件大小
- 组件显示控制
- 布局模板保存

**📊 信息面板**
- 实时时钟显示
- 天气信息集成
- 系统状态监控
- 倒计时提醒

</td>
</tr>
</table>

### ⚙️ 高级功能

<table>
<tr>
<td width="50%">

**🔌 插件系统**
- 插件热加载
- API 接口开放
- 第三方扩展支持
- 插件市场

**🛡️ 安全特性**
- 数据加密存储
- 配置文件保护
- 安全更新机制
- 隐私保护模式

</td>
<td width="50%">

**📈 性能优化**
- 内存使用监控
- 智能缓存机制
- 异步操作支持
- 资源自动清理

**🌐 国际化支持**
- 多语言界面
- 本地化适配
- 时区自动识别
- 区域格式设置

</td>
</tr>
</table>

## 📸 应用截图

<div align="center">

### 主界面
![主界面](https://via.placeholder.com/800x500/4A90E2/FFFFFF?text=主界面截图)

### 智能浮窗
![智能浮窗](https://via.placeholder.com/400x100/34C759/FFFFFF?text=智能浮窗)

### 设置界面
![设置界面](https://via.placeholder.com/600x400/FF9500/FFFFFF?text=设置界面)

</div>

## 🚀 快速上手

### 第一次使用

1. **启动应用**
   ```bash
   python main.py  # RinUI版本
# 或使用启动脚本
python run_rinui.py
   ```

2. **创建课程表**
   - 点击 "新建课程表" 按钮
   - 选择模板或从空白开始
   - 添加课程信息

3. **配置提醒**
   - 进入设置 → 通知设置
   - 选择提醒方式和时间
   - 测试提醒效果

4. **个性化定制**
   - 选择喜欢的主题
   - 调整界面布局
   - 配置浮窗显示

### 导入现有数据

<details>
<summary>📊 从 Excel 导入</summary>

1. 准备 Excel 文件（支持 .xlsx, .xls 格式）
2. 文件 → 导入 → 选择 Excel 文件
3. 映射字段对应关系
4. 确认导入设置

</details>

<details>
<summary>🔄 从 ClassIsland 迁移</summary>

1. 导出 ClassIsland 数据文件
2. 文件 → 导入 → ClassIsland 格式
3. 自动转换数据格式
4. 验证导入结果

</details>

## 🛠️ 开发指南

### 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/ziyi127/TimeNest.git
cd TimeNest

# 2. 创建开发环境
python -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
# dev-env\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python main.py  # RinUI版本
# 或使用启动脚本
python run_rinui.py
```

### 项目架构

```
TimeNest/
├── 📁 core/                    # 🔧 核心业务逻辑
│   ├── app_manager.py          # 应用管理器
│   ├── config_manager.py       # 配置管理
│   ├── notification_manager.py # 通知系统
│   ├── floating_manager.py     # 浮窗管理
│   ├── schedule_manager.py     # 课程表管理
│   ├── theme_manager.py        # 主题管理
│   ├── plugin_base.py          # 插件基础
│   ├── plugin_marketplace.py   # 插件市场
│   └── plugin_system/          # 插件系统
├── 📁 models/                  # 📊 数据模型
│   ├── schedule.py             # 课程表模型
│   ├── notification.py         # 通知模型
│   └── theme.py                # 主题模型
├── 📁 ui/                      # 🎨 用户界面
│   ├── floating_widget/        # 浮窗组件
│   ├── modules/                # 功能模块
│   ├── plugin_settings/        # 插件设置
│   ├── startup/                # 启动界面
│   └── system_tray.py          # 系统托盘
├── 📁 components/              # 🧩 UI组件
│   ├── base_component.py       # 基础组件
│   ├── schedule_component.py   # 课程表组件
│   ├── clock_component.py      # 时钟组件
│   └── weather_component.py    # 天气组件
├── 📁 utils/                   # 🔧 工具函数
│   ├── excel_exporter_v2.py    # Excel 导出
│   ├── performance_utils.py    # 性能工具
│   └── text_to_speech.py       # 语音合成
├── 📁 sdk/                     # 🛠️ 开发工具包
│   ├── powershell_executor.py  # PowerShell 执行器
│   └── security_validator.py   # 安全验证器
├── 📁 resources/               # 📦 资源文件
│   └── icons/                  # 图标文件
├── 📁 config/                  # ⚙️ 配置文件
│   ├── config.json             # 主配置文件
│   └── floating_widget_optimized.json # 浮窗配置
└── 📁 plugin_template/         # 🔌 插件模板
    ├── main.py                 # 模板主文件
    ├── plugin.json             # 插件配置
    └── README.md               # 模板说明
```

### 代码规范

项目遵循 PEP 8 Python 代码规范，建议使用以下工具进行代码检查：

```bash
# 代码格式化（可选）
black . --line-length 88

# 代码检查（可选）
flake8 . --max-line-length 88
```

### 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(notification): 添加邮件提醒功能

- 支持 SMTP 邮件发送
- 可配置邮件模板
- 添加邮件发送状态监控

Closes #123
```

## 🤝 参与贡献

我们欢迎所有形式的贡献！无论您是开发者、设计师、文档编写者还是用户，都可以为 TimeNest 做出贡献。

### 🐛 报告问题

发现 bug 或有功能建议？

1. 查看 [现有 Issues](https://github.com/ziyi127/TimeNest/issues) 避免重复
2. 创建新的 Issue 描述问题
3. 提供详细的复现步骤和环境信息
4. 添加相关的标签

### 💻 代码贡献

想要贡献代码？

1. **Fork** 项目到您的 GitHub 账户
2. **Clone** 您的 fork 到本地
3. 创建新的功能分支：`git checkout -b feature/amazing-feature`
4. 进行您的修改
5. 确保代码符合规范
6. 提交您的更改：`git commit -m 'feat: add amazing feature'`
7. 推送到分支：`git push origin feature/amazing-feature`
8. 创建 **Pull Request**

### 📝 文档贡献

帮助改进文档：

- 修正错别字和语法错误
- 添加使用示例和教程
- 翻译文档到其他语言
- 改进 API 文档

### 🎨 设计贡献

设计师可以贡献：

- UI/UX 设计改进建议
- 图标和插图设计
- 主题和配色方案
- 用户体验优化建议

### 🌍 本地化贡献

帮助 TimeNest 支持更多语言：

- 翻译界面文本
- 本地化日期时间格式
- 适配不同地区的使用习惯

## 📊 项目统计

<div align="center">

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=ziyi127&repo=TimeNest&show_icons=true&theme=default)

![Language Stats](https://github-readme-stats.vercel.app/api/top-langs/?username=ziyi127&layout=compact&theme=default)

</div>

## 🏆 致谢

### 核心贡献者

<table>
<tr>
<td align="center">
<a href="https://github.com/ziyi127">
<img src="https://github.com/ziyi127.png" width="100px;" alt="ziyi127"/>
<br />
<sub><b>ziyi127</b></sub>
</a>
<br />
<span title="Code">💻</span>
<span title="Documentation">📖</span>
<span title="Design">🎨</span>
</td>
<!-- 更多贡献者 -->
</tr>
</table>

### 特别感谢

- ClassIsland - 提供了灵感和参考
- [RinUI](https://github.com/RinLit-233-shiroko/Rin-UI) - 现代化的 Qt Quick UI 框架
- [PySide6](https://www.qt.io/qt-for-python) - 优秀的 GUI 框架
- 所有提供反馈和建议的用户们

### 开源项目

TimeNest 使用了以下优秀的开源项目：

- **PyQt6** - GUI 框架
- **pandas** - 数据处理
- **requests** - HTTP 请求
- **PyYAML** - YAML 解析
- **Pillow** - 图像处理
- **cryptography** - 加密支持

## 📄 许可证

本项目基于 [ 许可证](LICENSE) 开源。

```
MIT License

Copyright (c) 2024 TimeNest Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 联系我们

<div align="center">

### 🌐 官方渠道

[![官方网站](https://img.shields.io/badge/🌐_官方网站-ziyi127.github.io/TimeNest--Website-blue?style=for-the-badge)](https://ziyi127.github.io/TimeNest-Website)

[![GitHub](https://img.shields.io/badge/GitHub-ziyi127/TimeNest-black?style=for-the-badge&logo=github)](https://github.com/ziyi127/TimeNest)

[![Email](https://img.shields.io/badge/📧_邮箱-ziyihed@outlook.com-red?style=for-the-badge)](mailto:ziyihed@outlook.com)

### 💬 社区交流

- **问题反馈**: [GitHub Issues](https://github.com/ziyi127/TimeNest/issues)
- **功能建议**: [GitHub Discussions](https://github.com/ziyi127/TimeNest/discussions)
- **安全问题**: [安全政策](https://github.com/ziyi127/TimeNest/security/policy)

### 📱 关注我们

- **GitHub**: [@ziyi127](https://github.com/ziyi127)
- **邮箱**: [ziyihed@outlook.com](mailto:ziyihed@outlook.com)

</div>

---

<div align="center">

**⭐ 如果 TimeNest 对您有帮助，请给我们一个 Star！**

**🚀 TimeNest - 让时间管理更简单，让学习更高效！**

*Made with ❤️ by TimeNest Team*

</div>
