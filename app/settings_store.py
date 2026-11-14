import json
from pathlib import Path
from app.paths import app_data_dir, default_download_dir

SETTINGS_FILE = app_data_dir() / "settings.json"

DEFAULTS = {
    "download_dir": str(default_download_dir()),
    "default_format": "mp3",
    "audio_quality": "320",
    "video_quality": "1080",
    "theme": "dark",
    "embed_thumbnail": True,
    "fetch_lyrics": True,
}

def load_settings() -> dict:
    try:
        saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return {**DEFAULTS, **saved}
    except (OSError, json.JSONDecodeError):
        return DEFAULTS.copy()

def save_settings(settings: dict) -> None:
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
