@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "scripts\demo_sustentacion.py"
) else (
  python "scripts\demo_sustentacion.py"
)
if errorlevel 1 echo La demostracion encontro un error. Revise el mensaje anterior.
pause
