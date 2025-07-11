import pytest
from unittest.mock import Mock
from TimeNest.core.app_manager import AppManager

class TestAppManager:
    """AppManager 单元测试"""
    
    @pytest.fixture
    def app_manager(self):
        """测试用的AppManager实例"""
        return AppManager()
    
    def test_initialization(self, app_manager):
        """测试初始化"""
        assert app_manager.config_manager is None
        assert app_manager.schedule_manager is None
        assert app_manager.notification_manager is None
        
    def test_initialize_success(self, app_manager, mocker):
        """测试成功初始化"""
        mocker.patch.object(app_manager, '_init_config_manager')
        mocker.patch.object(app_manager, '_init_schedule_manager')
        mocker.patch.object(app_manager, '_init_notification_manager')
        
        assert app_manager.initialize() is True
        app_manager._init_config_manager.assert_called_once()
        app_manager._init_schedule_manager.assert_called_once()
        app_manager._init_notification_manager.assert_called_once()