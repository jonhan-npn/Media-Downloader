# MediaDownloader — Windows desktop

A Windows-first desktop application built with Python, PySide6, yt-dlp, SQLite, PyInstaller and Inno Setup.

## Features

- Paste a supported media URL.
- Select MP3 audio or MP4 video.
- Choose a download folder.
- Select MP3 bitrate and maximum MP4 video height.
- Show download progress, speed and ETA.
- Cancel the active download.
- Store local download history in SQLite.
- Save local settings and choose a dark or light theme.
- Embed available thumbnails in MP3 files.
- Optionally try to retrieve synced lyrics and save an `.lrc` sidecar file.
- No API-key configuration or LLM integration.

Use this only for media you own or have permission to download, and follow the relevant website's terms.

## Development setup (Windows PowerShell)

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

FFmpeg is required for MP3 extraction/conversion and MP4 merging. During development, either add `ffmpeg.exe` to Windows `PATH`, or place `ffmpeg.exe` and `ffprobe.exe` in `packaging/windows/ffmpeg/bin/`.

## Build a Windows installer

Read `packaging/windows/README.md`, then run:

```bat
packaging\windows\build_windows.bat
```

The result is `release\MediaDownloader-Setup-1.0.0.exe`.

This repository contains the installer recipe, not a precompiled Windows `.exe`: the build must run on Windows to produce and validate the Windows installer.

## Local data

Settings and SQLite history are stored in `%APPDATA%\\MediaDownloader\\`.

## Current limitations

- One active download at a time; no multi-item queue yet.
- yt-dlp's supported sources and formats can change over time.
- Cancellation is cooperative and may take a moment while FFmpeg is processing.
- The app does not bypass DRM, access controls, subscriptions or platform restrictions.
- Spotify links/API integration from the old script are intentionally omitted because this build does not use API keys.
