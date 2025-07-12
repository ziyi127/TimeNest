# 🆘 TimeNest 紧急恢复指南

## 📋 问题描述

由于最近的增强功能导致了系统崩溃，包括：
- 浮窗消失
- UI无法操作
- 托盘菜单不见
- 系统崩溃

## 🔄 已执行的紧急措施

### 1. 系统回滚
- 已回滚到稳定版本 (commit: bfe9a62)
- 删除了所有导致问题的增强文件
- 清理了Python缓存和编译文件

### 2. 提供恢复工具
- `fix_system.py` - 系统清理和修复工具
- `safe_start.py` - 最小化安全启动脚本
- `main_emergency.py` - 紧急备用启动器
- `emergency_test.py` - 基本功能测试

## 🚀 恢复步骤

### 步骤 1: 基本环境检查
```bash
# 检查Python版本
python --version

# 检查当前目录
pwd
ls -la

# 确认在TimeNest目录中
```

### 步骤 2: 安装依赖
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或者使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 步骤 3: 尝试安全启动
```bash
# 方法1: 安全启动脚本
python safe_start.py

# 方法2: 如果方法1失败，使用紧急启动
python main_emergency.py

# 方法3: 如果都失败，测试基本功能
python emergency_test.py
```

### 步骤 4: 系统清理（如果需要）
```bash
# 运行系统修复工具
python fix_system.py

# 手动清理缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## 🔧 故障排除

### 问题1: PyQt6导入失败
```bash
# 解决方案
pip uninstall PyQt6
pip install PyQt6

# 或者尝试不同版本
pip install PyQt6==6.4.0
```

### 问题2: 系统托盘不可用
- **Linux**: 确保桌面环境支持系统托盘
- **Windows**: 检查系统托盘设置
- **macOS**: 确保应用有权限访问菜单栏

### 问题3: 权限问题
```bash
# 检查文件权限
ls -la *.py

# 修复权限
chmod +x *.py
```

### 问题4: 内存问题
- 重启计算机清理内存
- 关闭其他占用内存的程序
- 检查系统资源使用情况

## ✅ 验证恢复

### 基本功能检查
1. **托盘图标**: 应该能看到系统托盘中的TimeNest图标
2. **右键菜单**: 右键点击托盘图标应该显示菜单
3. **基本操作**: 菜单项应该可以点击
4. **无错误**: 控制台不应该有严重错误

### 成功标志
- ✅ 托盘图标正常显示
- ✅ 右键菜单可以打开
- ✅ 没有Python错误
- ✅ 系统运行稳定

## 🚨 重要注意事项

### 暂时避免的功能
- ❌ 不要使用复杂的增强功能
- ❌ 不要尝试添加新的模块
- ❌ 不要修改核心文件
- ❌ 避免同时运行多个实例

### 安全使用建议
- ✅ 只使用基本的课程表功能
- ✅ 定期保存数据
- ✅ 监控系统资源使用
- ✅ 遇到问题立即停止使用

## 📞 如果仍有问题

### 联系信息
如果按照上述步骤仍无法恢复，请提供以下信息：

1. **系统信息**:
   - 操作系统版本
   - Python版本
   - 错误消息

2. **执行结果**:
   ```bash
   python emergency_test.py > test_result.txt 2>&1
   ```

3. **日志文件**:
   - 查看是否有生成的日志文件
   - 提供最近的错误日志

### 最后手段
如果所有方法都失败：

1. **完全重新安装**:
   ```bash
   # 备份配置
   cp config.yaml config_backup.yaml
   
   # 重新克隆项目
   cd ..
   git clone https://github.com/ziyi127/TimeNest.git TimeNest_new
   cd TimeNest_new
   
   # 恢复配置
   cp ../TimeNest/config_backup.yaml config.yaml
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 测试启动
   python main.py
   ```

2. **使用更早的稳定版本**:
   ```bash
   git checkout main
   git pull origin main
   ```

## 📚 经验教训

### 问题原因分析
1. **过度复杂化**: 添加了太多复杂功能
2. **依赖冲突**: 新模块可能引起依赖问题
3. **内存泄漏**: 复杂功能可能导致内存问题
4. **测试不足**: 没有充分测试就部署

### 未来预防措施
1. **渐进式开发**: 一次只添加一个小功能
2. **充分测试**: 每次修改都要测试
3. **备份机制**: 保持稳定版本的备份
4. **简单优先**: 优先保证基本功能稳定

---

**🎯 目标: 恢复到稳定可用状态，确保基本功能正常工作**

记住：稳定性比功能丰富性更重要！
