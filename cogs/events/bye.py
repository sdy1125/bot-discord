import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BANNER_URL = os.getenv('BANNER_URL')

def get_channel_id(guild_id, channel_name):
    with open('data/channel_ids.json', 'r') as f:
        data = json.load(f)
    guild_data = data.get(str(guild_id), {})
    return guild_data.get(channel_name)

class ByeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_users = set()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Sự kiện khi thành viên rời khỏi server hoặc bị cấm."""

        if member.id in self.banned_users:
            # Tạo embed thông báo bị cấm
            embed = discord.Embed(
                title="Thành viên bị cấm",
                description=f"Thành viên {member.mention} đã bị cấm khỏi server.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            self.banned_users.remove(member.id)
        else:
            # Tạo embed thông báo rời khỏi server
            embed = discord.Embed(
                title="Thành viên đã rời khỏi server",
                description=f"Thành viên {member.mention} đã rời khỏi server. Chúng tôi sẽ nhớ bạn! 😢",
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url=member.display_avatar.url)

        # Thêm URL ảnh từ BANNER_URL
        if BANNER_URL:
            embed.set_image(url=BANNER_URL)

        # Thêm footer với icon bot
        embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

        # Lấy ID kênh goodbye cho máy chủ hiện tại
        goodbye_channel_id = get_channel_id(member.guild.id, 'goodbye_channel_id')
        if not goodbye_channel_id:
            print(f"ID kênh goodbye không tồn tại trong file channel_ids.json cho guild {member.guild.id}.")
            return

        # Lấy kênh goodbye
        goodbye_channel = member.guild.get_channel(goodbye_channel_id)
        if goodbye_channel:
            await goodbye_channel.send(embed=embed)
        else:
            print(f"Không tìm thấy kênh goodbye với ID {goodbye_channel_id} trong guild {member.guild.id}.")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Sự kiện khi thành viên bị cấm."""
        self.banned_users.add(user.id)

async def setup(bot):
    await bot.add_cog(ByeCog(bot))