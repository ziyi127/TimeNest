# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\hujin\\Desktop\\TimeNest\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\hujin\\Desktop\\TimeNest\\timetable.json', '.'), ('C:\\Users\\hujin\\Desktop\\TimeNest\\TKtimetable.ico', '.')],
    hiddenimports=['tkinter', 'PIL', 'pystray'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TimeNest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\hujin\\Desktop\\TimeNest\\TKtimetable.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TimeNest',
)
