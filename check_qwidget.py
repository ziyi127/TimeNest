#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget

# 检查 QWidget 类的所有属性，寻找与 translucent 相关的属性
print("检查 QWidget 类的属性...")

# 获取 QWidget 类的所有属性
widget_attrs = dir(QWidget)

# 搜索与 translucent 相关的属性
print("\n与 translucent 相关的属性:")
for attr in widget_attrs:
    if "translucent" in attr.lower():
        print(f"找到: {attr}")

# 搜索以 WA_ 开头的属性（窗口属性）
print("\n以 WA_ 开头的属性 (窗口属性):")
for attr in widget_attrs:
    if attr.startswith("WA_"):
        print(f"找到: {attr}")

print("\n检查完成。")
