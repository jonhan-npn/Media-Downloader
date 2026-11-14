@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" main.py
) else (
    start "" "C:\Users\Johan\AppData\Local\Programs\Python\Python313\python.exe" main.py
)
