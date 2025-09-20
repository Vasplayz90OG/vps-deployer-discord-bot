import random
import discord
from config import Config

def generate_vps_id():
    """Generate a unique VPS ID"""
    return f"vps{random.randint(10000, 99999)}"

async def send_dm_embed(ctx, vps):
    """Send VPS details via DM to user"""
    try:
        embed = vps.get_deployment_embed()
        embed.set_footer(text=Config.FOOTER_TEXT)
        await ctx.author.send(embed=embed)
        return True
    except discord.Forbidden:
        return False

def format_uptime(seconds):
    """Format seconds into a human-readable uptime string"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
        
    return " ".join(parts)
