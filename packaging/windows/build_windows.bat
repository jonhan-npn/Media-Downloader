@echo off
setlocal
cd /d "%~dp0..\.."

echo [1/5] Checking Python...
set "PY_CMD="
py -3 --version >nul 2>&1 && set "PY_CMD=py -3"
if not defined PY_CMD (
  python --version >nul 2>&1 && set "PY_CMD=python"
)
if not defined PY_CMD (
  if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PY_CMD="%LOCALAPPDATA%\Programs\Python\Python313\python.exe""
  )
)
if not defined PY_CMD (
  echo Python 3 is required. Install Python from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

echo [2/5] Creating virtual environment...
if not exist .venv %PY_CMD% -m venv .venv
call .venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [4/5] Checking FFmpeg binaries...
if not exist packaging\windows\ffmpeg\bin\ffmpeg.exe (
  echo ERROR: Put ffmpeg.exe in packaging\windows\ffmpeg\bin\
  echo Also put ffprobe.exe in the same folder.
  echo Obtain a Windows FFmpeg build and review its license terms.
  pause
  exit /b 1
)
if not exist packaging\windows\ffmpeg\bin\ffprobe.exe (
  echo ERROR: ffprobe.exe is missing from packaging\windows\ffmpeg\bin\
  pause
  exit /b 1
)

echo Building application with PyInstaller...
python -m PyInstaller --noconfirm --clean packaging\windows\mediadownloader.spec
if errorlevel 1 (
  echo PyInstaller build failed.
  pause
  exit /b 1
)

echo [5/5] Creating installer...
where ISCC >nul 2>nul
if errorlevel 1 (
  echo Inno Setup compiler ISCC.exe was not found.
  echo Install Inno Setup 6, then run:
  echo ISCC packaging\windows\installer.iss
  pause
  exit /b 1
)
ISCC packaging\windows\installer.iss
if errorlevel 1 (
  echo Inno Setup compilation failed.
  pause
  exit /b 1
)

echo.
echo SUCCESS. Installer is in the release folder.
pause
