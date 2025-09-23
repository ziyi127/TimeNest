import os
import sys
import subprocess
import shutil
import time
from datetime import datetime

# 设置标准输出编码为UTF-8
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def log_message(message, level="INFO"):
    """日志函数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        print(f"[{timestamp}] [{level}] {message}")
    except UnicodeEncodeError:
        # 在Windows环境下处理编码问题，使用ASCII安全的输出
        safe_message = message.encode('ascii', errors='replace').decode('ascii')
        print(f"[{timestamp}] [{level}] {safe_message}")

def check_nuitka():
    """检查Nuitka是否安装"""
    try:
        result = subprocess.run([sys.executable, '-m', 'nuitka', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        log_message(f"Nuitka版本: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_message("未找到Nuitka，正在安装...", "WARNING")
        return False

def install_nuitka():
    """安装Nuitka"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'nuitka==2.4.11'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'ordered-set'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'zstandard'], check=True)
        log_message("Nuitka安装完成", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"Nuitka安装失败: {e}", "ERROR")
        return False

def clean_build_directory(build_dir):
    """清理构建目录"""
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
            log_message(f"清理构建目录: {build_dir}")
        except Exception as e:
            log_message(f"清理目录失败: {e}", "WARNING")

def get_nuitka_command(current_dir):
    """获取Nuitka命令参数"""
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
        '--lto=yes',  # 启用链接时优化
        '--output-filename=TimeNest',  # 输出文件名
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
    
    return nuitka_cmd

def add_data_files(nuitka_cmd, current_dir):
    """添加数据文件"""
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
            log_message(f"包含数据文件: {data_file}")
    
    return nuitka_cmd

def compile_with_nuitka(nuitka_cmd, current_dir):
    """使用Nuitka编译"""
    log_message("开始编译...这可能需要几分钟时间，请耐心等待")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            nuitka_cmd,
            cwd=current_dir,
            check=True,
            capture_output=False,
            text=False
        )
        
        end_time = time.time()
        compile_time = end_time - start_time
        log_message(f"编译完成! 耗时: {compile_time:.2f}秒", "SUCCESS")
        return True
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        compile_time = end_time - start_time
        log_message(f"编译失败! 耗时: {compile_time:.2f}秒, 错误: {e}", "ERROR")
        return False
    except Exception as e:
        log_message(f"编译过程异常: {e}", "ERROR")
        return False

def create_distribution_package(current_dir):
    """创建分发包"""
    try:
        dist_dir = os.path.join(current_dir, 'dist_nuitka', 'main.dist')
        if not os.path.exists(dist_dir):
            log_message("构建目录不存在", "ERROR")
            return False
        
        # 创建压缩包
        if os.name == 'nt':  # Windows系统
            try:
                import zipfile
                zip_path = os.path.join(current_dir, 'dist_nuitka', 'TimeNest.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(dist_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, dist_dir)
                            zipf.write(file_path, arcname)
                log_message(f"Windows压缩包已创建: {zip_path}", "SUCCESS")
                return True
            except Exception as e:
                log_message(f"创建Windows压缩包时出错: {e}", "ERROR")
                return False
        else:  # Linux系统
            try:
                tar_path = os.path.join(current_dir, 'dist_nuitka', 'TimeNest-linux.tar.gz')
                subprocess.run(['tar', '-czf', tar_path, '-C', dist_dir, '.'], check=True)
                log_message(f"Linux压缩包已创建: {tar_path}", "SUCCESS")
                return True
            except Exception as e:
                log_message(f"创建Linux压缩包时出错: {e}", "ERROR")
                return False
                
    except Exception as e:
        log_message(f"创建分发包失败: {e}", "ERROR")
        return False

def verify_executable(current_dir):
    """验证可执行文件"""
    dist_dir = os.path.join(current_dir, 'dist_nuitka', 'main.dist')
    
    if os.name == 'nt':  # Windows
        exe_path = os.path.join(dist_dir, 'TimeNest.exe')
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path)
            log_message(f"Windows可执行文件验证成功: {exe_path}, 大小: {file_size:,} 字节", "SUCCESS")
            return True
        else:
            log_message("Windows可执行文件未找到", "ERROR")
            return False
    else:  # Linux
        exe_path = os.path.join(dist_dir, 'TimeNest')
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path)
            log_message(f"Linux可执行文件验证成功: {exe_path}, 大小: {file_size:,} 字节", "SUCCESS")
            return True
        else:
            log_message("Linux可执行文件未找到", "ERROR")
            return False

def main():
    """主函数"""
    log_message("开始TimeNest构建过程")
    
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_message(f"项目目录: {current_dir}")
    
    # 检查Python版本
    python_version = sys.version
    log_message(f"Python版本: {python_version}")
    
    # 检查Nuitka
    if not check_nuitka():
        if not install_nuitka():
            sys.exit(1)
    
    # 清理构建目录
    build_dir = os.path.join(current_dir, 'dist_nuitka')
    clean_build_directory(build_dir)
    
    # 获取Nuitka命令
    nuitka_cmd = get_nuitka_command(current_dir)
    nuitka_cmd = add_data_files(nuitka_cmd, current_dir)
    
    log_message("Nuitka命令参数:")
    log_message(' '.join(nuitka_cmd))
    
    # 编译
    if not compile_with_nuitka(nuitka_cmd, current_dir):
        log_message("尝试使用简化参数重新编译", "WARNING")
        # 简化版本
        simple_nuitka_cmd = [
            sys.executable,
            '-m', 'nuitka',
            '--standalone',
            '--enable-plugin=tk-inter',
            '--output-dir=' + build_dir,
            '--windows-icon-from-ico=' + os.path.join(current_dir, 'TKtimetable.ico'),
            '--windows-disable-console',
            '--include-data-dir=' + os.path.join(current_dir, 'ui') + '=ui',
            '--output-filename=TimeNest',
            os.path.join(current_dir, 'main.py')
        ]
        simple_nuitka_cmd = add_data_files(simple_nuitka_cmd, current_dir)
        
        if not compile_with_nuitka(simple_nuitka_cmd, current_dir):
            log_message("简化参数编译也失败，构建终止", "ERROR")
            sys.exit(1)
    
    # 验证可执行文件
    if not verify_executable(current_dir):
        sys.exit(1)
    
    # 创建分发包
    if not create_distribution_package(current_dir):
        log_message("创建分发包失败，但可执行文件已生成", "WARNING")
    
    log_message("构建过程完成!", "SUCCESS")
    log_message(f"可执行文件位于: {os.path.join(current_dir, 'dist_nuitka', 'main.dist')}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log_message("构建过程被用户中断", "WARNING")
        sys.exit(1)
    except Exception as e:
        log_message(f"构建过程发生未预期的错误: {e}", "ERROR")
        sys.exit(1)