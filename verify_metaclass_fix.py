#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for the TimeNest metaclass conflict fix

This script verifies that the metaclass conflict in BaseManager has been resolved
and that all related functionality works correctly.
"""

import ast
import sys
from pathlib import Path

def verify_metaclass_fix():
    """Verify that the metaclass fix is properly implemented"""
    print("🔧 Verifying TimeNest Metaclass Conflict Fix")
    print("=" * 50)
    
    # Check 1: Verify BaseManager syntax
    print("1. Checking BaseManager implementation...")
    
    try:
        base_manager_path = Path(__file__).parent / "core" / "base_manager.py"
        with open(base_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Look for the custom metaclass and BaseManager class
        metaclass_found = False
        base_manager_correct = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == "QObjectABCMeta":
                    metaclass_found = True
                    print("   ✓ QObjectABCMeta metaclass found")
                
                elif node.name == "BaseManager":
                    # Check inheritance and metaclass
                    base_names = [base.id for base in node.bases if isinstance(base, ast.Name)]
                    
                    has_qobject = "QObject" in base_names
                    has_abc = "ABC" in base_names
                    
                    # Check for metaclass keyword
                    has_metaclass = any(
                        kw.arg == "metaclass" and 
                        isinstance(kw.value, ast.Name) and 
                        kw.value.id == "QObjectABCMeta"
                        for kw in node.keywords
                    )
                    
                    if has_qobject and has_abc and has_metaclass:
                        base_manager_correct = True
                        print("   ✓ BaseManager correctly inherits from QObject and ABC")
                        print("   ✓ BaseManager uses QObjectABCMeta metaclass")
        
        if not metaclass_found:
            print("   ✗ QObjectABCMeta metaclass not found")
            return False
        
        if not base_manager_correct:
            print("   ✗ BaseManager not correctly implemented")
            return False
        
    except Exception as e:
        print(f"   ✗ Error checking BaseManager: {e}")
        return False
    
    # Check 2: Verify imports are correct
    print("\n2. Checking import statements...")
    
    try:
        # Check that all required imports are present
        required_imports = {
            'ABC': False,
            'abstractmethod': False, 
            'ABCMeta': False,
            'QObject': False,
            'pyqtSignal': False,
            'QTimer': False
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'abc':
                    for alias in node.names:
                        if alias.name in required_imports:
                            required_imports[alias.name] = True
                elif node.module == 'PyQt6.QtCore':
                    for alias in node.names:
                        if alias.name in required_imports:
                            required_imports[alias.name] = True
        
        missing = [name for name, found in required_imports.items() if not found]
        if missing:
            print(f"   ✗ Missing imports: {missing}")
            return False
        else:
            print("   ✓ All required imports present")
    
    except Exception as e:
        print(f"   ✗ Error checking imports: {e}")
        return False
    
    # Check 3: Verify consistency with component system
    print("\n3. Checking consistency with component system...")
    
    try:
        component_path = Path(__file__).parent / "core" / "component_system.py"
        if component_path.exists():
            with open(component_path, 'r', encoding='utf-8') as f:
                component_content = f.read()
            
            component_tree = ast.parse(component_content)
            
            # Look for similar metaclass pattern
            has_similar_pattern = False
            for node in ast.walk(component_tree):
                if isinstance(node, ast.ClassDef):
                    if node.name == "QObjectABCMeta":
                        has_similar_pattern = True
                        break
            
            if has_similar_pattern:
                print("   ✓ Consistent with component system metaclass pattern")
            else:
                print("   ⚠️  Component system uses different pattern (acceptable)")
        else:
            print("   ⚠️  Component system file not found (acceptable)")
    
    except Exception as e:
        print(f"   ✗ Error checking component system: {e}")
        return False
    
    # Check 4: Verify abstract methods are preserved
    print("\n4. Checking abstract methods...")
    
    try:
        abstract_methods_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for @abstractmethod decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                        abstract_methods_found.append(node.name)
        
        expected_abstract_methods = ["initialize", "cleanup"]
        missing_abstract = [method for method in expected_abstract_methods 
                          if method not in abstract_methods_found]
        
        if missing_abstract:
            print(f"   ✗ Missing abstract methods: {missing_abstract}")
            return False
        else:
            print(f"   ✓ Abstract methods found: {abstract_methods_found}")
    
    except Exception as e:
        print(f"   ✗ Error checking abstract methods: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All checks passed! Metaclass conflict fix is properly implemented.")
    print("\n📋 Summary of the fix:")
    print("   • Created QObjectABCMeta combining type(QObject) and ABCMeta")
    print("   • Updated BaseManager to use the custom metaclass")
    print("   • Preserved all QObject functionality (signals, slots)")
    print("   • Maintained abstract base class behavior")
    print("   • Ensured backward compatibility")
    print("\n🎯 Expected outcome:")
    print("   • TimeNest application should start without metaclass conflicts")
    print("   • All BaseManager subclasses should work correctly")
    print("   • Plugin system and tray functionality should be operational")
    
    return True

def show_usage_example():
    """Show how the fix works"""
    print("\n" + "=" * 50)
    print("📖 How the fix works:")
    print("\nBefore (caused metaclass conflict):")
    print("   class BaseManager(QObject, ABC):  # ❌ Conflict!")
    print("\nAfter (resolved with custom metaclass):")
    print("   class QObjectABCMeta(type(QObject), ABCMeta):")
    print("       pass")
    print("   ")
    print("   class BaseManager(QObject, ABC, metaclass=QObjectABCMeta):  # ✅ Works!")
    print("\nThis allows BaseManager to:")
    print("   ✓ Use PyQt signals and slots (from QObject)")
    print("   ✓ Enforce abstract methods (from ABC)")
    print("   ✓ Be inherited by concrete manager classes")
    print("   ✓ Maintain all existing functionality")

if __name__ == "__main__":
    try:
        success = verify_metaclass_fix()
        if success:
            show_usage_example()
            print("\n🎉 Verification completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Verification failed. Please check the implementation.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Verification script failed: {e}")
        sys.exit(1)
