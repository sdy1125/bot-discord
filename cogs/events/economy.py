import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
import re

DATA_FILE = "data/coins.json"
RP_DATA_FILE = 'data/rp_data.json'
SHOP_FILE = 'data/shop.json'
REWARD_MILESTONES = [100, 500, 1000, 2000, 5000]
COOLDOWN_SECONDS = 5  # Cooldown for commands

RP_CHANNELS = {
    'chat-rieng': 20,
    'event-rp': 30,
    'hoat-dong-rp': 25,
}

QUOTES = [
    "Đừng chạy theo thành công, hãy làm điều bạn yêu thích.",
    "Hôm nay là một ngày tuyệt vời để bắt đầu điều gì đó mới!",
    "Làm điều bạn yêu thích, và bạn sẽ không phải làm việc một ngày nào trong đời.",
    "Thành công không đến từ may mắn, mà từ sự kiên trì.",
    "Tớ là bot nhưng tớ cũng biết buồn đấy...",
    "Bạn không thể thay đổi quá khứ, nhưng bạn có thể bắt đầu từ hiện tại để tạo ra một kết thúc mới."
]

MEMES = [
    "https://i.redd.it/391eu1s8wn9e1.gif",
    "https://anhnail.vn/wp-content/uploads/2025/01/meme-bua-10.webp",
    "https://m.yodycdn.com/blog/anh-meme-cheems-yodyvn57.jpg",
    "https://i.makeagif.com/media/4-03-2020/JKM8oN.mp4",
    "https://maunhi.com/wp-content/uploads/2025/04/meme-tet-3.jpeg",
    "https://tapl.edu.vn/public/upload/2025/01/meme-viet-nam-09.webp",
    "https://tapl.edu.vn/public/upload/2025/01/meme-viet-nam-17.webp",
    "https://thuvienmeme.com/wp-content/uploads/2024/03/meo-luom-nguyt-nhieu-cai-tao-con-chua-them-noi-dau.jpg",
    "https://thuvienmeme.com/wp-content/uploads/2025/06/meme-tieng-viet-lop-1-viet-anh.jpg",
    "https://thuvienmeme.com/wp-content/uploads/2025/06/meme-anh-yeu-em-tien-mat.jpg"
]

SHOP_ITEMS = {
    "vip_role": {"name": "VIP Role", "price": 1000, "description": "Thẻ VIP đặc biệt 30 ngày"},
    "custom_nickname": {"name": "Custom Nickname", "price": 500, "description": "Đổi biệt danh tùy chỉnh"},
    "meme_pack": {"name": "Meme Pack", "price": 200, "description": "Gói 5 meme độc quyền"}
}

def load_json(path, default={}):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_json(DATA_FILE)
        self.rp_data = load_json(RP_DATA_FILE)
        self.shop_data = load_json(SHOP_FILE, SHOP_ITEMS)
        self.command_cooldowns = {}

    def get_balance(self, user_id):
        return self.data.get(str(user_id), {}).get("coins", 0)

    def set_balance(self, user_id, amount):
        user = self.data.setdefault(str(user_id), {})
        user["coins"] = max(0, amount)
        save_json(DATA_FILE, self.data)

    def can_claim_daily(self, user_id):
        user = self.data.setdefault(str(user_id), {})
        last_claim = user.get("last_daily")
        if not last_claim:
            return True
        try:
            last_time = datetime.fromisoformat(last_claim)
            return datetime.now() - last_time >= timedelta(hours=24)
        except ValueError:
            return True

    def check_cooldown(self, user_id, command):
        if user_id not in self.command_cooldowns:
            self.command_cooldowns[user_id] = {}
        
        last_used = self.command_cooldowns[user_id].get(command, 0)
        current_time = datetime.now().timestamp()
        
        if current_time - last_used < COOLDOWN_SECONDS:
            return False
        
        self.command_cooldowns[user_id][command] = current_time
        return True

    async def claim_daily(self, ctx):
        user_id = str(ctx.author.id)
        if not self.check_cooldown(user_id, 'daily'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return False
            
        if not self.can_claim_daily(user_id):
            next_claim = datetime.fromisoformat(self.data[user_id]["last_daily"]) + timedelta(hours=24)
            time_left = next_claim - datetime.now()
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            await ctx.send(f"\U0001F552 Bạn đã nhận quà hôm nay rồi! Hãy quay lại sau {hours}h {minutes}m nhé.")
            return False

        user_data = self.data.setdefault(user_id, {})
        user_data["last_daily"] = datetime.now().isoformat()
        user_data["coins"] = self.get_balance(user_id) + 100
        save_json(DATA_FILE, self.data)
        await ctx.send("\U0001F381 Bạn đã nhận **100 coins** hôm nay! Hẹn gặp lại vào ngày mai!")
        return True

    @commands.command(name='coin')
    async def check_coin(self, ctx, member: discord.Member = None):
        if not self.check_cooldown(str(ctx.author.id), 'coin'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        member = member or ctx.author
        balance = self.get_balance(str(member.id))
        embed = discord.Embed(
            title=f"\U0001F4B0 Ví của {member.display_name}",
            description=f"Hiện có **{balance} coins**",
            color=0xFFD700
        )
        await ctx.send(embed=embed)

    @commands.command(name='daily')
    async def daily_coin(self, ctx):
        await self.claim_daily(ctx)

    @commands.command(name='give')
    async def give_coin(self, ctx, member: discord.Member, amount: int):
        if not self.check_cooldown(str(ctx.author.id), 'give'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        giver_id = str(ctx.author.id)
        receiver_id = str(member.id)

        if giver_id == receiver_id:
            await ctx.send("\u274C Bạn không thể tự tặng coin cho mình!")
            return

        if amount <= 0:
            await ctx.send("\u274C Số lượng coin phải lớn hơn 0.")
            return

        if self.get_balance(giver_id) < amount:
            await ctx.send("\u274C Bạn không đủ coin để thực hiện giao dịch.")
            return

        self.set_balance(giver_id, self.get_balance(giver_id) - amount)
        self.set_balance(receiver_id, self.get_balance(receiver_id) + amount)

        embed = discord.Embed(
            title="\U0001F4B8 Giao Dịch Thành Công",
            description=f"{ctx.author.display_name} đã tặng **{amount} coins** cho {member.display_name}!",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name='topcoin')
    async def top_coin(self, ctx):
        if not self.check_cooldown(str(ctx.author.id), 'topcoin'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        top_users = sorted(self.data.items(), key=lambda x: x[1].get("coins", 0), reverse=True)[:10]
        if not top_users:
            await ctx.send("\U0001F4C4 Hiện chưa có ai trong bảng xếp hạng coin!")
            return
        embed = discord.Embed(title="\U0001F3C6 Bảng Xếp Hạng Coin", color=0xFFD700)
        for i, (user_id, user_data) in enumerate(top_users, 1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User ID {user_id}"
            coins = user_data.get("coins", 0)
            embed.add_field(name=f"{i}. {name}", value=f"{coins} coins", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="quote")
    async def quote(self, ctx):
        if not self.check_cooldown(str(ctx.author.id), 'quote'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
        embed = discord.Embed(
            title="\U0001F4AC Trích Dẫn",
            description=random.choice(QUOTES),
            color=0x3498db
        )
        await ctx.send(embed=embed)

    @commands.command(name="meme")
    async def meme(self, ctx):
        if not self.check_cooldown(str(ctx.author.id), 'meme'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
        await ctx.send(random.choice(MEMES))

    @commands.command(name="shop")
    async def shop(self, ctx):
        if not self.check_cooldown(str(ctx.author.id), 'shop'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        embed = discord.Embed(title="\U0001F6D2 Cửa Hàng", color=0xFF00FF)
        for item_id, item in self.shop_data.items():
            embed.add_field(
                name=f"{item['name']} - {item['price']} coins",
                value=item['description'],
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, *, item_name):
        if not self.check_cooldown(str(ctx.author.id), 'buy'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        user_id = str(ctx.author.id)
        item_id = None
        for key, item in self.shop_data.items():
            if item['name'].lower() == item_name.lower():
                item_id = key
                break

        if not item_id:
            await ctx.send("\u274C Không tìm thấy vật phẩm này trong cửa hàng!")
            return

        item = self.shop_data[item_id]
        balance = self.get_balance(user_id)
        if balance < item['price']:
            await ctx.send("\u274C Bạn không đủ coin để mua vật phẩm này!")
            return

        self.set_balance(user_id, balance - item['price'])
        embed = discord.Embed(
            title="\U0001F6D2 Mua Hàng Thành Công",
            description=f"Bạn đã mua **{item['name']}** với giá {item['price']} coins!",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
        try:
            await ctx.author.send(f"\U0001F389 Bạn đã mua {item['name']}! Vui lòng liên hệ admin để nhận vật phẩm.")
        except discord.Forbidden:
            await ctx.send(f"\U0001F4E9 Vui lòng mở DM để nhận thông báo mua hàng!")

    @commands.command(name="flip")
    async def flip(self, ctx, choice: str, amount: int):
        if not self.check_cooldown(str(ctx.author.id), 'flip'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return

        user_id = str(ctx.author.id)
        choice = choice.lower()
        if choice not in ['heads', 'tails', 'ngửa', 'sấp']:
            await ctx.send("\u274C Vui lòng chọn 'heads', 'tails', 'ngửa', hoặc 'sấp'!")
            return

        if amount <= 0:
            await ctx.send("\u274C Số coin cược phải lớn hơn 0!")
            return

        if self.get_balance(user_id) < amount:
            await ctx.send("\u274C Bạn không đủ coin để cược!")
            return

        result = random.choice(['heads', 'tails'])
        vietnamese_result = 'ngửa' if result == 'heads' else 'sấp'
        win = (choice in ['heads', 'ngửa'] and result == 'heads') or (choice in ['tails', 'sấp'] and result == 'tails')

        embed = discord.Embed(
            title="\U0001F3B2 Tung Đồng Xu",
            color=0xFFD700 if win else 0xFF0000
        )
        embed.add_field(name="Kết quả", value=f"Đồng xu ra **{vietnamese_result}**!", inline=False)

        if win:
            winnings = amount
            self.set_balance(user_id, self.get_balance(user_id) + winnings)
            embed.add_field(name="Kết quả cược", value=f"Bạn thắng **{winnings} coins**!", inline=False)
        else:
            self.set_balance(user_id, self.get_balance(user_id) - amount)
            embed.add_field(name="Kết quả cược", value=f"Bạn thua **{amount} coins**. Thử lại nhé!", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="gamble")
    async def gamble(self, ctx, amount: int):
        if not self.check_cooldown(str(ctx.author.id), 'gamble'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return

        user_id = str(ctx.author.id)
        if amount <= 0:
            await ctx.send("\u274C Số coin cược phải lớn hơn 0!")
            return

        if self.get_balance(user_id) < amount:
            await ctx.send("\u274C Bạn không đủ coin để cược!")
            return

        outcomes = [
            {"multiplier": 0, "chance": 0.40, "message": "Thua hết! May mắn lần sau nhé!"},
            {"multiplier": 0.5, "chance": 0.25, "message": "Thua một nửa, tiếc quá!"},
            {"multiplier": 1, "chance": 0.20, "message": "Hòa vốn, không mất không được!"},
            {"multiplier": 1.5, "chance": 0.10, "message": "Thắng lớn! Gấp rưỡi tiền cược!"},
            {"multiplier": 2, "chance": 0.05, "message": "JACKPOT! Gấp đôi tiền cược!"}
        ]

        rand = random.random()
        cumulative = 0
        for outcome in outcomes:
            cumulative += outcome["chance"]
            if rand <= cumulative:
                multiplier = outcome["multiplier"]
                message = outcome["message"]
                break

        winnings = int(amount * multiplier) - amount if multiplier > 0 else -amount
        new_balance = self.get_balance(user_id) + winnings
        self.set_balance(user_id, new_balance)

        embed = discord.Embed(
            title="\U0001F3B0 Cờ Bạc",
            description=message,
            color=0x00FF00 if winnings > 0 else 0xFF0000 if winnings < 0 else 0xFFFF00
        )
        embed.add_field(name="Số coin cược", value=f"{amount} coins", inline=True)
        embed.add_field(name="Kết quả", value=f"{winnings:+} coins", inline=True)
        embed.add_field(name="Số dư hiện tại", value=f"{new_balance} coins", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="le-tan")
    async def check_points(self, ctx):
        if not self.check_cooldown(str(ctx.author.id), 'le-tan'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        user_id = str(ctx.author.id)
        if user_id in self.rp_data:
            embed = discord.Embed(
                title="\U0001F4B3 Thẻ Thành Tích RP",
                description=f"Xin chào {ctx.author.display_name}, điểm RP hiện tại của bạn là:",
                color=0x3498db
            )
            embed.add_field(name="\U0001F4BC Điểm RP", value=f"{self.rp_data[user_id]['points']} điểm", inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("\u274C Bạn chưa có điểm RP nào trong hệ thống.")

    @commands.command(name='lich-su')
    async def view_history(self, ctx):
        if not self.check_cooldown(str(ctx.author.id), 'lich-su'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        user_id = str(ctx.author.id)
        if user_id in self.rp_data:
            history = self.rp_data[user_id].get('history', [])[-10:]
            if not history:
                await ctx.send("\U0001F4C4 Hiện chưa có lịch sử RP nào trong hồ sơ.")
                return
            lines = [f"- \U0001F539 [{h['time']}] tại '{h['channel']}' nhận +{h['points']} điểm" for h in history]
            embed = discord.Embed(title="\U0001F570 Lịch Sử RP Của Bạn", description="\n".join(lines), color=0x95a5a6)
            await ctx.send(embed=embed)
        else:
            await ctx.send("\U0001F4C4 Hiện chưa có lịch sử RP nào trong hồ sơ.")

    @commands.command(name='toprp')
    async def top_rp(self, ctx):
        if not self.check_cooldown(str(ctx.author.id), 'toprp'):
            await ctx.send(f"\U0001F552 Vui lòng đợi {COOLDOWN_SECONDS} giây trước khi dùng lệnh này!")
            return
            
        sorted_users = sorted(self.rp_data.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        if not sorted_users:
            await ctx.send("\U0001F4C4 Hiện chưa có ai trong bảng xếp hạng RP!")
            return
        embed = discord.Embed(title="\U0001F3C6 Bảng Xếp Hạng Khách Danh RP", color=0xFFD700)
        for i, (user_id, data) in enumerate(sorted_users, 1):
            embed.add_field(name=f"{i}. {data['name']}", value=f"\U0001F4BC {data['points']} điểm RP", inline=False)
        await ctx.send(embed=embed)

    async def check_milestones(self, user_id, member):
        user_points = self.rp_data[user_id]['points']
        for milestone in REWARD_MILESTONES:
            key = f"milestone_{milestone}"
            if user_points >= milestone and not self.rp_data[user_id].get(key):
                self.rp_data[user_id][key] = True
                save_json(RP_DATA_FILE, self.rp_data)
                try:
                    embed = discord.Embed(
                        title="\U0001F389 Chúc Mừng Đột Phá!",
                        description=f"Bạn đã đạt **{milestone} điểm RP** tại khách sạn! Hãy kiểm tra phần thưởng tại !shop",
                        color=0xFFAA00
                    )
                    await member.send(embed=embed)
                except discord.Forbidden:
                    print(f"Không thể gửi DM cho {member.name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        user_id = str(message.author.id)
        channel_name = message.channel.name
        msg_lower = message.content.lower()

        # Handle bot mentions
        if self.bot.user in message.mentions:
            responses = [
                "Hử? Có chuyện gì thế?",
                "Bạn muốn hỏi gì vậy?",
                "Bot đang online đây! Gọi tui có gì không?",
                "OwO? Bạn vừa nhắc đến mình à?"
            ]
            await message.channel.send(random.choice(responses))
            return  # Prevent double response with keywords

        # Handle keyword responses
        keywords = {
            "xin chào": ["Chào bạn!", "Chào nhé! Bot đang nghe đây."],
            "hello": ["Hello!", "Hi there!"],
            "coin": ["Bạn muốn kiểm tra coin à? Dùng !coin nhé!"],
            "buồn": ["Đừng buồn nữa mà... Có bot ở đây rồi!", "Buồn làm chi, vào !gamble vui hơn nè."],
            "meme": ["Gõ !meme để nhận hình hài hước nhé!"],
            "bot ngu": ["sao bằng bạn được"],
            "iu": ["say gex với a sdy"],
            "kama": ["là sinh vật đi bằng 4 chân của AOV và VGVD"],
            "chuoi": ["kẻ hủy diệt team mình, ngon từ mắt kiểm soát"],
            "hsi": ["ngu hết phần thiên hạ"],
            "clina": ["vợ yêu của tổng tài bá đạo"],
            "kdy" : ["kdy bi khunggg"],
            "minhh" :["cung goi la cute"]
        }

        for key, replies in keywords.items():
            if re.search(rf"\b{re.escape(key)}\b", msg_lower):
                await message.channel.send(random.choice(replies))
                return  # Prevent double response with RP points

        # Handle RP points
        if channel_name in RP_CHANNELS:
            points = RP_CHANNELS[channel_name]
            user_data = self.rp_data.get(user_id, {
                "name": message.author.display_name,
                "points": 0,
                "history": []
            })
            user_data["name"] = message.author.display_name
            user_data["points"] += points
            user_data["history"].append({
                "channel": channel_name,
                "points": points,
                "time": datetime.now().strftime('%Y-%m-%d %H:%M')
            })
            self.rp_data[user_id] = user_data
            save_json(RP_DATA_FILE, self.rp_data)
            await self.check_milestones(user_id, message.author)

       

async def setup(bot):
    await bot.add_cog(Economy(bot))
