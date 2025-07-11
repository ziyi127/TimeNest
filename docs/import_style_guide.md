# TimeNest 项目导入风格指南

## 导入分组规范
1. **标准库导入** - Python内置模块
2. **第三方库导入** - 通过pip安装的库
3. **本地模块导入** - 项目内部模块

每组导入之间用空行分隔，并添加注释说明

## 导入排序规则
1. 每组导入按字母顺序排序
2. 从同一模块导入多个内容时，使用圆括号分组
3. 避免使用通配符导入（from module import *）

## 示例

```python
# 标准库
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

# 第三方库
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QApplication, 
    QLabel, 
    QVBoxLayout
)

# 本地模块
from core.config_manager import ConfigManager
from core.notification_manager import NotificationManager
from core.time_manager import TimeManager
```

## 最佳实践
1. 保持导入语句简洁明了
2. 移除未使用的导入
3. 避免相对导入（优先使用绝对导入）
4. 导入类时，保持一致的命名风格
5. 导入模块时，避免名称冲突
```