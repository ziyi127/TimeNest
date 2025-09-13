# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\SoftwareDevelop\\TimeNest\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\SoftwareDevelop\\TimeNest\\timetable.json', '.'), ('D:\\SoftwareDevelop\\TimeNest\\TKtimetable.ico', '.'), ('D:\\SoftwareDevelop\\TimeNest\\classtableMeta.json', '.'), ('D:\\SoftwareDevelop\\TimeNest\\timetable_ui_settings.json', '.'), ('D:\\SoftwareDevelop\\TimeNest\\ui', 'ui')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['unittest', 'distutils', 'setuptools', 'pip', 'numpy', 'scipy', 'matplotlib', 'pandas', 'sklearn', 'tensorflow', 'torch', 'email', 'http', 'html', 'xml', 'urllib', 'ftplib', 'cgi', 'concurrent', 'multiprocessing', 'socket', 'ssl', 'sqlite3', 'mysql', 'psycopg2', 'pytest', 'nose'],
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
    strip=True,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\SoftwareDevelop\\TimeNest\\TKtimetable.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=False,
    upx_exclude=[],
    name='TimeNest',
)
