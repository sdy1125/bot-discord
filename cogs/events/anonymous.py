import discord
from discord.ext import commands
from datetime import datetime
import logging

class Anonymous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_cooldowns = {}
        self.COOLDOWN_SECONDS = 5  # Cooldown 5 giây
        self.ANONYMOUS_CHANNEL_ID = None  # Thay bằng ID kênh ẩn danh nếu muốn cố định kênh

    def check_cooldown(self, user_id, command):
        if user_id not in self.command_cooldowns:
            self.command_cooldowns[user_id] = {}
        
        last_used = self.command_cooldowns[user_id].get(command, 0)
        current_time = datetime.now().timestamp()
        
        if current_time - last_used < self.COOLDOWN_SECONDS:
            return False
        
        self.command_cooldowns[user_id][command] = current_time
        return True

    @commands.command(name='anonymous', aliases=['anon'])
    async def send_anonymous(self, ctx, *, message: str):
        """Gửi tin nhắn ẩn danh dưới dạng văn bản thông thường."""
        user_id = str(ctx.author.id)
        if not self.check_cooldown(user_id, 'anonymous'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {self.COOLDOWN_SECONDS} giây trước khi dùng lệnh này!", delete_after=5)
            return

        if not message:
            await ctx.send("\u274C Vui lòng cung cấp nội dung tin nhắn ẩn danh!", delete_after=5)
            return

        # Xóa tin nhắn lệnh của người dùng để giữ ẩn danh
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("\u274C Bot không có quyền xóa tin nhắn. Vui lòng cấp quyền **Manage Messages**.", delete_after=5)
            return

        # Gửi tin nhắn văn bản thuần túy
        target_channel = self.bot.get_channel(self.ANONYMOUS_CHANNEL_ID) if self.ANONYMOUS_CHANNEL_ID else ctx.channel
        if not target_channel:
            await ctx.send("\u274C Kênh ẩn danh không tồn tại! Vui lòng liên hệ admin.", delete_after=5)
            return

        try:
            await target_channel.send(message)  # Gửi tin nhắn dạng văn bản thông thường
            # Gửi xác nhận qua DM cho người gửi
            try:
                await ctx.author.send("\U0001F4E9 Tin nhắn ẩn danh của bạn đã được gửi thành công!")
            except discord.Forbidden:
                await ctx.send("\U0001F4E9 Tin nhắn ẩn danh đã được gửi, nhưng bot không thể gửi DM xác nhận. Vui lòng mở DM!", delete_after=5)
            # Ghi log cho admin
            logging.info(f"Anonymous message from {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}): {message}")
        except discord.Forbidden:
            await ctx.send("\u274C Bot không có quyền gửi tin nhắn trong kênh này. Vui lòng cấp quyền **Send Messages**.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Anonymous(bot))
