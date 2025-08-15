# TimeNest 课程表软件数据管理文档

## 1. 数据文件结构说明

TimeNest 使用 JSON 文件存储所有数据，数据文件位于 `data/` 目录下。主要数据文件包括：

```
data/
├── courses.json          # 课程数据
├── schedules.json        # 课程表数据
├── temp_changes.json     # 临时换课数据
├── cycle_schedules.json  # 循环课程表数据
├── user_settings.json    # 用户设置
├── plugins.json          # 插件配置
└── backups/              # 数据备份目录
    ├── courses.json.backup_20231015_120000
    ├── schedules.json.backup_20231015_120000
    └── ...
```

### 1.1 课程数据文件 (courses.json)

存储所有课程信息，每个课程包含以下字段：
- `id`: 课程唯一标识符
- `name`: 课程名称
- `teacher`: 授课教师
- `location`: 上课地点
- `duration`: 上课时间（包含开始时间和结束时间）

### 1.2 课程表数据文件 (schedules.json)

存储课程表信息，每个课程表项包含以下字段：
- `id`: 课程表项唯一标识符
- `day_of_week`: 星期几 (0-6, 0表示星期日)
- `week_parity`: 周奇偶性 ("odd"表示奇数周, "even"表示偶数周, "both"表示每周)
- `course_id`: 关联的课程ID
- `valid_from`: 有效开始日期
- `valid_to`: 有效结束日期

### 1.3 临时换课数据文件 (temp_changes.json)

存储临时换课信息，每个临时换课包含以下字段：
- `id`: 临时换课唯一标识符
- `original_schedule_id`: 原课程表项ID
- `new_course_id`: 新课程ID
- `change_date`: 换课日期
- `is_permanent`: 是否为永久换课
- `used`: 是否已使用

### 1.4 循环课程表数据文件 (cycle_schedules.json)

存储循环课程表信息，每个循环课程表包含以下字段：
- `id`: 循环课程表唯一标识符
- `name`: 循环课程表名称
- `cycle_length`: 循环长度
- `schedules`: 循环课程表项列表

### 1.5 用户设置文件 (user_settings.json)

存储用户设置信息，包含以下字段：
- `theme`: 主题设置
- `language`: 语言设置
- `auto_backup`: 是否自动备份
- `backup_interval`: 自动备份间隔（小时）
- `data_dir`: 数据存储目录

### 1.6 插件配置文件 (plugins.json)

存储插件配置信息，包含启用的插件列表及其配置。

## 2. 数据备份和恢复方法

### 2.1 自动备份

TimeNest 支持自动备份功能，可以通过 `user_settings.json` 中的以下配置项进行设置：
- `auto_backup`: 是否启用自动备份（默认为 true）
- `backup_interval`: 自动备份间隔（小时，默认为 24）

自动备份会在指定的时间间隔内自动创建所有数据文件的备份，备份文件存储在 `data/backups/` 目录下。

### 2.2 手动备份

可以通过代码或命令行工具手动执行备份操作。备份文件命名格式为：
```
{原文件名}.backup_{时间戳}
```

例如：
```
courses.json.backup_20231015_120000
```

### 2.3 数据恢复

#### 2.3.1 从备份文件恢复

要从备份文件恢复数据，请按照以下步骤操作：

1. 停止 TimeNest 应用
2. 进入 `data/backups/` 目录
3. 找到需要恢复的备份文件
4. 将备份文件复制到 `data/` 目录下，替换原文件
5. 启动 TimeNest 应用

#### 2.3.2 使用恢复工具

如果 TimeNest 提供了恢复工具，可以通过以下命令恢复数据：
```bash
python restore_data.py --file courses.json --backup courses.json.backup_20231015_120000
```

### 2.4 备份文件管理

- 备份文件按时间戳排序，最新的备份在最前面
- 建议定期清理旧的备份文件以节省存储空间
- 重要数据变更前建议手动创建备份

## 3. 数据迁移指南

### 3.1 不同版本间的数据迁移

当 TimeNest 发布新版本时，可能需要进行数据迁移以适应新的数据结构。

#### 3.1.1 自动迁移

TimeNest 会在启动时检查数据文件版本，并自动执行必要的迁移操作。

#### 3.1.2 手动迁移

如果自动迁移失败或需要特殊处理，可以按照以下步骤手动迁移数据：

1. 备份当前数据文件
2. 查看新版本的文档了解数据结构变更
3. 使用脚本或手动编辑数据文件以适应新结构
4. 验证迁移后的数据是否正确

### 3.2 数据导入/导出

#### 3.2.1 导出数据

可以通过插件或命令行工具导出数据：
```bash
python export_data.py --format json --output timenest_data_export.json
```

支持的导出格式：
- JSON (默认)
- CSV
- Excel

#### 3.2.2 导入数据

可以通过插件或命令行工具导入数据：
```bash
python import_data.py --format json --input timenest_data_import.json
```

### 3.3 数据验证

TimeNest 在加载数据时会进行验证，确保数据格式正确且完整性良好。如果发现数据问题，会在日志中记录错误信息。

### 3.4 数据安全

- 建议定期备份重要数据
- 敏感数据应进行加密存储
- 限制对数据目录的访问权限
- 在生产环境中使用时，应配置适当的日志级别以避免敏感信息泄露