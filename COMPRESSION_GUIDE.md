# TimeNest 多架构打包指南

## 🎯 **打包策略概述**

TimeNest v2.2.0 采用简化的多架构打包策略，为不同平台提供通用格式的压缩包。

## 📋 **统一命名规则**

所有平台的包文件都采用统一的命名格式：
```
TimeNest_{版本号}_{架构}.{格式}
```

### **架构支持**
- **x86_64** - 64位Intel/AMD处理器
- **arm64** - 64位ARM处理器（Apple Silicon、ARM64服务器）

### **格式说明**
- **Windows**: `.zip` - 通用ZIP格式，兼容性最佳
- **Linux**: `.tar.gz` - 标准tar.gz格式，Linux通用
- **macOS**: `.zip` - 包含.app的ZIP格式

### **命名示例**
- `TimeNest_2.2.0_x86_64.zip` - Windows x64版本
- `TimeNest_2.2.0_arm64.tar.gz` - Linux ARM64版本
- `TimeNest_2.2.0_arm64.zip` - macOS Apple Silicon版本

## 📦 **Windows 平台**

### **格式**
- **TimeNest_{版本}_{架构}.zip** - 标准ZIP格式

### **压缩方式**
```powershell
# 使用PowerShell内置压缩
Compress-Archive -Path TimeNest-portable\* -DestinationPath TimeNest_2.2.0_x86_64.zip -CompressionLevel Optimal
```

### **支持架构**
- **x86_64** - 64位Intel/AMD处理器
- **arm64** - 64位ARM处理器（Windows 11 ARM）

## 🐧 **Linux 平台**

### **格式**
- **TimeNest_{版本}_{架构}.tar.gz** - 标准tar.gz格式

### **压缩方式**
```bash
# 使用tar和gzip压缩
tar -czf TimeNest_2.2.0_x86_64.tar.gz TimeNest-portable-linux/
```

### **支持架构**
- **x86_64** - 64位Intel/AMD处理器
- **arm64** - 64位ARM处理器（ARM64服务器、树莓派等）

### **包含内容**
- 可执行文件
- 资源文件
- 配置文件
- 启动脚本

## 🍎 **macOS 平台**

### **格式**
- **TimeNest_{版本}_{架构}.zip** - 包含.app的ZIP格式

### **压缩方式**
```bash
# 使用zip压缩
zip -r TimeNest_2.2.0_arm64.zip TimeNest-portable-macos/
```

### **支持架构**
- **x86_64** - 64位Intel处理器（Intel Mac）
- **arm64** - 64位ARM处理器（Apple Silicon Mac）

### **包含内容**
- TimeNest.app应用程序包
- 资源文件
- 说明文档

## 🏗️ **多架构支持**

### **GitHub Actions Matrix构建**
```yaml
strategy:
  matrix:
    arch: [x86_64, arm64]
```

### **架构检测**
- **Windows**: 使用matrix.arch参数
- **Linux**: 使用matrix.arch参数，ARM64通过QEMU模拟
- **macOS**: 使用matrix.arch参数，原生支持Intel和Apple Silicon

### **支持的架构**
- **x86_64**: Intel/AMD 64位处理器
- **arm64**: ARM 64位处理器（Apple Silicon、ARM64服务器）

## 📊 **格式对比**

### **兼容性**
- **ZIP**: 最佳兼容性，所有平台原生支持
- **tar.gz**: Linux标准格式，广泛支持

### **压缩效果**
- **ZIP**: 中等压缩比，快速解压
- **tar.gz**: 良好压缩比，标准格式

## 🛠️ **用户指南**

### **下载选择**
- **Windows用户**: 下载对应架构的`.zip`文件
- **Linux用户**: 下载对应架构的`.tar.gz`文件
- **macOS用户**: 下载对应架构的`.zip`文件

### **架构选择**
- **Intel/AMD处理器**: 选择`x86_64`版本
- **ARM处理器**: 选择`arm64`版本
- **不确定**: 大多数情况下选择`x86_64`版本

## 🔧 **解压方法**

### **Windows**
```cmd
# 右键解压或使用命令行
powershell Expand-Archive TimeNest_2.2.0_x86_64.zip
```

### **Linux**
```bash
# 解压tar.gz文件
tar -xzf TimeNest_2.2.0_x86_64.tar.gz
```

### **macOS**
```bash
# 双击解压或使用命令行
unzip TimeNest_2.2.0_arm64.zip
```

## 📈 **优势**

### **简化的构建流程**
- 每个平台每个架构只有一个包
- 使用通用格式，兼容性最佳
- 减少用户选择困难

### **多架构支持**
- 原生支持x86_64和ARM64
- 自动化构建流程
- 统一的命名规则

### **用户友好**
- 无需额外解压工具
- 文件大小适中
- 下载和安装简单

现在TimeNest提供了简洁高效的多架构打包方案！🚀
