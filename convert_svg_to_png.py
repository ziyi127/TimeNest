#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG到PNG转换工具

支持多种转换方法，确保兼容性
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


def check_dependencies() -> dict:
    """检查可用的转换工具"""
    tools = {
        'cairosvg': False,
        'wand': False,
        'inkscape': False,
        'rsvg-convert': False
    }
    
    # 检查Python库
    try:
        import cairosvg
        tools['cairosvg'] = True
        print("✅ cairosvg 可用")
    except ImportError:
        print("❌ cairosvg 不可用")
    
    try:
        from wand.image import Image
        tools['wand'] = True
        print("✅ Wand (ImageMagick) 可用")
    except ImportError:
        print("❌ Wand (ImageMagick) 不可用")
    
    # 检查命令行工具
    try:
        subprocess.run(['inkscape', '--version'], capture_output=True, check=True)
        tools['inkscape'] = True
        print("✅ Inkscape 可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Inkscape 不可用")
    
    try:
        subprocess.run(['rsvg-convert', '--version'], capture_output=True, check=True)
        tools['rsvg-convert'] = True
        print("✅ rsvg-convert 可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ rsvg-convert 不可用")
    
    return tools


def convert_with_cairosvg(svg_path: Path, png_path: Path, size: int = 180) -> bool:
    """使用cairosvg转换"""
    try:
        import cairosvg
        
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=size,
            output_height=size
        )
        print(f"✅ cairosvg转换成功: {png_path}")
        return True
        
    except Exception as e:
        print(f"❌ cairosvg转换失败: {e}")
        return False


def convert_with_wand(svg_path: Path, png_path: Path, size: int = 180) -> bool:
    """使用Wand (ImageMagick)转换"""
    try:
        from wand.image import Image
        
        with Image(filename=str(svg_path)) as img:
            img.format = 'png'
            img.resize(size, size)
            img.save(filename=str(png_path))
        
        print(f"✅ Wand转换成功: {png_path}")
        return True
        
    except Exception as e:
        print(f"❌ Wand转换失败: {e}")
        return False


def convert_with_inkscape(svg_path: Path, png_path: Path, size: int = 180) -> bool:
    """使用Inkscape转换"""
    try:
        cmd = [
            'inkscape',
            '--export-type=png',
            f'--export-filename={png_path}',
            f'--export-width={size}',
            f'--export-height={size}',
            str(svg_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Inkscape转换成功: {png_path}")
            return True
        else:
            print(f"❌ Inkscape转换失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Inkscape转换失败: {e}")
        return False


def convert_with_rsvg(svg_path: Path, png_path: Path, size: int = 180) -> bool:
    """使用rsvg-convert转换"""
    try:
        cmd = [
            'rsvg-convert',
            '-w', str(size),
            '-h', str(size),
            '-f', 'png',
            '-o', str(png_path),
            str(svg_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ rsvg-convert转换成功: {png_path}")
            return True
        else:
            print(f"❌ rsvg-convert转换失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ rsvg-convert转换失败: {e}")
        return False


def convert_svg_to_png(svg_path: Path, output_dir: Path, sizes: List[int] = None) -> List[Path]:
    """转换SVG到PNG，支持多种尺寸"""
    if sizes is None:
        sizes = [16, 24, 32, 48, 64, 128, 180, 256, 512]
    
    if not svg_path.exists():
        print(f"❌ SVG文件不存在: {svg_path}")
        return []
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查可用工具
    tools = check_dependencies()
    available_tools = [tool for tool, available in tools.items() if available]
    
    if not available_tools:
        print("❌ 没有可用的转换工具！")
        print("请安装以下工具之一:")
        print("  - pip install cairosvg")
        print("  - pip install Wand (需要ImageMagick)")
        print("  - sudo apt install inkscape (Linux)")
        print("  - sudo apt install librsvg2-bin (Linux)")
        return []
    
    print(f"🔧 可用转换工具: {', '.join(available_tools)}")
    
    # 转换函数映射
    converters = {
        'cairosvg': convert_with_cairosvg,
        'wand': convert_with_wand,
        'inkscape': convert_with_inkscape,
        'rsvg-convert': convert_with_rsvg
    }
    
    converted_files = []
    
    for size in sizes:
        png_path = output_dir / f"tray_icon_{size}x{size}.png"
        success = False
        
        print(f"\n🔄 转换 {size}x{size} PNG...")
        
        # 尝试每个可用的转换工具
        for tool in available_tools:
            if tool in converters:
                if converters[tool](svg_path, png_path, size):
                    converted_files.append(png_path)
                    success = True
                    break
        
        if not success:
            print(f"❌ 无法转换 {size}x{size} PNG")
    
    return converted_files


def create_app_icon(svg_path: Path, output_dir: Path) -> Optional[Path]:
    """创建应用图标 (主要的PNG文件)"""
    app_icon_path = output_dir / "app_icon.png"
    
    tools = check_dependencies()
    
    # 优先使用cairosvg，质量最好
    if tools['cairosvg']:
        if convert_with_cairosvg(svg_path, app_icon_path, 256):
            return app_icon_path
    
    # 备选方案
    for tool, converter in [
        ('inkscape', convert_with_inkscape),
        ('rsvg-convert', convert_with_rsvg),
        ('wand', convert_with_wand)
    ]:
        if tools[tool]:
            if converter(svg_path, app_icon_path, 256):
                return app_icon_path
    
    return None


def main():
    """主函数"""
    print("🎨 SVG到PNG转换工具")
    print("=" * 40)
    
    # 文件路径
    svg_path = Path("resources/icons/tray_icon.svg")
    output_dir = Path("resources/icons")
    
    if not svg_path.exists():
        print(f"❌ SVG文件不存在: {svg_path}")
        return False
    
    print(f"📁 输入文件: {svg_path}")
    print(f"📁 输出目录: {output_dir}")
    
    # 转换多种尺寸
    print("\n🔄 开始转换多种尺寸...")
    converted_files = convert_svg_to_png(svg_path, output_dir)
    
    # 创建主应用图标
    print("\n🔄 创建主应用图标...")
    app_icon = create_app_icon(svg_path, output_dir)
    
    # 总结
    print("\n" + "=" * 40)
    print("📊 转换结果:")
    
    if converted_files:
        print(f"✅ 成功转换 {len(converted_files)} 个文件:")
        for file in converted_files:
            print(f"  - {file.name}")
    
    if app_icon:
        print(f"✅ 主应用图标: {app_icon.name}")
    
    if not converted_files and not app_icon:
        print("❌ 转换失败！请检查依赖项。")
        return False
    
    print("\n🎉 转换完成！")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
