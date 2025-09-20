import discord
import random
import datetime

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
        
        # Add status emoji based on current status
        status_emoji = "🟢" if self.status == "Running" else "🔴"
        embed.set_author(name=f"{status_emoji} {self.id} - {self.status}")
        
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
        return embed

    def get_short_info(self):
        status_emoji = "🟢" if self.status == "Running" else "🔴"
        return f"{status_emoji} {self.id} | {self.ram}GB RAM | {self.cpu} CPU | {self.disk}GB Disk | {self.os}"
