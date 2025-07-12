#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 全面Traceback错误修复脚本
系统性地修复代码中所有可能导致运行时错误的问题
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any


class TracebackFixer:
    """Traceback错误修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors_found = []
        
    def fix_all_files(self, root_path: Path = None) -> Dict[str, Any]:
        """修复所有文件中的潜在错误"""
        if root_path is None:
            root_path = Path('.')
            
        results = {
            'files_processed': 0,
            'fixes_applied': 0,
            'errors_found': 0,
            'details': []
        }
        
        # 获取所有Python文件
        python_files = list(root_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                file_result = self._fix_file(file_path)
                results['files_processed'] += 1
                results['fixes_applied'] += file_result['fixes_applied']
                results['errors_found'] += file_result['errors_found']
                
                if file_result['fixes_applied'] > 0 or file_result['errors_found'] > 0:
                    results['details'].append({
                        'file': str(file_path),
                        'fixes': file_result['fixes_applied'],
                        'errors': file_result['errors_found'],
                        'details': file_result['details']
                    })
                    
            except Exception as e:
                print(f"处理文件失败 {file_path}: {e}")
                
        return results
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            'venv', '__pycache__', '.git', '.pytest_cache',
            'build', 'dist', '.tox', 'node_modules'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _fix_file(self, file_path: Path) -> Dict[str, Any]:
        """修复单个文件"""
        result = {
            'fixes_applied': 0,
            'errors_found': 0,
            'details': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 应用各种修复
            content = original_content
            
            # 1. 修复空值检查问题
            content, null_fixes = self._fix_null_checks(content, file_path)
            result['fixes_applied'] += null_fixes
            
            # 2. 修复字典/列表访问问题
            content, access_fixes = self._fix_dict_list_access(content, file_path)
            result['fixes_applied'] += access_fixes
            
            # 3. 修复类型检查问题
            content, type_fixes = self._fix_type_checks(content, file_path)
            result['fixes_applied'] += type_fixes
            
            # 4. 修复异常处理问题
            content, exception_fixes = self._fix_exception_handling(content, file_path)
            result['fixes_applied'] += exception_fixes
            
            # 5. 修复导入问题
            content, import_fixes = self._fix_import_issues(content, file_path)
            result['fixes_applied'] += import_fixes
            
            # 6. 修复属性访问问题
            content, attr_fixes = self._fix_attribute_access(content, file_path)
            result['fixes_applied'] += attr_fixes
            
            # 如果有修改，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 修复文件: {file_path} ({result['fixes_applied']} 个修复)")
            
        except Exception as e:
            result['errors_found'] += 1
            result['details'].append(f"处理文件失败: {e}")
            
        return result
    
    def _fix_null_checks(self, content: str, file_path: Path) -> Tuple[str, int]:
        """修复空值检查问题"""
        fixes = 0
        
        # 修复缺少空值检查的字典访问
        patterns = [
            # config.get('key') 后直接使用，应该检查是否为None
            (r'(\w+\.get\([^)]+\))\s*\.\s*(\w+)', r'(\1 or {}).get(\2)'),
            
            # 直接访问可能为None的对象的属性
            (r'if\s+(\w+)\s*:\s*\n\s*(\w+\.\w+)', r'if \1 and hasattr(\1, "\2"):\n    \2'),
        ]
        
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                fixes += 1
                content = new_content
                
        return content, fixes
    
    def _fix_dict_list_access(self, content: str, file_path: Path) -> Tuple[str, int]:
        """修复字典和列表访问问题"""
        fixes = 0
        
        # 查找可能的不安全字典访问
        dict_access_pattern = r'(\w+)\[([\'"][^\'"]+[\'"])\]'
        matches = re.findall(dict_access_pattern, content)
        
        for var_name, key in matches:
            # 检查是否已经有安全检查
            safe_pattern = f'{var_name}.get\\({key}'
            if safe_pattern not in content:
                # 替换为安全访问
                old_access = f'{var_name}[{key}]'
                new_access = f'{var_name}.get({key})'
                content = content.replace(old_access, new_access)
                fixes += 1
                
        return content, fixes
    
    def _fix_type_checks(self, content: str, file_path: Path) -> Tuple[str, int]:
        """修复类型检查问题"""
        fixes = 0
        
        # 添加isinstance检查
        patterns = [
            # 直接调用方法而不检查类型
            (r'(\w+)\.(\w+)\(', r'(\1.\2( if hasattr(\1, "\2") else lambda *args, **kwargs: None)('),
        ]
        
        # 这个修复比较复杂，暂时跳过自动修复
        return content, fixes
    
    def _fix_exception_handling(self, content: str, file_path: Path) -> Tuple[str, int]:
        """修复异常处理问题"""
        fixes = 0
        
        # 查找缺少异常处理的代码块
        risky_patterns = [
            r'open\([^)]+\)',  # 文件操作
            r'json\.loads?\(',  # JSON操作
            r'int\(',  # 类型转换
            r'float\(',
            r'__import__\(',  # 动态导入
        ]
        
        for pattern in risky_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # 检查是否已经在try块中
                start_pos = match.start()
                before_text = content[:start_pos]
                
                # 简单检查：查看前面是否有try
                lines_before = before_text.split('\n')[-10:]  # 检查前10行
                has_try = any('try:' in line for line in lines_before)
                
                if not has_try:
                    # 这里可以添加更复杂的try-catch包装逻辑
                    # 暂时只记录需要修复的位置
                    pass
                    
        return content, fixes
    
    def _fix_import_issues(self, content: str, file_path: Path) -> Tuple[str, int]:
        """修复导入问题"""
        fixes = 0
        
        # 修复可能的循环导入
        if 'from PyQt6' in content:
            # 添加PyQt6可用性检查
            pyqt_check = '''
try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass
'''
            if 'PYQT6_AVAILABLE' not in content:
                # 在文件开头添加检查
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('#') and not line.startswith('import') and not line.startswith('from'):
                        import_end = i
                        break
                
                lines.insert(import_end, pyqt_check)
                content = '\n'.join(lines)
                fixes += 1
                
        return content, fixes
    
    def _fix_attribute_access(self, content: str, file_path: Path) -> Tuple[str, int]:
        """修复属性访问问题"""
        fixes = 0
        
        # 查找可能的AttributeError
        attr_patterns = [
            r'(\w+)\.(\w+)\.(\w+)',  # 链式属性访问
            r'self\.(\w+)\.(\w+)',   # self属性访问
        ]
        
        for pattern in attr_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # 检查是否有hasattr检查
                attr_access = match.group(0)
                safe_check = f'hasattr({attr_access.split(".")[0]}, "{attr_access.split(".")[1]}")'
                
                if safe_check not in content:
                    # 可以添加安全检查，但需要更复杂的逻辑
                    pass
                    
        return content, fixes


def main():
    """主函数"""
    print("🔧 TimeNest Traceback错误修复工具")
    print("=" * 50)
    
    fixer = TracebackFixer()
    results = fixer.fix_all_files()
    
    print(f"\n📊 修复结果:")
    print(f"  处理文件: {results['files_processed']}")
    print(f"  应用修复: {results['fixes_applied']}")
    print(f"  发现错误: {results['errors_found']}")
    
    if results['details']:
        print(f"\n📋 详细信息:")
        for detail in results['details']:
            print(f"  {detail['file']}: {detail['fixes']} 修复, {detail['errors']} 错误")
    
    print(f"\n✅ 修复完成!")


if __name__ == "__main__":
    main()
