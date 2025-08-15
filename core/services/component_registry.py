from typing import Any, Dict, Optional, Type

from PySide6.QtCore import QObject, Signal


class ComponentInfo:
    """组件信息类"""

    def __init__(
        self, guid: str, name: str, icon_glyph: str = "", description: str = ""
    ):
        self.guid = guid
        self.name = name
        self.icon_glyph = icon_glyph
        self.description = description
        self.settings_type: Optional[Type[Any]] = None
        self.component_type: Optional[Type[QObject]] = None
        self.is_component_container = False


class ComponentRegistryService(QObject):
    """组件注册服务 - 负责组件的注册和管理"""

    # 定义信号
    component_added = Signal(ComponentInfo)
    component_removed = Signal(ComponentInfo)

    # 组件注册表
    registered_components: Dict[str, ComponentInfo] = {}
    registered_settings: Dict[str, ComponentInfo] = {}

    # 组件迁移映射
    migration_pairs: Dict[str, str] = {}

    def __init__(self):
        super().__init__()
        # 初始化内置组件
        self._register_builtin_components()

    def _register_builtin_components(self):
        """注册内置组件"""
        # 注册时钟组件信息
        clock_component_info = ComponentInfo(
            guid="9E1AF71D-8F77-4B21-A342-448787104DD9",
            name="时钟",
            icon_glyph="clock-digital",
            description="显示现在的时间，支持精确到秒。",
        )
        self.registered_components[clock_component_info.guid] = clock_component_info
        self.registered_settings[clock_component_info.guid] = clock_component_info

        # 注册日期组件信息
        date_component_info = ComponentInfo(
            guid="DF3F8295-21F6-482E-BADA-FA0E5F14BB66",
            name="日期",
            icon_glyph="calendar",
            description="显示今天的日期和星期。",
        )
        self.registered_components[date_component_info.guid] = date_component_info
        self.registered_settings[date_component_info.guid] = date_component_info

        # 注册课程表组件信息
        schedule_component_info = ComponentInfo(
            guid="1DB2017D-E374-4BC6-9D57-0B4ADF03A6B8",
            name="课程表",
            icon_glyph="schedule",
            description="显示当前的课程表信息。",
        )
        self.registered_components[schedule_component_info.guid] = (
            schedule_component_info
        )
        self.registered_settings[schedule_component_info.guid] = schedule_component_info

        # 注册文本组件信息
        text_component_info = ComponentInfo(
            guid="EE8F66BD-C423-4E7C-AB46-AA9976B00E08",
            name="文本",
            icon_glyph="format-text",
            description="显示自定义文本。",
        )
        self.registered_components[text_component_info.guid] = text_component_info
        self.registered_settings[text_component_info.guid] = text_component_info

        # 注册天气组件信息
        weather_component_info = ComponentInfo(
            guid="A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
            name="天气",
            icon_glyph="weather",
            description="显示天气信息。",
        )
        self.registered_components[weather_component_info.guid] = weather_component_info
        self.registered_settings[weather_component_info.guid] = weather_component_info

        # 注册倒计时组件信息
        countdown_component_info = ComponentInfo(
            guid="F0E1D2C3-B4A5-6789-0123-456789ABCDEF",
            name="倒计时",
            icon_glyph="timer",
            description="显示倒计时信息。",
        )
        self.registered_components[countdown_component_info.guid] = (
            countdown_component_info
        )
        self.registered_settings[countdown_component_info.guid] = (
            countdown_component_info
        )

        # 注册滚动组件信息
        rolling_component_info = ComponentInfo(
            guid="12345678-90AB-CDEF-1234-567890ABCDEF",
            name="滚动",
            icon_glyph="scroll",
            description="显示滚动组件。",
        )
        self.registered_components[rolling_component_info.guid] = rolling_component_info
        self.registered_settings[rolling_component_info.guid] = rolling_component_info

        # 注册分组组件信息
        group_component_info = ComponentInfo(
            guid="ABCDEF12-3456-7890-ABCD-EF1234567890",
            name="分组",
            icon_glyph="group",
            description="分组组件。",
        )
        self.registered_components[group_component_info.guid] = group_component_info
        self.registered_settings[group_component_info.guid] = group_component_info

        # 注册幻灯片组件信息
        slide_component_info = ComponentInfo(
            guid="7E19A113-D281-4F33-970A-834A0B78B5AD",
            name="轮播组件",
            icon_glyph="slideshow",
            description="轮播多个组件。",
        )
        self.registered_components[slide_component_info.guid] = slide_component_info
        self.registered_settings[slide_component_info.guid] = slide_component_info

        # 注册分割线组件信息
        separator_component_info = ComponentInfo(
            guid="AB0F26D5-9DF6-4575-B844-73B04D0907C1",
            name="分割线",
            icon_glyph="arrow-split-vertical",
            description="显示一个分割线，视觉上对组件进行分组。",
        )
        self.registered_components[separator_component_info.guid] = (
            separator_component_info
        )
        self.registered_settings[separator_component_info.guid] = (
            separator_component_info
        )

    def register_component(self, component_info: ComponentInfo):
        """注册组件"""
        if component_info.guid in self.registered_components:
            raise ValueError(f"组件ID {component_info.guid} 已被占用")

        self.registered_components[component_info.guid] = component_info
        if component_info.settings_type:
            self.registered_settings[component_info.guid] = component_info

        # 发出组件添加信号
        self.component_added.emit(component_info)

    def get_component_info(self, guid: str) -> Optional[ComponentInfo]:
        """根据GUID获取组件信息"""
        return self.registered_components.get(guid)

    def get_all_components(self) -> Dict[str, ComponentInfo]:
        """获取所有已注册的组件"""
        return self.registered_components.copy()

    def get_component_by_name(self, name: str) -> Optional[ComponentInfo]:
        """根据名称获取组件信息"""
        for component_info in self.registered_components.values():
            if component_info.name == name:
                return component_info
        return None

    def migrate_component(self, source_guid: str, target_guid: str):
        """注册组件迁移映射"""
        self.migration_pairs[source_guid] = target_guid

    def remove_component(self, guid: str):
        """移除组件"""
        if guid in self.registered_components:
            component_info = self.registered_components[guid]
            del self.registered_components[guid]
            if guid in self.registered_settings:
                del self.registered_settings[guid]

            # 发出组件移除信号
            self.component_removed.emit(component_info)

    def create_component_instance(
        self, guid: str, *args: Any, **kwargs: Any
    ) -> Optional[QObject]:
        """根据GUID创建组件实例"""
        component_info = self.get_component_info(guid)
        if not component_info or not component_info.component_type:
            return None

        try:
            # 创建组件实例
            instance = component_info.component_type(*args, **kwargs)
            return instance
        except Exception as e:
            print(f"创建组件实例失败 {guid}: {e}")
            return None


# 全局组件注册服务实例
component_registry = ComponentRegistryService()


def get_component_info_by_guid(guid: str) -> Optional[ComponentInfo]:
    """获取组件信息的便捷函数"""
    return component_registry.get_component_info(guid)


def get_component_by_name(name: str) -> Optional[ComponentInfo]:
    """根据名称获取组件信息的便捷函数"""
    return component_registry.get_component_by_name(name)


def get_all_components() -> Dict[str, ComponentInfo]:
    """获取所有组件的便捷函数"""
    return component_registry.get_all_components()


def register_component(component_info: ComponentInfo):
    """注册组件的便捷函数"""
    component_registry.register_component(component_info)


def create_component_instance(
    guid: str, *args: Any, **kwargs: Any
) -> Optional[QObject]:
    """创建组件实例的便捷函数"""
    return component_registry.create_component_instance(guid, *args, **kwargs)


# 测试代码
if __name__ == "__main__":
    # 测试组件注册服务
    print("=== 组件注册服务测试 ===")

    # 获取所有组件
    all_components = get_all_components()
    print(f"已注册组件数量: {len(all_components)}")

    # 查找时钟组件
    clock_component = get_component_by_name("时钟")
    if clock_component:
        print(f"时钟组件信息:")
        print(f"  GUID: {clock_component.guid}")
        print(f"  名称: {clock_component.name}")
        print(f"  描述: {clock_component.description}")
        print(f"  图标: {clock_component.icon_glyph}")

    # 测试创建组件实例
    try:
        clock_instance = create_component_instance(
            "9E1AF71D-8F77-4B21-A342-448787104DD9"
        )
        if clock_instance:
            print("✓ 时钟组件实例创建成功")
        else:
            print("✗ 时钟组件实例创建失败")
    except Exception as e:
        print(f"✗ 创建时钟组件实例时出错: {e}")
