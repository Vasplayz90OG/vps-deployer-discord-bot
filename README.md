# ArizNodes VPS Bot

A Discord bot for managing VPS instances directly from Discord.

## Features

- Create VPS instances with custom RAM, CPU, Disk, and OS
- Manage VPS instances (Start, Stop, Restart, Reinstall OS)
- View VPS information and status
- Admin management system
- Direct messaging of VPS credentials

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your details
4. Run the bot: `python bot.py`

## Docker Setup

1. Copy `.env.example` to `.env` and fill in your details
2. Build and run: `docker-compose up -d`

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
