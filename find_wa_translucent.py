#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import inspect
from PySide6 import QtCore, QtWidgets, QtGui

# 搜索 WA_TranslucentBackground 在 PySide6 模块中的位置
print("搜索 WA_TranslucentBackground 在 PySide6 模块中的位置...")

# 检查 QtCore 模块
print("\n检查 QtCore 模块:")
for name, obj in inspect.getmembers(QtCore):
    if 'translucent' in name.lower() or 'WA' in name:
        print(f"找到: {name}")

# 检查 QtWidgets 模块
print("\n检查 QtWidgets 模块:")
for name, obj in inspect.getmembers(QtWidgets):
    if 'translucent' in name.lower() or 'WA' in name:
        print(f"找到: {name}")

# 检查 QtGui 模块
print("\n检查 QtGui 模块:")
for name, obj in inspect.getmembers(QtGui):
    if 'translucent' in name.lower() or 'WA' in name:
        print(f"找到: {name}")

print("\n搜索完成。")