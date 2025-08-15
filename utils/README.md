# TimeNest 工具模块

## 概述

工具模块提供了 TimeNest 课程表软件所需的各种辅助功能，包括数据验证、日期时间处理、日志记录和异常处理等。

## 功能模块

### 验证工具 (validation_utils.py)
提供数据验证和业务规则验证功能：
- 课程数据验证
- 课程表数据验证
- 时间冲突检测
- 教师时间冲突检测
- 教室资源冲突检测

### 日期时间工具 (date_utils.py)
提供日期时间相关的计算和转换功能：
- 计算周奇偶性
- 获取周日期列表
- 检查日期范围
- 计算循环周索引

### 日志工具 (logger.py)
提供统一的日志记录功能：
- 服务专用日志记录器
- 控制台和文件日志输出
- 异常信息记录

### 异常处理 (exceptions.py)
定义业务逻辑层的统一异常层次结构：
- TimeNestException: 基础异常类
- ValidationException: 数据验证异常
- ConflictException: 资源冲突异常
- NotFoundException: 资源未找到异常
- DataAccessException: 数据访问异常
- BusinessLogicException: 业务逻辑异常

## 使用方法

### 验证工具使用

```python
from utils.validation_utils import validate_course_data

# 验证课程数据
course = ClassItem(...)
is_valid, errors = validate_course_data(course)
if not is_valid:
    print("验证失败:", errors)
```

### 日期时间工具使用

```python
from utils.date_utils import get_week_parity

# 计算周奇偶性
parity = get_week_parity("2023-10-15", "2023-09-01")
print("周奇偶性:", parity)  # odd 或 even
```

### 日志工具使用

```python
from utils.logger import get_service_logger

# 获取服务专用日志记录器
logger = get_service_logger("course_service")
logger.info("这是一条信息日志")
```

### 异常处理使用

```python
from utils.exceptions import ValidationException

# 抛出验证异常
raise ValidationException("课程数据验证失败", ["课程名称不能为空", "教师姓名不能为空"])
```

## 设计原则

1. **单一职责**: 每个工具函数只负责一个特定的功能
2. **可重用性**: 工具函数设计为无状态的纯函数，可在不同场景下重用
3. **易测试性**: 工具函数不依赖外部状态，便于单元测试
4. **类型安全**: 使用类型注解提高代码可读性和安全性