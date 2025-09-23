import os
import sys
import subprocess

def main():
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查Nuitka是否安装
    try:
        subprocess.run([sys.executable, '-m', 'nuitka', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print('未找到Nuitka，正在安装...')
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'nuitka'], check=True)
    except FileNotFoundError:
        print('Python解释器未找到')
        sys.exit(1)
    
    # 定义Nuitka命令
    nuitka_cmd = [
        sys.executable,
        '-m', 'nuitka',
        '--standalone',  # 创建独立可执行文件
        '--enable-plugin=tk-inter',  # 启用tkinter插件
        '--output-dir=' + os.path.join(current_dir, 'dist_nuitka'),  # 输出目录
        '--windows-icon-from-ico=' + os.path.join(current_dir, 'TKtimetable.ico'),  # 图标文件
        '--windows-disable-console',  # Windows下禁用控制台
        '--follow-imports',  # 跟随导入
        '--include-data-dir=' + os.path.join(current_dir, 'ui') + '=ui',  # 包含UI目录
        '--no-prefer-source-code',  # 不优先使用源代码
        '--python-flag=no_site',  # 不加载site模块
        '--python-flag=no_warnings',  # 不显示警告
        '--assume-yes-for-downloads',  # 自动下载依赖
        # 排除不必要的模块以减小打包体积
        '--nofollow-import-to=unittest',
        '--nofollow-import-to=distutils',
        '--nofollow-import-to=setuptools',
        '--nofollow-import-to=pip',
        '--nofollow-import-to=numpy',
        '--nofollow-import-to=scipy',
        '--nofollow-import-to=matplotlib',
        '--nofollow-import-to=pandas',
        '--nofollow-import-to=sklearn',
        '--nofollow-import-to=tensorflow',
        '--nofollow-import-to=torch',
        '--nofollow-import-to=email',
        '--nofollow-import-to=http',
        '--nofollow-import-to=html',
        '--nofollow-import-to=xml',
        '--nofollow-import-to=urllib',
        '--nofollow-import-to=ftplib',
        '--nofollow-import-to=cgi',
        '--nofollow-import-to=concurrent',
        '--nofollow-import-to=multiprocessing',
        '--nofollow-import-to=socket',
        '--nofollow-import-to=ssl',
        '--nofollow-import-to=sqlite3',
        '--nofollow-import-to=mysql',
        '--nofollow-import-to=psycopg2',
        '--nofollow-import-to=pytest',
        '--nofollow-import-to=nose',
        # 主程序文件
        os.path.join(current_dir, 'main.py')
    ]
    
    # 添加必要的数据文件
    data_files = [
        'timetable.json',
        'TKtimetable.ico',
        'classtableMeta.json',
        'timetable_ui_settings.json'
    ]
    
    for data_file in data_files:
        data_file_path = os.path.join(current_dir, data_file)
        if os.path.exists(data_file_path):
            nuitka_cmd.extend(['--include-data-file=' + data_file_path + '=' + data_file])
    
    print('执行Nuitka命令:')
    print(' '.join(nuitka_cmd))
    
    try:
        # 执行Nuitka命令
        result = subprocess.run(nuitka_cmd, cwd=current_dir, check=True)
        print('\n编译完成!')
        print(f'可执行文件位于: {os.path.join(current_dir, "dist_nuitka", "main.dist")}')
        
        # 创建压缩包方便分发
        if os.name == 'nt':  # Windows系统
            try:
                import zipfile
                zip_path = os.path.join(current_dir, 'dist_nuitka', 'TimeNest.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    dist_dir = os.path.join(current_dir, 'dist_nuitka', 'main.dist')
                    for root, _, files in os.walk(dist_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, dist_dir)
                            zipf.write(file_path, arcname)
                print(f'压缩包已创建: {zip_path}')
            except Exception as e:
                print(f'创建压缩包时出错: {e}')
    except subprocess.CalledProcessError as e:
        print(f'\n编译失败: {e}')
        sys.exit(1)
    except FileNotFoundError:
        print('\n错误: 未找到Nuitka')
        sys.exit(1)

if __name__ == '__main__':
    main()