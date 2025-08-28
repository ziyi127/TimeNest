import tkinter as tk
from tkinter import ttk
import json
import os
import datetime

class DragWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("课程表悬浮窗")
        self.geometry("250x150")
# 设置窗口属性
        self.overrideredirect(True)  # 无边框窗口
        
        # 跨平台窗口置顶设置
        self._set_always_on_top()
        
        # 初始化可拖动状态
        print("初始化可拖动状态")
        self.is_draggable = False
        print(f"可拖动状态初始化完成: is_draggable={self.is_draggable}")
        
        # 初始化after任务ID列表
        self.after_ids = []
        
        # 初始化更新任务ID
        self.update_job = None
        
        # 加载窗口位置
        self.load_window_position()
        print("已完成窗口位置加载")
        
        # 加载UI设置
        self.load_ui_settings()
        print("已完成UI设置加载")
        
        # 配置背景颜色
        self.configure(bg=self.background_color)
        
        # 创建主框架
        self.main_frame = tk.Frame(self, bg=self.background_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建时间框架
        self.time_frame = tk.Frame(self.main_frame, bg=self.background_color)
        self.time_frame.pack(anchor='w')
        
        # 创建时间标签
        self.time_label = tk.Label(self.time_frame, font=("Arial", 16), bg=self.background_color, fg=self.text_color)
        self.time_label.pack(side='left')
        print("已创建时间标签")
        
        # 设置初始鼠标穿透状态
        # 使用after方法确保窗口完全初始化后再设置
        self.after(100, self._initialize_transparency)
        
    def _initialize_transparency(self):
        """初始化透明度设置 - 强制启用指针穿透"""
        # 强制启用指针穿透，无论之前的设置如何
        print("强制启用指针穿透模式")
        
        # 确保必要属性已初始化
        if not hasattr(self, 'background_color'):
            self.background_color = "#2c3e50"
            print("初始化背景色为默认值: #2c3e50")
        if not hasattr(self, 'text_color'):
            self.text_color = "#ffffff"
            print("初始化文字色为默认值: #ffffff")
        if not hasattr(self, 'transparency'):
            self.transparency = 80
            print("初始化透明度为默认值: 80")
            
        # 设置指针穿透为True
        self.pointer_passthrough = True
        self.is_draggable = False  # 强制设置为不可拖动以启用指针穿透
        print(f"设置指针穿透: {self.pointer_passthrough}, 可拖动: {self.is_draggable}")
        
        # 创建日期和星期标签
        self.date_label = tk.Label(self.time_frame, font=("Arial", 13), bg=self.background_color, fg=self.text_color)
        self.date_label.pack(side='left', padx=(10, 0))
        print("已创建日期标签")
        
        # 创建课程信息标签
        self.class_info_label = tk.Label(self.main_frame, font=("Arial", 10), bg=self.background_color, fg=self.text_color)
        self.class_info_label.pack(anchor='w')
        print("已创建课程信息标签")
        
        # 创建下一节课信息标签
        self.next_class_label = tk.Label(self.main_frame, font=("Arial", 10), bg=self.background_color, fg=self.text_color)
        self.next_class_label.pack(anchor='w')
        print("已创建下一节课信息标签")
        
        # 加载课程表
        self.timetable = self.load_timetable()
        print("已完成课程表加载")
        
        # 绑定鼠标事件
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.on_motion)
        print("已绑定鼠标事件")
        
        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        print("已绑定窗口关闭事件")
        
        # 开始更新时间
        self.update_time()
        print("已启动时间更新")
        
        # 现在强制应用指针穿透设置，确保所有组件已创建
        self._force_pointer_passthrough()
        print("已强制应用指针穿透设置")
        
        # 延迟再次应用指针穿透设置，确保生效
        self.after(200, self._force_pointer_passthrough)
        print("已安排延迟应用指针穿透设置")
    
    def _apply_background_and_transparency(self):
        """应用背景色和透明度设置"""
        try:
            print("开始应用背景色和透明度设置")
            # 确保属性存在
            if not hasattr(self, 'background_color'):
                self.background_color = "#2c3e50"
                print("背景色属性不存在，已初始化为默认值")
            if not hasattr(self, 'text_color'):
                self.text_color = "#ffffff"
                print("文字色属性不存在，已初始化为默认值")
            if not hasattr(self, 'transparency'):
                self.transparency = 80
                print("透明度属性不存在，已初始化为默认值")
                
            # 重新设置背景色
            self.configure(bg=self.background_color)
            self.main_frame.configure(bg=self.background_color)
            print(f"已设置窗口背景色: {self.background_color}")
            
            # 安全地配置所有标签
            widgets = [self.time_label, self.date_label, self.class_info_label, self.next_class_label]
            for w in widgets:
                if w and w.winfo_exists():
                    w.configure(bg=self.background_color, fg=self.text_color)
            print("已更新所有标签的背景色和文字色")
            
            # 应用透明度
            alpha = self.transparency / 100.0
            self.wm_attributes("-alpha", alpha)
            print(f"已应用透明度设置: {alpha}")
            
            # 强制刷新显示
            self.update_idletasks()
            print("已强制刷新显示")
            
        except Exception as e:
            print(f"应用背景色和透明度时出错: {e}")
            # 回退到基本设置
            try:
                self.wm_attributes("-alpha", 0.8)
                self.configure(bg="#2c3e50")
                self.main_frame.configure(bg="#2c3e50")
                print("已回退到基本设置")
            except:
                print("回退设置时也发生错误")
                pass
    
    def load_ui_settings(self):
        """加载UI设置"""
        try:
            print("开始加载UI设置")
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            print(f"设置文件路径: {settings_file}")
            
            # 默认设置 - 强制启用指针穿透
            self.background_color = "#2c3e50"
            self.text_color = "#ffffff"
            self.transparency = 80
            self.show_next_class = True
            self.show_countdown = True
            self.compact_mode = False
            self.pointer_passthrough = True  # 强制启用指针穿透
            print("已初始化默认设置，强制启用指针穿透")
            
            if os.path.exists(settings_file):
                print("设置文件存在，开始加载")
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                print(f"已加载设置: {settings}")
                
                # 加载设置，但强制指针穿透为True
                self.background_color = settings.get("background_color", "#2c3e50")
                self.text_color = settings.get("text_color", "#ffffff")
                self.transparency = settings.get("transparency", 80)
                self.show_next_class = settings.get("show_next_class", True)
                self.show_countdown = settings.get("show_countdown", True)
                self.compact_mode = settings.get("compact_mode", False)
                self.pointer_passthrough = True  # 强制启用指针穿透，忽略文件中的设置
                
                print(f"已加载设置: 背景色={self.background_color}, 文字色={self.text_color}, 透明度={self.transparency}%")
                print("指针穿透已强制启用")
            else:
                print("设置文件不存在，将使用默认设置并创建设置文件")
                # 使用默认设置并创建设置文件
                self.save_ui_settings()
            
            # 应用透明度
            alpha = self.transparency / 100.0
            try:
                self.wm_attributes("-alpha", alpha)
                print(f"已应用透明度: {alpha}")
            except Exception as e:
                print(f"应用透明度时出错: {e}")
                
            # 应用指针穿透设置
            self.after(200, self._force_pointer_passthrough)  # 延迟应用以确保窗口完全初始化
            print("已安排延迟应用指针穿透设置")
            
        except Exception as e:
            print(f"加载UI设置时出错: {e}")
            # 使用默认设置，但指针穿透始终为True
            self.background_color = "#2c3e50"
            self.text_color = "#ffffff"
            self.transparency = 80
            self.show_next_class = True
            self.show_countdown = True
            self.compact_mode = False
            self.pointer_passthrough = True  # 强制启用指针穿透
            print("使用默认设置，指针穿透已强制启用")
    
    def set_draggable(self, draggable):
        """设置窗口是否可拖动"""
        print(f"设置窗口是否可拖动: {draggable}")
        self.is_draggable = draggable
        if draggable:
            print("启用拖动模式")
            # 启用拖动模式
            self.config(cursor="arrow")
            # 绑定鼠标事件
            self.bind("<Button-1>", self.start_move)
            self.bind("<ButtonRelease-1>", self.stop_move)
            print("已绑定鼠标事件")
        else:
            print("禁用拖动模式")
            # 禁用拖动模式
            self.config(cursor="")
            # 解绑鼠标事件
            self.unbind("<Button-1>")
            self.unbind("<ButtonRelease-1>")
            print("已解绑鼠标事件")
        
    def _apply_pointer_passthrough(self):
        """应用指针穿透设置"""
        print(f"开始应用指针穿透设置: {self.pointer_passthrough}")
        if not self.winfo_exists():
            print("窗口不存在，返回")
            return
            
        if self.pointer_passthrough:
            print("启用指针穿透")
            # 启用指针穿透
            self.wm_attributes("-transparentcolor", self.background_color)
            print(f"已设置透明色: {self.background_color}")
        else:
            print("禁用指针穿透")
            # 禁用指针穿透
            self.wm_attributes("-transparentcolor", "")
            print("已清除透明色设置")
            
        # 强制更新窗口
        self.update_idletasks()
        self.update()
        print("已强制更新窗口")
    
    def _force_pointer_passthrough(self):
        """强制启用指针穿透"""
        print("开始强制启用指针穿透")
        try:
            if not hasattr(self, 'winfo_exists') or not self.winfo_exists():
                print("窗口不存在，返回")
                return
                
            # 强制设置指针穿透为True
            self.pointer_passthrough = True
            print(f"已设置指针穿透: {self.pointer_passthrough}")
            
            # 确保属性存在
            if not hasattr(self, 'is_draggable'):
                self.is_draggable = False  # 强制设置为不可拖动以启用指针穿透
                print(f"初始化可拖动状态: {self.is_draggable}")
            
            print(f"强制启用指针穿透: pointer_passthrough=True, is_draggable=False")
            
            # 应用透明度
            alpha = self.transparency / 100.0
            self.wm_attributes("-alpha", alpha)
            print(f"已应用透明度: {alpha}")
            
            # 使用透明色方法实现鼠标穿透，避免Windows API干扰窗口显示
            try:
                print("开始使用透明色方法实现鼠标穿透")
                # 首先清除之前的透明色设置
                self.wm_attributes("-transparentcolor", "")
                print("已清除之前的透明色设置")
                # 然后设置背景色为透明色
                self.wm_attributes("-transparentcolor", self.background_color)
                print("指针穿透已启用：使用透明色方法")
            except Exception as e:
                print(f"透明色方法失败: {e}")
                # 回退到基本透明度设置
                self.wm_attributes("-alpha", alpha)
                print("已回退到基本透明度设置")
            
            # 确保背景色正确显示
            self.configure(bg=self.background_color)
            self.main_frame.configure(bg=self.background_color)
            print("已设置窗口背景色")
            
            # 更新所有标签的背景色
            if hasattr(self, 'time_label') and self.time_label.winfo_exists():
                self.time_label.configure(bg=self.background_color)
            if hasattr(self, 'date_label') and self.date_label.winfo_exists():
                self.date_label.configure(bg=self.background_color)
            if hasattr(self, 'class_info_label') and self.class_info_label.winfo_exists():
                self.class_info_label.configure(bg=self.background_color)
            if hasattr(self, 'next_class_label') and self.next_class_label.winfo_exists():
                self.next_class_label.configure(bg=self.background_color)
            print("已更新所有标签背景色")
                
            # 强制更新显示
            self.update_idletasks()
            print("已强制更新显示")
            
        except Exception as e:
            print(f"强制启用指针穿透时出错: {e}")
            # 回退到基本设置
            try:
                alpha = self.transparency / 100.0
                self.wm_attributes("-alpha", alpha)
                self.configure(bg=self.background_color)
                self.main_frame.configure(bg=self.background_color)
                print("已回退到基本设置")
            except:
                print("回退到基本设置时也发生错误")
                pass
            
    def reload_settings(self):
        """重新加载设置"""
        print("开始重新加载设置")
        # 重新加载UI设置
        self.load_ui_settings()
        print("已完成UI设置加载")
        
        # 重新应用背景和透明度
        self._apply_background_and_transparency()
        print("已完成背景和透明度应用")
        
        # 重新应用紧凑模式
        self._apply_compact_mode()
        print("已完成紧凑模式应用")
        
        # 重新应用指针穿透
        self._apply_pointer_passthrough()
        print("已完成指针穿透应用")
        
        # 确保窗口可见
        self._ensure_window_visible()
        print("已完成窗口可见性确保")
    
    def start_move(self, event):
        """开始移动窗口"""
        print("开始移动窗口")
        if self.is_draggable:
            self.x = event.x
            self.y = event.y
            print(f"记录鼠标按下时的相对位置: ({self.x}, {self.y})")
        else:
            print("窗口当前不可拖动")
    
    def stop_move(self, event):
        """停止移动窗口"""
        print("停止移动窗口")
        if self.is_draggable:
            # 保存窗口位置
            self.save_window_position()
            print("已保存窗口位置")
        else:
            print("窗口当前不可拖动")
    
    def on_motion(self, event):
        """移动窗口"""
        print("处理鼠标移动事件")
        if self.is_draggable:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            print(f"计算新的窗口位置: ({x}, {y})")
            self.set_display_postion(x, y)
        else:
            print("窗口当前不可拖动")
    
    def set_display_postion(self, x, y):
        """设置窗口显示位置，确保不会超出屏幕边界"""
        print(f"设置窗口显示位置: ({x}, {y})")
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 获取窗口尺寸
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        print(f"窗口尺寸: {window_width}x{window_height}")
        
        # 确保窗口不会超出屏幕边界
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))
        print(f"限制后的窗口位置: ({x}, {y})")
        
        self.geometry(f"+{x}+{y}")
        print("已设置窗口位置")
        
    def _set_always_on_top(self):
        """跨平台设置窗口始终置顶"""
        print("开始设置窗口置顶")
        import platform
        system = platform.system().lower()
        
        try:
            if system == "windows":
                # Windows: 使用topmost属性
                self.wm_attributes("-topmost", True)
                # 额外设置，确保不会被其他窗口覆盖
                self.after(100, lambda: self.wm_attributes("-topmost", True))
                print("已完成Windows窗口置顶设置")
                
            elif system == "darwin":
                # macOS: 使用topmost属性
                self.wm_attributes("-topmost", True)
                # macOS可能需要额外设置
                self.lift()
                self.call("::tk::unsupported::MacWindowStyle", "style", self._w, "help", "none")
                print("已完成macOS窗口置顶设置")
                
            elif system == "linux":
                # Linux: 使用topmost属性
                self.wm_attributes("-topmost", True)
                # 某些Linux桌面环境可能需要额外设置
                self.lift()
                print("已完成Linux窗口置顶设置")
                
            else:
                # 其他系统，使用通用方法
                self.wm_attributes("-topmost", True)
                self.lift()
                print("已完成通用窗口置顶设置")
                
        except Exception as e:
            print(f"设置窗口置顶时出错: {e}")
            # 回退到基本设置
            self.wm_attributes("-topmost", True)
            print("已完成窗口置顶设置回退")
            
    def _ensure_window_visible(self):
        """确保窗口在屏幕可见区域内"""
        print("开始确保窗口可见")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 获取当前窗口位置
        x = self.winfo_x()
        y = self.winfo_y()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        # 计算新位置，确保在屏幕内
        new_x = max(0, min(x, screen_width - window_width))
        new_y = max(0, min(y, screen_height - window_height))
        
        # 如果位置需要调整，则移动窗口
        if new_x != x or new_y != y:
            self.set_display_postion(new_x, new_y)
            print(f"已调整窗口位置至: ({new_x}, {new_y})")
        else:
            print("窗口位置无需调整")
    
    def update_time(self):
        """更新时间显示"""
        try:
            print("开始更新时间显示")
            # 获取当前时间
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%m-%d")
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]
            print(f"当前时间: {current_time}, 日期: {current_date}, 星期: {weekday}")
            
            # 更新标签
            self.time_label.config(text=current_time)
            self.date_label.config(text=f"{current_date} {weekday}")
            print("已更新时间标签和日期标签")
            
            # 更新课程信息
            self.update_info(now)
            print("已完成课程信息更新")
            
            # 计算下次更新时间（下一秒开始时）
            next_update = 1000 - now.microsecond // 1000
            if next_update <= 0:
                next_update = 1000
            print(f"下次更新时间间隔: {next_update}ms")
                
            # 安排下次更新
            self.update_job = self.after(next_update, self.update_time)
            print(f"已安排下次更新任务: {self.update_job}")
            
        except Exception as e:
            print(f"更新时间时出错: {e}")
    
    def load_timetable(self):
        """从项目目录加载课程表JSON文件"""
        try:
            print("开始加载课程表")
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            timetable_file = os.path.join(project_path, "timetable.json")
            print(f"项目路径: {project_path}")
            print(f"课程表文件路径: {timetable_file}")
            
            if os.path.exists(timetable_file):
                print("课程表文件存在，开始加载")
                with open(timetable_file, 'r', encoding='utf-8') as f:
                    self.timetable_data = json.load(f)
                print(f"已加载课程表数据: {self.timetable_data}")
                data = self.timetable_data
            else:
                print("课程表文件不存在，使用空数据")
                self.timetable_data = {}
                data = {}
                
            # 处理可能的嵌套结构
            if "timetable" in data:
                timetable = data["timetable"]
                print("检测到嵌套结构，已提取timetable字段")
            else:
                timetable = data
                print("使用顶层数据作为课程表")
            
            # 转换星期名称为英文
            converted_timetable = {}
            weekdays_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            
            for i, day_cn in enumerate(weekdays_cn):
                if day_cn in timetable:
                    converted_timetable[weekdays_en[i]] = timetable[day_cn]
                    print(f"已转换{day_cn}课程数据")
                elif weekdays_en[i] in timetable:
                    converted_timetable[weekdays_en[i]] = timetable[weekdays_en[i]]
                    print(f"已加载{day_cn}课程数据")
                else:
                    converted_timetable[weekdays_en[i]] = []
                    print(f"{day_cn}无课程数据")
            
            # 输出课程信息
            print("课表加载完成:")
            for i, day_cn in enumerate(weekdays_cn):
                if converted_timetable[weekdays_en[i]]:
                    print(f"{day_cn}: {converted_timetable[weekdays_en[i]]}")
                else:
                    print(f"{day_cn}: 无课程")
            
            return converted_timetable
        except Exception as e:
            print(f"加载课程表时出错: {e}")
            self.timetable_data = {}
            print("已使用空数据作为课程表")
            import traceback
            traceback.print_exc()  # 打印详细的错误信息
            return {}
    
    def update_info(self, now=None):
        """更新课程信息显示"""
        try:
            print("开始更新课程信息显示")
            if now is None:
                now = datetime.datetime.now()
            print(f"当前时间: {now}")
            
            # 获取当前星期和时间
            weekday_index = now.weekday()
            current_time = now.time()
            print(f"星期索引: {weekday_index}, 当前时间: {current_time}")
            
            # 星期名称映射
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            current_weekday = weekdays[weekday_index]
            print(f"当前星期: {current_weekday}")
            
            # 获取当天的课程表
            day_schedule = self.timetable.get(current_weekday, [])
            print(f"当天课程表: {day_schedule}")
            
            # 查找当前和下一节课
            current_class = None
            next_class = None
            
            for class_info in day_schedule:
                start_time = datetime.datetime.strptime(class_info["start_time"], "%H:%M").time()
                end_time = datetime.datetime.strptime(class_info["end_time"], "%H:%M").time()
                print(f"检查课程: {class_info}, 开始时间: {start_time}, 结束时间: {end_time}")
                
                if start_time <= current_time <= end_time:
                    current_class = class_info
                    print(f"找到当前课程: {current_class}")
                elif start_time > current_time and (next_class is None or start_time < datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()):
                    next_class = class_info
                    print(f"找到下一课程: {next_class}")
            
            # 构建显示文本
            info_text = ""
            next_text = ""
            
            if current_class:
                info_text = f"{current_class['subject']} ({current_class['start_time']}-{current_class['end_time']})"
                print(f"当前课程文本: {info_text}")
            
            if next_class:
                next_start = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
                # 计算距离下一节课的分钟数
                time_diff = datetime.datetime.combine(now.date(), next_start) - datetime.datetime.combine(now.date(), current_time)
                minutes_until_next = time_diff.total_seconds() // 60
                print(f"距离下一节课分钟数: {minutes_until_next}")
                
                if minutes_until_next > 0:
                    next_text = f"下一节: {next_class['subject']} ({next_class['start_time']}) {int(minutes_until_next)}分钟后"
                else:
                    next_text = f"下一节: {next_class['subject']} ({next_class['start_time']})"
                print(f"下一课程文本: {next_text}")
            
            # 更新标签
            self.class_info_label.config(text=info_text)
            self.next_class_label.config(text=next_text)
            print("已更新课程信息标签")
            
        except Exception as e:
            print(f"更新课程信息时出错: {e}")
        
    def _apply_compact_mode(self):
        """应用紧凑模式设置"""
        print(f"开始应用紧凑模式设置，当前紧凑模式状态: {getattr(self, 'compact_mode', False)}")
        if hasattr(self, 'compact_mode') and self.compact_mode:
            print("启用紧凑模式")
            # 紧凑模式：减小字体大小和间距
            self.time_label.config(font=("Arial", 14))
            self.date_label.config(font=("Arial", 11))
            self.class_info_label.config(font=("Arial", 9))
            self.next_class_label.config(font=("Arial", 9))
            self.main_frame.config(padx=5, pady=2)
            print("已应用紧凑模式设置")
        else:
            print("启用正常模式")
            # 正常模式
            self.time_label.config(font=("Arial", 16))
            self.date_label.config(font=("Arial", 13))
            self.class_info_label.config(font=("Arial", 10))
            self.next_class_label.config(font=("Arial", 10))
            self.main_frame.config(padx=10, pady=5)
            print("已应用正常模式设置")
    
    def load_window_position(self):
        """加载窗口位置"""
        try:
            print("开始加载窗口位置")
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            position_file = os.path.join(project_path, "timetable_window_position.json")
            print(f"窗口位置文件路径: {position_file}")
            
            # 默认位置（屏幕右上角）
            default_x = self.winfo_screenwidth() - 300
            default_y = 100
            print(f"默认窗口位置: ({default_x}, {default_y})")
            
            if os.path.exists(position_file):
                print("窗口位置文件存在，开始加载")
                with open(position_file, 'r', encoding='utf-8') as f:
                    position = json.load(f)
                
                # 获取保存的位置
                x = position.get("x", default_x)
                y = position.get("y", default_y)
                print(f"已加载窗口位置: ({x}, {y})")
                
                # 确保位置在屏幕内
                self.set_display_postion(x, y)
                print("已设置窗口位置")
            else:
                print("窗口位置文件不存在，使用默认位置")
                # 使用默认位置
                self.set_display_postion(default_x, default_y)
                print("已设置默认窗口位置")
                
            # 确保窗口可见
            self.after(100, self._ensure_window_visible)
            print("已安排确保窗口可见")
            
        except Exception as e:
            print(f"加载窗口位置时出错: {e}")
            # 使用默认位置
            default_x = self.winfo_screenwidth() - 300
            default_y = 100
            self.set_display_postion(default_x, default_y)
            print("使用默认位置设置窗口位置")
    
    def save_window_position(self):
        """保存窗口位置"""
        try:
            print("开始保存窗口位置")
            # 检查窗口是否存在
            if not hasattr(self, 'winfo_exists') or not self.winfo_exists():
                print("窗口不存在，返回")
                return
                
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            position_file = os.path.join(project_path, "timetable_window_position.json")
            print(f"窗口位置文件路径: {position_file}")
            
            try:
                # 获取当前窗口位置
                x = self.winfo_x()
                y = self.winfo_y()
                print(f"当前窗口位置: ({x}, {y})")
                
                # 确保位置在合理范围内
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                print(f"屏幕尺寸: {screen_width}x{screen_height}")
                
                # 如果窗口在屏幕外，使用默认位置
                if x < -1000 or y < -1000 or x > screen_width + 1000 or y > screen_height + 1000:
                    x = max(0, screen_width - 300)
                    y = 100
                    print(f"窗口位置超出范围，使用默认位置: ({x}, {y})")
                
                # 保存位置信息
                position = {
                    "x": x,
                    "y": y
                }
                print(f"保存位置信息: {position}")
                
                with open(position_file, 'w', encoding='utf-8') as f:
                    json.dump(position, f, ensure_ascii=False, indent=2)
                    print("已保存窗口位置到文件")
                    
            except tk.TclError:
                # 窗口已销毁，忽略错误
                print("窗口已销毁，忽略错误")
                pass
                
        except Exception as e:
            print(f"保存窗口位置时出错: {e}")
    
    def on_closing(self):
        """窗口关闭时的处理"""
        try:
            print("开始窗口关闭处理")
            # 保存窗口位置
            self.save_window_position()
            print("已完成窗口位置保存")
            
            # 取消所有待执行的after任务
            if hasattr(self, 'after_ids'):
                print(f"取消{len(self.after_ids)}个待执行的after任务")
                for after_id in self.after_ids:
                    try:
                        self.after_cancel(after_id)
                        print(f"已取消after任务: {after_id}")
                    except tk.TclError:
                        # 任务已取消或窗口已销毁，忽略错误
                        print(f"取消after任务时出错或任务已取消: {after_id}")
                        pass
                self.after_ids.clear()
                print("已清空after任务列表")
            
            # 取消更新任务
            if hasattr(self, 'update_job') and self.update_job:
                print(f"取消更新任务: {self.update_job}")
                try:
                    self.after_cancel(self.update_job)
                    print("已取消更新任务")
                except tk.TclError:
                    # 任务已取消或窗口已销毁，忽略错误
                    print("取消更新任务时出错或任务已取消")
                    pass
            
            # 检查窗口是否仍然存在
            try:
                if self.winfo_exists():
                    print("窗口仍然存在，开始销毁")
                    self.destroy()
                    print("窗口已销毁")
                else:
                    print("窗口已不存在")
            except tk.TclError:
                # 窗口已销毁，无需处理
                print("窗口已销毁，无需处理")
                pass
                
        except Exception as e:
            print(f"销毁窗口时出错: {e}")
            try:
                if hasattr(self, 'winfo_exists') and self.winfo_exists():
                    print("尝试再次销毁窗口")
                    self.destroy()
                    print("窗口已销毁")
            except tk.TclError:
                print("销毁窗口时出错")
                pass