import json
import discord
from discord.ext import commands

def get_channel_id(guild_id, channel_name):
    with open('data/channel_ids.json', 'r') as f:
        data = json.load(f)
    guild_data = data.get(str(guild_id), {})
    return guild_data.get(channel_name)

class BoosterEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        booster_server_channel_id = get_channel_id(after.guild.id, 'booster_server_channel_id')
        if not booster_server_channel_id:
            print(f"ID kênh booster-server không tồn tại trong file channel_ids.json cho guild {after.guild.id}.")
            return

        log_channel = after.guild.get_channel(booster_server_channel_id)
        if not log_channel:
            print(f"Không tìm thấy kênh booster-server với ID {booster_server_channel_id} trong guild {after.guild.id}.")
            return

        # Check if the member started boosting
        if not before.premium_since and after.premium_since:
            embed = discord.Embed(
                title="Thành viên đã boost server!",
                description=f"{after.mention} đã bắt đầu boost server.\n#booster",
                color=discord.Color.purple()
            )
            embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)
            await log_channel.send(embed=embed)

        # Check if the member stopped boosting
        elif before.premium_since and not after.premium_since:
            embed = discord.Embed(
                title="Thành viên đã ngừng boost server!",
                description=f"{after.mention} đã ngừng boost server.\n#booster",
                color=discord.Color.dark_purple()
            )
            embed.set_footer(text="Log Status Created by Creative", icon_url=self.bot.user.avatar.url)
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BoosterEventsCog(bot))