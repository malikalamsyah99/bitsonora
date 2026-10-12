# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve()
ASSETS = ROOT / "assets"
FFMPEG_DIR = ROOT / "vendor" / "ffmpeg"

suffix = ".exe" if os.name == "nt" else ""
ffmpeg_path = FFMPEG_DIR / f"ffmpeg{suffix}"
ffprobe_path = FFMPEG_DIR / f"ffprobe{suffix}"

if sys.platform == "darwin":
    icon_path = ASSETS / "bitsonora.icns"
elif sys.platform == "win32":
    icon_path = ASSETS / "bitsonora.ico"
else:
    icon_path = None

required = [
    ffmpeg_path,
    ffprobe_path,
    ASSETS / "bitsonora.png",
]

if icon_path is not None:
    required.append(icon_path)

for item in required:
    if not item.is_file():
        raise SystemExit(f"Required build file is missing: {item}")

datas = [
    (str(ASSETS / "bitsonora.png"), "assets"),
]

binaries = [
    (str(ffmpeg_path), "bin"),
    (str(ffprobe_path), "bin"),
]

a = Analysis(
    [str(ROOT / "run_bitsonora.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
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
    name="Bitsonora",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Bitsonora",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Bitsonora.app",
        icon=str(icon_path),
        bundle_identifier="com.malikalamsyah99.bitsonora",
    )
