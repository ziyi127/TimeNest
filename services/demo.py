"""
业务逻辑层使用演示
展示如何使用各种服务类处理业务逻辑
"""

from models.class_item import ClassItem, TimeSlot
from models.class_plan import ClassPlan
from models.temp_change import TempChange
from models.cycle_schedule import CycleSchedule, CycleScheduleItem, ScheduleItem
from services.service_factory import ServiceFactory
from services.business_coordinator import BusinessCoordinator
from utils.exceptions import ValidationException, ConflictException


def demo_course_service():
    """演示课程服务的使用"""
    print("=== 课程服务演示 ===")
    
    # 获取课程服务
    course_service = ServiceFactory.get_course_service()
    
    # 创建课程
    course = ClassItem(
        id="math_001",
        name="高等数学",
        teacher="张教授",
        location="A101",
        duration=TimeSlot(start_time="08:00", end_time="09:30")
    )
    
    try:
        created_course = course_service.create_course(course)
        print(f"创建课程成功: {created_course.name}")
        
        # 查询课程
        retrieved_course = course_service.get_course_by_id("math_001")
        if retrieved_course:
            print(f"查询课程成功: {retrieved_course.name}")
            
            # 更新课程
            retrieved_course.name = "线性代数"
            updated_course = course_service.update_course("math_001", retrieved_course)
            print(f"更新课程成功: {updated_course.name}")
        else:
            print("查询课程失败: 课程不存在")
        
        # 查询所有课程
        all_courses = course_service.get_all_courses()
        print(f"共有 {len(all_courses)} 门课程")
        
    except ValidationException as e:
        print(f"数据验证失败: {e.message}, 错误: {e.errors}")
    except ConflictException as e:
        print(f"资源冲突: {e.message}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def demo_schedule_service():
    """演示课程表服务的使用"""
    print("\n=== 课程表服务演示 ===")
    
    # 获取课程表服务
    schedule_service = ServiceFactory.get_schedule_service()
    
    # 创建课程表项
    schedule = ClassPlan(
        id="schedule_001",
        day_of_week=1,  # 星期一
        week_parity="both",  # 每周都有
        course_id="math_001",
        valid_from="2023-09-01",
        valid_to="2023-12-31"
    )
    
    try:
        created_schedule = schedule_service.create_schedule(schedule)
        print(f"创建课程表项成功: {created_schedule.id}")
        
        # 查询课程表项
        retrieved_schedule = schedule_service.get_schedule_by_id("schedule_001")
        if retrieved_schedule:
            print(f"查询课程表项成功: 星期{retrieved_schedule.day_of_week}")
        else:
            print("查询课程表项失败: 课程表项不存在")
        
        # 根据日期查询课程表项
        schedules_by_date = schedule_service.get_schedules_by_date("2023-10-15")
        print(f"2023-10-15 有 {len(schedules_by_date)} 个课程表项")
        
    except ValidationException as e:
        print(f"数据验证失败: {e.message}, 错误: {e.errors}")
    except ConflictException as e:
        print(f"资源冲突: {e.message}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def demo_temp_change_service():
    """演示临时换课服务的使用"""
    print("\n=== 临时换课服务演示 ===")
    
    # 获取临时换课服务
    temp_change_service = ServiceFactory.get_temp_change_service()
    
    # 创建临时换课
    temp_change = TempChange(
        id="temp_001",
        original_schedule_id="schedule_001",
        new_course_id="math_001",
        change_date="2023-10-20"
    )
    
    try:
        created_temp_change = temp_change_service.create_temp_change(temp_change)
        print(f"创建临时换课成功: {created_temp_change.id}")
        
        # 查询临时换课
        retrieved_temp_change = temp_change_service.get_temp_change_by_id("temp_001")
        if retrieved_temp_change:
            print(f"查询临时换课成功: 换课日期 {retrieved_temp_change.change_date}")
        else:
            print("查询临时换课失败: 临时换课不存在")
        
        # 标记为已使用
        used_temp_change = temp_change_service.mark_temp_change_as_used("temp_001")
        if used_temp_change:
            print(f"标记临时换课为已使用: {used_temp_change.used}")
        else:
            print("标记临时换课为已使用失败: 临时换课不存在")
        
    except ValidationException as e:
        print(f"数据验证失败: {e.message}, 错误: {e.errors}")
    except ConflictException as e:
        print(f"资源冲突: {e.message}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def demo_cycle_schedule_service():
    """演示循环课程表服务的使用"""
    print("\n=== 循环课程表服务演示 ===")
    
    # 获取循环课程表服务
    cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
    
    # 创建循环课程表项
    schedule_items = [
        ScheduleItem(day_of_week=1, course_id="math_001"),  # 星期一: 高等数学
        ScheduleItem(day_of_week=3, course_id="math_001")   # 星期三: 高等数学
    ]
    
    cycle_schedule_item = CycleScheduleItem(
        week_index=0,
        schedule_items=schedule_items
    )
    
    # 创建循环课程表
    cycle_schedule = CycleSchedule(
        id="cycle_001",
        name="数学循环课程表",
        cycle_length=2,
        schedules=[cycle_schedule_item]
    )
    
    try:
        created_cycle_schedule = cycle_schedule_service.create_cycle_schedule(cycle_schedule)
        print(f"创建循环课程表成功: {created_cycle_schedule.name}")
        
        # 查询循环课程表
        retrieved_cycle_schedule = cycle_schedule_service.get_cycle_schedule_by_id("cycle_001")
        if retrieved_cycle_schedule:
            print(f"查询循环课程表成功: 循环长度 {retrieved_cycle_schedule.cycle_length}")
        else:
            print("查询循环课程表失败: 循环课程表不存在")
        
        # 生成指定日期的课程表项
        schedule_items = cycle_schedule_service.generate_schedule_for_date(
            "cycle_001", 
            "2023-10-16",  # 星期一
            "2023-09-01"
        )
        print(f"生成课程表项成功: 共 {len(schedule_items)} 个课程")
        
    except ValidationException as e:
        print(f"数据验证失败: {e.message}, 错误: {e.errors}")
    except ConflictException as e:
        print(f"资源冲突: {e.message}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def demo_business_coordinator():
    """演示业务协调器的使用"""
    print("\n=== 业务协调器演示 ===")
    
    # 创建业务协调器
    coordinator = BusinessCoordinator()
    
    # 创建课程和课程表项
    course = ClassItem(
        id="physics_001",
        name="大学物理",
        teacher="李教授",
        location="B201",
        duration=TimeSlot(start_time="10:00", end_time="11:30")
    )
    
    schedule = ClassPlan(
        id="schedule_physics_001",
        day_of_week=2,  # 星期二
        week_parity="both",
        course_id="",  # 会在协调器中设置
        valid_from="2023-09-01",
        valid_to="2023-12-31"
    )
    
    try:
        created_course, created_schedule = coordinator.create_course_with_schedule(course, schedule)
        print(f"创建课程和课程表项成功: {created_course.name}, {created_schedule.id}")
        
    except ValidationException as e:
        print(f"数据验证失败: {e.message}, 错误: {e.errors}")
    except ConflictException as e:
        print(f"资源冲突: {e.message}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def main():
    """主函数"""
    print("TimeNest 业务逻辑层演示")
    print("=" * 50)
    
    # 演示各个服务的使用
    demo_course_service()
    demo_schedule_service()
    demo_temp_change_service()
    demo_cycle_schedule_service()
    demo_business_coordinator()
    
    print("\n演示完成")


if __name__ == "__main__":
    main()
