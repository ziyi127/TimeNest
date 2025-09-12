import tkinter as tk
import tkinter.font as tkFont
import json
import os
import datetime


class DragWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("课程表悬浮窗")
        self.geometry("180x70")
        
        # 检查操作系统类型，Linux环境下不使用无边框窗口以避免兼容性问题
        import platform
        import os
        
        if platform.system() != "Linux":
            self.overrideredirect(True)  # 无边框窗口
            self.wm_attributes("-topmost", True)  # 窗口置顶 # type: ignore
        else:
            # Linux环境下使用普通窗口并设置为工具窗口以减少装饰
            # 根据桌面环境设置不同的窗口类型
            desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            if 'kde' in desktop_env:
                self.wm_attributes("-type", "dock")  # KDE推荐 # type: ignore
            else:
                self.wm_attributes("-type", "splash")  # GNOME等其他桌面环境 # type: ignore
            # 在Linux环境下也设置窗口置顶
            self.wm_attributes("-topmost", True) # type: ignore #why:pylance :臣妾做不到啊XD
            self.resizable(False, False)  # 禁止调整大小
            '''
            这段好像是linux特有的库，所以win下报错也正常，看到pylance报错当没看到就好了
            '''
        
        # 初始化可拖动状态，默认为不可拖动
        self.is_draggable = False
        
        # 初始化after任务ID列表
        self.after_ids = []
        
        # 初始化更新任务ID
        self.update_job = None
        
        # 加载UI设置
        self.load_ui_settings()
        
        # 使用after方法确保窗口完全初始化后再加载窗口位置
        self.after(100, self.load_window_position)
        
        # 配置背景颜色
        self.configure(bg=self.background_color)
        
        # 创建主框架
        self.main_frame = tk.Frame(self, bg=self.background_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 创建时间框架
        self.time_frame = tk.Frame(self.main_frame, bg=self.background_color)
        self.time_frame.pack(anchor='w')
        
        # 创建时间标签
        time_font = tkFont.Font(family="Arial", size=self.time_font_size)
        self.time_label = tk.Label(self.time_frame, font=time_font, fg=self.text_color, bg=self.background_color)
        self.time_label.pack(side='left')
        
        # 设置初始鼠标穿透状态
        # 使用after方法确保窗口完全初始化后再设置
        self.after(100, self._initialize_transparency)
        
    def _initialize_transparency(self):
        """初始化透明度设置"""
        # 创建日期和星期标签
        date_font = tkFont.Font(family="Arial", size=self.date_font_size)
        self.date_label = tk.Label(self.time_frame, font=date_font, bg=self.background_color, fg=self.text_color)
        self.date_label.pack(side='left', padx=(3, 0))
        
        # 创建右键菜单
        self.context_menu = None
        
        # 创建课程信息标签
        class_info_font = tkFont.Font(family="Arial", size=self.class_info_font_size)
        self.class_info_label = tk.Label(self.main_frame, font=class_info_font, bg=self.background_color, fg=self.text_color)
        if self.show_next_class:
            self.class_info_label.pack(anchor='w')
        
        # 创建下一节课信息标签
        next_class_font = tkFont.Font(family="Arial", size=self.next_class_font_size)
        self.next_class_label = tk.Label(self.main_frame, font=next_class_font, bg=self.background_color, fg=self.text_color)
        if self.show_countdown:
            self.next_class_label.pack(anchor='w')
        
        # 加载课程表
        self.timetable = self.load_timetable()   
        
        # 绑定鼠标事件
        self.bind("<ButtonPress-1>", self.start_move)# type: ignore
        self.bind("<ButtonRelease-1>", self.stop_move)# type: ignore
        self.bind("<B1-Motion>", self.on_motion)# type: ignore
        
        # Linux环境下绑定右键菜单事件
        import platform
        if platform.system() == "Linux":
            self.bind("<Button-3>", self._show_context_menu)# type: ignore
        
        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 开始更新时间
        self.update_time()
        
        # Linux环境下定期检查并确保窗口置顶
        import platform
        if platform.system() == "Linux":
            self._ensure_topmost()
    
    def _adjust_font_size(self, label, text):
        """根据文本长度调整标签的字体大小"""
        # 获取标签的宽度
        label_width = label.winfo_width()
        
        # 如果标签宽度为0（可能还未完全初始化），使用窗口宽度作为参考
        if label_width <= 0:
            label_width = self.winfo_width() - 20  # 减去一些边距
        
    
        

    def _apply_fonts(self):
        """应用字体设置"""
        # 应用时间标签字体
        time_font = tkFont.Font(family="Arial", size=self.time_font_size)
        self.time_label.config(font=time_font)
        
        # 应用日期标签字体
        date_font = tkFont.Font(family="Arial", size=self.date_font_size)
        self.date_label.config(font=date_font)
        
        # 应用课程信息标签字体
        class_info_font = tkFont.Font(family="Arial", size=self.class_info_font_size)
        self.class_info_label.config(font=class_info_font)
        
        # 应用下节课标签字体
        next_class_font = tkFont.Font(family="Arial", size=self.next_class_font_size)
        self.next_class_label.config(font=next_class_font)
        
        # 调整字体大小以适应窗口
        # 注意：_adjust_font_size需要参数，不能直接调用
        # 在_apply_background_and_transparency中会处理字体调整
        
    def _apply_background_and_transparency(self):
        """应用背景色和透明度设置"""
        # 重新设置背景色
        self.configure(bg=self.background_color)
        self.main_frame.configure(bg=self.background_color)
        self.time_label.configure(bg=self.background_color)
        self.date_label.configure(bg=self.background_color)
        self.class_info_label.configure(bg=self.background_color)
        self.next_class_label.configure(bg=self.background_color)
        
        # 应用透明度
        alpha = self.transparency / 100.0
        try:
            self.wm_attributes("-alpha", alpha)
        except Exception as e:
            print(f"应用透明度时出错: {e}")
        
        # 重新调整课程信息标签的字体大小
        if hasattr(self, 'class_info_label') and self.class_info_label.cget("text"):
            self._adjust_font_size(self.class_info_label, self.class_info_label.cget("text"))
        if hasattr(self, 'next_class_label') and self.next_class_label.cget("text"):
            self._adjust_font_size(self.next_class_label, self.next_class_label.cget("text"))
    
    def _get_screen_resolution(self):
        """获取屏幕分辨率"""
        try:
            # 使用winfo_screenwidth和winfo_screenheight获取屏幕分辨率
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            return screen_width, screen_height
        except Exception as e:
            print(f"获取屏幕分辨率时出错: {e}")
            # 返回默认分辨率
            return 1920, 1080
    
    def _calculate_window_position(self, screen_width, screen_height, base_x=878, base_y=0, base_screen_width=1920, base_screen_height=1080):
        """根据屏幕分辨率计算窗口位置，使窗口在不同分辨率下出现在同一相对位置"""
        # 计算相对位置比例
        x_ratio = base_x / base_screen_width
        y_ratio = base_y / base_screen_height
        
        # 根据比例计算新位置
        new_x = int(screen_width * x_ratio)
        new_y = int(screen_height * y_ratio)
        
        return new_x, new_y
    
    def _center_window(self, window):
        """将窗口居中显示在屏幕中央"""
        try:
            # 获取屏幕分辨率
            screen_width, screen_height = self._get_screen_resolution()
            
            # 获取窗口尺寸
            window.update_idletasks()  # 确保窗口尺寸已更新
            window_width = window.winfo_width()
            window_height = window.winfo_height()
            
            # 计算居中位置
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # 设置窗口位置
            window.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"居中窗口时出错: {e}")

    def _show_context_menu(self, event):#这个只有linux会起作用，win不会被激活
        """显示右键菜单"""
        # 创建菜单
        if not self.context_menu:
            self.context_menu = tk.Menu(self, tearoff=0)
            self.context_menu.add_command(label="允许编辑悬浮窗", command=self._toggle_drag_from_menu)
            self.context_menu.add_command(label="UI设置", command=self._open_ui_settings_from_menu)
            self.context_menu.add_command(label='临时调课', command=self._open_temp_class_change_from_menu)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="退出", command=self._quit_from_menu)
        
        # 显示菜单
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def _toggle_drag_from_menu(self):
        """从菜单切换拖拽状态"""
        # 这个方法需要与托盘管理器交互
        if hasattr(self, 'tray_manager'):
            # 切换拖拽状态
            current_state = self.tray_manager.allow_drag.get()
            self.tray_manager.allow_drag.set(not current_state)
            self.set_draggable(not current_state)
            print(f"允许拖拽状态: {not current_state}")
            
            # 更新菜单项文本
            self.tray_manager._update_menu_text()
    
    def _open_ui_settings_from_menu(self):
        """从菜单打开UI设置"""
        if hasattr(self, 'tray_manager'):
            self.tray_manager.open_ui_settings(None, None)
    
    def _open_temp_class_change_from_menu(self):
        """从菜单打开linshitiaoke"""
        if hasattr(self, 'tray_manager'):
            self.tray_manager.open_temp_class_change(None, None)
    
    def _quit_from_menu(self):
        """从菜单退出程序"""
        if hasattr(self, 'tray_manager'):
            self.tray_manager.quit_window(None, None)
        else:
            self.destroy()
    
    def _ensure_topmost(self):
        """确保窗口在Linux环境下保持置顶"""
        try:
            # 重新设置窗口置顶属性
            self.wm_attributes("-topmost", True)
        except Exception as e:
            print(f"设置窗口置顶时出错: {e}")
        
        # 每5秒检查一次窗口置顶状态
        try:
            after_id = self.after(5000, self._ensure_topmost)
            self.after_ids.append(after_id)
        except Exception as e:
            print(f"安排下次检查窗口置顶时出错: {e}")
    
    def update_display_settings(self):
        """更新显示设置"""
        # 控制课程信息标签的显示
        if self.show_next_class:
            self.class_info_label.pack(anchor='w')
        else:
            self.class_info_label.pack_forget()
        
        # 控制下一节课信息标签的显示
        if self.show_countdown:
            self.next_class_label.pack(anchor='w')
        else:
            self.next_class_label.pack_forget()
    
    def load_ui_settings(self):
        """加载UI设置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            # 默认设置
            self.background_color = "white"
            self.text_color = "black"
            self.transparency = 100
            self.show_next_class = True
            self.show_countdown = True
            self.time_font_size = 14
            self.date_font_size = 12
            self.class_info_font_size = 12
            self.next_class_font_size = 12
            self.window_width = 180
            self.window_height = 70
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 应用设置
                self.background_color = settings.get("background_color", "white")
                self.text_color = settings.get("text_color", "black")
                self.transparency = settings.get("transparency", 100)
                self.show_next_class = settings.get("show_next_class", True)
                self.show_countdown = settings.get("show_countdown", True)
                self.time_font_size = settings.get("time_font_size", 14)
                self.date_font_size = settings.get("date_font_size", 12)
                self.class_info_font_size = settings.get("class_info_font_size", 12)
                self.next_class_font_size = settings.get("next_class_font_size", 12)
                self.window_width = settings.get("window_width", 180)
                self.window_height = settings.get("window_height", 70)
            
            # 设置窗口大小
            self.geometry(f"{self.window_width}x{self.window_height}")
            
            # 应用透明度
            alpha = self.transparency / 100.0
            try:
                self.wm_attributes("-alpha", alpha)
            except Exception as e:
                print(f"应用透明度时出错: {e}")
        except Exception as e:
            print(f"加载UI设置时出错: {e}")
            # 使用默认设置
            self.background_color = "white"
            self.text_color = "black"
            self.transparency = 100
            self.show_next_class = True
            self.show_countdown = True
            self.time_font_size = 14
            self.date_font_size = 12
            self.class_info_font_size = 12
            self.next_class_font_size = 12
            self.window_width = 180
            self.window_height = 70
    
    def set_draggable(self, draggable):
        """设置窗口是否可拖动"""
        self.is_draggable = draggable
        print(f"设置可拖动状态: {draggable}")
        
        # 强制更新窗口
        self.update()
    
    def start_move(self, event):
        """开始移动窗口"""
        if self.is_draggable:
            self.x = event.x
            self.y = event.y
    
    def stop_move(self, event):
        """停止移动窗口"""
        if self.is_draggable:
            # 保存窗口位置
            self.save_window_position()
    
    def on_motion(self, event):
        """移动窗口"""
        if self.is_draggable:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.set_display_postion(x, y)
    
    def set_display_postion(self, x, y):
        """设置窗口显示位置"""
        self.geometry(f"+{x}+{y}")
    
    def update_time(self):
        """更新时间显示"""
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%m-%d")
            
            # 获取星期
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            weekday = weekdays[now.weekday()]
            
            # 更新时间标签
            self.time_label.config(text=current_time)
            self.date_label.config(text=f"{current_date} {weekday}")
            
            # 更新课程信息
            self.update_info(now)
        except Exception as e:
            # 窗口可能已被销毁，停止更新
            print(f"更新时间时出错: {e}")
            return
        
        # 每秒更新一次
        try:
            after_id = self.after(1000, self.update_time)
            self.after_ids.append(after_id)
            # 保存更新任务ID
            self.update_job = after_id
        except Exception as e:
            # 窗口可能已被销毁，停止更新
            print(f"安排下次更新时出错: {e}")
    
    def load_timetable(self):
        """从项目目录加载课程表JSON文件"""
        try:
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 定义文件路径
            timetable_file_path = os.path.join(project_path, "timetable.json")
            classtable_meta_file_path = os.path.join(project_path, "classtableMeta.json")
            
            # 检查文件存在性
            timetable_exists = os.path.exists(timetable_file_path)
            classtable_meta_exists = os.path.exists(classtable_meta_file_path)
            
            # 如果两个文件都不存在，弹窗提示
            if not timetable_exists and not classtable_meta_exists:
                print("未找到课程表文件，请您自定义课表之后重启程序")
                # 创建提示窗口
                self._show_no_timetable_dialog()
                return {}
            
            # 如果只有classtableMeta.json存在，转换为timetable.json
            if classtable_meta_exists and not timetable_exists:
                print("发现classtableMeta.json，正在转换为timetable.json...")
                self._convert_classtable_meta_to_timetable(classtable_meta_file_path, timetable_file_path)
            
            # 如果只有timetable.json存在，转换为classtableMeta.json
            elif timetable_exists and not classtable_meta_exists:
                print("发现timetable.json，正在转换为classtableMeta.json...")
                self._convert_timetable_to_classtable_meta(timetable_file_path, classtable_meta_file_path)
            
            # 加载classtableMeta.json（如果存在）
            if classtable_meta_exists:
                with open(classtable_meta_file_path, 'r', encoding='utf-8') as f:
                    self.classtable_meta = json.load(f)
            else:
                self.classtable_meta = None
            
            # 加载课程表
            with open(timetable_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理可能的嵌套结构
            if "timetable" in data:
                timetable = data["timetable"]
            else:
                timetable = data
            
            # 转换星期名称为英文
            converted_timetable = {}
            weekdays_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            
            for i, day_cn in enumerate(weekdays_cn):
                if day_cn in timetable:
                    converted_timetable[weekdays_en[i]] = timetable[day_cn]
                elif weekdays_en[i] in timetable:
                    converted_timetable[weekdays_en[i]] = timetable[weekdays_en[i]]
                else:
                    converted_timetable[weekdays_en[i]] = []
            
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
    
    def _convert_classtable_meta_to_timetable(self, meta_file_path, timetable_file_path):
        """将classtableMeta.json转换为timetable.json"""
        try:
            # 读取classtableMeta.json
            with open(meta_file_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            # 构建timetable.json数据结构
            timetable_data = {"timetable": {}}
            
            # 获取classtable和timetable数据
            classtable = meta_data.get("classtable", {})
            time_slots = meta_data.get("timetable", {})
            
            # 合并时间信息和课程信息
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            
            for i, day in enumerate(weekdays):
                if day in time_slots and day in classtable:
                    # 合并时间信息和课程信息
                    timetable_data["timetable"][day] = []
                    for j, time_slot in enumerate(time_slots[day]):
                        if j < len(classtable[day]):
                            # 添加课程信息
                            slot = time_slot.copy()
                            slot["subject"] = classtable[day][j]
                            # 添加默认的教师和教室信息
                            slot["teacher"] = "教师"
                            slot["classroom"] = "教室"
                            timetable_data["timetable"][day].append(slot)
                elif day in time_slots:
                    # 只有时间信息，没有课程信息
                    timetable_data["timetable"][day] = time_slots[day]
                elif day in classtable:
                    # 只有课程信息，没有时间信息
                    timetable_data["timetable"][day] = [{"subject": subject} for subject in classtable[day]]
            
            # 写入timetable.json
            with open(timetable_file_path, 'w', encoding='utf-8') as f:
                json.dump(timetable_data, f, ensure_ascii=False, indent=2)
            
            print("转换完成: classtableMeta.json -> timetable.json")
        except Exception as e:
            print(f"转换classtableMeta.json时出错: {e}")
    
    def _convert_timetable_to_classtable_meta(self, timetable_file_path, meta_file_path):
        """将timetable.json转换为classtableMeta.json"""
        try:
            # 读取timetable.json
            with open(timetable_file_path, 'r', encoding='utf-8') as f:
                timetable_data = json.load(f)
            
            # 处理可能的嵌套结构
            if "timetable" in timetable_data:
                timetable = timetable_data["timetable"]
            else:
                timetable = timetable_data
            
            # 构建classtableMeta.json数据结构
            meta_data = {
                "timetable": {},
                "classtable": {},
                "allclass": []
            }
            
            # 提取时间信息和课程信息
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            all_classes = set()
            
            for day in weekdays:
                if day in timetable:
                    # 提取时间信息
                    meta_data["timetable"][day] = [
                        {"start_time": slot.get("start_time", ""), "end_time": slot.get("end_time", "")}
                        for slot in timetable[day]
                    ]
                    
                    # 提取课程信息
                    meta_data["classtable"][day] = [slot.get("subject", "") for slot in timetable[day]]
                    
                    # 收集所有课程
                    all_classes.update(meta_data["classtable"][day])    
            # 设置allclass
            meta_data["allclass"] = list(all_classes)
            
            # 写入classtableMeta.json
            with open(meta_file_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            print("转换完成: timetable.json -> classtableMeta.json")
        except Exception as e:
            print(f"转换timetable.json时出错: {e}")
    
    def _show_no_timetable_dialog(self):
        """显示无课表文件对话框"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # 创建一个隐藏的主窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 显示消息框，提供自定义课表选项
            result = messagebox.askyesno("课表设置", "未找到课程表文件，是否现在自定义课表？")
            
            # 销毁隐藏的主窗口
            root.destroy()
            
            # 如果用户选择自定义课表，打开时间表设置向导
            if result:
                self.open_timetable_wizard()
        except Exception as e:
            print(f"显示对话框时出错: {e}")
            import traceback
            traceback.print_exc()  # 打印详细的错误信息
            return


    def open_timetable_wizard(self):
        """打开时间表设置向导"""
        try:
            # 导入时间表设置向导
            from .timetable_wizard import TimetableWizard
            
            # 创建时间表设置向导实例
            if not hasattr(self, 'timetable_wizard'):
                self.timetable_wizard = TimetableWizard(self, self)
            
            # 打开向导窗口
            self.timetable_wizard.open_window()
        except Exception as e:
            print(f"打开时间表设置向导时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def open_class_table_wizard(self):
        """打开课程表设置向导"""
        try:
            # 导入课程表设置向导
            from .classtable_wizard import ClassTableWizard
            
            # 创建课程表设置向导实例
            if not hasattr(self, 'class_table_wizard'):
                self.class_table_wizard = ClassTableWizard(self, self)
            
            # 打开向导窗口
            self.class_table_wizard.open_window()
        except Exception as e:
            print(f"打开课程表设置向导时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def update_info(self, now):
        """更新课程信息显示"""
        # 获取当前星期
        weekdays_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        current_weekday_en = weekdays_en[now.weekday()]
        current_weekday_cn = weekdays_cn[now.weekday()]
        
        # print(f"当前时间: {now}")  # 调试信息
        # print(f"当前星期: {current_weekday_cn} ({current_weekday_en})")  # 调试信息
        
        # 获取当前时间和下一节课信息
        current_class = None
        next_class = None
        
        # 使用英文键访问课表
        if current_weekday_en in self.timetable:
            classes = self.timetable[current_weekday_en]
            # print(f"当天课程: {classes}")  # 调试信息
            
            # 遍历课程查找当前和下一节课
            for i, class_info in enumerate(classes):
                start_time = datetime.datetime.strptime(class_info["start_time"], "%H:%M").time()
                end_time = datetime.datetime.strptime(class_info["end_time"], "%H:%M").time()
                
                # print(f"检查课程: {class_info['subject']} ({start_time}-{end_time})")  # 调试信息
                # print(f"当前时间是否在课程时间段内: {start_time <= now.time() <= end_time}")  # 调试信息
                
                # 检查当前时间是否在课程时间段内
                if start_time <= now.time() <= end_time:
                    current_class = class_info
                
                # 查找下一节课
                if start_time > now.time() and (next_class is None or start_time < datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()):
                    next_class = class_info
        
        # 应用单次课程更改（如果有）
        if current_class:
            # 检查是否有单次课程更改
            if hasattr(self, 'classtable_meta') and self.classtable_meta and "single_changes" in self.classtable_meta:
                # 星期中文到英文的映射
                day_map = {
                    "周一": "monday",
                    "周二": "tuesday",
                    "周三": "wednesday",
                    "周四": "thursday",
                    "周五": "friday"
                }
                
                # 获取当前课程的索引
                current_day_en = current_weekday_en
                current_period_index = None
                
                # 查找当前课程在课表中的索引
                for i, class_info in enumerate(self.timetable[current_day_en]):
                    if class_info["start_time"] == current_class["start_time"] and class_info["end_time"] == current_class["end_time"]:
                        current_period_index = i
                        break
                
                # 如果找到了索引，检查是否有单次更改
                if current_period_index is not None:
                    change_key = f"{current_day_en}_{current_period_index}"
                    if change_key in self.classtable_meta["single_changes"]:
                        # 应用单次更改
                        single_change = self.classtable_meta["single_changes"][change_key]
                        current_class["subject"] = single_change["new_class"]
        
        # 更新当前课程信息
        if current_class:
            text = f"现在是:{current_class['subject']}({current_class['start_time']}-{current_class['end_time']})"
            self.class_info_label.config(text=text)
            self._adjust_font_size(self.class_info_label, text)
            # print(f"当前课程: {current_class['subject']} ({current_class['start_time']}-{current_class['end_time']})")  # 调试信息
        else:
            # 特殊处理周末和课间休息
            if current_weekday_en in ['saturday', 'sunday'] and not self.timetable.get(current_weekday_en):
                text = "今天休息，无课程安排"
                self.class_info_label.config(text=text)
                self._adjust_font_size(self.class_info_label, text)
            elif next_class:
                # 计算距离下一节课的时间
                next_class_time = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
                next_class_datetime = datetime.datetime.combine(now.date(), next_class_time)
                
                # 如果下一节课是明天的，需要调整日期
                if next_class_datetime < now:
                    next_class_datetime += datetime.timedelta(days=1)
                text = "课间休息中"
                self.class_info_label.config(text=text)
                self._adjust_font_size(self.class_info_label, text)
            elif self.timetable.get(current_weekday_en):
                # 当天有课程但不在课间休息时间（第一节课前或放学后）
                if classes:  # 确保当天有课程安排
                    text = "今天没有课程进行中"
                    self.class_info_label.config(text=text)
                    self._adjust_font_size(self.class_info_label, text)
                else:
                    text = "今天没有课程安排"
                    self.class_info_label.config(text=text)
                    self._adjust_font_size(self.class_info_label, text)
            else:
                # 当天无课程安排
                text = "今天没有课程安排"
                self.class_info_label.config(text=text)
                self._adjust_font_size(self.class_info_label, text)
            # print("今天没有课程")  # 调试信息
        
        # 更新下一节课信息
        if next_class and current_class:  # 只有在有当前课程时才显示下一节课信息
            # 计算距离下一节课的时间
            next_class_time = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
            next_class_datetime = datetime.datetime.combine(now.date(), next_class_time)
            
            # 如果下一节课是明天的，需要调整日期
            if next_class_datetime < now:
                next_class_datetime += datetime.timedelta(days=1)
            
            time_diff = next_class_datetime - now
            
            text = f"下节课: {next_class['subject']}({next_class['start_time']})"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
            # print(f"下一节课: {next_class['subject']} ({next_class['start_time']})")  # 调试信息
        elif next_class and not current_class:
            # 在非课间时间显示下一节课信息（第一节课前）
            # 计算距离下一节课的时间
            next_class_time = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
            next_class_datetime = datetime.datetime.combine(now.date(), next_class_time)
            
            # 如果下一节课是明天的，需要调整日期
            if next_class_datetime < now:
                next_class_datetime += datetime.timedelta(days=1)
            
            time_diff = next_class_datetime - now
            minutes_diff = int(time_diff.total_seconds() / 60)
            
            text = f"下一节课: {next_class['subject']} ({next_class['start_time']}) 还有{minutes_diff}分钟"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
        elif current_class and not next_class:
            # 有当前课程但没有下一节课（这天的最后一节课）
            text = "这是今天的最后一节课"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
            
            # 检查是否需要清除已完成的临时调课记录
            self._clear_completed_single_changes(current_weekday_en, now)
        elif self.timetable.get(current_weekday_en):
            # 当天有课程但没有当前课程也没有下一节课（已放学）
            text = "今天课程已结束"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
            
            # 检查是否需要清除已完成的临时调课记录
            self._clear_completed_single_changes(current_weekday_en, now)
        else:
            # 即使当天没有更多课程也保持程序正常运行
            text = "今天没有更多课程"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
            # print("今天没有更多课程")  # 调试信息
    
    def load_window_position(self):
        """加载窗口位置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            # 获取屏幕分辨率
            screen_width, screen_height = self._get_screen_resolution()
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 根据屏幕分辨率计算窗口位置
                x, y = self._calculate_window_position(screen_width, screen_height, 
                                                       settings.get("position_x", 878), 
                                                       settings.get("position_y", 0))
                # 设置窗口位置
                self.set_display_postion(x, y)
            else:
                # 如果没有设置文件，使用默认位置
                x, y = self._calculate_window_position(screen_width, screen_height)
                self.set_display_postion(x, y)
        except Exception as e:
            print(f"加载窗口位置时出错: {e}")
    
    def save_window_position(self):
        """保存窗口位置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            # 检查窗口是否仍然存在
            if self.winfo_exists():
                # 获取当前窗口位置
                x = self.winfo_x()
                y = self.winfo_y()
                
                # 读取现有设置
                if os.path.exists(settings_file):
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                else:
                    settings = {}
                
                # 更新位置信息
                settings["position_x"] = x
                settings["position_y"] = y
                
                # 保存设置到文件
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                print(f"窗口位置已保存: x={x}, y={y}")
        except Exception as e:
            print(f"保存窗口位置时出错: {e}")
    
    def on_closing(self):
        """窗口关闭事件"""
        try:
            # 停止更新循环标志
            if hasattr(self, 'update_loop_running'):
                self.update_loop_running = False
            
            # 取消所有待执行的after任务
            if hasattr(self, 'after_ids'):
                for after_id in self.after_ids:
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass  # 忽略可能的异常
                self.after_ids.clear()
            
            # 停止所有可能的更新循环
            if hasattr(self, 'update_job') and self.update_job:
                try:
                    self.after_cancel(self.update_job)
                except:
                    pass  # 忽略可能的异常
            
            # 取消所有可能的定时任务
            try:
                # 取消_topmost检查任务
                if hasattr(self, '_ensure_topmost_job') and self._ensure_topmost_job:
                    self.after_cancel(self._ensure_topmost_job)
            except:
                pass
            
            # 保存窗口位置
            # 在解除事件绑定和销毁窗口之前保存位置
            try:
                # 检查窗口是否仍然存在
                if self.winfo_exists():
                    self.save_window_position()
            except:
                pass  # 忽略可能的异常
            
            # 解除所有事件绑定
            try:
                # 在窗口销毁前解除所有事件绑定，不检查窗口是否存在
                for widget in self.winfo_children():
                    try:
                        widget.unbind("<Button-1>")
                    except:
                        pass
                    try:
                        widget.unbind("<B1-Motion>")
                    except:
                        pass
                    try:
                        widget.unbind("<ButtonRelease-1>")
                    except:
                        pass
                    
                    # 解除其他可能的事件绑定
                    try:
                        widget.unbind("<Configure>")
                    except:
                        pass
                    try:
                        widget.unbind("<Destroy>")
                    except:
                        pass
                    try:
                        widget.unbind("<FocusIn>")
                    except:
                        pass
                    try:
                        widget.unbind("<FocusOut>")
                    except:
                        pass
            except:
                # 忽略解除绑定时的任何异常
                pass
            
            # 清理所有子窗口和顶级窗口
            try:
                # 销毁所有子窗口
                for child in self.winfo_children():
                    try:
                        if hasattr(child, 'destroy'):
                            child.destroy()
                    except:
                        pass
            except:
                pass
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
        finally:
            # 销毁窗口
            try:
                # 直接销毁窗口，不再检查是否存在
                self.destroy()
            except Exception as e:
                # 忽略销毁时的异常
                pass

    def _clear_completed_single_changes(self, current_weekday_en, now):
        """清除已完成的临时调课记录"""
        # 检查是否有单次课程更改需要清理
        if hasattr(self, 'classtable_meta') and self.classtable_meta and "single_changes" in self.classtable_meta:
            # 获取当天的所有课程
            day_classes = self.timetable.get(current_weekday_en, [])
            
            # 如果当天没有课程，则直接返回
            if not day_classes:
                return
            
            # 检查当天的最后一节课是否已经结束
            last_class = day_classes[-1]
            last_class_end_time = datetime.datetime.strptime(last_class["end_time"], "%H:%M").time()
            
            # 如果当前时间已经超过了最后一节课的结束时间，则清理当天的临时调课记录
            if now.time() > last_class_end_time:
                # 收集需要删除的键
                keys_to_remove = []
                for key in self.classtable_meta["single_changes"]:
                    # 检查键是否以当前星期开头
                    if key.startswith(current_weekday_en + "_"):
                        keys_to_remove.append(key)
                
                # 删除收集到的键
                for key in keys_to_remove:
                    del self.classtable_meta["single_changes"][key]
                
                # 如果single_changes为空，则删除该字段
                if not self.classtable_meta["single_changes"]:
                    del self.classtable_meta["single_changes"]
                
                # 保存更新后的classtable_meta到文件
                try:
                    # 获取程序主目录
                    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    classtable_meta_file = os.path.join(project_path, "classtableMeta.json")
                    
                    with open(classtable_meta_file, 'w', encoding='utf-8') as f:
                        json.dump(self.classtable_meta, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"保存classtableMeta.json时出错: {e}")
