import os
import sys
import subprocess

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 安装依赖
def install_requirements():
    requirements_path = os.path.join(current_dir, 'requirements.txt')
    if os.path.exists(requirements_path):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])

# 使用Nuitka打包
def build_app():
    # 构建命令
    cmd = [
        sys.executable,
        '-m',
        'nuitka',
        '--standalone',  # 独立模式，不使用onefile
        '--windows-disable-console',  # 禁用控制台窗口
        '--windows-icon-from-ico=' + os.path.join(current_dir, 'TKtimetable.ico'),  # 设置图标
        '--enable-plugin=tk-inter',  # 启用tkinter插件
        '--output-dir=' + os.path.join(current_dir, 'dist'),  # 输出目录
        '--include-data-file=' + f'{os.path.join(current_dir, "timetable.json")}=timetable.json',  # 包含数据文件
        '--include-data-file=' + f'{os.path.join(current_dir, "TKtimetable.ico")}=TKtimetable.ico',  # 包含图标文件
        '--include-package=tkinter',  # 包含tkinter包
        '--include-package=PIL',  # 包含PIL包
        '--include-package=pystray',  # 包含pystray包
        os.path.join(current_dir, 'main.py')
    ]
    
    # 执行打包命令
    subprocess.check_call(cmd)

if __name__ == '__main__':
    install_requirements()
    build_app()
    print('使用Nuitka打包完成！')