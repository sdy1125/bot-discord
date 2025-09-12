import discord
from discord.ext import commands

class UserInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Hiển thị thông tin chi tiết về người dùng")
    async def userinfo(self, ctx, member: discord.Member):
        # Lấy URL avatar của user được tag với kích thước lớn nhất
        avatar_url = member.avatar.replace(format="png", size=1024).url

        # Lấy thông tin chi tiết của người dùng
        user_id = member.id
        username = member.name
        mention = member.mention
        joined_at = member.joined_at.strftime('%d/%m/%Y - %H:%M:%S')
        created_at = member.created_at.strftime('%d/%m/%Y - %H:%M:%S')
        roles = ' '.join([role.mention for role in member.roles[1:]])

        # Tạo embed cho thông tin của user được tag
        embed = discord.Embed(title=f"Thông tin của {username}")
        embed.set_thumbnail(url=avatar_url)  # Đặt avatar bên cạnh thẻ icon
        embed.set_author(name=username, icon_url=avatar_url)  # Đặt avatar bên cạnh thông tin người dùng

        # Thêm các trường thông tin vào embed
        embed.add_field(name="🆔 ID Người Dùng", value=user_id, inline=True)
        embed.add_field(name="👤 Tên Người Dùng", value=username, inline=True)
        embed.add_field(name="🏷️ Tên Discord", value=mention, inline=True)
        embed.add_field(name="📅 Ngày Tạo Tài Khoản", value=created_at, inline=True)
        embed.add_field(name="📅 Đã Tham Gia Nhóm", value=joined_at, inline=True)
        embed.add_field(name="📜 Vai Trò", value=roles, inline=False)

        # Gửi embed
        await ctx.send(embed=embed)

# Thiết lập để bot có thể load extension này
async def setup(bot):
    await bot.add_cog(UserInfoCog(bot))