from __future__ import annotations
from pathlib import Path
import re
import shutil
import threading
import yt_dlp

class DownloadCancelled(Exception):
    pass

def find_ffmpeg() -> str | None:
    from app.paths import bundled_ffmpeg
    bundled = bundled_ffmpeg()
    if bundled:
        return bundled
    return shutil.which("ffmpeg")

def clean_title(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value or "download")
    return value.strip(" .")[:180] or "download"

class MediaDownloader:
    def __init__(self, progress_callback, log_callback, cancel_event: threading.Event,
                 settings: dict):
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_event = cancel_event
        self.settings = settings

    def _progress_hook(self, data):
        if self.cancel_event.is_set():
            raise DownloadCancelled("Download cancelled by user.")
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            done = data.get("downloaded_bytes", 0)
            percent = int(done * 100 / total) if total else 0
            self.progress_callback(
                percent,
                data.get("_speed_str", ""),
                data.get("_eta_str", ""),
                data.get("filename", ""),
            )
        elif status == "finished":
            self.progress_callback(100, "", "", data.get("filename", ""))
            self.log_callback("Download finished; processing media…")

    def download(self, url: str, media_format: str, output_dir: str):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            raise RuntimeError(
                "FFmpeg was not found. Install FFmpeg and add ffmpeg.exe to PATH, "
                "or place ffmpeg.exe and ffprobe.exe in packaging/windows/ffmpeg/bin "
                "before building the installer."
            )

        if media_format == "mp3":
            quality = str(self.settings.get("audio_quality", "320"))
            options = {
                "format": "bestaudio/best",
                "outtmpl": str(output / "%(title).180B [%(id)s].%(ext)s"),
                "noplaylist": True,
                "windowsfilenames": True,
                "writethumbnail": bool(self.settings.get("embed_thumbnail", True)),
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3",
                     "preferredquality": quality},
                    {"key": "FFmpegMetadata"},
                ],
                "progress_hooks": [self._progress_hook],
                "quiet": True,
                "no_warnings": False,
                "ignoreerrors": False,
            }
            if self.settings.get("embed_thumbnail", True):
                options["postprocessors"].append({"key": "EmbedThumbnail"})
        else:
            height = int(self.settings.get("video_quality", "1080"))
            options = {
                "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best",
                "merge_output_format": "mp4",
                "outtmpl": str(output / "%(title).180B [%(id)s].%(ext)s"),
                "noplaylist": True,
                "windowsfilenames": True,
                "progress_hooks": [self._progress_hook],
                "quiet": True,
                "no_warnings": False,
                "ignoreerrors": False,
            }

        options["ffmpeg_location"] = ffmpeg
        self.log_callback(f"Starting {media_format.upper()} download…")
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise RuntimeError("The downloader did not return media information.")
            title = info.get("title") or "Downloaded media"
            requested = info.get("requested_downloads") or []
            filepath = None
            for item in requested:
                filepath = item.get("filepath") or filepath
            if not filepath:
                filepath = ydl.prepare_filename(info)
                if media_format == "mp3":
                    filepath = str(Path(filepath).with_suffix(".mp3"))
                elif Path(filepath).suffix.lower() not in (".mp4", ".m4v"):
                    filepath = str(Path(filepath).with_suffix(".mp4"))
            filepath = str(Path(filepath))
        if media_format == "mp3" and self.settings.get("fetch_lyrics", True):
            self._try_fetch_lyrics(info, filepath)
        return title, filepath

    def _try_fetch_lyrics(self, info: dict, mp3_path: str):
        path = Path(mp3_path)
        if not path.is_file():
            return
        artist = info.get("artist") or info.get("uploader") or ""
        title = info.get("track") or info.get("title") or ""
        if not artist or not title:
            return
        try:
            import syncedlyrics
            lyrics = syncedlyrics.search(f"{artist} {title}", allow_plain_format=False)
            if not lyrics:
                return
            lrc_path = path.with_suffix(".lrc")
            lrc_path.write_text(lyrics, encoding="utf-8")
            try:
                from mutagen.id3 import ID3, USLT, SYLT, Encoding, ID3NoHeaderError
                import re
                try:
                    tags = ID3(path)
                except ID3NoHeaderError:
                    tags = ID3()
                plain = re.sub(r"\[\d+:\d+[.:]?\d*\]", "", lyrics).strip()
                tags.add(USLT(encoding=Encoding.UTF8, lang="eng", desc="", text=plain))
                pairs = []
                for line in lyrics.splitlines():
                    match = re.match(r"\[(\d+):(\d+)[.:](\d+)\](.*)", line)
                    if match:
                        mins, secs, fraction, text = match.groups()
                        ms = (int(mins) * 60 + int(secs)) * 1000 + int(fraction) * 10
                        pairs.append((text.strip(), ms))
                if pairs:
                    tags.add(SYLT(encoding=Encoding.UTF8, lang="eng",
                                  format=2, type=1, desc="", text=pairs))
                tags.save(path, v2_version=3)
            except Exception as exc:
                self.log_callback(f"Lyrics saved as .lrc; tag embedding skipped: {exc}")
            self.log_callback("Synced lyrics saved.")
        except Exception as exc:
            self.log_callback(f"Lyrics were not available: {exc}")
