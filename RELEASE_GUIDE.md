# TimeNest 发布指南

本指南介绍如何使用自动化工具进行 TimeNest 的构建和发布。

## 📁 文件说明

### GitHub Actions 工作流
- `.github/workflows/release.yml` - 自动发布工作流（标签触发）
- `.github/workflows/build.yml` - 开发版本构建工作流（推送触发）

### 构建配置
- `TimeNest.spec` - PyInstaller 打包配置文件
- `version_info.txt` - Windows 可执行文件版本信息

### 本地工具
- `build_release.bat` - 本地构建脚本
- `release.py` - 版本管理和发布助手

## 🚀 发布流程

### 方法一：自动发布（推荐）

1. **准备发布**
   ```bash
   python release.py 1.0.1
   ```
   这将：
   - 更新版本信息文件
   - 创建 Git 标签
   - 提示下一步操作

2. **推送标签触发发布**
   ```bash
   git push origin v1.0.1
   ```
   GitHub Actions 将自动：
   - 构建 Windows 可执行文件
   - 创建便携版包
   - 发布 GitHub Release
   - 上传构建文件

### 方法二：本地构建

1. **本地构建**
   ```bash
   build_release.bat
   ```
   这将生成：
   - `dist/TimeNest.exe` - 可执行文件
   - `TimeNest-portable.zip` - 便携版包

2. **手动发布**
   - 在 GitHub 创建新的 Release
   - 上传生成的文件

## 🔧 配置说明

### PyInstaller 配置 (TimeNest.spec)

```python
# 包含的数据文件
datas=[
    ('config', 'config'),           # 配置文件
    ('resources', 'resources'),     # 资源文件
    ('plugin_template', 'plugin_template'),  # 插件模板
    # ... 其他目录
],

# 隐藏导入的模块
hiddenimports=[
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    # ... 其他模块
],
```

### 版本信息配置 (version_info.txt)

包含 Windows 可执行文件的元数据：
- 文件版本
- 产品版本
- 公司信息
- 版权信息

## 📋 发布检查清单

### 发布前
- [ ] 确保所有功能正常工作
- [ ] 更新 README.md 中的版本信息
- [ ] 检查依赖项是否最新
- [ ] 运行本地测试

### 发布时
- [ ] 使用 `release.py` 更新版本号
- [ ] 检查 Git 状态，确保无未提交更改
- [ ] 推送标签触发自动发布

### 发布后
- [ ] 验证 GitHub Release 是否正确创建
- [ ] 测试下载的可执行文件
- [ ] 更新项目文档

## 🛠️ 故障排除

### 构建失败
1. 检查 Python 环境和依赖
2. 确保所有资源文件存在
3. 查看 PyInstaller 错误日志

### GitHub Actions 失败
1. 检查工作流日志
2. 确保 GITHUB_TOKEN 权限正确
3. 验证标签格式 (v*.*.* )

### 版本号问题
1. 确保版本号格式为 x.y.z
2. 检查 version_info.txt 语法
3. 验证 Git 标签是否正确

## 📝 自定义配置

### 修改构建目标
编辑 `TimeNest.spec` 文件：
- 添加/删除数据文件
- 修改隐藏导入
- 调整可执行文件选项

### 修改发布流程
编辑 `.github/workflows/release.yml`：
- 更改触发条件
- 修改构建步骤
- 自定义 Release 描述

### 添加多平台支持
在工作流中添加其他操作系统：
```yaml
strategy:
  matrix:
    os: [windows-latest, ubuntu-latest, macos-latest]
```

## 🔗 相关链接

- [PyInstaller 文档](https://pyinstaller.readthedocs.io/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)