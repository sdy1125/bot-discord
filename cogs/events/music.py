import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import random

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': False,
    'noplaylist': True,
    'default_search': 'ytsearch',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'geo_bypass': True,
    'nocheckcertificate': True,
    'cookiefile': 'cookies.txt',  # Optional: Add cookies file
    # 'proxy': 'http://your-proxy:port',  # Uncomment and configure if needed
}

ffmpeg_options = {
    'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'executable': 'ffmpeg'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Song:
    def __init__(self, url, title):
        self.url = url
        self.title = title

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.now_playing = {}
        self.autoplay = {}

    def get_audio_source(self, query, retries=3):
        formats = ['bestaudio/best', '140', '251']
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.youtube.com/',
        }
        for attempt in range(retries):
            for fmt in formats:
                try:
                    ytdl_opts = ytdl_format_options.copy()
                    ytdl_opts['format'] = fmt
                    ytdl_opts['http_headers'] = headers
                    ytdl = youtube_dl.YoutubeDL(ytdl_opts)
                    info = ytdl.extract_info(query, download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    return Song(info['url'], info.get('title', 'Không rõ'))
                except Exception as e:
                    print(f"Lỗi khi lấy nguồn âm thanh (thử {attempt + 1}/{retries}, format {fmt}): {e}")
            asyncio.sleep(2)
        raise Exception(f"Không thể lấy nguồn âm thanh sau {retries} lần thử với tất cả định dạng.")

    async def search_related_song(self, ctx, current_song_title):
        try:
            search_query = f"ytsearch:{current_song_title} related"
            loop = asyncio.get_event_loop()
            song = await loop.run_in_executor(None, lambda: self.get_audio_source(search_query))
            await asyncio.sleep(1)
            return song
        except Exception as e:
            try:
                search_query = f"ytsearch:{current_song_title}"
                loop = asyncio.get_event_loop()
                song = await loop.run_in_executor(None, lambda: self.get_audio_source(search_query))
                await asyncio.sleep(1)
                return song
            except Exception as e2:
                await ctx.send(f"❌ Lỗi khi tìm bài hát liên quan: {e2}")
                return None

    async def ensure_queue(self, ctx):
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = asyncio.Queue()
        if ctx.guild.id not in self.autoplay:
            self.autoplay[ctx.guild.id] = False

    async def play_next(self, ctx, max_autoplay_attempts=3):
        queue = self.queues[ctx.guild.id]
        attempts = 0
        while queue.empty() and self.autoplay.get(ctx.guild.id, False) and attempts < max_autoplay_attempts:
            current_song = self.now_playing.get(ctx.guild.id)
            if current_song:
                related_song = await self.search_related_song(ctx, current_song.title)
                if related_song:
                    await queue.put(related_song)
                    await ctx.send(f"🔄 Autoplay: Đã thêm **{related_song.title}** vào hàng đợi.")
                else:
                    attempts += 1
            else:
                break

        if queue.empty():
            await ctx.send("✅ Hàng đợi đã hết.")
            self.now_playing[ctx.guild.id] = None
            if ctx.voice_client:
                ctx.voice_client.stop()
            return

        song = await queue.get()
        self.now_playing[ctx.guild.id] = song
        vc = ctx.voice_client
        if vc:
            try:
                source = discord.FFmpegPCMAudio(song.url, **ffmpeg_options)
                vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                await ctx.send(f"🎶 Đang phát: **{song.title}**")
            except Exception as e:
                await ctx.send(f"❌ Lỗi khi phát bài hát: {e}")
                if vc:
                    vc.stop()
                    print(f"Đã dừng voice client do lỗi: {e}")
        else:
            await ctx.send("❌ Bot không ở trong kênh thoại.")

    @commands.command(name='join')
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Bạn phải vào kênh thoại trước.")
            return
        try:
            await ctx.author.voice.channel.connect()
            await ctx.send("✅ Đã vào kênh thoại.")
        except discord.errors.ClientException:
            await ctx.send("❌ Bot đã ở trong kênh thoại rồi.")
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi vào kênh thoại: {e}")

    @commands.command(name='leave')
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Bot đã rời kênh.")
            self.queues.pop(ctx.guild.id, None)
            self.now_playing.pop(ctx.guild.id, None)
            self.autoplay.pop(ctx.guild.id, None)
        else:
            await ctx.send("❌ Bot không ở trong kênh thoại.")

    @commands.command(name='play')
    async def play(self, ctx, *, url: str):
        if not ctx.author.voice:
            await ctx.send("❌ Bạn phải vào kênh thoại trước.")
            return

        if not ctx.voice_client:
            try:
                await ctx.author.voice.channel.connect()
                await ctx.send("✅ Đã vào kênh thoại.")
            except Exception as e:
                await ctx.send(f"❌ Lỗi khi vào kênh thoại: {e}")
                return

        await self.ensure_queue(ctx)
        try:
            loop = asyncio.get_event_loop()
            song = await loop.run_in_executor(None, lambda: self.get_audio_source(url))
        except Exception as e:
            await ctx.send(f"❌ Không thể phát nhạc: {e}")
            return

        await self.queues[ctx.guild.id].put(song)
        await ctx.send(f"✅ Đã thêm vào hàng đợi: **{song.title}**")

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.command(name='pause')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Đã tạm dừng.")
        else:
            await ctx.send("❌ Không có bài nào đang phát.")

    @commands.command(name='resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Tiếp tục phát.")
        else:
            await ctx.send("❌ Không có bài nào bị tạm dừng.")

    @commands.command(name='skip')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Đã chuyển bài.")
        else:
            await ctx.send("❌ Không có bài nào đang phát.")

    @commands.command(name='queue')
    async def queue(self, ctx):
        await self.ensure_queue(ctx)
        queue = list(self.queues[ctx.guild.id]._queue)
        if not queue:
            await ctx.send("📭 Hàng đợi trống.")
        else:
            msg = "\n".join([f"{idx+1}. {song.title}" for idx, song in enumerate(queue)])
            await ctx.send(f"📃 Hàng đợi:\n{msg}")

    @commands.command(name='clear_m')
    async def clear(self, ctx):
        await self.ensure_queue(ctx)
        self.queues[ctx.guild.id] = asyncio.Queue()
        await ctx.send("🧹 Hàng đợi đã được xóa.")

    @commands.command(name='autoplay')
    async def autoplay_toggle(self, ctx):
        await self.ensure_queue(ctx)
        self.autoplay[ctx.guild.id] = not self.autoplay.get(ctx.guild.id, False)
        status = "bật" if self.autoplay[ctx.guild.id] else "tắt"
        await ctx.send(f"🔄 Autoplay đã được **{status}**.")

async def setup(bot):
    await bot.add_cog(Music(bot))
