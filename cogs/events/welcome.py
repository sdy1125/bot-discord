import json
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BANNER_URL = os.getenv('BANNER_URL')

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_channel_id(self, guild_id, channel_name):
        with open('data/channel_ids.json', 'r') as f:
            data = json.load(f)
        guild_data = data.get(str(guild_id), {})
        return guild_data.get(channel_name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Sự kiện khi thành viên mới tham gia server."""

        # Tạo embed
        embed = discord.Embed(
            title="Chào mừng đến với server!",
            description=f"Xin chào {member.mention}, chào mừng bạn đến với server của chúng tôi! 👋",
            color=discord.Color.green()
        )

        # Thêm ảnh đại diện của thành viên
        embed.set_thumbnail(url=member.display_avatar.url)

        # Thêm URL ảnh từ BANNER_URL
        if BANNER_URL:
            embed.set_image(url=BANNER_URL)

        # Thêm footer với icon bot
        embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)

        # Lấy ID kênh welcome từ file channel_ids.json
        welcome_channel_id = self.get_channel_id(member.guild.id, "welcome_channel_id")
        if not welcome_channel_id:
            print(f"ID kênh welcome không tồn tại trong file channel_ids.json cho guild {member.guild.id}.")
            return

        # Lấy kênh welcome
        welcome_channel = member.guild.get_channel(welcome_channel_id)
        if not welcome_channel:
            print("Không tìm thấy kênh welcome.")
            return

        # Gửi thông báo vào kênh welcome
        await welcome_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))