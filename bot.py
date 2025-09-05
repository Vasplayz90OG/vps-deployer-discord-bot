# bot.py
import os
import json
import secrets
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
from vps_manager import (
    create_vps,
    delete_vps,
    list_vps,
    get_vps_info,
    start_vps,
    stop_vps,
    restart_vps,
    reinstall_vps,
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN missing in .env")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
CREDITS = os.getenv("CREDITS", "Vasplayz90")
DEFAULT_IMAGE = os.getenv("DEFAULT_IMAGE", "rastasheep/ubuntu-sshd:22.04")
DATA_FILE = "data.json"

# persistent store
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        DATA = json.load(f)
else:
    DATA = {"vps": {}, "admins": [], "banned_vps": [], "banned_users": []}


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)


def is_owner(user_id: int):
    return user_id == OWNER_ID


def is_admin(user_id: int):
    return is_owner(user_id) or str(user_id) in DATA.get("admins", [])


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="ArizNodes Cloud By Vasplayz90")
    await bot.change_presence(activity=activity)
    print(f"✅ Bot online. Credits: {CREDITS}")
    try:
        await bot.tree.sync()
    except Exception as e:
        print("Warning: failed to sync commands:", e)


# ---------------- Commands ----------------

@bot.tree.command(name="deploy", description="Create a Docker-based VPS (default image). DMs credentials.")
@app_commands.describe(
    ram_mb="Memory in MB (example: 2048)",
    cpu_cores="CPU cores (example: 2)",
    disk_gb="Disk size label in GB (informational)",
)
async def deploy(interaction: discord.Interaction, ram_mb: int = 1024, cpu_cores: int = 1, disk_gb: int = 10):
    await interaction.response.defer(ephemeral=True)
    user = interaction.user
    uid = str(user.id)
    if uid in DATA.get("banned_users", []):
        await interaction.followup.send("You are banned from creating VPS.", ephemeral=True)
        return

    # create VPS with default image
    try:
        info = create_vps(
            owner_id=uid,
            image=DEFAULT_IMAGE,
            ram=f"{ram_mb}m",
            cpus=int(cpu_cores),
            disk_label=f"{disk_gb}G",
        )
    except Exception as e:
        await interaction.followup.send(f"Failed to create VPS: {e}", ephemeral=True)
        return

    vps_id = info["id"]
    DATA["vps"][vps_id] = {
        "owner": uid,
        "image": info.get("image", DEFAULT_IMAGE),
        "ram_mb": ram_mb,
        "cpu_cores": cpu_cores,
        "disk_gb": disk_gb,
        "created": datetime.utcnow().isoformat(),
    }
    save_data()

    # Build embed DM with all requested fields and credit
    embed = discord.Embed(
        title="🎉 ArizNodes VPS Creation Successful",
        description=f"**🆔 VPS ID**\n`{vps_id}`",
        color=0x1abc9c,
        timestamp=datetime.utcnow(),
    )
    embed.add_field(name="💾 Memory", value=f"{ram_mb} MB", inline=True)
    embed.add_field(name="⚡ CPU", value=f"{cpu_cores} cores", inline=True)
    embed.add_field(name="💿 Disk", value=f"{disk_gb} GB (label)", inline=True)
    embed.add_field(name="👤 Username", value=f"{info.get('username', 'root')}", inline=True)
    embed.add_field(name="🔑 User Password", value=f"`{info.get('user_password', '—')}`", inline=True)
    embed.add_field(name="🔑 Root Password", value=f"`{info.get('root_password', '—')}`", inline=True)
    if info.get("ssh_command"):
        embed.add_field(name="🔒 SSH Command", value=f"`{info['ssh_command']}`", inline=False)
    embed.add_field(name="🔌 Direct connection", value=f"{info.get('direct_conn', 'host:port unknown')}", inline=False)
    embed.add_field(
        name="ℹ️ Note",
        value="This is an ArizNodes VPS instance. You can install and configure additional packages as needed.",
        inline=False,
    )
    embed.set_footer(text=f"Credits: {CREDITS} — Watching ArizNodes Cloud By Vasplayz90")

    try:
        await user.send(embed=embed)
        await interaction.followup.send("VPS created — details sent to your DM.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("Could not DM you — enable DMs from server members.", ephemeral=True)


@bot.tree.command(name="deletevps", description="Delete a VPS by ID (owner/admin can).")
@app_commands.describe(vps_id="VPS ID to delete")
async def deletevps(interaction: discord.Interaction, vps_id: str):
    uid = str(interaction.user.id)
    vmeta = DATA.get("vps", {}).get(vps_id)
    if not vmeta:
        await interaction.response.send_message("VPS not found.", ephemeral=True)
        return
    if vmeta["owner"] != uid and not is_admin(interaction.user.id):
        await interaction.response.send_message("You don't have permission to delete this VPS.", ephemeral=True)
        return
    ok = delete_vps(vps_id)
    if ok:
        DATA["vps"].pop(vps_id, None)
        save_data()
        await interaction.response.send_message(f"VPS {vps_id} deleted.", ephemeral=True)
    else:
        await interaction.response.send_message("Failed to delete VPS from backend.", ephemeral=True)


@bot.tree.command(name="ban_vps", description="Owner only: ban/unban a VPS ID.")
@app_commands.describe(vps_id="VPS ID", ban="true to ban, false to unban")
async def ban_vps(interaction: discord.Interaction, vps_id: str, ban: bool):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("Only owner can ban/unban vps.", ephemeral=True)
        return
    if ban:
        DATA.setdefault("banned_vps", []).append(vps_id)
        await interaction.response.send_message(f"VPS {vps_id} banned.", ephemeral=True)
    else:
        if vps_id in DATA.get("banned_vps", []):
            DATA["banned_vps"].remove(vps_id)
        await interaction.response.send_message(f"VPS {vps_id} unbanned.", ephemeral=True)
    save_data()


@bot.tree.command(name="list", description="List VPS (owner/admin see all, members see own).")
async def list_cmd(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    lines = []
    for vid, m in DATA.get("vps", {}).items():
        if m["owner"] == uid or is_admin(interaction.user.id):
            lines.append(
                f"`{vid}` — owner: <@{m['owner']}> — OS image: `{m.get('image')}` — RAM: {m.get('ram_mb')}MB — CPU: {m.get('cpu_cores')} cores"
            )
    if not lines:
        await interaction.response.send_message("No VPS found.", ephemeral=True)
    else:
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


@bot.tree.command(name="add_admin", description="Owner only: add admin by Discord ID.")
@app_commands.describe(user_id="Discord user ID to add as admin")
async def add_admin(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("Only owner can add admins.", ephemeral=True)
        return
    if user_id in DATA.get("admins", []):
        await interaction.response.send_message("User already admin.", ephemeral=True)
        return
    DATA.setdefault("admins", []).append(user_id)
    save_data()
    await interaction.response.send_message(f"Added admin {user_id}.", ephemeral=True)


@bot.tree.command(name="manage_vps", description="Manage a VPS (Start / Stop / Restart / Reinstall OS).")
@app_commands.describe(vps_id="VPS ID to manage")
async def manage_vps(interaction: discord.Interaction, vps_id: str):
    uid = str(interaction.user.id)
    meta = DATA.get("vps", {}).get(vps_id)
    if not meta:
        await interaction.response.send_message("VPS not found.", ephemeral=True)
        return
    if meta["owner"] != uid and not is_admin(interaction.user.id):
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return

    info = get_vps_info(vps_id)
    if not info:
        await interaction.response.send_message("Backend info not found for this VPS.", ephemeral=True)
        return

    # Build status embed
    status = info.get("status", "unknown")
    embed = discord.Embed(title=f"Manage VPS `{vps_id}`", color=0x3498db)
    embed.add_field(name="Status", value=f"🟢 Running" if status == "running" else f"🔴 {status}", inline=False)
    embed.add_field(name="Memory", value=f"{meta.get('ram_mb')} MB", inline=True)
    embed.add_field(name="CPU", value=f"{meta.get('cpu_cores')} cores", inline=True)
    embed.add_field(name="Disk", value=f"{meta.get('disk_gb')} GB", inline=True)
    embed.add_field(name="Username", value=info.get("username", "root"), inline=True)
    embed.add_field(name="Created", value=meta.get("created", "unknown"), inline=True)
    embed.add_field(name="OS image", value=meta.get("image"), inline=False)
    embed.set_footer(text=f"Credits: {CREDITS} — Watching ArizNodes Cloud By Vasplayz90")

    # send ephemeral response and DM full details
    await interaction.response.send_message("Opening management DM with actions...", ephemeral=True)

    # DM with action instructions and examples
    user = interaction.user
    dm = (
        f"Manage VPS `{vps_id}`\n"
        f"Use these commands in server or DM:\n"
        f"/start_vps {vps_id}\n"
        f"/stop_vps {vps_id}\n"
        f"/restart_vps {vps_id}\n"
        f"/reinstall_vps {vps_id} <choice>\n\n"
        f"Reinstall choices: `docker` (default), `ubuntu_22_04`, `debian_12`, `chatgpt_choice`.\n\n"
        f"Example Status:\n"
        f"🟢 Running\n"
        f"Memory: {meta.get('ram_mb')}MB\n"
        f"CPU: {meta.get('cpu_cores')} cores\n"
        f"Disk: {meta.get('disk_gb')}GB\n"
        f"Username: {info.get('username','root')}\n"
        f"Created: {meta.get('created')}\n"
        f"OS: {meta.get('image')}\n"
    )

    try:
        await user.send(embed=embed)
        await user.send(dm)
    except discord.Forbidden:
        await interaction.followup.send("Cannot DM you — enable DMs from server members.", ephemeral=True)


# Operational commands for buttons
@bot.tree.command(name="start_vps", description="Start a stopped VPS")
@app_commands.describe(vps_id="VPS ID to start")
async def start_vps_cmd(interaction: discord.Interaction, vps_id: str):
    uid = str(interaction.user.id)
    meta = DATA.get("vps", {}).get(vps_id)
    if not meta:
        await interaction.response.send_message("VPS not found.", ephemeral=True)
        return
    if meta["owner"] != uid and not is_admin(interaction.user.id):
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    ok = start_vps(vps_id)
    await interaction.response.send_message("Started." if ok else "Failed to start.", ephemeral=True)


@bot.tree.command(name="stop_vps", description="Stop a running VPS")
@app_commands.describe(vps_id="VPS ID to stop")
async def stop_vps_cmd(interaction: discord.Interaction, vps_id: str):
    uid = str(interaction.user.id)
    meta = DATA.get("vps", {}).get(vps_id)
    if not meta:
        await interaction.response.send_message("VPS not found.", ephemeral=True)
        return
    if meta["owner"] != uid and not is_admin(interaction.user.id):
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    ok = stop_vps(vps_id)
    await interaction.response.send_message("Stopped." if ok else "Failed to stop.", ephemeral=True)


@bot.tree.command(name="restart_vps", description="Restart a VPS")
@app_commands.describe(vps_id="VPS ID to restart")
async def restart_vps_cmd(interaction: discord.Interaction, vps_id: str):
    uid = str(interaction.user.id)
    meta = DATA.get("vps", {}).get(vps_id)
    if not meta:
        await interaction.response.send_message("VPS not found.", ephemeral=True)
        return
    if meta["owner"] != uid and not is_admin(interaction.user.id):
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    ok = restart_vps(vps_id)
    await interaction.response.send_message("Restarted." if ok else "Failed to restart.", ephemeral=True)


@bot.tree.command(name="reinstall_vps", description="Reinstall OS on the VPS (owner/admin).")
@app_commands.describe(vps_id="VPS ID", choice="Choice: docker, ubuntu_22_04, debian_12, chatgpt_choice")
async def reinstall_vps_cmd(interaction: discord.Interaction, vps_id: str, choice: str):
    uid = str(interaction.user.id)
    meta = DATA.get("vps", {}).get(vps_id)
    if not meta:
        await interaction.response.send_message("VPS not found.", ephemeral=True)
        return
    if meta["owner"] != uid and not is_admin(interaction.user.id):
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return

    choice_map = {
        "docker": os.getenv("DEFAULT_IMAGE", DEFAULT_IMAGE),
        "ubuntu_22_04": "rastasheep/ubuntu-sshd:22.04",
        "debian_12": "rastasheep/debian-sshd:12",
        "chatgpt_choice": "ubuntu:22.04",
    }
    image = choice_map.get(choice.lower())
    if not image:
        await interaction.response.send_message("Invalid choice. Use: docker, ubuntu_22_04, debian_12, chatgpt_choice", ephemeral=True)
        return

    try:
        new_info = reinstall_vps(vps_id, image=image)
    except Exception as e:
        await interaction.response.send_message(f"Reinstall failed: {e}", ephemeral=True)
        return

    # update stored metadata
    DATA["vps"][vps_id]["image"] = image
    save_data()
    await interaction.response.send_message(f"Reinstalled {vps_id} with image `{image}`. Check DM for details.", ephemeral=True)
    try:
        await interaction.user.send(f"VPS {vps_id} reinstalled with image `{image}`. New access: {new_info.get('direct_conn','unknown')}")
    except discord.Forbidden:
        pass


@bot.tree.command(name="clear", description="Owner only: delete all VPS (dangerous).")
async def clear_cmd(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("Only owner can clear all VPS.", ephemeral=True)
        return
    vids = list(DATA.get("vps", {}).keys())
    failed = []
    for v in vids:
        if not delete_vps(v):
            failed.append(v)
        else:
            DATA["vps"].pop(v, None)
    save_data()
    await interaction.response.send_message(f"Cleared. Failed: {failed}", ephemeral=True)


if __name__ == "__main__":
    bot.run(TOKEN)
