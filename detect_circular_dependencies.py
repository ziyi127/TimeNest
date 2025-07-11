#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 循环依赖检测脚本
检测项目中的循环依赖问题
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque

def extract_imports(file_path: Path) -> List[str]:
    """提取文件中的导入语句"""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配各种导入模式
        patterns = [
            r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',  # from module import
            r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',         # import module
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        # 过滤掉标准库和第三方库
        filtered_imports = []
        for imp in imports:
            # 只保留项目内部的导入
            if (imp.startswith('core.') or imp.startswith('ui.') or 
                imp.startswith('models.') or imp.startswith('utils.') or
                imp in ['core', 'ui', 'models', 'utils']):
                filtered_imports.append(imp)
        
        return filtered_imports
        
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return []

def build_dependency_graph(project_root: Path) -> Dict[str, List[str]]:
    """构建依赖关系图"""
    graph = defaultdict(list)
    
    # 扫描所有Python文件
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith('.') or 'venv' in str(py_file):
            continue
        
        # 获取模块名
        relative_path = py_file.relative_to(project_root)
        module_name = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
        
        # 提取导入
        imports = extract_imports(py_file)
        
        for imp in imports:
            graph[module_name].append(imp)
    
    return dict(graph)

def find_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
    """查找循环依赖"""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node: str) -> bool:
        if node in rec_stack:
            # 找到循环，提取循环路径
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return True
        
        if node in visited:
            return False
        
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True
        
        rec_stack.remove(node)
        path.pop()
        return False
    
    for node in graph:
        if node not in visited:
            dfs(node)
    
    return cycles

def analyze_dependencies():
    """分析依赖关系"""
    print("🔍 TimeNest 循环依赖检测")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    
    # 构建依赖图
    print("📊 构建依赖关系图...")
    graph = build_dependency_graph(project_root)
    
    print(f"✓ 扫描到 {len(graph)} 个模块")
    
    # 显示关键模块的依赖关系
    key_modules = [
        'main',
        'core.app_manager',
        'core.floating_manager', 
        'core.notification_manager',
        'ui.main_window',
        'ui.floating_widget',
        'ui.system_tray'
    ]
    
    print("\n📋 关键模块依赖关系:")
    for module in key_modules:
        if module in graph:
            deps = graph[module]
            print(f"  {module}:")
            for dep in deps[:5]:  # 只显示前5个依赖
                print(f"    → {dep}")
            if len(deps) > 5:
                print(f"    ... 还有 {len(deps) - 5} 个依赖")
        else:
            print(f"  {module}: 未找到")
    
    # 检测循环依赖
    print("\n🔄 检测循环依赖...")
    cycles = find_cycles(graph)
    
    if cycles:
        print(f"❌ 发现 {len(cycles)} 个循环依赖:")
        for i, cycle in enumerate(cycles, 1):
            print(f"\n  循环 {i}:")
            for j, module in enumerate(cycle):
                if j < len(cycle) - 1:
                    print(f"    {module} → {cycle[j + 1]}")
                else:
                    print(f"    {module}")
    else:
        print("✅ 未发现循环依赖")
    
    # 分析具体的问题模块
    print("\n🎯 问题分析:")
    
    # 检查 app_manager 的依赖
    if 'core.app_manager' in graph:
        app_deps = graph['core.app_manager']
        floating_deps = []
        if 'core.floating_manager' in app_deps:
            floating_deps.append('core.floating_manager')
        
        print(f"  app_manager 依赖: {len(app_deps)} 个模块")
        if floating_deps:
            print(f"    ⚠️ 依赖浮窗管理器: {floating_deps}")
    
    # 检查 floating_manager 的依赖
    if 'core.floating_manager' in graph:
        floating_deps = graph['core.floating_manager']
        app_deps = []
        if 'core.app_manager' in floating_deps:
            app_deps.append('core.app_manager')
        
        print(f"  floating_manager 依赖: {len(floating_deps)} 个模块")
        if app_deps:
            print(f"    ❌ 依赖应用管理器: {app_deps} (循环依赖!)")
    
    # 检查相对导入问题
    print("\n📁 相对导入检查:")
    relative_import_files = []
    
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith('.') or 'venv' in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'from ..' in content or 'from .' in content:
                relative_path = py_file.relative_to(project_root)
                relative_import_files.append(str(relative_path))
        except:
            continue
    
    if relative_import_files:
        print(f"  ⚠️ 发现 {len(relative_import_files)} 个文件使用相对导入:")
        for file in relative_import_files[:10]:  # 只显示前10个
            print(f"    - {file}")
        if len(relative_import_files) > 10:
            print(f"    ... 还有 {len(relative_import_files) - 10} 个文件")
    else:
        print("  ✅ 未发现相对导入")
    
    return cycles, graph

def generate_dependency_report(cycles: List[List[str]], graph: Dict[str, List[str]]):
    """生成依赖关系报告"""
    report_path = Path(__file__).parent / "dependency_analysis_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# TimeNest 依赖关系分析报告\n\n")
        f.write(f"生成时间: {os.popen('date').read().strip()}\n\n")
        
        f.write("## 循环依赖检测结果\n\n")
        if cycles:
            f.write(f"❌ **发现 {len(cycles)} 个循环依赖**\n\n")
            for i, cycle in enumerate(cycles, 1):
                f.write(f"### 循环依赖 {i}\n\n")
                f.write("```\n")
                for j, module in enumerate(cycle):
                    if j < len(cycle) - 1:
                        f.write(f"{module} → {cycle[j + 1]}\n")
                    else:
                        f.write(f"{module}\n")
                f.write("```\n\n")
        else:
            f.write("✅ **未发现循环依赖**\n\n")
        
        f.write("## 模块依赖关系\n\n")
        for module, deps in sorted(graph.items()):
            f.write(f"### {module}\n\n")
            if deps:
                for dep in deps:
                    f.write(f"- {dep}\n")
            else:
                f.write("- 无依赖\n")
            f.write("\n")
        
        f.write("## 修复建议\n\n")
        f.write("1. **使用依赖注入**: 通过构造函数传递依赖，而非直接导入\n")
        f.write("2. **接口抽象**: 创建抽象基类，减少具体类之间的依赖\n")
        f.write("3. **延迟导入**: 将导入语句移到函数内部\n")
        f.write("4. **事件系统**: 使用信号槽机制替代直接方法调用\n")
        f.write("5. **重构架构**: 调整模块职责，提取共同依赖\n")
    
    print(f"\n📄 依赖关系报告已生成: {report_path}")

def main():
    """主函数"""
    try:
        cycles, graph = analyze_dependencies()
        generate_dependency_report(cycles, graph)
        
        if cycles:
            print(f"\n❌ 检测到 {len(cycles)} 个循环依赖，需要修复")
            return False
        else:
            print(f"\n✅ 依赖关系检查通过")
            return True
            
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
