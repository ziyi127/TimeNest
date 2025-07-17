# 插件发布包目录

这个目录包含所有插件的发布包（ZIP文件）。

## 发布包命名规范

发布包应按照以下格式命名：
```
{plugin_id}_v{version}.zip
```

例如：
- `weather_enhanced_v1.0.0.zip`
- `pomodoro_timer_v2.1.0.zip`
- `dark_theme_v1.5.2.zip`

## 发布包内容

每个发布包应包含：
- `manifest.json` - 插件元数据
- `plugin.py` - 主插件代码
- `README.md` - 插件说明文档
- `icon.png` - 插件图标（可选）
- 其他必要的资源文件

## 创建发布包

### 手动创建
```bash
cd plugins/your_plugin_id
zip -r ../../releases/your_plugin_id_v1.0.0.zip .
```

### 自动化脚本
可以使用自动化脚本来创建发布包：

```bash
#!/bin/bash
PLUGIN_ID=$1
VERSION=$2

if [ -z "$PLUGIN_ID" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <plugin_id> <version>"
    exit 1
fi

cd plugins/$PLUGIN_ID
zip -r ../../releases/${PLUGIN_ID}_v${VERSION}.zip .
echo "Created release package: ${PLUGIN_ID}_v${VERSION}.zip"
```

## 校验和验证

每个发布包都应该：
1. 包含有效的 `manifest.json`
2. 版本号与文件名一致
3. 通过插件验证测试
4. 生成SHA256校验和

## 当前发布包

- `weather_enhanced_v1.0.0.zip` - 增强天气插件
- `pomodoro_timer_v2.1.0.zip` - 番茄钟插件
- `dark_theme_v1.5.2.zip` - 深色主题包
- `calendar_sync_v1.3.1.zip` - 日历同步插件

## 下载统计

发布包的下载统计会自动更新到 `plugins.json` 文件中。
