# TimeNest-Store

TimeNest官方插件商城，为TimeNest应用提供丰富的插件扩展功能。

## 🌟 特色插件

- **增强天气插件** - 详细的天气信息显示
- **番茄钟插件** - 专业的番茄工作法计时器
- **深色主题包** - 精美的深色主题集合
- **日历同步插件** - 与主流日历服务同步

## 📁 仓库结构

```
TimeNest-Store/
├── plugins.json          # 插件列表配置文件
├── plugins/              # 插件源码目录
│   ├── weather_enhanced/
│   ├── pomodoro_timer/
│   ├── dark_theme/
│   └── calendar_sync/
├── releases/             # 发布包目录
├── docs/                 # 文档目录
└── README.md
```

## 🚀 快速开始

### 安装插件

1. 打开TimeNest应用
2. 右键系统托盘图标 → "插件管理"
3. 在"插件商城"选项卡中浏览插件
4. 点击"安装"按钮下载并安装插件

### 开发插件

1. 查看 `plugins/` 目录中的示例插件
2. 参考插件开发文档
3. 按照规范创建插件
4. 提交Pull Request

## 📋 插件分类

- **组件 (Component)** - 浮窗显示组件
- **工具 (Utility)** - 实用工具插件
- **主题 (Theme)** - 界面主题包
- **集成 (Integration)** - 第三方服务集成
- **通知 (Notification)** - 通知增强插件

## 🔧 开发规范

### 插件结构

每个插件必须包含以下文件：

```
plugin_name/
├── manifest.json    # 插件元数据
├── plugin.py       # 主插件代码
├── README.md       # 插件说明
├── icon.png        # 插件图标 (48x48px)
└── screenshots/    # 截图目录
```

### manifest.json 示例

```json
{
    "id": "your_plugin_id",
    "name": "插件名称",
    "version": "1.0.0",
    "description": "插件描述",
    "author": "作者名称",
    "plugin_class": "PluginClassName",
    "plugin_type": "component",
    "api_version": "1.0.0",
    "min_app_version": "1.0.0",
    "settings": {
        "setting_name": {
            "type": "string",
            "default": "默认值",
            "description": "设置描述"
        }
    }
}
```

## 📊 统计信息

- **总插件数**: 4
- **总下载量**: 13,240
- **平均评分**: 4.75/5.0
- **最新更新**: 2025-01-14

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 Apache-2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- **Issues**: [GitHub Issues](https://github.com/ziyi127/TimeNest-Store/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ziyi127/TimeNest-Store/discussions)
- **Email**: support@timenest.app

## 🔗 相关链接

- [TimeNest 主项目](https://github.com/ziyi127/TimeNest)
- [插件开发文档](docs/plugin-development.md)
- [API 参考](docs/api-reference.md)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
