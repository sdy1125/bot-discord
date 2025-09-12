import json
import discord
from discord.ext import commands

class ServerEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_channel_id(self, guild_id, channel_name):
        with open('data/channel_ids.json', 'r') as f:
            data = json.load(f)
        guild_data = data.get(str(guild_id), {})
        return guild_data.get(channel_name)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_channel_id = self.get_channel_id(channel.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {channel.guild.id}.")
            return

        log_channel = channel.guild.get_channel(log_channel_id)
        if not log_channel:
            print("Không tìm thấy kênh server-update.")
            return

        entry = None
        async for log in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if log.target.id == channel.id:
                entry = log
                break

        embed = discord.Embed(
            title="Kênh Mới Được Tạo",
            description=f"Kênh {channel.mention} đã được tạo.",
            color=discord.Color.green()
        )
        if entry:
            embed.set_footer(text=f"Người tạo: {entry.user}", icon_url=entry.user.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel_id = self.get_channel_id(channel.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {channel.guild.id}.")
            return

        log_channel = channel.guild.get_channel(log_channel_id)
        if not log_channel:
            print("Không tìm thấy kênh server-update.")
            return

        entry = None
        async for log in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            if log.target.id == channel.id:
                entry = log
                break

        embed = discord.Embed(
            title="Kênh Đã Bị Xóa",
            description=f"Kênh {channel.name} đã bị xóa.",
            color=discord.Color.red()
        )
        if entry:
            embed.set_footer(text=f"Người xóa: {entry.user}", icon_url=entry.user.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        log_channel_id = self.get_channel_id(after.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {after.guild.id}.")
            return

        log_channel = after.guild.get_channel(log_channel_id)
        if not log_channel:
            print("Không tìm thấy kênh server-update.")
            return

        entry = None
        async for log in after.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1):
            if log.target.id == after.id:
                entry = log
                break

        if before.name != after.name:
            embed = discord.Embed(
                title="Tên Kênh Đã Thay Đổi",
                description=f"Tên kênh đã được đổi từ {before.name} thành {after.mention}.",
                color=discord.Color.blue()
            )
            if entry:
                embed.set_footer(text=f"Người thay đổi: {entry.user}", icon_url=entry.user.avatar.url)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        log_channel_id = self.get_channel_id(role.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {role.guild.id}.")
            return

        log_channel = role.guild.get_channel(log_channel_id)
        if not log_channel:
            print("Không tìm thấy kênh server-update.")
            return

        entry = None
        async for log in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            if log.target.id == role.id:
                entry = log
                break

        embed = discord.Embed(
            title="Vai Trò Mới Được Tạo",
            description=f"Vai trò {role.mention} đã được tạo.",
            color=discord.Color.green()
        )
        if entry:
            embed.set_footer(text=f"Người tạo: {entry.user}", icon_url=entry.user.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        log_channel_id = self.get_channel_id(role.guild.id, "server_update_channel_id")
        if not log_channel_id:
            print(f"ID kênh server-update không tồn tại trong file channel_ids.json cho guild {role.guild.id}.")
            return

        log_channel = role.guild.get_channel(log_channel_id)
        if not log_channel:
            print("Không tìm thấy kênh server-update.")
            return

        entry = None
        async for log in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if log.target.id == role.id:
                entry = log
                break

        embed = discord.Embed(
            title="Vai Trò Đã Bị Xóa",
            description=f"Vai trò {role.name} đã bị xóa.",
            color=discord.Color.red()
        )
        if entry:
            embed.set_footer(text=f"Người xóa: {entry.user}", icon_url=entry.user.avatar.url)
        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerEventsCog(bot))