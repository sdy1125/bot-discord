import discord
from discord.ext import commands
from datetime import datetime

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_cooldowns = {}
        self.COOLDOWN_SECONDS = 5  # Cooldown 5 giây cho lệnh

    def check_cooldown(self, user_id, command):
        if user_id not in self.command_cooldowns:
            self.command_cooldowns[user_id] = {}
        
        last_used = self.command_cooldowns[user_id].get(command, 0)
        current_time = datetime.now().timestamp()
        
        if current_time - last_used < self.COOLDOWN_SECONDS:
            return False
        
        self.command_cooldowns[user_id][command] = current_time
        return True

    @commands.command(name='avatar', aliases=['avt'])
    async def get_avatar(self, ctx, member: discord.Member = None):
        """Lấy avatar của bạn hoặc người dùng được đề cập."""
        user_id = str(ctx.author.id)
        if not self.check_cooldown(user_id, 'avatar'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {self.COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return

        # Nếu không đề cập người dùng, lấy avatar của người gửi lệnh
        member = member or ctx.author

        # Tạo Embed để hiển thị avatar
        embed = discord.Embed(
            title=f"\U0001F5BC Avatar của {member.display_name}",
            color=0x3498db
        )
        
        # Lấy URL avatar (ưu tiên avatar động nếu có)
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Yêu cầu bởi {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        # Gửi Embed
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Avatar(bot))
