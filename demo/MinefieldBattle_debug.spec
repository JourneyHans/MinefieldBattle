# -*- mode: python ; coding: utf-8 -*-
# 调试版本 - 显示控制台窗口以便查看错误信息
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files
import os

# 收集 pygame 的所有依赖
datas = []
binaries = []
hiddenimports = []

# 强制收集 pygame - 使用多种方法确保完整性
try:
    # 方法1: collect_all 是最全面的方法
    tmp_ret = collect_all('pygame')
    if tmp_ret:
        datas += tmp_ret[0] if tmp_ret[0] else []
        binaries += tmp_ret[1] if tmp_ret[1] else []
        hiddenimports += tmp_ret[2] if tmp_ret[2] else []
except Exception as e:
    print(f"Warning: collect_all('pygame') failed: {e}")

# 方法2: 收集所有子模块
try:
    submodules = collect_submodules('pygame')
    if submodules:
        hiddenimports += submodules
except Exception as e:
    print(f"Warning: collect_submodules('pygame') failed: {e}")

# 方法3: 显式添加 pygame 核心模块
pygame_core_modules = [
    'pygame',
    'pygame.base',
    'pygame.bufferproxy',
    'pygame.color',
    'pygame.constants',
    'pygame.cursors',
    'pygame.display',
    'pygame.draw',
    'pygame.event',
    'pygame.font',
    'pygame.image',
    'pygame.joystick',
    'pygame.key',
    'pygame.mouse',
    'pygame.mixer',
    'pygame.mixer.music',
    'pygame.pixelcopy',
    'pygame.rect',
    'pygame.sndarray',
    'pygame.sprite',
    'pygame.surface',
    'pygame.surfarray',
    'pygame.sysfont',
    'pygame.time',
    'pygame.transform',
    'pygame.version',
    'pygame._freetype',
    'pygame.pkgdata',
]
hiddenimports += pygame_core_modules

# 方法4: 收集数据文件
try:
    data_files = collect_data_files('pygame')
    if data_files:
        datas += data_files
except Exception as e:
    print(f"Warning: collect_data_files('pygame') failed: {e}")

# 去重并确保 pygame 在列表中
hiddenimports = list(set(hiddenimports))
if 'pygame' not in hiddenimports:
    hiddenimports.insert(0, 'pygame')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='MinefieldBattle_debug',
    debug=True,  # 启用调试
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 调试时禁用压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

