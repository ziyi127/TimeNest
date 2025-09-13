import os
import sys
import subprocess

# 获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义PyInstaller命令
pyinstaller_cmd = [
    sys.executable,  # Python可执行文件路径
    '-m', 'PyInstaller',
    '--windowed',  # 不显示控制台窗口
    '--icon', os.path.join(current_dir, 'TKtimetable.ico'),  # 图标文件
    '--name', 'TimeNest',  # 可执行文件名称
    '--distpath', os.path.join(current_dir, 'dist_pyinstaller'),  # 输出目录
    '--workpath', os.path.join(current_dir, 'build_pyinstaller'),  # 构建目录
    '--specpath', current_dir,  # spec文件路径
    '--noconfirm',  # 覆盖输出目录而不询问
    '--clean',  # 清理临时文件
    '--onedir',  # 使用onedir模式而不是onefile模式，减少内存占用
    # 优化选项
    '--strip',  # 移除符号表
    '--noupx',  # 不使用UPX压缩（避免兼容性问题）
    # 排除不必要的模块以减小打包体积
    '--exclude-module', 'unittest',
    '--exclude-module', 'distutils',
    '--exclude-module', 'setuptools',
    '--exclude-module', 'pip',
    '--exclude-module', 'numpy',
    '--exclude-module', 'scipy',
    '--exclude-module', 'matplotlib',
    '--exclude-module', 'pandas',
    '--exclude-module', 'sklearn',
    '--exclude-module', 'tensorflow',
    '--exclude-module', 'torch',
    '--exclude-module', 'email',
    '--exclude-module', 'http',
    '--exclude-module', 'html',
    '--exclude-module', 'xml',
    '--exclude-module', 'urllib',
    '--exclude-module', 'ftplib',
    '--exclude-module', 'cgi',
    '--exclude-module', 'concurrent',
    '--exclude-module', 'multiprocessing',
    '--exclude-module', 'socket',
    '--exclude-module', 'ssl',
    '--exclude-module', 'sqlite3',
    '--exclude-module', 'mysql',
    '--exclude-module', 'psycopg2',
    '--exclude-module', 'pytest',
    '--exclude-module', 'nose',
    # 主程序文件
    os.path.join(current_dir, 'main.py')
]

# 添加数据文件
# timetable.json
data_files = [
    'timetable.json',
    'TKtimetable.ico',
    'classtableMeta.json',
    'timetable_ui_settings.json'
]

for data_file in data_files:
    data_file_path = os.path.join(current_dir, data_file)
    if os.path.exists(data_file_path):
        pyinstaller_cmd.extend(['--add-data', f'{data_file_path}{os.pathsep}.'])

# 添加UI目录
ui_dir = os.path.join(current_dir, 'ui')
if os.path.exists(ui_dir):
    pyinstaller_cmd.extend(['--add-data', f'{ui_dir}{os.pathsep}ui'])

print('执行PyInstaller命令:')
print(' '.join(pyinstaller_cmd))

try:
    # 执行PyInstaller命令
    result = subprocess.run(pyinstaller_cmd, cwd=current_dir, check=True)
    print('\n打包完成!')
    print(f'可执行文件位于: {os.path.join(current_dir, "dist_pyinstaller", "TimeNest")}')
except subprocess.CalledProcessError as e:
    print(f'\n打包失败: {e}')
    sys.exit(1)
except FileNotFoundError:
    print('\n错误: 未找到PyInstaller，请确保已安装PyInstaller')
    print('可以使用以下命令安装: pip install pyinstaller')
    sys.exit(1)