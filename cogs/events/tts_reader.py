# cogs/tts_reader.py

import discord
from discord.ext import commands
from gtts import gTTS
import asyncio
import os

class TTSReader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.inactivity_timers = {}

    @commands.command(name="leavevc")
    async def leave_voice(self, ctx):
        """Bot rời voice channel"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.command(name="d")
    async def speak(self, ctx, *, message: str):
        """Bot tự vào voice channel và đọc tin nhắn"""
        if ctx.author.voice is None:
            return  # User không ở voice thì bỏ qua

        channel = ctx.author.voice.channel
        vc = ctx.voice_client

        # Nếu bot chưa vào thì join
        if not vc or not vc.is_connected():
            vc = await channel.connect()

        # Nếu bot ở kênh khác thì move
        elif vc.channel != channel:
            await vc.move_to(channel)

        # Nếu đang phát thì bỏ qua
        if vc.is_playing():
            return

        # Giới hạn tin nhắn
        if len(message) > 200:
            return

        try:
            tts = gTTS(text=message, lang="vi")
            tts.save("temp.mp3")

            vc.play(discord.FFmpegPCMAudio("temp.mp3"),
                    after=lambda e: os.remove("temp.mp3"))

            await ctx.message.add_reaction("🔊")

            # Reset timer
            await self.reset_inactivity_timer(ctx.guild.id, vc)

            while vc.is_playing():
                await asyncio.sleep(0.5)

        except Exception:
            pass  # Không nhả lỗi ra chat

    async def reset_inactivity_timer(self, guild_id, vc):
        """Tự rời sau 5 phút không hoạt động"""
        if guild_id in self.inactivity_timers:
            self.inactivity_timers[guild_id].cancel()

        async def timer():
            await asyncio.sleep(300)  # 5 phút
            if vc and vc.is_connected():
                await vc.disconnect()

        self.inactivity_timers[guild_id] = asyncio.create_task(timer())

async def setup(bot):
    await bot.add_cog(TTSReader(bot))
