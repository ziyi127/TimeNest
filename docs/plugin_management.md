# TimeNest 课程表软件插件管理文档

## 1. 插件安装和卸载方法

### 1.1 插件安装

TimeNest 支持动态加载插件，插件安装步骤如下：

1. 将插件文件夹复制到 `plugins/` 目录下
2. 确保插件文件夹包含插件主文件（文件名与文件夹名相同）
3. 在 `plugins/configs/` 目录下创建插件配置文件（可选）
4. 重启 TimeNest 应用或通过插件管理接口加载插件

### 1.2 插件卸载

插件卸载步骤如下：

1. 通过插件管理接口卸载插件
2. 从 `plugins/` 目录下删除插件文件夹
3. 从 `plugins/configs/` 目录下删除插件配置文件（可选）

## 2. 插件配置方法

### 2.1 插件配置文件

每个插件的配置信息存储在 `plugins/configs/` 目录下的 JSON 文件中，文件名格式为 `{plugin_id}.json`。

配置文件结构如下：
```json
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
```

### 2.2 配置项说明

| 配置项 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|--------|------|
| id | string | 是 | - | 插件唯一标识符 |
| name | string | 是 | - | 插件名称 |
| version | string | 是 | - | 插件版本 |
| enabled | boolean | 否 | true | 插件是否启用 |
| config | object | 否 | {} | 插件特定配置 |
| dependencies | array | 否 | [] | 插件依赖列表 |
| metadata | object | 否 | {} | 插件元数据 |

### 2.3 插件启用/禁用

可以通过修改配置文件中的 `enabled` 字段来启用或禁用插件，也可以通过插件管理接口动态启用或禁用插件。

## 3. 插件开发指南

### 3.1 插件基本结构

一个完整的 TimeNest 插件应包含以下文件：
```
plugins/
└── plugin_name/
    ├── plugin_name.py          # 插件主文件
    └── __init__.py             # Python 包初始化文件
```

### 3.2 插件接口

TimeNest 提供了多种插件接口，开发者可以根据需要选择合适的接口：

#### 3.2.1 基础插件接口 (PluginInterface)

所有插件都必须实现基础插件接口：

```python
class PluginInterface(ABC):
    def __init__(self, plugin_id: str, name: str, version: str):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.enabled = False
    
    @abstractmethod
    def initialize(self, app_context: Any) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """执行插件功能"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """清理插件资源"""
        pass
```

#### 3.2.2 课程插件接口 (CoursePluginInterface)

用于处理课程相关功能的插件：

```python
class CoursePluginInterface(PluginInterface, ABC):
    @abstractmethod
    def add_course(self, course: ClassItem) -> bool:
        """添加课程"""
        pass
    
    @abstractmethod
    def remove_course(self, course_id: str) -> bool:
        """删除课程"""
        pass
    
    @abstractmethod
    def update_course(self, course_id: str, course: ClassItem) -> bool:
        """更新课程"""
        pass
    
    @abstractmethod
    def get_course(self, course_id: str) -> Optional[ClassItem]:
        """获取课程"""
        pass
    
    @abstractmethod
    def list_courses(self) -> List[ClassItem]:
        """列出所有课程"""
        pass
```

#### 3.2.3 时间表插件接口 (SchedulePluginInterface)

用于处理时间表相关功能的插件：

```python
class SchedulePluginInterface(PluginInterface, ABC):
    @abstractmethod
    def add_schedule(self, schedule: ClassPlan) -> bool:
        """添加时间表项"""
        pass
    
    @abstractmethod
    def remove_schedule(self, schedule_id: str) -> bool:
        """删除时间表项"""
        pass
    
    @abstractmethod
    def update_schedule(self, schedule_id: str, schedule: ClassPlan) -> bool:
        """更新时间表项"""
        pass
    
    @abstractmethod
    def get_schedule(self, schedule_id: str) -> Optional[ClassPlan]:
        """获取时间表项"""
        pass
    
    @abstractmethod
    def list_schedules(self) -> List[ClassPlan]:
        """列出所有时间表项"""
        pass
```

#### 3.2.4 UI 插件接口 (UIPluginInterface)

用于处理用户界面相关功能的插件：

```python
class UIPluginInterface(PluginInterface, ABC):
    @abstractmethod
    def render_widget(self, widget_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """渲染UI组件"""
        pass
    
    @abstractmethod
    def handle_ui_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """处理UI事件"""
        pass
    
    @abstractmethod
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        pass
```

#### 3.2.5 数据插件接口 (DataPluginInterface)

用于处理数据相关功能的插件：

```python
class DataPluginInterface(PluginInterface, ABC):
    @abstractmethod
    def process_data(self, data: Any, processor_config: Optional[Dict[str, Any]] = None) -> Any:
        """处理数据"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Any, validation_rules: Optional[Dict[str, Any]] = None) -> bool:
        """验证数据"""
        pass
    
    @abstractmethod
    def transform_data(self, data: Any, transformation_rules: Dict[str, Any]) -> Any:
        """转换数据"""
        pass
    
    @abstractmethod
    def export_data(self, data: Any, export_format: str, export_config: Optional[Dict[str, Any]] = None) -> bool:
        """导出数据"""
        pass
    
    @abstractmethod
    def import_data(self, source: str, import_config: Optional[Dict[str, Any]] = None) -> Any:
        """导入数据"""
        pass
```

### 3.3 插件开发示例

以下是一个简单的课程提醒插件示例：

```python
from plugins.course_plugin_interface import CoursePluginInterface
from models.class_item import ClassItem

class CourseReminderPlugin(CoursePluginInterface):
    def __init__(self):
        super().__init__("course_reminder", "课程提醒插件", "1.0.0")
        self.courses = {}
    
    def initialize(self, app_context) -> bool:
        # 初始化插件
        return True
    
    def execute(self, params: Dict[str, Any]) -> Any:
        # 执行插件功能
        action = params.get("action", "")
        if action == "remind":
            course_id = params.get("course_id")
            return self.remind_course(course_id)
        return {"success": False, "message": "未知操作"}
    
    def cleanup(self) -> bool:
        # 清理插件资源
        return True
    
    def add_course(self, course: ClassItem) -> bool:
        self.courses[course.id] = course
        return True
    
    def remove_course(self, course_id: str) -> bool:
        if course_id in self.courses:
            del self.courses[course_id]
            return True
        return False
    
    def update_course(self, course_id: str, course: ClassItem) -> bool:
        self.courses[course_id] = course
        return True
    
    def get_course(self, course_id: str) -> Optional[ClassItem]:
        return self.courses.get(course_id)
    
    def list_courses(self) -> List[ClassItem]:
        return list(self.courses.values())
    
    def remind_course(self, course_id: str) -> Dict[str, Any]:
        course = self.get_course(course_id)
        if course:
            # 实现提醒逻辑
            return {"success": True, "message": f"已提醒课程: {course.name}"}
        return {"success": False, "message": "课程不存在"}
```

### 3.4 插件配置文件

插件配置文件应放置在 `plugins/configs/` 目录下，文件名为 `{plugin_id}.json`：

```json
{
  "id": "course_reminder",
  "name": "课程提醒插件",
  "version": "1.0.0",
  "enabled": true,
  "config": {
    "reminder_time": "07:30",
    "reminder_method": "notification"
  },
  "dependencies": [],
  "metadata": {
    "author": "开发者名称",
    "description": "插件功能描述",
    "website": "插件网站"
  }
}
```

### 3.5 插件测试

开发完成后，应进行以下测试：
1. 插件加载测试：确保插件能正确加载
2. 功能测试：验证插件功能是否正常工作
3. 异常处理测试：检查插件对异常情况的处理
4. 性能测试：评估插件对系统性能的影响

## 4. 插件管理接口

### 4.1 加载插件

通过插件管理器加载指定插件：
```
POST /plugins/load
{
  "plugin_id": "course_reminder"
}
```

### 4.2 卸载插件

通过插件管理器卸载指定插件：
```
POST /plugins/unload
{
  "plugin_id": "course_reminder"
}
```

### 4.3 获取插件列表

获取所有已加载插件的信息：
```
GET /plugins
```

### 4.4 执行插件功能

执行指定插件的功能：
```
POST /plugins/{plugin_id}/execute
{
  "action": "remind",
  "course_id": "course_001"
}
```

## 5. 插件最佳实践

### 5.1 命名规范

- 插件ID应使用小写字母和下划线，如 `course_reminder`
- 插件文件夹名应与插件ID一致
- 插件主文件名应与插件ID一致

### 5.2 错误处理

- 插件应妥善处理所有可能的异常情况
- 提供清晰的错误信息便于调试
- 在适当的时候记录日志

### 5.3 性能优化

- 避免在插件中执行耗时操作
- 合理使用缓存减少重复计算
- 及时释放不再使用的资源

### 5.4 安全性

- 验证所有输入参数
- 避免执行不安全的操作
- 保护敏感信息不被泄露

### 5.5 兼容性

- 确保插件与不同版本的 TimeNest 兼容
- 在插件文档中明确说明兼容的版本范围
- 提供升级指南