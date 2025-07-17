# 深色主题包

精美的深色主题集合，保护眼睛，提升夜间使用体验。

## 功能特性

- 🌙 多种深色主题变体
- 🎨 可自定义强调色
- ⏰ 自动时间切换
- 👁️ 护眼设计
- 🎯 全局主题应用
- ⚙️ 丰富的个性化设置

## 主题变体

### 午夜蓝 (Midnight)
深邃的午夜蓝色主题，营造宁静的工作环境。

### 炭黑 (Charcoal)
经典的炭黑色主题，专业而优雅。

### 黑曜石 (Obsidian)
纯黑的黑曜石主题，极致的深色体验。

### 石板灰 (Slate)
优雅的石板灰主题，现代简约风格。

## 强调色选项

- **蓝色** - 经典的蓝色强调
- **绿色** - 清新的绿色强调
- **紫色** - 神秘的紫色强调
- **橙色** - 活力的橙色强调
- **红色** - 热情的红色强调

## 安装方法

### 通过插件商城安装
1. 打开TimeNest
2. 右键系统托盘图标 → 插件管理
3. 在插件商城中搜索"深色主题包"
4. 点击安装按钮

## 使用说明

### 基本使用
1. 安装插件后，在插件设置中选择喜欢的主题变体
2. 选择合适的强调色
3. 主题将立即应用到整个应用程序

### 设置配置

#### 主题设置
- **主题变体**：选择深色主题的具体样式
- **强调色**：选择界面的强调色彩

#### 自动切换
- **自动切换**：根据时间自动切换深色主题
- **开始时间**：深色主题开始时间（如18:00）
- **结束时间**：深色主题结束时间（如06:00）

#### 应用范围
- **应用到浮窗**：将主题应用到TimeNest浮窗
- **应用到对话框**：将主题应用到所有对话框

### 自动切换功能

自动切换功能可以根据时间自动在浅色和深色主题之间切换：

1. 设置开始时间（如18:00）和结束时间（如06:00）
2. 在指定时间段内自动使用深色主题
3. 其他时间自动恢复默认主题

这个功能特别适合：
- 白天使用浅色主题保持清晰
- 夜晚使用深色主题保护眼睛
- 减少蓝光对睡眠的影响

## 护眼原理

深色主题的护眼效果主要体现在：

1. **减少蓝光**：深色背景减少屏幕蓝光输出
2. **降低对比度**：减少眼睛疲劳
3. **节省电量**：OLED屏幕显示黑色更省电
4. **夜间友好**：在暗环境中更舒适

## 开发说明

### 插件结构
```
dark_theme/
├── manifest.json    # 插件元数据
├── plugin.py       # 主插件代码
├── README.md       # 说明文档
└── themes/         # 主题文件目录
```

### 核心功能
- 主题管理
- 样式表生成
- 自动切换
- 设置管理

### 主题定义
每个主题包含以下颜色定义：
- `background` - 背景色
- `surface` - 表面色
- `primary` - 主色
- `text` - 文本色
- `text_secondary` - 次要文本色
- `border` - 边框色

## API接口

### 应用主题
```python
plugin.apply_current_theme()
```

### 获取主题列表
```python
themes = plugin.get_available_themes()
```

### 获取强调色列表
```python
colors = plugin.get_available_accent_colors()
```

## 自定义主题

开发者可以通过修改主题定义来创建自定义主题：

```python
custom_theme = {
    'name': '自定义主题',
    'background': '#your_color',
    'surface': '#your_color',
    'primary': '#your_color',
    'text': '#your_color',
    'text_secondary': '#your_color',
    'border': '#your_color'
}
```

## 许可证

MIT License

## 作者

Design Studio

## 版本历史

- v1.5.2：修复兼容性问题，新增多种配色方案
- v1.5.0：新增自动切换功能
- v1.4.0：新增强调色自定义
- v1.0.0：初始版本发布

## 支持

如有问题或建议，请访问：
- GitHub: https://github.com/ziyi127/TimeNest-Store
- Issues: https://github.com/ziyi127/TimeNest-Store/issues

## 相关资源

- [深色模式设计指南](https://material.io/design/color/dark-theme.html)
- [护眼知识](https://www.aao.org/eye-health/tips-prevention/computer-usage)
- [色彩理论](https://www.interaction-design.org/literature/topics/color-theory)
