# Build with: pyinstaller packaging/windows/mediadownloader.spec
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

project = Path(SPECPATH).resolve().parents[1]
(project / "build" / "mediadownloader").mkdir(parents=True, exist_ok=True)
datas = []
binaries = []
hiddenimports = ["app.application", "ui.main_window"]
for package in ("yt_dlp", "syncedlyrics", "mutagen", "PIL"):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

ffmpeg_dir = project / "packaging" / "windows" / "ffmpeg" / "bin"
for name in ("ffmpeg.exe", "ffprobe.exe"):
    candidate = ffmpeg_dir / name
    if candidate.exists():
        binaries.append((str(candidate), "."))

a = Analysis(
    [str(project / "main.py")],
    pathex=[str(project)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "notebook"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="MediaDownloader",
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
)
coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MediaDownloader",
)
