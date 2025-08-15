# TimeNest 后端API接口文档

## 目录

1. [概述](#概述)
2. [服务架构](#服务架构)
3. [核心服务接口](#核心服务接口)
   - [课程管理服务 (CourseService)](#课程管理服务-courseservice)
   - [课程表管理服务 (ScheduleService)](#课程表管理服务-scheduleservice)
   - [临时换课服务 (TempChangeService)](#临时换课服务-tempchangeservice)
   - [循环课程表服务 (CycleScheduleService)](#循环课程表服务-cyclescheduleservice)
4. [功能服务接口](#功能服务接口)
   - [用户服务 (UserService)](#用户服务-userservice)
   - [通知服务 (NotificationService)](#通知服务-notificationservice)
   - [数据服务 (DataService)](#数据服务-dataservice)
   - [备份服务 (BackupService)](#备份服务-backupservice)
   - [冲突检测服务 (ConflictDetectionService)](#冲突检测服务-conflictdetectionservice)
   - [提醒服务 (ReminderService)](#提醒服务-reminderservice)
   - [统计服务 (StatisticsService)](#统计服务-statisticsservice)
   - [同步服务 (SyncService)](#同步服务-syncservice)
   - [配置服务 (ConfigService)](#配置服务-configservice)
   - [任务调度服务 (TaskSchedulerService)](#任务调度服务-taskschedulerservice)
   - [天气服务 (WeatherService)](#天气服务-weatherservice)
   - [倒计时服务 (CountdownService)](#倒计时服务-countdownservice)
   - [课程别名服务 (CourseAliasService)](#课程别名服务-coursealiasservice)
   - [启动服务 (StartupService)](#启动服务-startupservice)
   - [调试服务 (DebugService)](#调试服务-debugservice)
   - [时间同步服务 (TimeSyncService)](#时间同步服务-timesyncservice)
5. [协调服务](#协调服务)
   - [业务协调器 (BusinessCoordinator)](#业务协调器-businesscoordinator)
   - [服务工厂 (ServiceFactory)](#服务工厂-servicefactory)
6. [使用示例](#使用示例)
7. [最佳实践](#最佳实践)

## 概述

本文档详细描述了 TimeNest 课程表软件的所有后端 API 接口，包括服务接口定义、使用方法和示例代码。这些接口构成了 TimeNest 后端服务的核心，提供了课程管理、课程表安排、临时换课、循环课程表等核心功能。

TimeNest 采用服务化架构，每个功能模块都封装在独立的服务类中，通过服务工厂统一管理和获取。这种设计提高了代码的可维护性和可扩展性。

## 服务架构

TimeNest 后端服务采用分层架构设计：

1. **服务层 (Services)**: 实现核心业务逻辑
2. **模型层 (Models)**: 定义数据结构
3. **数据访问层 (Data Access)**: 处理数据持久化
4. **工具层 (Utils)**: 提供通用工具函数

服务之间通过服务工厂进行统一管理，避免了服务之间的直接依赖。

## 核心服务接口

### 课程管理服务 (CourseService)

课程管理服务负责处理课程相关的业务逻辑。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取课程服务实例
course_service = ServiceFactory.get_course_service()
```

#### 接口列表

##### create_course(course: ClassItem) -> ClassItem

创建新课程

**参数**:
- `course`: ClassItem 对象，包含课程信息

**返回值**:
- ClassItem 对象，创建的课程

**异常**:
- ValidationException: 数据验证失败
- ConflictException: 课程冲突

**示例**:
```python
from models.class_item import ClassItem, TimeSlot

# 创建课程对象
time_slot = TimeSlot(start_time="08:00", end_time="09:30")
course = ClassItem(
    id="math101",
    name="高等数学",
    teacher="张教授",
    location="A101",
    duration=time_slot
)

# 创建课程
created_course = course_service.create_course(course)
print(f"课程创建成功: {created_course.name}")
```

##### update_course(course_id: str, updated_course: ClassItem) -> ClassItem

更新课程信息

**参数**:
- `course_id`: str, 课程ID
- `updated_course`: ClassItem 对象，更新后的课程信息

**返回值**:
- ClassItem 对象，更新后的课程

**异常**:
- ValidationException: 数据验证失败
- NotFoundException: 课程未找到
- ConflictException: 课程冲突

**示例**:
```python
# 获取现有课程并更新
course = course_service.get_course_by_id("math101")
course.teacher = "李教授"
updated_course = course_service.update_course("math101", course)
print(f"课程更新成功: {updated_course.teacher}")
```

##### delete_course(course_id: str) -> bool

删除课程

**参数**:
- `course_id`: str, 课程ID

**返回值**:
- bool, 是否删除成功

**异常**:
- NotFoundException: 课程未找到

**示例**:
```python
# 删除课程
success = course_service.delete_course("math101")
if success:
    print("课程删除成功")
```

##### get_course_by_id(course_id: str) -> Optional[ClassItem]

根据ID获取课程

**参数**:
- `course_id`: str, 课程ID

**返回值**:
- ClassItem 对象或 None（如果未找到）

**示例**:
```python
# 获取课程
course = course_service.get_course_by_id("math101")
if course:
    print(f"找到课程: {course.name}")
else:
    print("课程未找到")
```

##### get_all_courses() -> List[ClassItem]

获取所有课程

**返回值**:
- List[ClassItem], 课程列表

**示例**:
```python
# 获取所有课程
courses = course_service.get_all_courses()
print(f"共有 {len(courses)} 门课程")
for course in courses:
    print(f"- {course.name}")
```

### 课程表管理服务 (ScheduleService)

课程表管理服务负责处理课程表相关的业务逻辑。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取课程表服务实例
schedule_service = ServiceFactory.get_schedule_service()
```

#### 接口列表

##### create_schedule(schedule: ClassPlan) -> ClassPlan

创建课程表项

**参数**:
- `schedule`: ClassPlan 对象，课程表信息

**返回值**:
- ClassPlan 对象，创建的课程表项

**异常**:
- ValidationException: 数据验证失败
- ConflictException: 课程表冲突

**示例**:
```python
from models.class_plan import ClassPlan

# 创建课程表对象
schedule = ClassPlan(
    id="schedule001",
    day_of_week=1,  # 星期一
    week_parity="both",  # 每周
    course_id="math101",
    valid_from="2024-09-01",
    valid_to="2025-01-31"
)

# 创建课程表项
created_schedule = schedule_service.create_schedule(schedule)
print(f"课程表项创建成功: {created_schedule.id}")
```

##### update_schedule(schedule_id: str, updated_schedule: ClassPlan) -> ClassPlan

更新课程表项

**参数**:
- `schedule_id`: str, 课程表项ID
- `updated_schedule`: ClassPlan 对象，更新后的课程表信息

**返回值**:
- ClassPlan 对象，更新后的课程表项

**异常**:
- ValidationException: 数据验证失败
- NotFoundException: 课程表项未找到

**示例**:
```python
# 获取现有课程表项并更新
schedule = schedule_service.get_schedule_by_id("schedule001")
schedule.location = "B201"
updated_schedule = schedule_service.update_schedule("schedule001", schedule)
print(f"课程表项更新成功")
```

##### delete_schedule(schedule_id: str) -> bool

删除课程表项

**参数**:
- `schedule_id`: str, 课程表项ID

**返回值**:
- bool, 是否删除成功

**异常**:
- NotFoundException: 课程表项未找到

**示例**:
```python
# 删除课程表项
success = schedule_service.delete_schedule("schedule001")
if success:
    print("课程表项删除成功")
```

##### get_schedule_by_id(schedule_id: str) -> Optional[ClassPlan]

根据ID获取课程表项

**参数**:
- `schedule_id`: str, 课程表项ID

**返回值**:
- ClassPlan 对象或 None（如果未找到）

**示例**:
```python
# 获取课程表项
schedule = schedule_service.get_schedule_by_id("schedule001")
if schedule:
    print(f"找到课程表项: {schedule.course_id}")
else:
    print("课程表项未找到")
```

##### get_all_schedules() -> List[ClassPlan]

获取所有课程表项

**返回值**:
- List[ClassPlan], 课程表项列表

**示例**:
```python
# 获取所有课程表项
schedules = schedule_service.get_all_schedules()
print(f"共有 {len(schedules)} 个课程表项")
```

### 临时换课服务 (TempChangeService)

临时换课服务负责处理临时换课相关的业务逻辑。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取临时换课服务实例
temp_change_service = ServiceFactory.get_temp_change_service()
```

#### 接口列表

##### create_temp_change(temp_change: TempChange) -> TempChange

创建临时换课

**参数**:
- `temp_change`: TempChange 对象，临时换课信息

**返回值**:
- TempChange 对象，创建的临时换课

**异常**:
- ValidationException: 数据验证失败
- ConflictException: 临时换课冲突

**示例**:
```python
from models.temp_change import TempChange

# 创建临时换课对象
temp_change = TempChange(
    id="tc001",
    original_schedule_id="schedule001",
    new_course_id="eng101",
    change_date="2024-10-15"
)

# 创建临时换课
created_temp_change = temp_change_service.create_temp_change(temp_change)
print(f"临时换课创建成功: {created_temp_change.id}")
```

##### update_temp_change(temp_change_id: str, updated_temp_change: TempChange) -> TempChange

更新临时换课

**参数**:
- `temp_change_id`: str, 临时换课ID
- `updated_temp_change`: TempChange 对象，更新后的临时换课信息

**返回值**:
- TempChange 对象，更新后的临时换课

**异常**:
- ValidationException: 数据验证失败
- NotFoundException: 临时换课未找到

**示例**:
```python
# 获取现有临时换课并更新
temp_change = temp_change_service.get_temp_change_by_id("tc001")
temp_change.new_course_id = "phy101"
updated_temp_change = temp_change_service.update_temp_change("tc001", temp_change)
print(f"临时换课更新成功")
```

##### delete_temp_change(temp_change_id: str) -> bool

删除临时换课

**参数**:
- `temp_change_id`: str, 临时换课ID

**返回值**:
- bool, 是否删除成功

**异常**:
- NotFoundException: 临时换课未找到

**示例**:
```python
# 删除临时换课
success = temp_change_service.delete_temp_change("tc001")
if success:
    print("临时换课删除成功")
```

##### get_temp_change_by_id(temp_change_id: str) -> Optional[TempChange]

根据ID获取临时换课

**参数**:
- `temp_change_id`: str, 临时换课ID

**返回值**:
- TempChange 对象或 None（如果未找到）

**示例**:
```python
# 获取临时换课
temp_change = temp_change_service.get_temp_change_by_id("tc001")
if temp_change:
    print(f"找到临时换课: {temp_change.original_schedule_id}")
else:
    print("临时换课未找到")
```

##### get_all_temp_changes() -> List[TempChange]

获取所有临时换课

**返回值**:
- List[TempChange], 临时换课列表

**示例**:
```python
# 获取所有临时换课
temp_changes = temp_change_service.get_all_temp_changes()
print(f"共有 {len(temp_changes)} 个临时换课")
```

##### get_temp_changes_by_date(date_str: str) -> List[TempChange]

根据日期获取临时换课

**参数**:
- `date_str`: str, 日期字符串 (YYYY-MM-DD)

**返回值**:
- List[TempChange], 指定日期的临时换课列表

**示例**:
```python
# 获取指定日期的临时换课
temp_changes = temp_change_service.get_temp_changes_by_date("2024-10-15")
print(f"2024-10-15 有 {len(temp_changes)} 个临时换课")
```

##### get_temp_changes_by_schedule(schedule_id: str) -> List[TempChange]

根据原课程表ID获取临时换课

**参数**:
- `schedule_id`: str, 原课程表ID

**返回值**:
- List[TempChange], 指定课程表的临时换课列表

**示例**:
```python
# 获取指定课程表的临时换课
temp_changes = temp_change_service.get_temp_changes_by_schedule("schedule001")
print(f"课程表项 schedule001 有 {len(temp_changes)} 个临时换课")
```

##### mark_temp_change_as_used(temp_change_id: str) -> TempChange

标记临时换课为已使用

**参数**:
- `temp_change_id`: str, 临时换课ID

**返回值**:
- TempChange 对象，更新后的临时换课

**异常**:
- NotFoundException: 临时换课未找到

**示例**:
```python
# 标记临时换课为已使用
updated_temp_change = temp_change_service.mark_temp_change_as_used("tc001")
print(f"临时换课 {updated_temp_change.id} 已标记为已使用")
```

### 循环课程表服务 (CycleScheduleService)

循环课程表服务负责处理循环课程表相关的业务逻辑。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取循环课程表服务实例
cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
```

#### 接口列表

##### create_cycle_schedule(cycle_schedule: CycleSchedule) -> CycleSchedule

创建循环课程表

**参数**:
- `cycle_schedule`: CycleSchedule 对象，循环课程表信息

**返回值**:
- CycleSchedule 对象，创建的循环课程表

**异常**:
- ValidationException: 数据验证失败
- ConflictException: 循环课程表冲突

**示例**:
```python
from models.cycle_schedule import CycleSchedule, CycleScheduleItem, ScheduleItem

# 创建循环课程表对象
schedule_items = [
    ScheduleItem(day_of_week=1, course_id="math101"),
    ScheduleItem(day_of_week=3, course_id="eng101")
]

cycle_schedule_items = [
    CycleScheduleItem(week_index=0, schedule_items=schedule_items)
]

cycle_schedule = CycleSchedule(
    id="cycle001",
    name="第一周循环课程表",
    cycle_length=1,
    schedules=cycle_schedule_items
)

# 创建循环课程表
created_cycle_schedule = cycle_schedule_service.create_cycle_schedule(cycle_schedule)
print(f"循环课程表创建成功: {created_cycle_schedule.name}")
```

##### update_cycle_schedule(cycle_schedule_id: str, updated_cycle_schedule: CycleSchedule) -> CycleSchedule

更新循环课程表

**参数**:
- `cycle_schedule_id`: str, 循环课程表ID
- `updated_cycle_schedule`: CycleSchedule 对象，更新后的循环课程表信息

**返回值**:
- CycleSchedule 对象，更新后的循环课程表

**异常**:
- ValidationException: 数据验证失败
- NotFoundException: 循环课程表未找到

**示例**:
```python
# 获取现有循环课程表并更新
cycle_schedule = cycle_schedule_service.get_cycle_schedule_by_id("cycle001")
cycle_schedule.name = "更新后的循环课程表"
updated_cycle_schedule = cycle_schedule_service.update_cycle_schedule("cycle001", cycle_schedule)
print(f"循环课程表更新成功: {updated_cycle_schedule.name}")
```

##### delete_cycle_schedule(cycle_schedule_id: str) -> bool

删除循环课程表

**参数**:
- `cycle_schedule_id`: str, 循环课程表ID

**返回值**:
- bool, 是否删除成功

**异常**:
- NotFoundException: 循环课程表未找到

**示例**:
```python
# 删除循环课程表
success = cycle_schedule_service.delete_cycle_schedule("cycle001")
if success:
    print("循环课程表删除成功")
```

##### get_cycle_schedule_by_id(cycle_schedule_id: str) -> Optional[CycleSchedule]

根据ID获取循环课程表

**参数**:
- `cycle_schedule_id`: str, 循环课程表ID

**返回值**:
- CycleSchedule 对象或 None（如果未找到）

**示例**:
```python
# 获取循环课程表
cycle_schedule = cycle_schedule_service.get_cycle_schedule_by_id("cycle001")
if cycle_schedule:
    print(f"找到循环课程表: {cycle_schedule.name}")
else:
    print("循环课程表未找到")
```

##### get_all_cycle_schedules() -> List[CycleSchedule]

获取所有循环课程表

**返回值**:
- List[CycleSchedule], 循环课程表列表

**示例**:
```python
# 获取所有循环课程表
cycle_schedules = cycle_schedule_service.get_all_cycle_schedules()
print(f"共有 {len(cycle_schedules)} 个循环课程表")
```

##### generate_schedule_for_date(cycle_schedule_id: str, date_str: str, start_date_str: str) -> List[ScheduleItem]

为指定日期生成课程表项

**参数**:
- `cycle_schedule_id`: str, 循环课程表ID
- `date_str`: str, 日期字符串 (YYYY-MM-DD)
- `start_date_str`: str, 循环开始日期字符串 (YYYY-MM-DD)

**返回值**:
- List[ScheduleItem], 指定日期的课程表项列表

**异常**:
- NotFoundException: 循环课程表未找到

**示例**:
```python
# 为指定日期生成课程表项
schedule_items = cycle_schedule_service.generate_schedule_for_date(
    "cycle001", 
    "2024-10-15", 
    "2024-09-01"
)
print(f"2024-10-15 有 {len(schedule_items)} 个课程表项")
```

## 功能服务接口

### 用户服务 (UserService)

用户服务负责处理用户认证和密码管理。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取用户服务实例
user_service = ServiceFactory.get_user_service()
```

#### 接口列表

##### set_password(password: str) -> bool

设置系统密码

**参数**:
- `password`: str, 新密码

**返回值**:
- bool, 是否设置成功

**异常**:
- ValidationException: 密码验证失败

**示例**:
```python
# 设置密码
success = user_service.set_password("new_password123")
if success:
    print("密码设置成功")
```

##### verify_password(password: str) -> bool

验证密码

**参数**:
- `password`: str, 要验证的密码

**返回值**:
- bool, 密码是否正确

**示例**:
```python
# 验证密码
is_valid = user_service.verify_password("new_password123")
if is_valid:
    print("密码验证成功")
else:
    print("密码验证失败")
```

##### disable_password() -> bool

禁用密码保护

**返回值**:
- bool, 是否禁用成功

**示例**:
```python
# 禁用密码保护
success = user_service.disable_password()
if success:
    print("密码保护已禁用")
```

##### is_password_enabled() -> bool

检查是否启用了密码保护

**返回值**:
- bool, 是否启用了密码保护

**示例**:
```python
# 检查是否启用了密码保护
is_enabled = user_service.is_password_enabled()
if is_enabled:
    print("密码保护已启用")
else:
    print("密码保护未启用")
```

##### get_password_config() -> PasswordConfig

获取密码配置

**返回值**:
- PasswordConfig 对象，密码配置

**示例**:
```python
# 获取密码配置
password_config = user_service.get_password_config()
print(f"密码保护状态: {'启用' if password_config.is_enabled else '未启用'}")
```

### 通知服务 (NotificationService)

通知服务负责处理系统通知。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取通知服务实例
notification_service = ServiceFactory.get_notification_service()
```

#### 接口列表

##### create_notification(title: str, content: str, priority: str = "normal", category: str = "general", target_users: Optional[List[str]] = None) -> Notification

创建通知

**参数**:
- `title`: str, 通知标题
- `content`: str, 通知内容
- `priority`: str, 通知优先级 ("low", "normal", "high")
- `category`: str, 通知分类
- `target_users`: Optional[List[str]], 目标用户列表

**返回值**:
- Notification 对象，创建的通知

**异常**:
- ValidationException: 数据验证失败

**示例**:
```python
# 创建通知
notification = notification_service.create_notification(
    title="系统更新",
    content="系统将在今晚进行维护",
    priority="high",
    category="system"
)
print(f"通知创建成功: {notification.title}")
```

##### update_notification(notification_id: str, title: Optional[str] = None, content: Optional[str] = None, priority: Optional[str] = None, category: Optional[str] = None, is_read: Optional[bool] = None) -> Notification

更新通知

**参数**:
- `notification_id`: str, 通知ID
- `title`: Optional[str], 通知标题
- `content`: Optional[str], 通知内容
- `priority`: Optional[str], 通知优先级
- `category`: Optional[str], 通知分类
- `is_read`: Optional[bool], 是否已读

**返回值**:
- Notification 对象，更新后的通知

**异常**:
- ValidationException: 数据验证失败
- NotFoundException: 通知未找到

**示例**:
```python
# 更新通知
updated_notification = notification_service.update_notification(
    "notification001",
    title="重要系统更新",
    is_read=True
)
print(f"通知更新成功: {updated_notification.title}")
```

##### delete_notification(notification_id: str) -> bool

删除通知

**参数**:
- `notification_id`: str, 通知ID

**返回值**:
- bool, 是否删除成功

**异常**:
- NotFoundException: 通知未找到

**示例**:
```python
# 删除通知
success = notification_service.delete_notification("notification001")
if success:
    print("通知删除成功")
```

##### get_notification_by_id(notification_id: str) -> Optional[Notification]

根据ID获取通知

**参数**:
- `notification_id`: str, 通知ID

**返回值**:
- Notification 对象或 None（如果未找到）

**示例**:
```python
# 获取通知
notification = notification_service.get_notification_by_id("notification001")
if notification:
    print(f"找到通知: {notification.title}")
else:
    print("通知未找到")
```

##### get_all_notifications() -> List[Notification]

获取所有通知

**返回值**:
- List[Notification], 通知列表

**示例**:
```python
# 获取所有通知
notifications = notification_service.get_all_notifications()
print(f"共有 {len(notifications)} 条通知")
```

##### get_unread_notifications() -> List[Notification]

获取未读通知

**返回值**:
- List[Notification], 未读通知列表

**示例**:
```python
# 获取未读通知
unread_notifications = notification_service.get_unread_notifications()
print(f"共有 {len(unread_notifications)} 条未读通知")
```

##### get_notifications_by_category(category: str) -> List[Notification]

根据分类获取通知

**参数**:
- `category`: str, 通知分类

**返回值**:
- List[Notification], 指定分类的通知列表

**示例**:
```python
# 获取指定分类的通知
system_notifications = notification_service.get_notifications_by_category("system")
print(f"系统通知有 {len(system_notifications)} 条")
```

##### mark_as_read(notification_id: str) -> Notification

标记通知为已读

**参数**:
- `notification_id`: str, 通知ID

**返回值**:
- Notification 对象，更新后的通知

**异常**:
- NotFoundException: 通知未找到

**示例**:
```python
# 标记通知为已读
read_notification = notification_service.mark_as_read("notification001")
print(f"通知 {read_notification.id} 已标记为已读")
```

##### mark_all_as_read() -> int

标记所有通知为已读

**返回值**:
- int, 更新的通知数量

**示例**:
```python
# 标记所有通知为已读
count = notification_service.mark_all_as_read()
print(f"标记了 {count} 条通知为已读")
```

### 数据服务 (DataService)

数据服务负责处理数据导入导出。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取数据服务实例
data_service = ServiceFactory.get_data_service()
```

#### 接口列表

##### export_data(config: DataExportConfig, export_path: str) -> str

导出数据

**参数**:
- `config`: DataExportConfig 对象，导出配置
- `export_path`: str, 导出文件路径

**返回值**:
- str, 导出文件的完整路径

**异常**:
- ValidationException: 数据验证失败

**示例**:
```python
from models.data_export import DataExportConfig, ExportFormat

# 创建导出配置
export_config = DataExportConfig(
    format=ExportFormat.JSON,
    include_courses=True,
    include_schedules=True
)

# 导出数据
export_file_path = data_service.export_data(export_config, "/path/to/export/data")
print(f"数据导出成功: {export_file_path}")
```

##### import_data(config: DataImportConfig, import_path: str) -> bool

导入数据

**参数**:
- `config`: DataImportConfig 对象，导入配置
- `import_path`: str, 导入文件路径

**返回值**:
- bool, 是否导入成功

**异常**:
- ValidationException: 数据验证失败

**示例**:
```python
from models.data_export import DataImportConfig, ExportFormat

# 创建导入配置
import_config = DataImportConfig(
    format=ExportFormat.JSON,
    validate_data=True,
    overwrite_existing=True
)

# 导入数据
success = data_service.import_data(import_config, "/path/to/import/data.json")
if success:
    print("数据导入成功")
```

### 备份服务 (BackupService)

备份服务负责处理数据备份。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取备份服务实例
backup_service = ServiceFactory.get_backup_service()
```

#### 接口列表

##### create_backup(name: str, description: str = "", compress: bool = True) -> BackupInfo

创建备份

**参数**:
- `name`: str, 备份名称
- `description`: str, 备份描述
- `compress`: bool, 是否压缩备份文件

**返回值**:
- BackupInfo 对象，备份信息

**异常**:
- ValidationException: 数据验证失败

**示例**:
```python
# 创建备份
backup_info = backup_service.create_backup(
    name="daily_backup",
    description="每日自动备份",
    compress=True
)
print(f"备份创建成功: {backup_info.name}")
```

##### restore_backup(backup_id: str) -> bool

恢复备份

**参数**:
- `backup_id`: str, 备份ID

**返回值**:
- bool, 是否恢复成功

**异常**:
- ValidationException: 数据验证失败
- NotFoundException: 备份未找到

**示例**:
```python
# 恢复备份
success = backup_service.restore_backup("backup001")
if success:
    print("备份恢复成功")
```

##### get_backup_info(backup_id: str) -> Optional[BackupInfo]

获取备份信息

**参数**:
- `backup_id`: str, 备份ID

**返回值**:
- BackupInfo 对象或 None（如果未找到）

**示例**:
```python
# 获取备份信息
backup_info = backup_service.get_backup_info("backup001")
if backup_info:
    print(f"找到备份: {backup_info.name}")
else:
    print("备份未找到")
```

##### list_backups() -> List[BackupInfo]

列出所有备份

**返回值**:
- List[BackupInfo], 备份列表

**示例**:
```python
# 列出所有备份
backups = backup_service.list_backups()
print(f"共有 {len(backups)} 个备份")
```

##### delete_backup(backup_id: str) -> bool

删除备份

**参数**:
- `backup_id`: str, 备份ID

**返回值**:
- bool, 是否删除成功

**异常**:
- NotFoundException: 备份未找到

**示例**:
```python
# 删除备份
success = backup_service.delete_backup("backup001")
if success:
    print("备份删除成功")
```

### 冲突检测服务 (ConflictDetectionService)

冲突检测服务负责检测课程安排冲突。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取冲突检测服务实例
conflict_service = ServiceFactory.get_conflict_detection_service()
```

#### 接口列表

##### detect_course_conflicts(course: ClassItem) -> List[str]

检测课程冲突

**参数**:
- `course`: ClassItem 对象，要检测的课程

**返回值**:
- List[str], 冲突信息列表

**示例**:
```python
from models.class_item import ClassItem, TimeSlot

# 创建课程对象
time_slot = TimeSlot(start_time="08:00", end_time="09:30")
course = ClassItem(
    id="math101",
    name="高等数学",
    teacher="张教授",
    location="A101",
    duration=time_slot
)

# 检测课程冲突
conflicts = conflict_service.detect_course_conflicts(course)
if conflicts:
    print(f"检测到 {len(conflicts)} 个冲突:")
    for conflict in conflicts:
        print(f"- {conflict}")
else:
    print("未检测到冲突")
```

##### detect_schedule_conflicts(schedule: ClassPlan) -> List[str]

检测课程表冲突

**参数**:
- `schedule`: ClassPlan 对象，要检测的课程表项

**返回值**:
- List[str], 冲突信息列表

**示例**:
```python
from models.class_plan import ClassPlan

# 创建课程表对象
schedule = ClassPlan(
    id="schedule001",
    day_of_week=1,
    week_parity="both",
    course_id="math101",
    valid_from="2024-09-01",
    valid_to="2025-01-31"
)

# 检测课程表冲突
conflicts = conflict_service.detect_schedule_conflicts(schedule)
if conflicts:
    print(f"检测到 {len(conflicts)} 个冲突:")
    for conflict in conflicts:
        print(f"- {conflict}")
else:
    print("未检测到冲突")
```

### 提醒服务 (ReminderService)

提醒服务负责处理课程提醒。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取提醒服务实例
reminder_service = ServiceFactory.get_reminder_service()
```

#### 接口列表

##### start_reminder_service()

启动提醒服务

**示例**:
```python
# 启动提醒服务
reminder_service.start_reminder_service()
print("提醒服务已启动")
```

##### stop_reminder_service()

停止提醒服务

**示例**:
```python
# 停止提醒服务
reminder_service.stop_reminder_service()
print("提醒服务已停止")
```

##### add_reminder_callback(callback: Callable[[Dict[str, str]], None])

添加提醒回调函数

**参数**:
- `callback`: Callable, 回调函数

**示例**:
```python
def my_reminder_callback(reminder_info: Dict[str, str]):
    print(f"收到提醒: {reminder_info}")

# 添加提醒回调函数
reminder_service.add_reminder_callback(my_reminder_callback)
```

##### remove_reminder_callback(callback: Callable[[Dict[str, str]], None])

移除提醒回调函数

**参数**:
- `callback`: Callable, 要移除的回调函数

**示例**:
```python
def my_reminder_callback(reminder_info: Dict[str, str]):
    print(f"收到提醒: {reminder_info}")

# 移除提醒回调函数
reminder_service.remove_reminder_callback(my_reminder_callback)
```

### 统计服务 (StatisticsService)

统计服务负责处理各种统计信息。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取统计服务实例
statistics_service = ServiceFactory.get_statistics_service()
```

#### 接口列表

##### get_course_statistics() -> CourseStatistics

获取课程统计信息

**返回值**:
- CourseStatistics 对象，课程统计信息

**示例**:
```python
# 获取课程统计信息
course_stats = statistics_service.get_course_statistics()
print(f"总课程数: {course_stats.total_courses}")
```

##### get_time_statistics() -> TimeStatistics

获取时间统计信息

**返回值**:
- TimeStatistics 对象，时间统计信息

**示例**:
```python
# 获取时间统计信息
time_stats = statistics_service.get_time_statistics()
print(f"学习总时长: {time_stats.total_study_time}")
```

##### get_teacher_statistics() -> TeacherStatistics

获取教师统计信息

**返回值**:
- TeacherStatistics 对象，教师统计信息

**示例**:
```python
# 获取教师统计信息
teacher_stats = statistics_service.get_teacher_statistics()
print(f"教师数量: {teacher_stats.total_teachers}")
```

### 同步服务 (SyncService)

同步服务负责处理数据同步。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取同步服务实例
sync_service = ServiceFactory.get_sync_service()
```

#### 接口列表

##### sync_to_directory(target_directory: str) -> bool

同步数据到指定目录

**参数**:
- `target_directory`: str, 目标目录路径

**返回值**:
- bool, 是否同步成功

**示例**:
```python
# 同步数据到指定目录
success = sync_service.sync_to_directory("/path/to/sync/directory")
if success:
    print("数据同步成功")
```

##### sync_from_directory(source_directory: str) -> bool

从指定目录同步数据

**参数**:
- `source_directory`: str, 源目录路径

**返回值**:
- bool, 是否同步成功

**示例**:
```python
# 从指定目录同步数据
success = sync_service.sync_from_directory("/path/to/sync/directory")
if success:
    print("数据同步成功")
```

### 配置服务 (ConfigService)

配置服务负责处理系统配置。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取配置服务实例
config_service = ServiceFactory.get_config_service()
```

#### 接口列表

##### get_system_config() -> Dict[str, Any]

获取系统配置

**返回值**:
- Dict[str, Any], 系统配置字典

**示例**:
```python
# 获取系统配置
config = config_service.get_system_config()
print(f"系统配置: {config}")
```

##### update_system_config(config_data: Dict[str, Any]) -> bool

更新系统配置

**参数**:
- `config_data`: Dict[str, Any], 配置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新系统配置
config_data = {"theme": "dark", "language": "zh-CN"}
success = config_service.update_system_config(config_data)
if success:
    print("系统配置更新成功")
```

### 任务调度服务 (TaskSchedulerService)

任务调度服务负责处理计划任务。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取任务调度服务实例
task_scheduler_service = ServiceFactory.get_task_scheduler_service()
```

#### 接口列表

##### get_settings() -> TaskSettings

获取任务调度设置

**返回值**:
- TaskSettings 对象，任务调度设置

**示例**:
```python
# 获取任务调度设置
settings = task_scheduler_service.get_settings()
print(f"任务调度启用状态: {settings.enabled}")
```

##### update_settings(settings_data: Dict[str, Any]) -> bool

更新任务调度设置

**参数**:
- `settings_data`: Dict[str, Any], 设置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新任务调度设置
settings_data = {"enabled": True, "max_concurrent_tasks": 5}
success = task_scheduler_service.update_settings(settings_data)
if success:
    print("任务调度设置更新成功")
```

##### get_scheduled_tasks() -> List[ScheduledTask]

获取所有计划任务

**返回值**:
- List[ScheduledTask], 计划任务列表

**示例**:
```python
# 获取所有计划任务
tasks = task_scheduler_service.get_scheduled_tasks()
print(f"计划任务数量: {len(tasks)}")
```

##### add_scheduled_task(task: ScheduledTask) -> bool

添加计划任务

**参数**:
- `task`: ScheduledTask 对象，要添加的任务

**返回值**:
- bool, 是否添加成功

**示例**:
```python
from models.scheduled_task import ScheduledTask

# 创建计划任务对象
task = ScheduledTask(
    id="task001",
    name="每日备份",
    command="backup_daily",
    schedule_type="daily",
    schedule_time="02:00"
)

# 添加计划任务
success = task_scheduler_service.add_scheduled_task(task)
if success:
    print("计划任务添加成功")
```

##### remove_scheduled_task(task_id: str) -> bool

移除计划任务

**参数**:
- `task_id`: str, 任务ID

**返回值**:
- bool, 是否移除成功

**示例**:
```python
# 移除计划任务
success = task_scheduler_service.remove_scheduled_task("task001")
if success:
    print("计划任务移除成功")
```

##### execute_task(task_id: str) -> bool

执行任务

**参数**:
- `task_id`: str, 任务ID

**返回值**:
- bool, 是否执行成功

**示例**:
```python
# 执行任务
success = task_scheduler_service.execute_task("task001")
if success:
    print("任务执行成功")
```

### 天气服务 (WeatherService)

天气服务负责处理天气数据。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取天气服务实例
weather_service = ServiceFactory.get_weather_service()
```

#### 接口列表

##### get_settings() -> WeatherSettings

获取天气设置

**返回值**:
- WeatherSettings 对象，天气设置

**示例**:
```python
# 获取天气设置
settings = weather_service.get_settings()
print(f"天气服务启用状态: {settings.enabled}")
```

##### update_settings(settings_data: Dict[str, Any]) -> bool

更新天气设置

**参数**:
- `settings_data`: Dict[str, Any], 设置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新天气设置
settings_data = {"enabled": True, "location": "北京"}
success = weather_service.update_settings(settings_data)
if success:
    print("天气设置更新成功")
```

##### get_current_weather() -> Optional[WeatherData]

获取当前天气数据

**返回值**:
- Optional[WeatherData], 当前天气数据

**示例**:
```python
# 获取当前天气数据
weather = weather_service.get_current_weather()
if weather:
    print(f"当前温度: {weather.temperature}°C")
else:
    print("无法获取天气数据")
```

##### refresh_weather_data() -> bool

刷新天气数据

**返回值**:
- bool, 是否刷新成功

**示例**:
```python
# 刷新天气数据
success = weather_service.refresh_weather_data()
if success:
    print("天气数据刷新成功")
```

### 倒计时服务 (CountdownService)

倒计时服务负责处理倒计时功能。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取倒计时服务实例
countdown_service = ServiceFactory.get_countdown_service()
```

#### 接口列表

##### get_settings() -> CountdownSettings

获取倒计时设置

**返回值**:
- CountdownSettings 对象，倒计时设置

**示例**:
```python
# 获取倒计时设置
settings = countdown_service.get_settings()
print(f"倒计时服务启用状态: {settings.enabled}")
```

##### update_settings(settings_data: Dict[str, Any]) -> bool

更新倒计时设置

**参数**:
- `settings_data`: Dict[str, Any], 设置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新倒计时设置
settings_data = {"enabled": True, "default_format": "days"}
success = countdown_service.update_settings(settings_data)
if success:
    print("倒计时设置更新成功")
```

##### get_countdown_items() -> List[CountdownItem]

获取所有倒计时项

**返回值**:
- List[CountdownItem], 倒计时项列表

**示例**:
```python
# 获取所有倒计时项
items = countdown_service.get_countdown_items()
print(f"倒计时项数量: {len(items)}")
```

##### add_countdown_item(item: CountdownItem) -> bool

添加倒计时项

**参数**:
- `item`: CountdownItem 对象，要添加的倒计时项

**返回值**:
- bool, 是否添加成功

**示例**:
```python
from models.countdown import CountdownItem
from datetime import datetime

# 创建倒计时项对象
item = CountdownItem(
    id="countdown001",
    name="期末考试",
    target_date=datetime(2024, 12, 31),
    description="本学期期末考试"
)

# 添加倒计时项
success = countdown_service.add_countdown_item(item)
if success:
    print("倒计时项添加成功")
```

##### remove_countdown_item(item_id: str) -> bool

移除倒计时项

**参数**:
- `item_id`: str, 倒计时项ID

**返回值**:
- bool, 是否移除成功

**示例**:
```python
# 移除倒计时项
success = countdown_service.remove_countdown_item("countdown001")
if success:
    print("倒计时项移除成功")
```

##### get_countdown_info(item_id: str) -> Optional[Dict[str, Any]]

获取倒计时信息

**参数**:
- `item_id`: str, 倒计时项ID

**返回值**:
- Optional[Dict[str, Any]], 倒计时信息

**示例**:
```python
# 获取倒计时信息
info = countdown_service.get_countdown_info("countdown001")
if info:
    print(f"剩余天数: {info['days']}")
else:
    print("倒计时项未找到")
```

### 课程别名服务 (CourseAliasService)

课程别名服务负责处理课程简称。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取课程别名服务实例
course_alias_service = ServiceFactory.get_course_alias_service()
```

#### 接口列表

##### get_settings() -> CourseAliasSettings

获取课程别名设置

**返回值**:
- CourseAliasSettings 对象，课程别名设置

**示例**:
```python
# 获取课程别名设置
settings = course_alias_service.get_settings()
print(f"课程别名服务启用状态: {settings.enabled}")
```

##### update_settings(settings_data: Dict[str, Any]) -> bool

更新课程别名设置

**参数**:
- `settings_data`: Dict[str, Any], 设置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新课程别名设置
settings_data = {"enabled": True, "auto_generate": True}
success = course_alias_service.update_settings(settings_data)
if success:
    print("课程别名设置更新成功")
```

##### get_course_aliases() -> List[CourseAlias]

获取所有课程别名

**返回值**:
- List[CourseAlias], 课程别名列表

**示例**:
```python
# 获取所有课程别名
aliases = course_alias_service.get_course_aliases()
print(f"课程别名数量: {len(aliases)}")
```

##### add_course_alias(alias: CourseAlias) -> bool

添加课程别名

**参数**:
- `alias`: CourseAlias 对象，要添加的课程别名

**返回值**:
- bool, 是否添加成功

**示例**:
```python
from models.course_alias import CourseAlias

# 创建课程别名对象
alias = CourseAlias(
    id="alias001",
    course_id="math101",
    alias="高数",
    is_custom=True
)

# 添加课程别名
success = course_alias_service.add_course_alias(alias)
if success:
    print("课程别名添加成功")
```

##### remove_course_alias(alias_id: str) -> bool

移除课程别名

**参数**:
- `alias_id`: str, 课程别名ID

**返回值**:
- bool, 是否移除成功

**示例**:
```python
# 移除课程别名
success = course_alias_service.remove_course_alias("alias001")
if success:
    print("课程别名移除成功")
```

##### get_course_alias(course_id: str) -> Optional[str]

获取课程别名

**参数**:
- `course_id`: str, 课程ID

**返回值**:
- Optional[str], 课程别名

**示例**:
```python
# 获取课程别名
alias = course_alias_service.get_course_alias("math101")
if alias:
    print(f"课程别名: {alias}")
else:
    print("未找到课程别名")
```

##### generate_course_alias(course: ClassItem) -> str

生成课程别名

**参数**:
- `course`: ClassItem 对象，课程对象

**返回值**:
- str, 生成的课程别名

**示例**:
```python
from models.class_item import ClassItem, TimeSlot

# 创建课程对象
time_slot = TimeSlot(start_time="08:00", end_time="09:30")
course = ClassItem(
    id="math101",
    name="高等数学",
    teacher="张教授",
    location="A101",
    duration=time_slot
)

# 生成课程别名
alias = course_alias_service.generate_course_alias(course)
print(f"生成的课程别名: {alias}")
```

### 启动服务 (StartupService)

启动服务负责处理开机自启功能。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取启动服务实例
startup_service = ServiceFactory.get_startup_service()
```

#### 接口列表

##### get_settings() -> StartupSettings

获取启动设置

**返回值**:
- StartupSettings 对象，启动设置

**示例**:
```python
# 获取启动设置
settings = startup_service.get_settings()
print(f"开机自启启用状态: {settings.enabled}")
```

##### update_settings(settings_data: Dict[str, Any]) -> bool

更新启动设置

**参数**:
- `settings_data`: Dict[str, Any], 设置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新启动设置
settings_data = {"enabled": True, "minimize_to_tray": True}
success = startup_service.update_settings(settings_data)
if success:
    print("启动设置更新成功")
```

##### get_startup_items() -> List[StartupItem]

获取所有启动项

**返回值**:
- List[StartupItem], 启动项列表

**示例**:
```python
# 获取所有启动项
items = startup_service.get_startup_items()
print(f"启动项数量: {len(items)}")
```

##### add_startup_item(item: StartupItem) -> bool

添加启动项

**参数**:
- `item`: StartupItem 对象，要添加的启动项

**返回值**:
- bool, 是否添加成功

**示例**:
```python
from models.startup_config import StartupItem

# 创建启动项对象
item = StartupItem(
    id="startup001",
    name="TimeNest",
    command="timenest.exe",
    enabled=True
)

# 添加启动项
success = startup_service.add_startup_item(item)
if success:
    print("启动项添加成功")
```

##### remove_startup_item(item_id: str) -> bool

移除启动项

**参数**:
- `item_id`: str, 启动项ID

**返回值**:
- bool, 是否移除成功

**示例**:
```python
# 移除启动项
success = startup_service.remove_startup_item("startup001")
if success:
    print("启动项移除成功")
```

##### enable_startup_item(item_id: str) -> bool

启用启动项

**参数**:
- `item_id`: str, 启动项ID

**返回值**:
- bool, 是否启用成功

**示例**:
```python
# 启用启动项
success = startup_service.enable_startup_item("startup001")
if success:
    print("启动项启用成功")
```

##### disable_startup_item(item_id: str) -> bool

禁用启动项

**参数**:
- `item_id`: str, 启动项ID

**返回值**:
- bool, 是否禁用成功

**示例**:
```python
# 禁用启动项
success = startup_service.disable_startup_item("startup001")
if success:
    print("启动项禁用成功")
```

### 调试服务 (DebugService)

调试服务负责处理系统调试功能。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取调试服务实例
debug_service = ServiceFactory.get_debug_service()
```

#### 接口列表

##### get_settings() -> DebugSettings

获取调试设置

**返回值**:
- DebugSettings 对象，调试设置

**示例**:
```python
# 获取调试设置
settings = debug_service.get_settings()
print(f"调试模式启用状态: {settings.enabled}")
```

##### update_settings(settings_data: Dict[str, Any]) -> bool

更新调试设置

**参数**:
- `settings_data`: Dict[str, Any], 设置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新调试设置
settings_data = {"enabled": True, "log_level": "DEBUG"}
success = debug_service.update_settings(settings_data)
if success:
    print("调试设置更新成功")
```

##### apply_debug_settings() -> bool

应用调试设置

**返回值**:
- bool, 是否应用成功

**示例**:
```python
# 应用调试设置
success = debug_service.apply_debug_settings()
if success:
    print("调试设置应用成功")
```

### 时间同步服务 (TimeSyncService)

时间同步服务负责处理系统时间同步功能。

#### 初始化服务

```python
from services.service_factory import ServiceFactory

# 获取时间同步服务实例
time_sync_service = ServiceFactory.get_time_sync_service()
```

#### 接口列表

##### get_settings() -> TimeSyncSettings

获取时间同步设置

**返回值**:
- TimeSyncSettings 对象，时间同步设置

**示例**:
```python
# 获取时间同步设置
settings = time_sync_service.get_settings()
print(f"时间同步启用状态: {settings.enabled}")
```

##### update_settings(settings_data: Dict[str, Any]) -> bool

更新时间同步设置

**参数**:
- `settings_data`: Dict[str, Any], 设置数据字典

**返回值**:
- bool, 是否更新成功

**示例**:
```python
# 更新时间同步设置
settings_data = {"enabled": True, "sync_interval": 3600}
success = time_sync_service.update_settings(settings_data)
if success:
    print("时间同步设置更新成功")
```

##### sync_time() -> bool

同步时间

**返回值**:
- bool, 是否同步成功

**示例**:
```python
# 同步时间
success = time_sync_service.sync_time()
if success:
    print("时间同步成功")
```

##### get_last_sync_time() -> Optional[datetime]

获取上次同步时间

**返回值**:
- Optional[datetime], 上次同步时间

**示例**:
```python
from datetime import datetime

# 获取上次同步时间
last_sync = time_sync_service.get_last_sync_time()
if last_sync:
    print(f"上次同步时间: {last_sync}")
else:
    print("尚未进行时间同步")
```

## 协调服务

### 业务协调器 (BusinessCoordinator)

业务协调器负责协调多个服务之间的复杂业务操作。

#### 初始化服务

```python
from services.business_coordinator import BusinessCoordinator

# 获取业务协调器实例
coordinator = BusinessCoordinator()
```

#### 接口列表

##### create_course_with_schedule(course: ClassItem, schedule: ClassPlan) -> tuple[ClassItem, ClassPlan]

创建课程并关联课程表项

**参数**:
- `course`: ClassItem 对象，课程信息
- `schedule`: ClassPlan 对象，课程表信息

**返回值**:
- tuple[ClassItem, ClassPlan], (创建的课程, 创建的课程表项)

**异常**:
- ValidationException: 数据验证失败
- ConflictException: 课程或课程表冲突

**示例**:
```python
from models.class_item import ClassItem, TimeSlot
from models.class_plan import ClassPlan

# 创建课程和课程表项
time_slot = TimeSlot(start_time="08:00", end_time="09:30")
course = ClassItem(
    id="math101",
    name="高等数学",
    teacher="张教授",
    location="A101",
    duration=time_slot
)

schedule = ClassPlan(
    id="schedule001",
    day_of_week=1,
    week_parity="both",
    course_id="",  # 会在创建过程中自动设置
    valid_from="2024-09-01",
    valid_to="2025-01-31"
)

# 创建课程和课程表项
created_course, created_schedule = coordinator.create_course_with_schedule(course, schedule)
print(f"课程 {created_course.name} 和课程表项创建成功")
```

##### apply_temp_change(temp_change: TempChange) -> bool

应用临时换课

**参数**:
- `temp_change`: TempChange 对象，临时换课信息

**返回值**:
- bool, 是否应用成功

**异常**:
- ValidationException: 数据验证失败
- NotFoundException: 原课程表项未找到
- ConflictException: 临时换课冲突

**示例**:
```python
from models.temp_change import TempChange

# 创建临时换课对象
temp_change = TempChange(
    id="tc001",
    original_schedule_id="schedule001",
    new_course_id="eng101",
    change_date="2024-10-15"
)

# 应用临时换课
success = coordinator.apply_temp_change(temp_change)
if success:
    print("临时换课应用成功")
```

##### generate_cycle_schedule(cycle_schedule: CycleSchedule, start_date_str: str, weeks: int) -> List[ClassPlan]

生成循环课程表

**参数**:
- `cycle_schedule`: CycleSchedule 对象，循环课程表信息
- `start_date_str`: str, 开始日期字符串 (YYYY-MM-DD)
- `weeks`: int, 周数

**返回值**:
- List[ClassPlan], 生成的课程表项列表

**示例**:
```python
from models.cycle_schedule import CycleSchedule, CycleScheduleItem, ScheduleItem

# 创建循环课程表对象
schedule_items = [
    ScheduleItem(day_of_week=1, course_id="math101"),
    ScheduleItem(day_of_week=3, course_id="eng101")
]

cycle_schedule_items = [
    CycleScheduleItem(week_index=0, schedule_items=schedule_items)
]

cycle_schedule = CycleSchedule(
    id="cycle001",
    name="第一周循环课程表",
    cycle_length=1,
    schedules=cycle_schedule_items
)

# 生成循环课程表
schedules = coordinator.generate_cycle_schedule(cycle_schedule, "2024-09-01", 4)
print(f"生成了 {len(schedules)} 个课程表项")
```

### 服务工厂 (ServiceFactory)

服务工厂负责统一管理所有服务实例。

#### 接口列表

##### get_service(service_type: str)

获取指定类型的服务实例

**参数**:
- `service_type`: str, 服务类型

**返回值**:
- 对应的服务实例

**示例**:
```python
from services.service_factory import ServiceFactory

# 获取服务实例
course_service = ServiceFactory.get_service("course")
schedule_service = ServiceFactory.get_service("schedule")
```

##### get_course_service() -> CourseService

获取课程服务实例

**返回值**:
- CourseService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

course_service = ServiceFactory.get_course_service()
```

##### get_schedule_service() -> ScheduleService

获取课程表服务实例

**返回值**:
- ScheduleService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

schedule_service = ServiceFactory.get_schedule_service()
```

##### get_temp_change_service() -> TempChangeService

获取临时换课服务实例

**返回值**:
- TempChangeService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

temp_change_service = ServiceFactory.get_temp_change_service()
```

##### get_cycle_schedule_service() -> CycleScheduleService

获取循环课程表服务实例

**返回值**:
- CycleScheduleService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
```

##### get_user_service() -> UserService

获取用户服务实例

**返回值**:
- UserService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

user_service = ServiceFactory.get_user_service()
```

##### get_notification_service() -> NotificationService

获取通知服务实例

**返回值**:
- NotificationService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

notification_service = ServiceFactory.get_notification_service()
```

##### get_statistics_service() -> StatisticsService

获取统计服务实例

**返回值**:
- StatisticsService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

statistics_service = ServiceFactory.get_statistics_service()
```

##### get_data_service() -> DataService

获取数据服务实例

**返回值**:
- DataService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

data_service = ServiceFactory.get_data_service()
```

##### get_backup_service() -> BackupService

获取备份服务实例

**返回值**:
- BackupService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

backup_service = ServiceFactory.get_backup_service()
```

##### get_conflict_detection_service() -> ConflictDetectionService

获取冲突检测服务实例

**返回值**:
- ConflictDetectionService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

conflict_service = ServiceFactory.get_conflict_detection_service()
```

##### get_reminder_service() -> ReminderService

获取提醒服务实例

**返回值**:
- ReminderService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

reminder_service = ServiceFactory.get_reminder_service()
```

##### get_sync_service() -> SyncService

获取同步服务实例

**返回值**:
- SyncService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

sync_service = ServiceFactory.get_sync_service()
```

##### get_config_service() -> ConfigService

获取配置服务实例

**返回值**:
- ConfigService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

config_service = ServiceFactory.get_config_service()
```

##### get_task_scheduler_service() -> TaskSchedulerService

获取任务调度服务实例

**返回值**:
- TaskSchedulerService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

task_scheduler_service = ServiceFactory.get_task_scheduler_service()
```

##### get_weather_service() -> WeatherService

获取天气服务实例

**返回值**:
- WeatherService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

weather_service = ServiceFactory.get_weather_service()
```

##### get_countdown_service() -> CountdownService

获取倒计时服务实例

**返回值**:
- CountdownService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

countdown_service = ServiceFactory.get_countdown_service()
```

##### get_course_alias_service() -> CourseAliasService

获取课程别名服务实例

**返回值**:
- CourseAliasService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

course_alias_service = ServiceFactory.get_course_alias_service()
```

##### get_startup_service() -> StartupService

获取启动服务实例

**返回值**:
- StartupService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

startup_service = ServiceFactory.get_startup_service()
```

##### get_debug_service() -> DebugService

获取调试服务实例

**返回值**:
- DebugService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

debug_service = ServiceFactory.get_debug_service()
```

##### get_time_sync_service() -> TimeSyncService

获取时间同步服务实例

**返回值**:
- TimeSyncService 实例

**示例**:
```python
from services.service_factory import ServiceFactory

time_sync_service = ServiceFactory.get_time_sync_service()
```

## 使用示例

### 完整示例：创建课程和课程表项

```python
from services.service_factory import ServiceFactory
from services.business_coordinator import BusinessCoordinator
from models.class_item import ClassItem, TimeSlot
from models.class_plan import ClassPlan
from models.temp_change import TempChange

# 初始化服务
coordinator = BusinessCoordinator()
course_service = ServiceFactory.get_course_service()
schedule_service = ServiceFactory.get_schedule_service()
temp_change_service = ServiceFactory.get_temp_change_service()

# 方式1: 使用业务协调器创建课程和课程表项
time_slot = TimeSlot(start_time="08:00", end_time="09:30")
course = ClassItem(
    id="math101",
    name="高等数学",
    teacher="张教授",
    location="A101",
    duration=time_slot
)

schedule = ClassPlan(
    id="schedule001",
    day_of_week=1,  # 星期一
    week_parity="both",  # 每周
    course_id="",  # 会自动设置
    valid_from="2024-09-01",
    valid_to="2025-01-31"
)

# 创建课程和课程表项
created_course, created_schedule = coordinator.create_course_with_schedule(course, schedule)

# 方式2: 分别创建课程和课程表项
# 创建课程
course2 = ClassItem(
    id="eng101",
    name="大学英语",
    teacher="王教授",
    location="B201",
    duration=TimeSlot(start_time="10:00", end_time="11:30")
)

created_course2 = course_service.create_course(course2)

# 创建课程表项
schedule2 = ClassPlan(
    id="schedule002",
    day_of_week=2,  # 星期二
    week_parity="both",
    course_id=created_course2.id,  # 关联课程ID
    valid_from="2024-09-01",
    valid_to="2025-01-31"
)

created_schedule2 = schedule_service.create_schedule(schedule2)

# 创建临时换课
temp_change = TempChange(
    id="tc001",
    original_schedule_id="schedule001",
    new_course_id="eng101",
    change_date="2024-10-15"
)

created_temp_change = temp_change_service.create_temp_change(temp_change)

# 查询所有课程
all_courses = course_service.get_all_courses()
print("所有课程:")
for course in all_courses:
    print(f"- {course.name} ({course.id})")

# 查询所有课程表项
all_schedules = schedule_service.get_all_schedules()
print("\n所有课程表项:")
for schedule in all_schedules:
    print(f"- {schedule.course_id} 星期{schedule.day_of_week}")

# 查询所有临时换课
all_temp_changes = temp_change_service.get_all_temp_changes()
print("\n所有临时换课:")
for temp_change in all_temp_changes:
    print(f"- {temp_change.original_schedule_id} -> {temp_change.new_course_id}")
```

## 最佳实践

1. **服务获取**: 始终通过 ServiceFactory 获取服务实例，避免直接实例化服务类
2. **异常处理**: 妥善处理服务接口可能抛出的异常
3. **数据验证**: 在调用服务接口前进行必要的数据验证
4. **资源管理**: 合理使用服务实例，避免重复创建
5. **事务处理**: 对于涉及多个服务的操作，使用 BusinessCoordinator 进行协调
6. **线程安全**: 提醒服务使用了多线程，在添加回调函数时要注意线程安全
7. **数据持久化**: 备份服务和数据服务提供了数据持久化功能，定期备份重要数据
8. **配置管理**: 配置服务提供了统一的配置管理接口，方便系统参数的读取和更新
9. **系统集成**: 启动服务、时间同步服务等提供了与操作系统的集成功能
10. **调试支持**: 调试服务提供了完整的调试功能，便于开发和问题排查