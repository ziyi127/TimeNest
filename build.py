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

# 使用PyInstaller打包
def build_app():
    # 构建命令
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--noconfirm',
        '--onedir',  # 使用onedir模式，而不是onefile
        '--windowed',
        '--icon', os.path.join(current_dir, 'TKtimetable.ico'),
        '--name', 'TimeNest',
        '--add-data', f'{os.path.join(current_dir, "timetable.json")};.',
        '--add-data', f'{os.path.join(current_dir, "TKtimetable.ico")};.',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'PIL',
        '--hidden-import', 'pystray',
        os.path.join(current_dir, 'main.py')
    ]
    
    # 执行打包命令
    subprocess.check_call(cmd)

if __name__ == '__main__':
    install_requirements()
    build_app()
    print('打包完成！')