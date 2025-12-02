# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for BPM - Blood Pressure Monitoring Analysis Tool

Build with:
    pyinstaller BPM.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Paths
src_path = Path('src')
resources_path = Path('resources')

# Data files to include
datas = [
    ('src/ui/styles.qss', 'ui'),
    ('resources/icons/logo.png', 'resources/icons'),
    ('resources/icons/app.ico', 'resources/icons'),
]

# Hidden imports for PySide6 and other modules
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'pandas',
    'numpy',
    'openpyxl',
    'reportlab',
    'reportlab.lib',
    'reportlab.lib.colors',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'reportlab.lib.enums',
    'reportlab.platypus',
    'reportlab.platypus.doctemplate',
    'reportlab.platypus.paragraph',
    'reportlab.platypus.tables',
]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Not used yet - reduces size
        'plotly',      # Not used yet - reduces size
        'scipy',       # Not used yet - reduces size
        'tkinter',
        'test',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BPM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico' if sys.platform == 'win32' else 'resources/icons/logo.png',
)

# macOS app bundle (optional)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='BPM.app',
        icon='resources/icons/logo.png',
        bundle_identifier='com.bpm.bloodpressure',
        info_plist={
            'CFBundleName': 'BPM',
            'CFBundleDisplayName': 'Blood Pressure Analysis',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
