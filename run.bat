@echo off
echo Installing ArizNodes VPS Bot...
echo Credits: Vasplayz90
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please edit the .env file with your Discord bot token and other settings.
)

echo.
echo Installation complete!
echo To run the bot: python bot.py
echo Credits: Vasplayz90
echo Watching ArizNodes Cloud By Vasplayz90 🚀🚀
pause
