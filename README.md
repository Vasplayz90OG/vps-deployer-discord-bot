# ArizNodes VPS Bot

A Discord bot for managing VPS instances directly from Discord.

## Features

- Create VPS instances with custom RAM, CPU, Disk, and OS
- Manage VPS instances (Start, Stop, Restart, Reinstall OS)
- View VPS information and status
- Admin management system
- Direct messaging of VPS credentials

## Setup

### Automatic Setup (Linux/Mac)
1. Run the setup script: `chmod +x setup.sh && ./setup.sh`
2. Edit the `.env` file with your Discord bot token
3. Run the bot: `python3 bot.py`

### Automatic Setup (Windows)
1. Run the batch file: `run.bat`
2. Edit the `.env` file with your Discord bot token
3. Run the bot: `python bot.py`

### Manual Setup
1. Install Python 3.8 or higher
2. Install requirements: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your details
4. Run the bot: `python3 bot.py`

## Creating a Discord Bot

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to the Bot section and create a bot
4. Copy the bot token and add it to the `.env` file
5. Enable the following intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent

## Commands

- `/deploy` - Create a new VPS instance
- `/deletevps` - Delete your VPS instance
- `/ban_vps` - Ban a VPS instance (Admin only)
- `/list` - List all your VPS instances
- `/add_admin` - Add an admin (Owner only)
- `/manage` - Manage your VPS instance
- `/clear` - Clear all your VPS instances
- `/help` - Show help information

## Credits

This bot was created by Vasplayz90 for ArizNodes Cloud.

Watching ArizNodes Cloud By Vasplayz90 🚀🚀
