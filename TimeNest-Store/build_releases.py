#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
插件发布包构建脚本
自动为所有插件创建发布包
"""

import os
import json
import zipfile
import hashlib
from pathlib import Path


def calculate_sha256(file_path):
    """计算文件的SHA256校验和"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def create_plugin_release(plugin_dir, releases_dir):
    """为单个插件创建发布包"""
    plugin_path = Path(plugin_dir)
    plugin_name = plugin_path.name
    
    # 读取manifest.json获取版本信息
    manifest_path = plugin_path / "manifest.json"
    if not manifest_path.exists():
        print(f"警告: {plugin_name} 缺少 manifest.json 文件")
        return None
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        plugin_id = manifest.get('id', plugin_name)
        version = manifest.get('version', '1.0.0')
        
        # 创建发布包文件名
        release_filename = f"{plugin_id}_v{version}.zip"
        release_path = Path(releases_dir) / release_filename
        
        # 创建ZIP文件
        with zipfile.ZipFile(release_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in plugin_path.rglob('*'):
                if file_path.is_file():
                    # 计算相对路径
                    arcname = file_path.relative_to(plugin_path)
                    zipf.write(file_path, arcname)
        
        # 计算文件大小和校验和
        file_size = release_path.stat().st_size
        checksum = calculate_sha256(release_path)
        
        print(f"✅ 创建发布包: {release_filename}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   校验和: {checksum}")
        
        return {
            'plugin_id': plugin_id,
            'version': version,
            'filename': release_filename,
            'size': file_size,
            'checksum': f"sha256:{checksum}"
        }
        
    except Exception as e:
        print(f"❌ 创建 {plugin_name} 发布包失败: {e}")
        return None


def update_plugins_json(releases_info, plugins_json_path):
    """更新plugins.json文件中的发布信息"""
    try:
        with open(plugins_json_path, 'r', encoding='utf-8') as f:
            plugins_data = json.load(f)
        
        # 更新插件信息
        for plugin in plugins_data.get('plugins', []):
            plugin_id = plugin.get('id')
            
            # 查找对应的发布信息
            release_info = next((r for r in releases_info if r['plugin_id'] == plugin_id), None)
            if release_info:
                # 更新下载URL
                base_url = "https://github.com/ziyi127/TimeNest-Store/releases/download"
                plugin['download_url'] = f"{base_url}/v{release_info['version']}/{release_info['filename']}"
                plugin['size'] = release_info['size']
                plugin['checksum'] = release_info['checksum']
                plugin['version'] = release_info['version']
                
                print(f"📝 更新 {plugin_id} 的发布信息")
        
        # 保存更新后的文件
        with open(plugins_json_path, 'w', encoding='utf-8') as f:
            json.dump(plugins_data, f, ensure_ascii=False, indent=4)
        
        print("✅ plugins.json 更新完成")
        
    except Exception as e:
        print(f"❌ 更新 plugins.json 失败: {e}")


def main():
    """主函数"""
    print("🚀 开始构建插件发布包...")
    
    # 设置路径
    store_dir = Path(__file__).parent
    plugins_dir = store_dir / "plugins"
    releases_dir = store_dir / "releases"
    plugins_json_path = store_dir / "plugins.json"
    
    # 确保releases目录存在
    releases_dir.mkdir(exist_ok=True)
    
    # 获取所有插件目录
    plugin_dirs = [d for d in plugins_dir.iterdir() if d.is_dir()]
    
    if not plugin_dirs:
        print("❌ 未找到任何插件目录")
        return
    
    print(f"📦 找到 {len(plugin_dirs)} 个插件:")
    for plugin_dir in plugin_dirs:
        print(f"   - {plugin_dir.name}")
    
    print("\n🔨 开始构建发布包...")
    
    # 为每个插件创建发布包
    releases_info = []
    for plugin_dir in plugin_dirs:
        release_info = create_plugin_release(plugin_dir, releases_dir)
        if release_info:
            releases_info.append(release_info)
    
    print(f"\n📊 构建完成:")
    print(f"   成功: {len(releases_info)} 个")
    print(f"   失败: {len(plugin_dirs) - len(releases_info)} 个")
    
    # 更新plugins.json
    if releases_info and plugins_json_path.exists():
        print("\n📝 更新插件配置...")
        update_plugins_json(releases_info, plugins_json_path)
    
    print("\n🎉 所有任务完成!")


if __name__ == "__main__":
    main()
