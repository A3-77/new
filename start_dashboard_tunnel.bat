@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo Python was not found.
        echo Please install Python 3.10 or newer, and check "Add Python to PATH".
        echo Download: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating local Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Failed to create Python environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

python -c "import streamlit, pandas, openpyxl, numpy, plotly" >nul 2>nul
if errorlevel 1 (
    echo Installing dashboard dependencies. First run may take a few minutes...
    python -m pip install --upgrade pip
    python -m pip install -r "dashboard_app\requirements.txt"
    if errorlevel 1 (
        echo Failed to install dependencies.
        echo Please check your network connection and try again.
        pause
        exit /b 1
    )
)

echo Starting dashboard for tunnel access...
echo Sakura/FRP local target should be 127.0.0.1:8501 or localhost:8501.
python -m streamlit run "dashboard_app\app.py" ^
  --server.port 8501 ^
  --server.address 0.0.0.0 ^
  --server.enableCORS false ^
  --server.enableXsrfProtection false

pause
