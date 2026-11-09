@echo off
REM ---- Build Pippo.exe (run from this folder) ----
REM The list template + team list are baked INTO the exe (--add-data), nothing else to copy.
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
  --name Pippo ^
  --add-data "data\slack_user_map.json;." ^
  --add-data "data\November_-_2026.json;." ^
  --collect-all customtkinter ^
  --collect-submodules slack_bolt ^
  --collect-submodules slack_sdk ^
  main.py
echo.
echo Done. Your app: dist\Pippo.exe
pause
