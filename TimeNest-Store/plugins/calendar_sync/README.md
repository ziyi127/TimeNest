# 日历同步插件

与Google日历、Outlook等主流日历服务同步，显示即将到来的事件。

## 功能特性

- 📅 多平台日历同步
- 🔄 自动定时同步
- ⏰ 事件提醒通知
- 📋 即将到来的事件显示
- 🎯 智能事件过滤
- ⚙️ 丰富的同步设置

## 支持的日历服务

### Google Calendar
- 完整的Google日历API集成
- 支持多个日历账户
- 实时事件同步

### Microsoft Outlook
- Outlook日历服务支持
- Office 365集成
- 企业级功能

### iCal格式
- 标准iCal格式支持
- 兼容大多数日历应用
- 导入/导出功能

## 安装方法

### 通过插件商城安装
1. 打开TimeNest
2. 右键系统托盘图标 → 插件管理
3. 在插件商城中搜索"日历同步插件"
4. 点击安装按钮

## 使用说明

### 基本设置

#### 启用同步
1. 在插件设置中启用"日历同步"
2. 设置同步间隔（5-60分钟）
3. 选择要同步的日历服务

#### Google日历配置
1. 启用"Google日历同步"
2. 获取Google Calendar API密钥
3. 输入API密钥并保存

#### Outlook日历配置
1. 启用"Outlook日历同步"
2. 获取Outlook客户端ID
3. 完成OAuth认证流程

### 显示设置

#### 事件显示
- **显示数量**：设置显示的即将到来事件数量（1-10个）
- **全天事件**：选择是否显示全天事件
- **时间格式**：12小时制或24小时制

#### 提醒设置
- **事件提醒**：启用/禁用事件提醒通知
- **提醒时间**：设置提前提醒时间（1-60分钟）

### API密钥获取

#### Google Calendar API
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用Calendar API
4. 创建API密钥
5. 配置API密钥权限

#### Microsoft Graph API
1. 访问 [Azure Portal](https://portal.azure.com/)
2. 注册新应用程序
3. 配置Calendar权限
4. 获取客户端ID和密钥

## 功能详解

### 自动同步
- 根据设置的间隔自动同步日历
- 智能增量同步，减少网络请求
- 错误重试机制

### 事件状态
- **进行中**：当前正在进行的事件
- **即将开始**：30分钟内开始的事件
- **即将到来**：未来的事件

### 智能提醒
- 根据事件重要性调整提醒
- 避免重复提醒
- 支持自定义提醒时间

## 隐私和安全

### 数据保护
- 所有API密钥本地加密存储
- 不会上传个人日历数据
- 遵循最小权限原则

### 网络安全
- 使用HTTPS加密传输
- OAuth 2.0安全认证
- 定期刷新访问令牌

## 故障排除

### 常见问题

#### 同步失败
1. 检查网络连接
2. 验证API密钥是否正确
3. 确认API配额是否充足

#### 事件不显示
1. 检查时间范围设置
2. 确认日历权限
3. 验证事件过滤条件

#### 提醒不工作
1. 检查通知权限
2. 确认提醒时间设置
3. 验证事件时间格式

### 日志调试
插件提供详细的日志信息：
- 同步状态日志
- API调用日志
- 错误详情日志

## 开发说明

### 插件结构
```
calendar_sync/
├── manifest.json    # 插件元数据
├── plugin.py       # 主插件代码
├── README.md       # 说明文档
└── api/            # API集成模块
```

### 核心功能
- 多平台API集成
- 事件数据处理
- 同步状态管理
- 提醒系统

### 扩展开发
支持添加新的日历服务：
1. 实现标准API接口
2. 添加认证流程
3. 配置同步逻辑

## API接口

### 手动同步
```python
plugin.sync_calendars()
```

### 获取事件
```python
events = plugin.events
```

### 设置提醒
```python
plugin.send_reminder(event_data)
```

## 许可证

MIT License

## 作者

Sync Solutions

## 版本历史

- v1.3.1：修复Google日历API兼容性问题
- v1.3.0：新增Outlook日历支持
- v1.2.0：新增事件提醒功能
- v1.1.0：优化同步性能
- v1.0.0：初始版本发布

## 支持

如有问题或建议，请访问：
- GitHub: https://github.com/ziyi127/TimeNest-Store
- Issues: https://github.com/ziyi127/TimeNest-Store/issues

## 相关资源

- [Google Calendar API文档](https://developers.google.com/calendar)
- [Microsoft Graph API文档](https://docs.microsoft.com/en-us/graph/)
- [iCal规范](https://tools.ietf.org/html/rfc5545)
