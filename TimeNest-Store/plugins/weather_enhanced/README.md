# 增强天气插件

这是一个TimeNest的示例插件，展示如何创建一个功能完整的天气显示插件。

## 功能特性

- 🌤️ 实时天气信息显示
- 🌡️ 支持摄氏度/华氏度切换
- 💧 湿度信息显示（可选）
- 💨 风速信息显示（可选）
- ⏰ 自定义更新间隔
- 🌍 自定义显示城市
- ⚙️ 丰富的设置选项

## 安装方法

### 方法1：通过插件商城安装（推荐）
1. 打开TimeNest
2. 右键系统托盘图标 → 插件管理
3. 在插件商城中搜索"增强天气插件"
4. 点击安装按钮

### 方法2：手动安装
1. 下载插件文件
2. 解压到 `~/.timenest/plugins/weather_enhanced/` 目录
3. 重启TimeNest或在插件管理中刷新

## 使用说明

### 基本使用
插件安装后会自动在浮窗中显示天气信息，包括：
- 当前天气状况
- 温度
- 湿度（可选）
- 风速（可选）
- 最后更新时间

### 设置配置
在插件管理界面中可以配置以下选项：

- **API密钥**：天气服务API密钥（可选，留空使用模拟数据）
- **更新间隔**：天气信息更新频率（60-3600秒）
- **显示湿度**：是否显示湿度信息
- **显示风速**：是否显示风速信息
- **温度单位**：摄氏度或华氏度
- **城市**：显示天气的城市名称

## 开发说明

### 插件结构
```
weather_enhanced/
├── manifest.json    # 插件元数据
├── plugin.py       # 主插件代码
├── README.md       # 说明文档
└── screenshots/    # 截图目录
```

### 核心类
- `WeatherEnhancedPlugin`：主插件类，实现IPlugin接口
- `WeatherWidget`：天气显示组件

### 关键方法
- `initialize()`：插件初始化
- `activate()`：插件激活
- `deactivate()`：插件停用
- `cleanup()`：资源清理
- `update_weather()`：更新天气数据

## API接口

### 获取天气数据
```python
weather_data = plugin.current_weather
```

### 更新设置
```python
plugin.update_settings({
    'update_interval': 600,
    'show_humidity': False,
    'location': '上海'
})
```

## 许可证

MIT License

## 作者

TimeNest Team

## 版本历史

- v1.0.0：初始版本
  - 基本天气显示功能
  - 设置配置支持
  - 自动更新机制
  - 城市自定义功能

## 支持

如有问题或建议，请访问：
- GitHub: https://github.com/ziyi127/TimeNest-Store
- Issues: https://github.com/ziyi127/TimeNest-Store/issues

## 相关插件

- 基础天气插件
- 天气预报插件
- 空气质量插件
