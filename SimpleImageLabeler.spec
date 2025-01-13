# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['SimpleImageLabeler.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SimpleImageLabeler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SimpleImageLabeler',
)

app = BUNDLE(
    coll,
    name='SimpleImageLabeler.app',
    icon=None,
    bundle_identifier='com.simplelabel.imagelabeler',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'CFBundleName': 'SimpleImageLabeler',
        'CFBundleDisplayName': 'SimpleImageLabeler',
        'CFBundleGetInfoString': 'Simple Image Labeling Tool',
        'NSHumanReadableCopyright': '© 2024',
    },
)
