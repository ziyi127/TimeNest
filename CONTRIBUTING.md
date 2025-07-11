# 贡献指南

感谢您对 TimeNest 项目的关注！我们欢迎所有形式的贡献，无论您是开发者、设计师、文档编写者还是用户。

## 🤝 贡献方式

### 🐛 报告问题

发现 bug 或有功能建议？

1. **搜索现有问题**: 查看 [Issues](https://github.com/ziyi127/TimeNest/issues) 避免重复报告
2. **使用模板**: 选择合适的 [Issue 模板](https://github.com/ziyi127/TimeNest/issues/new/choose)
3. **详细描述**: 提供复现步骤、环境信息、期望行为
4. **添加标签**: 选择合适的标签（bug、enhancement、question 等）

### 💻 代码贡献

#### 开发环境设置

```bash
# 1. Fork 并克隆项目
git clone https://github.com/YOUR_USERNAME/TimeNest.git
cd TimeNest

# 2. 添加上游仓库
git remote add upstream https://github.com/ziyi127/TimeNest.git

# 3. 创建开发环境
python -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
# dev-env\Scripts\activate   # Windows

# 4. 安装开发依赖
pip install -r requirements-dev.txt

# 5. 安装 pre-commit 钩子
pre-commit install
```

#### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **进行开发**
   - 遵循代码规范
   - 添加必要的测试
   - 更新相关文档

3. **运行测试**
   ```bash
   # 运行所有测试
   pytest tests/
   
   # 检查代码覆盖率
   pytest tests/ --cov=. --cov-report=html
   
   # 代码格式检查
   black . --check
   flake8 .
   mypy .
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### 📝 文档贡献

- **用户文档**: 改进使用指南、FAQ、教程
- **开发文档**: 完善 API 文档、架构说明
- **翻译**: 帮助翻译界面和文档到其他语言

### 🎨 设计贡献

- **UI/UX 改进**: 界面设计优化建议
- **图标设计**: 应用图标、功能图标
- **主题设计**: 新的配色方案和主题

## 📋 代码规范

### Python 代码风格

我们使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码检查
- **mypy**: 类型检查

```bash
# 格式化代码
black . --line-length 88
isort . --profile black

# 检查代码
flake8 . --max-line-length 88
mypy . --ignore-missing-imports
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI/CD 相关

**示例：**
```
feat(notification): 添加邮件提醒功能

- 支持 SMTP 邮件发送
- 可配置邮件模板
- 添加邮件发送状态监控

Closes #123
```

### 代码结构规范

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块说明
简要描述模块的功能和用途
"""

import os  # 标准库
import sys
from typing import Dict, List, Optional  # 类型注解

import requests  # 第三方库
from PyQt6.QtCore import QObject

from core.config_manager import ConfigManager  # 本地模块


class ExampleClass(QObject):
    """
    示例类
    
    详细描述类的功能和用法
    
    Args:
        param1: 参数说明
        param2: 参数说明
    """
    
    def __init__(self, param1: str, param2: int = 0):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
    
    def example_method(self, arg: str) -> bool:
        """
        示例方法
        
        Args:
            arg: 参数说明
            
        Returns:
            返回值说明
            
        Raises:
            ValueError: 异常说明
        """
        if not arg:
            raise ValueError("参数不能为空")
        
        return True
```

## 🧪 测试指南

### 测试结构

```
tests/
├── unit_tests/          # 单元测试
│   ├── test_core/       # 核心模块测试
│   ├── test_ui/         # UI 组件测试
│   └── test_utils/      # 工具函数测试
├── integration_tests/   # 集成测试
└── conftest.py         # 测试配置
```

### 编写测试

```python
import pytest
from unittest.mock import Mock, patch

from core.config_manager import ConfigManager


class TestConfigManager:
    """配置管理器测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.config_manager = ConfigManager()
    
    def test_load_config(self):
        """测试配置加载"""
        # 测试正常情况
        result = self.config_manager.load_config("test.json")
        assert result is True
        
        # 测试异常情况
        with pytest.raises(FileNotFoundError):
            self.config_manager.load_config("nonexistent.json")
    
    @patch('core.config_manager.Path.exists')
    def test_config_file_exists(self, mock_exists):
        """测试配置文件存在性检查"""
        mock_exists.return_value = True
        result = self.config_manager.config_file_exists()
        assert result is True
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit_tests/test_config_manager.py

# 运行特定测试方法
pytest tests/unit_tests/test_config_manager.py::TestConfigManager::test_load_config

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 并行运行测试
pytest -n auto
```

## 🔍 代码审查

### Pull Request 检查清单

提交 PR 前请确保：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有引入新的依赖（如有需要请说明）
- [ ] 考虑了向后兼容性

### 审查标准

我们会从以下方面审查代码：

1. **功能正确性**: 代码是否实现了预期功能
2. **代码质量**: 是否遵循最佳实践
3. **性能影响**: 是否有性能问题
4. **安全性**: 是否存在安全隐患
5. **可维护性**: 代码是否易于理解和维护
6. **测试覆盖**: 是否有足够的测试

## 🏷️ 发布流程

### 版本号规范

我们使用 [语义化版本](https://semver.org/) 规范：

- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 发布检查清单

- [ ] 更新版本号
- [ ] 更新 CHANGELOG.md
- [ ] 运行完整测试套件
- [ ] 更新文档
- [ ] 创建 Git 标签
- [ ] 构建发布包
- [ ] 发布到 GitHub Releases

## 📞 获取帮助

如果您在贡献过程中遇到问题：

1. **查看文档**: [开发指南](docs/developer_guide/)
2. **搜索 Issues**: 查看是否有类似问题
3. **创建 Discussion**: [GitHub Discussions](https://github.com/ziyi127/TimeNest/discussions)
4. **联系维护者**: [ziyihed@outlook.com](mailto:ziyihed@outlook.com)

## 🎉 贡献者认可

我们会在以下地方认可贡献者：

- README.md 贡献者列表
- 发布说明中的感谢
- 项目网站的贡献者页面

感谢您为 TimeNest 项目做出的贡献！🙏
