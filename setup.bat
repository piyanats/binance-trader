@echo off
REM Binance Thailand Trading Bot - Setup Script for Windows
REM This script creates a virtual environment and installs dependencies using uv

echo ========================================
echo Binance Thailand Trading Bot - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.13 or higher
    pause
    exit /b 1
)

REM Display Python version
echo [OK] Found Python:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Do you want to remove and recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Virtual environment recreated
    ) else (
        echo Using existing virtual environment
    )
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Check if uv is installed
echo Checking for uv package manager...
uv --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] uv is not installed. Installing uv...
    pip install uv
    if errorlevel 1 (
        echo [ERROR] Failed to install uv
        echo Falling back to pip...
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        goto :after_install
    )
    echo [OK] uv installed successfully
) else (
    echo [OK] uv is already installed
)

REM Display uv version
uv --version
echo.

REM Install dependencies using uv
echo Installing dependencies with uv...
uv pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

:after_install

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created
    echo [WARNING] Please edit .env file with your API keys and Slack webhook
) else (
    echo [WARNING] .env file already exists, skipping
)
echo.

REM Initialize portfolio
echo Initializing portfolio...
python initialize_portfolio.py
echo.

REM Display next steps
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Edit .env file with your credentials:
echo    notepad .env
echo.
echo 3. Test your configuration:
echo    python test_connection.py
echo.
echo 4. Run the trading bot:
echo    python trading_bot.py
echo.
echo For detailed instructions, see:
echo   - README.md for comprehensive documentation
echo   - QUICKSTART.md for quick start guide
echo.
pause
