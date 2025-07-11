#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 数据导入导出测试
"""

import unittest
import tempfile
import json
import yaml
import os
from pathlib import Path
from datetime import time, date

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from TimeNest.core.data_import_export import DataImportExportManager
from TimeNest.models.schedule import Schedule, Subject, TimeSlot, ClassItem


class TestDataImportExportManager(unittest.TestCase):
    """测试数据导入导出管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = DataImportExportManager()
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试课程表
        self.test_schedule = Schedule(name="测试课程表", description="用于测试的课程表")
        
        # 添加科目
        math_subject = Subject(id="math", name="数学", color="#FF5722", teacher="张老师")
        physics_subject = Subject(id="physics", name="物理", color="#2196F3", teacher="李老师")
        self.test_schedule.add_subject(math_subject)
        self.test_schedule.add_subject(physics_subject)
        
        # 添加时间段
        slot1 = TimeSlot(id="slot1", name="第一节", start_time=time(8, 0), end_time=time(8, 45))
        slot2 = TimeSlot(id="slot2", name="第二节", start_time=time(9, 0), end_time=time(9, 45))
        self.test_schedule.add_time_slot(slot1)
        self.test_schedule.add_time_slot(slot2)
        
        # 添加课程
        class1 = ClassItem(id="c1", subject_id="math", time_slot_id="slot1", weekday="monday", classroom="A101")
        class2 = ClassItem(id="c2", subject_id="physics", time_slot_id="slot2", weekday="monday", classroom="B201")
        self.test_schedule.add_class(class1)
        self.test_schedule.add_class(class2)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_supported_formats(self):
        """测试获取支持的格式"""
        formats = self.manager.get_supported_formats()
        
        self.assertIn('import', formats)
        self.assertIn('export', formats)
        self.assertIn('.json', formats['import'])
        self.assertIn('.yaml', formats['import'])
        self.assertIn('.xlsx', formats['import'])
        self.assertIn('.json', formats['export'])
        self.assertIn('.yaml', formats['export'])
        self.assertIn('.xlsx', formats['export'])
    
    def test_export_import_json(self):
        """测试JSON格式导出和导入"""
        # 导出
        json_file = os.path.join(self.temp_dir, "test_schedule.json")
        success = self.manager.export_schedule(self.test_schedule, json_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(json_file))
        
        # 导入
        imported_schedule = self.manager.import_schedule(json_file)
        self.assertIsNotNone(imported_schedule)
        
        # 验证数据完整性
        self.assertEqual(imported_schedule.name, self.test_schedule.name)
        self.assertEqual(len(imported_schedule.subjects), len(self.test_schedule.subjects))
        self.assertEqual(len(imported_schedule.time_slots), len(self.test_schedule.time_slots))
        self.assertEqual(len(imported_schedule.classes), len(self.test_schedule.classes))
    
    def test_export_import_yaml(self):
        """测试YAML格式导出和导入"""
        # 导出
        yaml_file = os.path.join(self.temp_dir, "test_schedule.yaml")
        success = self.manager.export_schedule(self.test_schedule, yaml_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(yaml_file))
        
        # 导入
        imported_schedule = self.manager.import_schedule(yaml_file)
        self.assertIsNotNone(imported_schedule)
        
        # 验证数据完整性
        self.assertEqual(imported_schedule.name, self.test_schedule.name)
        self.assertEqual(len(imported_schedule.subjects), len(self.test_schedule.subjects))
        self.assertEqual(len(imported_schedule.time_slots), len(self.test_schedule.time_slots))
        self.assertEqual(len(imported_schedule.classes), len(self.test_schedule.classes))
    
    def test_import_invalid_file(self):
        """测试导入无效文件"""
        # 不存在的文件
        result = self.manager.import_schedule("nonexistent.json")
        self.assertIsNone(result)
        
        # 无效格式的文件
        invalid_file = os.path.join(self.temp_dir, "invalid.txt")
        with open(invalid_file, 'w') as f:
            f.write("invalid content")
        
        result = self.manager.import_schedule(invalid_file)
        self.assertIsNone(result)
    
    def test_export_invalid_format(self):
        """测试导出到无效格式"""
        invalid_file = os.path.join(self.temp_dir, "test.invalid")
        success = self.manager.export_schedule(self.test_schedule, invalid_file)
        self.assertFalse(success)
    
    def test_classisland_import(self):
        """测试ClassIsland格式导入"""
        # 创建模拟的ClassIsland数据
        classisland_data = {
            "Name": "ClassIsland课程表",
            "TimeLayout": {
                "TimeLayoutItems": [
                    {"StartSecond": "28800", "EndSecond": "31500"},  # 8:00-8:45
                    {"StartSecond": "32400", "EndSecond": "35100"}   # 9:00-9:45
                ]
            },
            "Subjects": [
                {"Id": "math_id", "Name": "数学", "Color": "#FF5722", "Teacher": "张老师"},
                {"Id": "physics_id", "Name": "物理", "Color": "#2196F3", "Teacher": "李老师"}
            ],
            "Classes": [
                {"Subject": "math_id", "DayOfWeek": 0, "TimeLayoutItem": 0, "Classroom": "A101"},
                {"Subject": "physics_id", "DayOfWeek": 0, "TimeLayoutItem": 1, "Classroom": "B201"}
            ]
        }
        
        # 保存ClassIsland数据文件
        classisland_file = os.path.join(self.temp_dir, "classisland.json")
        with open(classisland_file, 'w', encoding='utf-8') as f:
            json.dump(classisland_data, f, ensure_ascii=False, indent=2)
        
        # 导入
        imported_schedule = self.manager.import_from_classisland(classisland_file)
        self.assertIsNotNone(imported_schedule)
        
        # 验证转换结果
        self.assertEqual(imported_schedule.name, "ClassIsland课程表")
        self.assertEqual(len(imported_schedule.subjects), 2)
        self.assertEqual(len(imported_schedule.time_slots), 2)
        self.assertEqual(len(imported_schedule.classes), 2)
        
        # 验证时间转换
        first_slot = imported_schedule.time_slots[0]
        self.assertEqual(first_slot.start_time, time(8, 0))
        self.assertEqual(first_slot.end_time, time(8, 45))
    
    def test_backup_and_restore(self):
        """测试备份和恢复功能"""
        backup_dir = os.path.join(self.temp_dir, "backups")
        
        # 创建备份
        success = self.manager.export_for_backup(self.test_schedule, backup_dir)
        self.assertTrue(success)
        
        # 检查备份文件是否存在
        backup_files = list(Path(backup_dir).glob("schedule_backup_*.json"))
        self.assertEqual(len(backup_files), 1)
        
        # 恢复备份
        backup_file = str(backup_files[0])
        restored_schedule = self.manager.restore_from_backup(backup_file)
        self.assertIsNotNone(restored_schedule)
        
        # 验证恢复的数据
        self.assertEqual(restored_schedule.name, self.test_schedule.name)
        self.assertEqual(len(restored_schedule.subjects), len(self.test_schedule.subjects))
        self.assertEqual(len(restored_schedule.time_slots), len(self.test_schedule.time_slots))
        self.assertEqual(len(restored_schedule.classes), len(self.test_schedule.classes))
    
    def test_excel_export(self):
        """测试Excel导出（需要pandas和openpyxl）"""
        try:
            import pandas as pd
            import openpyxl
        except ImportError:
            self.skipTest("pandas or openpyxl not available")
        
        # 导出到Excel
        excel_file = os.path.join(self.temp_dir, "test_schedule.xlsx")
        success = self.manager.export_schedule(self.test_schedule, excel_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(excel_file))
        
        # 验证Excel文件可以读取
        df = pd.read_excel(excel_file)
        self.assertIsNotNone(df)
        self.assertGreater(len(df.columns), 0)
    
    def test_excel_import(self):
        """测试Excel导入（需要pandas）"""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas not available")
        
        # 创建简单的Excel文件用于测试
        excel_file = os.path.join(self.temp_dir, "simple_schedule.xlsx")
        
        # 创建测试数据
        data = {
            '周一': ['数学', '物理', '', ''],
            '周二': ['', '数学', '物理', ''],
            '周三': ['物理', '', '数学', ''],
            '周四': ['数学', '物理', '', ''],
            '周五': ['', '', '数学', '物理']
        }
        
        df = pd.DataFrame(data, index=['第一节', '第二节', '第三节', '第四节'])
        df.to_excel(excel_file)
        
        # 导入
        imported_schedule = self.manager.import_schedule(excel_file)
        self.assertIsNotNone(imported_schedule)
        
        # 验证导入结果
        self.assertGreater(len(imported_schedule.subjects), 0)
        self.assertGreater(len(imported_schedule.time_slots), 0)
        self.assertGreater(len(imported_schedule.classes), 0)


class TestDataFormatConversion(unittest.TestCase):
    """测试数据格式转换"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = DataImportExportManager()
    
    def test_json_to_yaml_conversion(self):
        """测试JSON到YAML的转换"""
        # 创建测试数据
        test_data = {
            "name": "测试课程表",
            "subjects": [
                {"id": "math", "name": "数学", "color": "#FF5722"}
            ],
            "time_slots": [
                {"id": "slot1", "name": "第一节", "start_time": "08:00:00", "end_time": "08:45:00"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
            json.dump(test_data, json_file, ensure_ascii=False, indent=2)
            json_path = json_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as yaml_file:
            yaml_path = yaml_file.name
        
        try:
            # 导入JSON
            schedule = self.manager.import_schedule(json_path)
            self.assertIsNotNone(schedule)
            
            # 导出为YAML
            success = self.manager.export_schedule(schedule, yaml_path)
            self.assertTrue(success)
            
            # 验证YAML文件
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            self.assertEqual(yaml_data['name'], test_data['name'])
            
        finally:
            os.unlink(json_path)
            os.unlink(yaml_path)


if __name__ == '__main__':
    unittest.main()
