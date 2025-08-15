# TimeNest 课程表软件配置文档

## 1. 配置文件结构说明

TimeNest 使用 JSON 文件作为配置文件，所有配置文件都存储在 `data/` 目录下。主要配置文件包括：
- `user_settings.json`：用户设置配置
- `class_plans.json`：课程表数据
- `plugins.json`：插件配置

## 2. 用户设置配置说明 (user_settings.json)

### 2.1 文件结构
```json
{
  "theme": "light",
  "language": "zh-CN",
  "auto_backup": true,
  "backup_interval": 24,
  "data_dir": "./data"
}
```

### 2.2 配置项详细说明

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| theme | string | "light" | 主题设置，可选值："light"（浅色主题）、"dark"（深色主题） |
| language | string | "zh-CN" | 语言设置，目前支持："zh-CN"（简体中文） |
| auto_backup | boolean | true | 是否自动备份数据 |
| backup_interval | integer | 24 | 自动备份间隔（小时） |
| data_dir | string | "./data" | 数据存储目录路径 |

## 3. 课程表数据配置说明 (class_plans.json)

### 3.1 文件结构
```json
{
  "courses": [
    {
      "id": "course_001",
      "name": "数学",
      "teacher": "张老师",
      "location": "教学楼A101",
      "duration": {
        "start_time": "08:00",
        "end_time": "09:30"
      }
    }
  ],
  "schedules": [
    {
      "id": "schedule_001",
      "day_of_week": 1,
      "week_parity": "both",
      "course_id": "course_001",
      "valid_from": "2023-09-01",
      "valid_to": "2024-01-31"
    }
  ],
  "temp_changes": [
    {
      "id": "temp_001",
      "original_schedule_id": "schedule_001",
      "new_course_id": "course_002",
      "change_date": "2023-10-15",
      "is_permanent": false,
      "used": false
    }
  ],
  "cycle_schedules": [
    {
      "id": "cycle_001",
      "name": "双周循环课程表",
      "cycle_length": 2,
      "schedules": [
        {
          "week_index": 0,
          "schedule_items": [
            {
              "day_of_week": 1,
              "course_id": "course_001"
            }
          ]
        }
      ]
    }
  ]
}
```

### 3.2 课程数据结构 (courses)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 课程唯一标识符 |
| name | string | 是 | 课程名称 |
| teacher | string | 是 | 授课教师 |
| location | string | 是 | 上课地点 |
| duration | object | 是 | 上课时间 |
| duration.start_time | string | 是 | 开始时间 (格式: HH:MM) |
| duration.end_time | string | 是 | 结束时间 (格式: HH:MM) |

### 3.3 课程表数据结构 (schedules)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 课程表项唯一标识符 |
| day_of_week | integer | 是 | 星期几 (0-6, 0表示星期日) |
| week_parity | string | 是 | 周奇偶性 ("odd"表示奇数周, "even"表示偶数周, "both"表示每周) |
| course_id | string | 是 | 关联的课程ID |
| valid_from | string | 是 | 有效开始日期 (格式: YYYY-MM-DD) |
| valid_to | string | 是 | 有效结束日期 (格式: YYYY-MM-DD) |

### 3.4 临时换课数据结构 (temp_changes)

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | string | 是 | - | 临时换课唯一标识符 |
| original_schedule_id | string | 是 | - | 原课程表项ID |
| new_course_id | string | 是 | - | 新课程ID |
| change_date | string | 是 | - | 换课日期 (格式: YYYY-MM-DD) |
| is_permanent | boolean | 否 | false | 是否为永久换课 |
| used | boolean | 否 | false | 是否已使用 |

### 3.5 循环课程表数据结构 (cycle_schedules)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 循环课程表唯一标识符 |
| name | string | 是 | 循环课程表名称 |
| cycle_length | integer | 是 | 循环长度 |
| schedules | array | 是 | 循环课程表项列表 |
| schedules[].week_index | integer | 是 | 周索引 |
| schedules[].schedule_items | array | 是 | 课程表项列表 |
| schedule_items[].day_of_week | integer | 是 | 星期几 (0-6, 0表示星期日) |
| schedule_items[].course_id | string | 是 | 课程ID |

## 4. 插件配置说明 (plugins.json)

### 4.1 文件结构
```json
{
  "plugins": [
    {
      "id": "course_reminder",
      "name": "课程提醒插件",
      "version": "1.0.0",
      "enabled": true,
      "config": {
        "reminder_time": "07:30"
      },
      "dependencies": [],
      "metadata": {
        "author": "TimeNest Team",
        "description": "课程提醒插件"
      }
    }
  ]
}
```

### 4.2 配置项详细说明

| 配置项 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|--------|------|
| id | string | 是 | - | 插件唯一标识符 |
| name | string | 是 | - | 插件名称 |
| version | string | 是 | - | 插件版本 |
| enabled | boolean | 否 | true | 插件是否启用 |
| config | object | 否 | {} | 插件特定配置 |
| dependencies | array | 否 | [] | 插件依赖列表 |
| metadata | object | 否 | {} | 插件元数据 |

## 5. 配置文件管理

### 5.1 配置文件位置
所有配置文件都存储在 `data/` 目录下，可以通过 `user_settings.json` 中的 `data_dir` 配置项修改存储目录。

### 5.2 配置文件备份
TimeNest 支持自动备份配置文件，备份文件存储在 `data/backups/` 目录下，文件名格式为：
```
{原文件名}.backup_{时间戳}
```

### 5.3 配置文件验证
TimeNest 在加载配置文件时会进行数据验证，如果配置文件格式不正确或缺少必需字段，会在日志中记录错误信息。