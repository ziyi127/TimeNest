#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the metaclass syntax is correct
This test doesn't require PyQt6 to be installed
"""

import ast
import sys
from pathlib import Path

def test_metaclass_syntax():
    """Test that the metaclass syntax is correct in base_manager.py"""
    print("Testing metaclass syntax in base_manager.py...")
    
    try:
        # Read the file
        base_manager_path = Path(__file__).parent / "core" / "base_manager.py"
        with open(base_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        tree = ast.parse(content)
        print("✓ base_manager.py syntax is valid")
        
        # Check for the custom metaclass definition
        metaclass_found = False
        base_manager_found = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == "QObjectABCMeta":
                    metaclass_found = True
                    print("✓ QObjectABCMeta metaclass definition found")
                    
                    # Check that it inherits from both type(QObject) and ABCMeta
                    if len(node.bases) == 2:
                        print("✓ QObjectABCMeta has correct number of base classes")
                    else:
                        print(f"✗ QObjectABCMeta should have 2 base classes, found {len(node.bases)}")
                        return False
                
                elif node.name == "BaseManager":
                    base_manager_found = True
                    print("✓ BaseManager class definition found")
                    
                    # Check that it uses the custom metaclass
                    metaclass_keyword_found = False
                    for keyword in node.keywords:
                        if keyword.arg == "metaclass":
                            metaclass_keyword_found = True
                            if isinstance(keyword.value, ast.Name) and keyword.value.id == "QObjectABCMeta":
                                print("✓ BaseManager uses QObjectABCMeta metaclass")
                            else:
                                print("✗ BaseManager should use QObjectABCMeta metaclass")
                                return False
                    
                    if not metaclass_keyword_found:
                        print("✗ BaseManager should specify metaclass=QObjectABCMeta")
                        return False
                    
                    # Check that it inherits from QObject and ABC
                    base_names = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            base_names.append(base.id)
                    
                    if "QObject" in base_names and "ABC" in base_names:
                        print("✓ BaseManager inherits from both QObject and ABC")
                    else:
                        print(f"✗ BaseManager should inherit from QObject and ABC, found: {base_names}")
                        return False
        
        if not metaclass_found:
            print("✗ QObjectABCMeta metaclass definition not found")
            return False
        
        if not base_manager_found:
            print("✗ BaseManager class definition not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Syntax test failed: {e}")
        return False

def test_component_system_syntax():
    """Test that component system also has correct metaclass syntax"""
    print("\nTesting metaclass syntax in component_system.py...")
    
    try:
        # Read the file
        component_path = Path(__file__).parent / "core" / "component_system.py"
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        tree = ast.parse(content)
        print("✓ component_system.py syntax is valid")
        
        # Check for the custom metaclass definition
        metaclass_found = False
        base_component_found = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == "QObjectABCMeta":
                    metaclass_found = True
                    print("✓ QObjectABCMeta metaclass definition found in component_system.py")
                
                elif node.name == "BaseComponent":
                    base_component_found = True
                    print("✓ BaseComponent class definition found")
                    
                    # Check that it uses the custom metaclass
                    metaclass_keyword_found = False
                    for keyword in node.keywords:
                        if keyword.arg == "metaclass":
                            metaclass_keyword_found = True
                            break
                    
                    if metaclass_keyword_found:
                        print("✓ BaseComponent uses custom metaclass")
                    else:
                        print("✗ BaseComponent should specify metaclass")
                        return False
        
        if not metaclass_found:
            print("✗ QObjectABCMeta metaclass definition not found in component_system.py")
            return False
        
        if not base_component_found:
            print("✗ BaseComponent class definition not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Component system syntax test failed: {e}")
        return False

def test_imports_syntax():
    """Test that the import statements are correct"""
    print("\nTesting import statements...")
    
    try:
        # Test that we can parse the import logic without actually importing PyQt6
        import ast
        
        # Check base_manager.py imports
        base_manager_path = Path(__file__).parent / "core" / "base_manager.py"
        with open(base_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Look for the required imports
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
        
        missing_imports = [name for name, found in required_imports.items() if not found]
        if missing_imports:
            print(f"✗ Missing required imports: {missing_imports}")
            return False
        else:
            print("✓ All required imports are present")
            return True
        
    except Exception as e:
        print(f"✗ Import syntax test failed: {e}")
        return False

def test_metaclass_theory():
    """Test the metaclass combination theory without PyQt6"""
    print("\nTesting metaclass combination theory...")
    
    try:
        from abc import ABC, ABCMeta, abstractmethod
        
        # Create a mock QObject-like class with a simple metaclass
        class MockQObjectMeta(type):
            """Mock PyQt metaclass"""
            def __new__(cls, name, bases, attrs):
                # Add some mock PyQt-like functionality
                attrs['_mock_pyqt'] = True
                return super().__new__(cls, name, bases, attrs)
        
        class MockQObject(metaclass=MockQObjectMeta):
            """Mock QObject class"""
            def connect(self):
                return "connected"
        
        # Create the combined metaclass (same pattern as our fix)
        class MockQObjectABCMeta(MockQObjectMeta, ABCMeta):
            """Combined metaclass for testing"""
            pass
        
        # Create a test class that inherits from both MockQObject and ABC
        class TestManager(MockQObject, ABC, metaclass=MockQObjectABCMeta):
            """Test class with combined inheritance"""
            
            @abstractmethod
            def test_method(self):
                pass
        
        # Test that the metaclass combination works
        print("✓ Combined metaclass created successfully")
        print(f"✓ TestManager metaclass: {type(TestManager)}")
        print(f"✓ TestManager has mock PyQt functionality: {hasattr(TestManager, '_mock_pyqt')}")
        
        # Test that abstract methods are enforced
        try:
            instance = TestManager()
            print("✗ Abstract class should not be instantiable")
            return False
        except TypeError as e:
            if "abstract" in str(e).lower():
                print("✓ Abstract methods are properly enforced")
            else:
                print(f"✗ Unexpected error: {e}")
                return False
        
        # Create a concrete implementation
        class ConcreteManager(TestManager):
            def test_method(self):
                return "implemented"
        
        # Test that concrete implementation works
        concrete = ConcreteManager()
        print("✓ Concrete implementation can be instantiated")
        print(f"✓ Has QObject-like functionality: {hasattr(concrete, 'connect')}")
        print(f"✓ Abstract method implemented: {concrete.test_method()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Metaclass theory test failed: {e}")
        return False

def main():
    """Run all syntax tests"""
    print("🔧 Testing TimeNest Metaclass Fix Syntax")
    print("=" * 50)
    
    tests = [
        test_metaclass_syntax,
        test_component_system_syntax,
        test_imports_syntax,
        test_metaclass_theory,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {i+1}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All syntax tests passed! Metaclass fix is syntactically correct.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
