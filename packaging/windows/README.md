# Windows build and installer

## Requirements

- Windows 10/11, 64-bit
- Python 3.10 or newer
- Inno Setup 6
- FFmpeg Windows binaries: `ffmpeg.exe` and `ffprobe.exe`

## Prepare FFmpeg

Create this directory:

`packaging\windows\ffmpeg\bin\`

Place `ffmpeg.exe` and `ffprobe.exe` inside it. Use a Windows FFmpeg build from a source you trust. Review its license and distribution requirements before redistributing it.

The build script deliberately stops if those binaries are missing: MP3 conversion and MP4 stream merging require FFmpeg.

## Build

From the project root, run:

`packaging\windows\build_windows.bat`

The script creates `.venv`, installs Python dependencies, builds the onedir app with PyInstaller, and calls Inno Setup.

The final installer is written to:

`release\MediaDownloader-Setup-1.0.0.exe`

You can also run the steps manually:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean packaging\windows\mediadownloader.spec
ISCC packaging\windows\installer.iss
```

## Important release checks

- Test the installer on a clean Windows 10/11 machine.
- Test MP3 conversion and MP4 merging.
- Test uninstall and Start Menu shortcuts.
- Consider code signing before public distribution. Unsigned installers may trigger Microsoft SmartScreen warnings.
- Check the FFmpeg build's license and obligations before bundling it.
