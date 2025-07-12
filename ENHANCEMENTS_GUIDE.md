# TimeNest 增强功能使用指南

## 🎯 概述

TimeNest 在保持原有框架不变的基础上，新增了多项细分功能，提升学习效率和用户体验。

## 📚 课程表增强功能

### 学习任务管理
- **功能**: 创建、跟踪和管理学习任务
- **特性**:
  - 任务优先级设置（低、普通、高、紧急）
  - 预估时间和实际用时跟踪
  - 任务状态管理（待处理、进行中、已完成、已取消）
  - 标签分类系统

### 学习会话跟踪
- **功能**: 记录和分析学习会话
- **特性**:
  - 自动计时功能
  - 效率评分（1-5分）
  - 学习笔记记录
  - 会话历史查看

### 考试信息管理
- **功能**: 管理考试安排和准备
- **特性**:
  - 考试时间、地点、时长记录
  - 考试类型分类
  - 关联准备任务
  - 考试提醒设置

### 使用方法
```python
# 添加学习任务
task_id = schedule_enhancement.add_study_task(
    title="复习线性代数",
    subject="数学",
    due_date=datetime.now() + timedelta(days=3),
    priority=TaskPriority.HIGH,
    estimated_duration=120
)

# 开始学习会话
session_id = schedule_enhancement.start_study_session(task_id)

# 结束学习会话
schedule_enhancement.end_study_session(session_id, "完成第一章复习", 4)
```

## 🔔 通知增强功能

### 智能提醒系统
- **功能**: 创建智能化的提醒通知
- **特性**:
  - 多种提醒类型（课程开始、任务到期、休息时间等）
  - 自定义提醒样式（简约、标准、详细、紧急）
  - 重复提醒设置
  - 条件触发机制

### 专注模式
- **功能**: 番茄工作法式的专注学习
- **特性**:
  - 可自定义专注时长
  - 自动休息提醒
  - 专注期间通知过滤
  - 专注统计记录

### 课程和任务提醒
- **功能**: 自动生成课程和任务提醒
- **特性**:
  - 课程开始前提醒
  - 任务到期提醒
  - 智能提醒时间计算
  - 模板化消息生成

### 使用方法
```python
# 创建课程提醒
reminder_id = notification_enhancement.create_course_reminder(
    course_name="高等数学",
    start_time=datetime.now() + timedelta(hours=2),
    advance_minutes=15
)

# 启动专注模式
notification_enhancement.start_focus_mode(duration=25, break_duration=5)

# 创建自定义提醒
notification_enhancement.create_smart_reminder(
    title="复习提醒",
    message="该复习昨天的内容了",
    reminder_type=ReminderType.CUSTOM,
    trigger_time=datetime.now() + timedelta(hours=1)
)
```

## 🤖 智能学习助手

### 学习模式分析
- **功能**: 分析个人学习习惯和模式
- **特性**:
  - 最佳学习时间段识别
  - 学习模式检测（晨型人、夜型人、平衡型等）
  - 学习时长偏好分析
  - 科目分布统计

### 智能学习建议
- **功能**: 基于数据分析提供个性化建议
- **特性**:
  - 时间管理建议
  - 科目平衡建议
  - 学习效率优化建议
  - 环境优化建议

### 学习数据分析
- **功能**: 全面的学习数据统计和分析
- **特性**:
  - 总学习时间统计
  - 平均会话长度分析
  - 效率趋势图表
  - 任务完成率统计
  - 连续学习天数记录

### 使用方法
```python
# 分析学习模式
analysis = study_assistant.analyze_study_patterns()

# 生成学习建议
recommendations = study_assistant.generate_study_recommendations()

# 获取学习分析数据
analytics = study_assistant.get_learning_analytics()

# 获取每日学习总结
daily_summary = study_assistant.get_daily_study_summary()
```

## 🎈 浮窗增强功能

### 快速操作
- **功能**: 浮窗模块的快速操作菜单
- **特性**:
  - 系统状态模块快速操作
  - 任务管理器快速启动
  - 系统信息快速查看
  - 自定义操作扩展

### 紧凑模式
- **功能**: 浮窗的紧凑显示模式
- **特性**:
  - 节省屏幕空间
  - 保持核心信息显示
  - 动态切换模式
  - 自适应布局

### 智能隐藏
- **功能**: 根据使用情况自动隐藏浮窗
- **特性**:
  - 非活动时自动隐藏
  - 鼠标悬停显示
  - 优先级控制
  - 用户习惯学习

## 🎯 托盘增强功能

### 快速学习会话
- **功能**: 从托盘快速开始学习
- **特性**:
  - 一键开始25分钟学习会话
  - 自动创建学习任务
  - 科目快速选择
  - 会话状态显示

### 专注模式控制
- **功能**: 托盘快速控制专注模式
- **特性**:
  - 快速启动专注模式
  - 专注状态显示
  - 剩余时间提示
  - 快速结束功能

### 学习统计查看
- **功能**: 托盘快速查看学习数据
- **特性**:
  - 今日学习时间
  - 本周学习统计
  - 任务完成情况
  - 学习连续天数

### 快速操作菜单
- **功能**: 托盘的增强操作菜单
- **特性**:
  - 快速学习（Ctrl+Q）
  - 专注模式（Ctrl+F）
  - 学习统计（Ctrl+S）
  - 今日总结（Ctrl+D）

## 🚀 使用场景示例

### 场景1：开始学习会话
1. 右键点击托盘图标
2. 选择"快速学习"
3. 系统自动创建25分钟学习任务
4. 开始计时和效率跟踪

### 场景2：查看学习进度
1. 右键点击托盘图标
2. 选择"学习统计"
3. 查看详细的学习数据分析
4. 获取个性化学习建议

### 场景3：专注学习
1. 使用快捷键 Ctrl+F 启动专注模式
2. 系统进入25分钟专注状态
3. 过滤非重要通知
4. 自动提醒休息时间

### 场景4：任务管理
1. 通过托盘打开课程表管理
2. 添加学习任务和考试信息
3. 设置提醒和优先级
4. 跟踪完成进度

## 🔧 配置选项

### 学习助手配置
```yaml
study_assistant:
  daily_study_goal: 180  # 每日学习目标（分钟）
  preferred_session_length: 45  # 偏好会话长度
  break_length: 10  # 休息时长
  difficulty_preference: 3  # 难度偏好（1-5）
```

### 通知增强配置
```yaml
notification_enhancement:
  focus_mode:
    default_duration: 25  # 默认专注时长
    default_break: 5  # 默认休息时长
    allowed_notifications:  # 专注模式允许的通知类型
      - course_start
      - exam_approaching
```

### 浮窗增强配置
```yaml
floating_widget:
  enhancements:
    compact_mode: false  # 默认紧凑模式
    auto_hide: false  # 自动隐藏
    quick_actions_enabled: true  # 启用快速操作
```

## 📊 数据统计

增强功能提供丰富的数据统计：

- **学习时间**: 总时间、平均会话长度、最长会话
- **效率分析**: 效率评分趋势、最佳学习时段
- **任务管理**: 完成率、逾期率、优先级分布
- **科目分析**: 时间分配、进度对比、难度评估
- **习惯分析**: 学习模式、连续天数、周期性规律

## 🎉 总结

这些增强功能在不改变原有框架的基础上，显著提升了TimeNest的实用性：

1. **更智能**: 基于数据的个性化建议
2. **更高效**: 专注模式和智能提醒
3. **更全面**: 完整的学习生命周期管理
4. **更便捷**: 快速操作和一键功能
5. **更直观**: 丰富的数据可视化和统计

通过这些细分功能，TimeNest从简单的课程表工具升级为全面的智能学习助手。
