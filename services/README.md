# TimeNest 业务逻辑层

## 概述

业务逻辑层是 TimeNest 课程表软件的核心组件，负责处理所有与课程、课程表、临时换课和循环课程表相关的业务逻辑。该层提供了完整的 CRUD 操作、数据验证、冲突检测和复杂业务逻辑处理功能。

## 服务类

### CourseService (课程服务)
处理课程相关的业务逻辑：
- 创建、更新、删除、查询课程
- 课程数据验证
- 时间、教师、教室冲突检测

### ScheduleService (课程表服务)
处理课程表相关的业务逻辑：
- 创建、更新、删除、查询课程表项
- 课程表数据验证
- 根据日期或课程查询课程表项

### TempChangeService (临时换课服务)
处理临时换课相关的业务逻辑：
- 创建、更新、删除、查询临时换课
- 标记临时换课为已使用
- 根据日期或课程表项查询临时换课

### CycleScheduleService (循环课程表服务)
处理循环课程表相关的业务逻辑：
- 创建、更新、删除、查询循环课程表
- 生成指定日期的课程表项
- 循环课程表数据验证

## 工具类

### ServiceFactory (服务工厂)
用于统一管理所有服务的创建和访问：
- 单例模式管理服务实例
- 提供便捷的服务获取方法

### BusinessCoordinator (业务协调器)
协调各个服务之间的交互，处理复杂的业务逻辑：
- 创建课程并关联课程表项
- 应用临时换课
- 生成循环课程表
- 获取周课程表

## 使用方法

### 基本服务使用

```python
from services.service_factory import ServiceFactory

# 获取课程服务
course_service = ServiceFactory.get_course_service()

# 创建课程
course = ClassItem(
    id="course_001",
    name="数学",
    teacher="张老师",
    location="A101",
    duration=TimeSlot(start_time="08:00", end_time="09:30")
)
created_course = course_service.create_course(course)
```

### 使用业务协调器

```python
from services.business_coordinator import BusinessCoordinator

# 创建业务协调器
coordinator = BusinessCoordinator()

# 创建课程并关联课程表项
course = ClassItem(...)
schedule = ClassPlan(...)
created_course, created_schedule = coordinator.create_course_with_schedule(course, schedule)
```

### 运行演示

项目包含一个演示文件 `demo.py`，展示了如何使用各种服务：

```bash
python services/demo.py
```

## 错误处理

所有服务方法都会抛出以下异常：

- `ValidationException`: 数据验证失败
- `ConflictException`: 资源冲突
- `NotFoundException`: 资源未找到
- `DataAccessException`: 数据访问异常
- `BusinessLogicException`: 业务逻辑异常

## 日志记录

所有服务操作都会记录详细日志，日志文件存储在 `logs/` 目录下，按服务分类存储。

## 数据验证

所有服务都实现了严格的数据验证机制：
- 输入数据格式验证
- 业务规则验证
- 数据一致性检查

## 冲突检测

实现了多种冲突检测机制：
- 课程时间冲突检测
- 教师时间冲突检测
- 教室资源冲突检测