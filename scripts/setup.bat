@echo off
REM Pravi AI - Windows Setup Script
REM This script automates the installation and setup of Pravi AI on Windows

echo.
echo ================================================================
echo                     PRAVI AI SETUP (Windows)
echo                 Automated Installation Script
echo ================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version

REM Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found
    pause
    exit /b 1
)

echo [OK] pip is installed

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

echo.
echo Working directory: %CD%
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install backend dependencies
echo Installing backend dependencies...
if not exist "backend\requirements.txt" (
    echo [ERROR] backend\requirements.txt not found
    pause
    exit /b 1
)

pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Backend dependencies installed

REM Check for Ollama
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Ollama not found
    echo Please install Ollama from: https://ollama.com
    echo After installing, download a model with: ollama pull mistral:7b
) else (
    echo [OK] Ollama is installed

    REM Ask about model installation
    echo.
    echo Ollama Model Setup
    echo.
    echo Available model options:
    echo   1^) Phi-3 Mini (4GB VRAM^) - Fastest
    echo   2^) Mistral 7B (5GB VRAM^) - Balanced (Recommended^)
    echo   3^) Llama 3.1 8B (8GB VRAM^) - High Quality
    echo   4^) Skip model installation
    echo.

    set /p MODEL_CHOICE="Select model to download [1-4]: "

    if "%MODEL_CHOICE%"=="1" (
        echo Downloading phi3:mini...
        ollama pull phi3:mini
    ) else if "%MODEL_CHOICE%"=="2" (
        echo Downloading mistral:7b...
        ollama pull mistral:7b
    ) else if "%MODEL_CHOICE%"=="3" (
        echo Downloading llama3.1:8b...
        ollama pull llama3.1:8b
    ) else (
        echo Skipping model installation
    )
)

REM Create .env file if it doesn't exist
if not exist "backend\.env" (
    echo Creating configuration file...
    (
        echo # Pravi AI Configuration
        echo.
        echo # Multi-GPU Configuration
        echo ENABLE_MULTI_GPU=false
        echo MULTI_GPU_CONFIG=balanced
        echo.
        echo # Server Configuration
        echo HOST=0.0.0.0
        echo PORT=8000
        echo.
        echo # Ollama Configuration
        echo OLLAMA_HOST=http://localhost:11434
    ) > backend\.env
    echo [OK] Created backend\.env
)

REM Create data directories
if not exist "data\documents" mkdir data\documents
echo [OK] Created data directories

echo.
echo ================================================================
echo              SETUP COMPLETED SUCCESSFULLY!
echo ================================================================
echo.

echo Next steps:
echo.
echo 1. Start Ollama (in a new terminal^):
echo    ollama serve
echo.
echo 2. Start the backend (in a new terminal^):
echo    cd backend
echo    ..\venv\Scripts\activate
echo    python main.py
echo.
echo 3. Open the frontend:
echo    Open frontend\index.html in your browser
echo    Or run: cd frontend ^&^& python -m http.server 3000
echo.

REM Ask if user wants to start now
set /p START_NOW="Would you like to start the backend now? [y/N]: "

if /i "%START_NOW%"=="y" (
    echo.
    echo Starting Ollama...

    REM Check if Ollama is already running
    tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
    if %errorlevel% neq 0 (
        echo Starting Ollama in background...
        start /B ollama serve > logs\ollama.log 2>&1
        timeout /t 2 /nobreak >nul
        echo [OK] Ollama started
    ) else (
        echo [INFO] Ollama is already running
    )

    echo Starting backend server...
    cd backend
    call ..\venv\Scripts\activate.bat
    python main.py
) else (
    echo.
    echo Setup complete! Follow the steps above to start the application.
)

pause
