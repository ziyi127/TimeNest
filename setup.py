#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 安装脚本
一个功能强大的跨平台课程表管理工具
"""

import os
import sys
from setuptools import setup, find_packages

# 确保使用 UTF-8 编码
if sys.version_info < (3, 8):
    raise RuntimeError("TimeNest 需要 Python 3.8 或更高版本")

# 获取项目根目录
here = os.path.abspath(os.path.dirname(__file__))

# 读取 README 文件
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# 读取核心依赖
def read_requirements(filename):
    """读取依赖文件，过滤注释和空行"""
    requirements = []
    try:
        with open(os.path.join(here, filename), encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释、空行和 -r 引用
                if line and not line.startswith('#') and not line.startswith('-r'):
                    requirements.append(line)
    except FileNotFoundError:
        print(f"警告: {filename} 文件不存在")
    return requirements

# 核心运行时依赖
requirements = read_requirements('requirements.txt')

# 版本信息
version = '1.0.0'

# 项目信息
setup(
    name='TimeNest',
    version=version,
    description='一个功能强大的跨平台课程表管理工具',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='TimeNest Team',
    author_email='timenest@example.com',
    url='https://github.com/your-username/TimeNest',
    project_urls={
        'Bug Reports': 'https://github.com/your-username/TimeNest/issues',
        'Source': 'https://github.com/your-username/TimeNest',
        'Documentation': 'https://github.com/your-username/TimeNest/wiki',
    },
    
    # 包信息
    packages=find_packages(),
    package_data={
        'TimeNest': [
            'resources/icons/*.png',
            'resources/icons/*.svg',
            'resources/sounds/*.wav',
            'resources/sounds/*.mp3',
            'resources/themes/*.json',
            'resources/themes/*.qss',
        ],
    },
    include_package_data=True,
    
    # 依赖
    python_requires='>=3.8',
    install_requires=requirements,
    
    # 可选依赖
    extras_require={
        'minimal': read_requirements('requirements-minimal.txt'),
        'dev': read_requirements('requirements-dev.txt'),
        'prod': read_requirements('requirements-prod.txt'),
        'test': [
            'pytest>=7.4.0',
            'pytest-qt>=4.2.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.11.0',
        ],
        'build': [
            'PyInstaller>=5.13.0',
            'cx-Freeze>=6.15.0',
            'auto-py-to-exe>=2.40.0',
        ],
        'docs': [
            'Sphinx>=7.1.0',
            'sphinx-rtd-theme>=1.3.0',
            'sphinx-autodoc-typehints>=1.24.0',
        ],
        'security': [
            'bandit>=1.7.5',
            'safety>=2.3.0',
        ],
    },
    
    # 入口点
    entry_points={
        'console_scripts': [
            'timenest=TimeNest.main:main',
        ],
        'gui_scripts': [
            'timenest-gui=TimeNest.main:main',
        ],
    },
    
    # 分类信息
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Education',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Desktop Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Environment :: X11 Applications :: Qt',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: English',
    ],
    
    # 关键词
    keywords='schedule timetable education qt6 pyqt6 desktop cross-platform',
    
    # 许可证
    license='MIT',
    
    # 平台支持
    platforms=['Windows', 'macOS', 'Linux'],
    
    # ZIP 安全
    zip_safe=False,
)