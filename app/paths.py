from pathlib import Path
import os
import sys

APP_NAME = "MediaDownloader"

def app_data_dir() -> Path:
    if "MEDIADOWNLOADER_DATA_DIR" in os.environ:
        path = Path(os.environ["MEDIADOWNLOADER_DATA_DIR"])
        path.mkdir(parents=True, exist_ok=True)
        return path
    base = os.environ.get("APPDATA")
    if base:
        try:
            path = Path(base) / APP_NAME
            path.mkdir(parents=True, exist_ok=True)
            return path
        except OSError:
            pass
    try:
        path = Path.home() / ".mediadownloader"
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError:
        path = Path(__file__).resolve().parents[1] / ".mediadownloader"
        path.mkdir(parents=True, exist_ok=True)
        return path

def default_download_dir() -> Path:
    try:
        path = Path.home() / "Music" / "Downloads"
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError:
        path = Path(__file__).resolve().parents[1] / "downloads"
        path.mkdir(parents=True, exist_ok=True)
        return path

def bundled_ffmpeg() -> str | None:
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.extend([
            Path(sys._MEIPASS) / "ffmpeg.exe",
            Path(sys.executable).parent / "ffmpeg.exe",
        ])
    project = Path(__file__).resolve().parents[1]
    candidates.append(project / "packaging" / "windows" / "ffmpeg" / "bin" / "ffmpeg.exe")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None
