# Git 推送操作指南

## 基本推送流程

### 1. 添加文件到暂存区
```bash
git add .
```

### 2. 提交更改
```bash
git commit -m "描述你的更改"
```

### 3. 推送到远程仓库
```bash
git push origin main
```

## GitHub Actions自动构建

### 触发条件
推送代码到以下分支会自动触发构建：
- `main` 分支 - 生产环境构建
- `develop` 分支 - 开发环境构建
- `feature/*` 分支 - 功能测试构建
- `fix/*` 分支 - 修复测试构建

### 创建版本发布
创建并推送版本标签以触发发布：
```bash
# 创建标签
git tag v1.0.0

# 推送标签到远程
git push origin v1.0.0
```

### 查看构建状态
1. 访问GitHub仓库页面
2. 点击 "Actions" 选项卡
3. 查看最新的工作流运行状态

### 下载构建产物
1. 进入具体的workflow运行页面
2. 在 "Artifacts" 部分下载对应系统的构建产物

## 分支策略

### 主要分支
- `main`: 稳定版本，自动构建并发布
- `develop`: 开发版本，自动构建测试

### 功能分支
- `feature/功能名称`: 新功能开发
- `fix/修复名称`: 问题修复
- `hotfix/紧急修复`: 紧急修复

## 推送前检查

推送代码前建议进行以下检查：

1. **代码测试**
   ```bash
   python -m py_compile main.py
   python -m py_compile build_with_nuitka.py
   ```

2. **依赖检查**
   ```bash
   pip install -r requirements.txt
   ```

3. **构建测试**
   ```bash
   python build_with_nuitka.py
   ```

## 常见问题

### 构建失败
如果GitHub Actions构建失败：
1. 检查 "Actions" 页面中的错误日志
2. 确认所有必需文件已提交
3. 验证构建脚本语法

### 标签冲突
如果版本标签已存在：
```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0

# 重新创建并推送
git tag v1.0.0
git push origin v1.0.0
```

## 工作流文件

项目包含以下GitHub Actions工作流：

- `.github/workflows/auto-build.yml`: 主要构建和发布工作流
- `.github/workflows/test-build.yml`: 测试构建工作流
- `.github/workflows/validate-config.yml`: 配置验证工作流