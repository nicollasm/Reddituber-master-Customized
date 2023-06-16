@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Running Python script...
python main.py
IF %ERRORLEVEL% NEQ 0 (
  echo An error occurred. Press any key to exit.
  pause >nul
)
echo Deactivating virtual environment...
call path\to\venv\Scripts\deactivate.bat
