#!/bin/bash

echo "Installing ArizNodes VPS Bot..."
echo "Credits: Vasplayz90"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your Discord bot token and other settings."
fi

echo ""
echo "Installation complete!"
echo "To run the bot: python3 bot.py"
echo "Credits: Vasplayz90"
echo "Watching ArizNodes Cloud By Vasplayz90 🚀🚀"
