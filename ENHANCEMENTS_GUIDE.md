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

## 🌍 学习环境优化功能

### 环境监控
- **功能**: 实时监控学习环境状态
- **特性**:
  - 系统性能监控（CPU、内存、磁盘使用率）
  - 网络质量检测
  - 环境质量评分（0-100%）
  - 自动警告和建议

### 优化建议
- **功能**: 基于环境数据提供优化建议
- **特性**:
  - 智能分析环境问题
  - 分级优化建议（基础、标准、高级、专业）
  - 自动优化执行
  - 优化效果评估

### 使用方法
```python
# 启动环境监控
environment_optimizer.start_monitoring()

# 获取环境总结
summary = environment_optimizer.get_environment_summary()

# 获取优化建议
suggestions = environment_optimizer.get_optimization_suggestions()

# 应用自动优化
environment_optimizer.apply_auto_optimization(EnvironmentFactor.SYSTEM_PERFORMANCE)
```

## 📋 智能学习计划生成器

### 学习目标管理
- **功能**: 创建和跟踪学习目标
- **特性**:
  - 目标优先级设置
  - 预估时间管理
  - 里程碑跟踪
  - 进度可视化

### 智能计划生成
- **功能**: 基于目标和习惯自动生成学习计划
- **特性**:
  - 多种计划类型（日计划、周计划、月计划、考试准备）
  - 智能时间分配
  - 难度递进安排
  - 科目平衡优化

### 学习块管理
- **功能**: 细粒度的学习任务管理
- **特性**:
  - 任务类型分类（复习、预习、练习、记忆等）
  - 难度级别管理
  - 前置条件设置
  - 预期成果定义

### 使用方法
```python
# 创建学习目标
goal_id = study_planner.create_study_goal(
    title="掌握微积分",
    subject="数学",
    target_date=datetime.now() + timedelta(days=60),
    estimated_hours=80.0
)

# 生成学习计划
plan_id = study_planner.generate_study_plan(
    plan_name="数学强化计划",
    plan_type=PlanType.MONTHLY,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=30),
    goal_ids=[goal_id]
)

# 更新目标进度
study_planner.update_goal_progress(goal_id, 0.4)
```

## 📚 学习资源管理器

### 资源管理
- **功能**: 统一管理各类学习资源
- **特性**:
  - 多种资源类型支持（文档、视频、音频、图片、链接、笔记等）
  - 文件完整性检查（哈希验证）
  - 重复文件检测
  - 资源状态跟踪

### 智能分类
- **功能**: 自动分类和标签管理
- **特性**:
  - 智能标签系统
  - 科目分类
  - 资源集合管理
  - 访问频率统计

### 学习笔记
- **功能**: 集成的笔记管理系统
- **特性**:
  - 富文本笔记支持
  - 资源关联
  - 字数统计
  - 收藏功能

### 智能推荐
- **功能**: 基于学习行为的资源推荐
- **特性**:
  - 科目相关推荐
  - 标签相似度推荐
  - 评分排序
  - 访问历史分析

### 使用方法
```python
# 添加学习资源
resource_id = resource_manager.add_resource(
    title="线性代数教程",
    resource_type=ResourceType.DOCUMENT,
    subject="数学",
    file_path="/path/to/tutorial.pdf",
    tags={"数学", "教程", "重要"}
)

# 创建资源集合
collection_id = resource_manager.create_collection(
    name="数学学习资料",
    description="数学相关的所有学习资源",
    subject="数学",
    resource_ids={resource_id}
)

# 添加学习笔记
note_id = resource_manager.add_note(
    title="线性代数学习心得",
    content="今天学习了矩阵运算...",
    subject="数学",
    resource_id=resource_id
)

# 搜索资源
results = resource_manager.search_resources("线性代数", subject="数学")
```

## 🎈 增强浮窗功能

### 学习进度模块
- **功能**: 实时显示学习进度
- **特性**:
  - 当前学习会话状态
  - 今日学习时间
  - 本周学习统计
  - 目标完成进度条

### 学习环境模块
- **功能**: 显示环境状态
- **特性**:
  - 环境评分显示
  - 环境等级指示
  - 优化建议数量
  - 状态颜色指示器

### 资源快速访问模块
- **功能**: 快速访问学习资源
- **特性**:
  - 最近使用资源
  - 收藏资源列表
  - 快速搜索入口
  - 资源管理链接

### 专注模式模块
- **功能**: 专注模式控制
- **特性**:
  - 专注状态显示
  - 剩余时间倒计时
  - 一键开始/结束
  - 自定义时长设置

## 🎯 增强托盘功能

### 新增快速操作
- **添加资源** (Ctrl+R): 快速添加学习资源
- **创建计划** (Ctrl+P): 创建学习计划
- **环境优化** (Ctrl+E): 优化学习环境
- **快速笔记** (Ctrl+N): 记录学习笔记

### 智能功能集成
- **功能**: 所有增强功能的统一入口
- **特性**:
  - 一键访问所有新功能
  - 智能状态同步
  - 快捷键支持
  - 上下文相关操作

## 🔧 配置选项

### 环境优化配置
```yaml
environment_optimizer:
  monitoring_enabled: true
  auto_optimization_enabled: false
  optimization_level: "standard"  # basic, standard, advanced, professional
  monitor_interval: 30  # 秒
```

### 学习计划配置
```yaml
study_planner:
  planning_preferences:
    preferred_session_length: 45  # 分钟
    max_daily_hours: 8
    break_between_sessions: 15
    difficulty_progression: true
    subject_rotation: true
```

### 资源管理配置
```yaml
resource_manager:
  resource_base_path: "resources"
  auto_organize: true
  duplicate_detection: true
  file_integrity_check: true
```

## 📊 数据统计增强

新增功能提供更丰富的数据统计：

### 环境统计
- **环境质量**: 实时评分、历史趋势、改善建议
- **系统性能**: CPU/内存/磁盘使用率、网络质量
- **优化效果**: 优化前后对比、改善幅度

### 计划统计
- **计划执行**: 完成率、延期率、调整频率
- **目标达成**: 里程碑完成情况、时间预估准确性
- **学习块分析**: 类型分布、难度分布、时间分配

### 资源统计
- **资源使用**: 访问频率、使用时长、评分分布
- **资源分布**: 类型分布、科目分布、存储占用
- **笔记统计**: 笔记数量、字数统计、更新频率

## 🎉 总结增强

这些新增的细分功能进一步提升了TimeNest的实用性：

1. **更智能**: 环境感知和自动优化
2. **更全面**: 完整的学习生命周期管理
3. **更个性化**: 基于数据的个性化计划生成
4. **更便捷**: 丰富的快速操作和快捷键
5. **更直观**: 实时状态显示和进度跟踪
6. **更高效**: 智能资源管理和推荐系统

通过这些细分功能，TimeNest现在提供了一个完整的智能学习生态系统，涵盖了学习的各个方面。
