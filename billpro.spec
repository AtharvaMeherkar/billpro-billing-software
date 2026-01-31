# -*- mode: python ; coding: utf-8 -*-
"""
BillPro PyInstaller Spec File
Build with: pyinstaller billpro.spec
"""

import os
import sys

block_cipher = None

# Get the current directory
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['run.py'],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[
        # Include templates
        ('app/templates', 'app/templates'),
        # Include static files
        ('app/static', 'app/static'),
        # Include config files
        ('config', 'config'),
        # Include bill templates
        ('bill_templates', 'bill_templates'),
        # Create empty database folder
        ('database', 'database'),
    ],
    hiddenimports=[
        'flask',
        'flask_sqlalchemy',
        'sqlalchemy',
        'jinja2',
        'werkzeug',
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.colors',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.platypus',
        'reportlab.graphics',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'win32print',
        'win32ui',
        'escpos',
        'escpos.printer',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BillPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/static/img/icon.ico' if os.path.exists('app/static/img/icon.ico') else None,
)
