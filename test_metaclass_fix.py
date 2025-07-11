#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the metaclass conflict fix
"""

import sys
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_base_manager_import():
    """Test BaseManager import and instantiation"""
    print("Testing BaseManager metaclass fix...")
    
    try:
        # Test import
        from core.base_manager import BaseManager, QObjectABCMeta
        print("✓ BaseManager imported successfully")
        
        # Test metaclass
        print(f"✓ QObjectABCMeta created: {QObjectABCMeta}")
        print(f"✓ BaseManager metaclass: {type(BaseManager)}")
        
        # Test that BaseManager is abstract (cannot be instantiated directly)
        try:
            # This should fail because BaseManager has abstract methods
            manager = BaseManager(None, "test")
            print("✗ BaseManager should not be instantiable (has abstract methods)")
            return False
        except TypeError as e:
            if "abstract" in str(e).lower():
                print("✓ BaseManager correctly prevents direct instantiation (abstract class)")
            else:
                print(f"✗ Unexpected error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ BaseManager test failed: {e}")
        traceback.print_exc()
        return False

def test_time_calibration_service():
    """Test TimeCalibrationService (inherits from BaseManager)"""
    print("\nTesting TimeCalibrationService...")
    
    try:
        from core.time_calibration_service import TimeCalibrationService
        print("✓ TimeCalibrationService imported successfully")
        
        # Test instantiation
        service = TimeCalibrationService(None)
        print("✓ TimeCalibrationService instantiated successfully")
        
        # Test that it has both QObject and ABC functionality
        print(f"✓ Has QObject functionality: {hasattr(service, 'connect')}")
        print(f"✓ Has abstract methods implemented: {hasattr(service, 'initialize')}")
        
        return True
        
    except Exception as e:
        print(f"✗ TimeCalibrationService test failed: {e}")
        traceback.print_exc()
        return False

def test_plugin_development_tools():
    """Test PluginDevelopmentTools (inherits from BaseManager)"""
    print("\nTesting PluginDevelopmentTools...")
    
    try:
        from core.plugin_development_tools import PluginDevelopmentTools
        print("✓ PluginDevelopmentTools imported successfully")
        
        # Test instantiation
        tools = PluginDevelopmentTools(None)
        print("✓ PluginDevelopmentTools instantiated successfully")
        
        # Test that it has both QObject and ABC functionality
        print(f"✓ Has QObject functionality: {hasattr(tools, 'connect')}")
        print(f"✓ Has abstract methods implemented: {hasattr(tools, 'initialize')}")
        
        return True
        
    except Exception as e:
        print(f"✗ PluginDevelopmentTools test failed: {e}")
        traceback.print_exc()
        return False

def test_enhanced_plugin_manager():
    """Test EnhancedPluginManager (inherits from BaseManager)"""
    print("\nTesting EnhancedPluginManager...")
    
    try:
        from core.plugin_system.enhanced_plugin_manager import EnhancedPluginManager
        print("✓ EnhancedPluginManager imported successfully")
        
        # Test instantiation
        manager = EnhancedPluginManager(None)
        print("✓ EnhancedPluginManager instantiated successfully")
        
        # Test that it has both QObject and ABC functionality
        print(f"✓ Has QObject functionality: {hasattr(manager, 'connect')}")
        print(f"✓ Has abstract methods implemented: {hasattr(manager, 'initialize')}")
        
        return True
        
    except Exception as e:
        print(f"✗ EnhancedPluginManager test failed: {e}")
        traceback.print_exc()
        return False

def test_component_system():
    """Test component system metaclass fixes"""
    print("\nTesting component system...")
    
    try:
        from core.component_system import BaseComponent, QObjectABCMeta as ComponentMeta
        print("✓ Component system imported successfully")
        
        print(f"✓ Component QObjectABCMeta: {ComponentMeta}")
        print(f"✓ BaseComponent metaclass: {type(BaseComponent)}")
        
        # Test that BaseComponent is abstract
        try:
            component = BaseComponent()
            print("✗ BaseComponent should not be instantiable (has abstract methods)")
            return False
        except TypeError as e:
            if "abstract" in str(e).lower():
                print("✓ BaseComponent correctly prevents direct instantiation (abstract class)")
            else:
                print(f"✗ Unexpected error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Component system test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔧 Testing TimeNest Metaclass Conflict Fix")
    print("=" * 50)
    
    tests = [
        test_base_manager_import,
        test_time_calibration_service,
        test_plugin_development_tools,
        test_enhanced_plugin_manager,
        test_component_system,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            traceback.print_exc()
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
        print("🎉 All tests passed! Metaclass conflict is resolved.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
