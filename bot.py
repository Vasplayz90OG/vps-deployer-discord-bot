import discord
from discord.ext import commands
import asyncio
import random
import datetime
import os
from typing import Dict, List

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# Configuration
BOT_OWNER_ID = int(os.getenv('BOT_OWNER_ID', 0))
ADMIN_ONLY_DEPLOY = os.getenv('ADMIN_ONLY_DEPLOY', 'False').lower() == 'true'
STATUS_MESSAGE = os.getenv('STATUS_MESSAGE', 'Watching ArizNodes Cloud By Vasplayz90 🚀🚀')
FOOTER_TEXT = os.getenv('FOOTER_TEXT', 'ArizNodes Cloud By Vasplayz90 🚀🚀')
OS_OPTIONS = ["Docker", "Ubuntu 22.04", "Debian 12", "CentOS 9", "AlmaLinux 9", "Rocky Linux 9"]

# Mock data storage (in a real bot, you'd use a database)
vps_instances = {}
admins = {}
user_vps = {}

class VPS:
    def __init__(self, vps_id, owner_id, ram, disk, cpu, os="Docker"):
        self.id = vps_id
        self.owner_id = owner_id
        self.ram = ram
        self.disk = disk
        self.cpu = cpu
        self.os = os
        self.status = "Running"  # Can be Running, Stopped, Restarting
        self.created_at = datetime.datetime.now()
        self.username = f"user{random.randint(1000, 9999)}"
        self.password = f"pass{random.randint(10000, 99999)}"
        self.root_password = f"root{random.randint(10000, 99999)}"
        self.ip = f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
        self.tmate_session = f"tmate-{random.randint(100000000, 999999999)}"

    def get_info_embed(self):
        embed = discord.Embed(
            title=f"VPS Information - ID: {self.id}",
            color=0x00ff00 if self.status == "Running" else 0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Status", value=self.status, inline=True)
        embed.add_field(name="Memory", value=f"{self.ram}GB", inline=True)
        embed.add_field(name="CPU", value=f"{self.cpu} cores", inline=True)
        embed.add_field(name="Disk", value=f"{self.disk}GB", inline=True)
        embed.add_field(name="OS", value=self.os, inline=True)
        embed.add_field(name="Username", value=self.username, inline=True)
        embed.add_field(name="User Password", value=self.password, inline=True)
        embed.add_field(name="Root Password", value=self.root_password, inline=True)
        embed.add_field(name="IP Address", value=self.ip, inline=True)
        embed.add_field(name="Created", value=self.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Tmate Session", value=self.tmate_session, inline=False)
        embed.set_footer(text=FOOTER_TEXT)
        return embed

    def get_deployment_embed(self):
        embed = discord.Embed(
            title="🎉 ArizNodes VPS Creation Successful",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🆔 VPS ID", value=self.id, inline=True)
        embed.add_field(name="💾 Memory", value=f"{self.ram}GB", inline=True)
        embed.add_field(name="⚡ CPU", value=f"{self.cpu} cores", inline=True)
        embed.add_field(name="💿 Disk", value=f"{self.disk}GB", inline=True)
        embed.add_field(name="👤 Username", value=self.username, inline=True)
        embed.add_field(name="🔑 User Password", value=self.password, inline=True)
        embed.add_field(name="🔑 Root Password", value=self.root_password, inline=True)
        embed.add_field(name="🔒 Tmate Session", value=self.tmate_session, inline=True)
        embed.add_field(name="🔌 Direct Connection", value=self.ip, inline=True)
        embed.add_field(
            name="ℹ️ Note", 
            value="This is a ArizNodes VPS instance. You can install and configure additional packages as needed.",
            inline=False
        )
        embed.set_footer(text=FOOTER_TEXT)
        return embed

    def get_short_info(self):
        status_emoji = "🟢" if self.status == "Running" else "🔴"
        return f"{status_emoji} {self.id} | {self.ram}GB RAM | {self.cpu} CPU | {self.disk}GB Disk | {self.os}"

def generate_vps_id():
    """Generate a unique VPS ID"""
    return f"vps{random.randint(10000, 99999)}"

async def send_dm_embed(ctx, vps):
    """Send VPS details via DM to user"""
    try:
        embed = vps.get_deployment_embed()
        await ctx.author.send(embed=embed)
        return True
    except discord.Forbidden:
        return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name=STATUS_MESSAGE
    ))
    print(f'{bot.user} has logged in successfully!')
    print(STATUS_MESSAGE)

@bot.slash_command(name="deploy", description="Deploy a new VPS instance")
async def deploy(
    ctx, 
    ram: discord.Option(int, description="RAM in GB", min_value=1, max_value=64),
    disk: discord.Option(int, description="Disk space in GB", min_value=10, max_value=500),
    cpu: discord.Option(int, description="CPU cores", min_value=1, max_value=16),
    os: discord.Option(str, description="Operating System", 
                      choices=OS_OPTIONS, default="Docker")
):
    # Check if user is admin if admin system is enabled
    if ADMIN_ONLY_DEPLOY and ctx.author.id not in admins:
        await ctx.respond("❌ You don't have permission to use this command.")
        return
    
    # Generate a unique VPS ID
    vps_id = generate_vps_id()
    while vps_id in vps_instances:
        vps_id = generate_vps_id()
    
    # Create new VPS instance
    new_vps = VPS(vps_id, ctx.author.id, ram, disk, cpu, os)
    vps_instances[vps_id] = new_vps
    
    # Track user's VPS
    if ctx.author.id not in user_vps:
        user_vps[ctx.author.id] = []
    user_vps[ctx.author.id].append(vps_id)
    
    # Send VPS details via DM
    success = await send_dm_embed(ctx, new_vps)
    if success:
        await ctx.respond("✅ Your VPS has been deployed! Check your DMs for details.")
    else:
        # If DM fails, send in channel
        embed = new_vps.get_deployment_embed()
        await ctx.respond("✅ Your VPS has been deployed! I couldn't DM you, so here are your details:", embed=embed)

@bot.slash_command(name="deletevps", description="Delete your VPS instance")
async def deletevps(
    ctx, 
    vps_id: discord.Option(str, description="ID of the VPS to delete")
):
    if vps_id not in vps_instances:
        await ctx.respond("❌ VPS ID not found.")
        return
        
    vps = vps_instances[vps_id]
    
    # Check if user owns this VPS or is admin
    if vps.owner_id != ctx.author.id and ctx.author.id not in admins:
        await ctx.respond("❌ You can only delete your own VPS instances.")
        return
        
    # Delete the VPS
    del vps_instances[vps_id]
    if ctx.author.id in user_vps and vps_id in user_vps[ctx.author.id]:
        user_vps[ctx.author.id].remove(vps_id)
    
    await ctx.respond(f"✅ VPS {vps_id} has been deleted successfully.")

@bot.slash_command(name="ban_vps", description="Ban a VPS instance (Admin only)")
async def ban_vps(
    ctx, 
    vps_id: discord.Option(str, description="ID of the VPS to ban")
):
    if ctx.author.id not in admins:
        await ctx.respond("❌ You need admin permissions to use this command.")
        return
        
    if vps_id not in vps_instances:
        await ctx.respond("❌ VPS ID not found.")
        return
        
    # In a real implementation, this would actually ban the VPS
    # For this mock implementation, we'll just delete it
    vps = vps_instances[vps_id]
    owner_id = vps.owner_id
    
    del vps_instances[vps_id]
    if owner_id in user_vps and vps_id in user_vps[owner_id]:
        user_vps[owner_id].remove(vps_id)
    
    await ctx.respond(f"✅ VPS {vps_id} has been banned and deleted.")

@bot.slash_command(name="list", description="List all your VPS instances")
async def list_vps(ctx):
    if ctx.author.id not in user_vps or not user_vps[ctx.author.id]:
        await ctx.respond("❌ You don't have any VPS instances.")
        return
        
    embed = discord.Embed(
        title="Your VPS Instances",
        color=0x7289DA,
        timestamp=datetime.datetime.now()
    )
    
    for vps_id in user_vps[ctx.author.id]:
        if vps_id in vps_instances:
            vps = vps_instances[vps_id]
            embed.add_field(
                name=f"VPS {vps_id}",
                value=vps.get_short_info(),
                inline=False
            )
    
    embed.set_footer(text=FOOTER_TEXT)
    await ctx.respond(embed=embed)

@bot.slash_command(name="add_admin", description="Add an admin (Owner only)")
async def add_admin(
    ctx, 
    user: discord.Option(discord.User, description="User to make admin")
):
    # Only the bot owner can add admins
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.respond("❌ Only the bot owner can add admins.")
        return
        
    admins[user.id] = True
    await ctx.respond(f"✅ {user.mention} has been added as an admin.")

@bot.slash_command(name="manage", description="Manage your VPS instance")
async def manage_vps(
    ctx, 
    vps_id: discord.Option(str, description="ID of the VPS to manage"),
    action: discord.Option(str, description="Action to perform", 
                          choices=["Start", "Stop", "Restart", "Reinstall OS", "Info"])
):
    if vps_id not in vps_instances:
        await ctx.respond("❌ VPS ID not found.")
        return
        
    vps = vps_instances[vps_id]
    
    # Check if user owns this VPS
    if vps.owner_id != ctx.author.id and ctx.author.id not in admins:
        await ctx.respond("❌ You can only manage your own VPS instances.")
        return
        
    # Perform the requested action
    if action == "Start":
        vps.status = "Running"
        await ctx.respond(f"✅ VPS {vps_id} has been started.")
    elif action == "Stop":
        vps.status = "Stopped"
        await ctx.respond(f"✅ VPS {vps_id} has been stopped.")
    elif action == "Restart":
        vps.status = "Restarting"
        await ctx.respond(f"✅ VPS {vps_id} is restarting...")
        await asyncio.sleep(2)  # Simulate restart time
        vps.status = "Running"
        await ctx.edit(content=f"✅ VPS {vps_id} has been restarted.")
    elif action == "Reinstall OS":
        # In a real implementation, this would reinstall the OS
        await ctx.respond(f"✅ VPS {vps_id} is being reinstalled...")
        await asyncio.sleep(3)  # Simulate reinstall time
        await ctx.edit(content=f"✅ VPS {vps_id} has been reinstalled with {vps.os}.")
    elif action == "Info":
        await ctx.respond(embed=vps.get_info_embed())

@bot.slash_command(name="clear", description="Clear all your VPS instances")
async def clear_vps(ctx):
    if ctx.author.id not in user_vps or not user_vps[ctx.author.id]:
        await ctx.respond("❌ You don't have any VPS instances to clear.")
        return
        
    # Confirm before clearing
    confirm_embed = discord.Embed(
        title="⚠️ Confirm Clear All VPS",
        description="This will delete ALL your VPS instances. This action cannot be undone.",
        color=0xff9900
    )
    confirm_embed.set_footer(text="Type 'confirm' to proceed or anything else to cancel.")
    
    await ctx.respond(embed=confirm_embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        if msg.content.lower() != 'confirm':
            await ctx.respond("❌ Clear operation cancelled.")
            return
            
        # Delete all user's VPS instances
        for vps_id in user_vps[ctx.author.id][:]:
            if vps_id in vps_instances:
                del vps_instances[vps_id]
        user_vps[ctx.author.id] = []
        
        await ctx.respond("✅ All your VPS instances have been deleted.")
    except asyncio.TimeoutError:
        await ctx.respond("❌ Clear operation timed out.")

@bot.slash_command(name="help", description="Show help information")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="ArizNodes VPS Bot Help",
        description="Manage your VPS instances directly from Discord!",
        color=0x7289DA
    )
    
    embed.add_field(
        name="Available Commands",
        value=(
            "`/deploy` - Create a new VPS instance\n"
            "`/deletevps` - Delete your VPS instance\n"
            "`/ban_vps` - Ban a VPS instance (Admin only)\n"
            "`/list` - List all your VPS instances\n"
            "`/add_admin` - Add an admin (Owner only)\n"
            "`/manage` - Manage your VPS instance\n"
            "`/clear` - Clear all your VPS instances\n"
            "`/help` - Show this help message"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Features",
        value=(
            "• Choose RAM, CPU, Disk, and OS options\n"
            "• Start, Stop, Restart your VPS\n"
            "• Reinstall OS with different options\n"
            "• Direct connection details\n"
            "• Tmate session for SSH access"
        ),
        inline=False
    )
    
    embed.set_footer(text=FOOTER_TEXT)
    await ctx.respond(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set.")
        print("Please set your bot token before running the bot.")
        exit(1)
        
    bot.run(token)
