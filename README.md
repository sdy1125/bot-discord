# DCS Creative BOT

DCS Creative BOT là một bot Discord mạnh mẽ với nhiều tính năng quản lý máy chủ, tăng cường tương tác người dùng và giải trí. Bot được tổ chức thành nhiều module khác nhau, mỗi module xử lý các chức năng riêng biệt.

## Cấu trúc dự án

```
project_root/
│
├── cogs/
│   ├── commands/
│   │   ├── admin/
│   │   │   ├── ban_unban.py
│   │   │   ├── clear.py
│   │   │   ├── mute_unmute.py
│   │   │   ├── reaction_role.py
│   │   │   ├── setup.py
│   │   │   ├── status.py
│   │   │   ├── cuop_emoji.py
│   │   │   ├── get_avatar.py
│   │   │   ├── help_command.py
│   │   │   ├── info_server.py
│   │   │   ├── info_user.py
│   │   │   ├── list_emoji.py
│   │   │   ├── ping.py
│   │   ├── events/
│   │   │   ├── ban.py
│   │   │   ├── booster_update.py
│   │   │   ├── bye.py
│   │   │   ├── counting.py
│   │   │   ├── member_update.py
│   │   │   ├── message_update.py
│   │   │   ├── server_update.py
│   │   │   ├── unban.py
│   │   │   ├── welcome.py
│   │   ├── utils/
│   │   │   ├── database_utils.py
│   │   ├── vc/
│   │   ├── voice/
│   │       ├── voice.py
│   ├── data/
│   │   ├── channel_ids.json
│   │   ├── database_utils.py
│   │   ├── playlists.db
│   │   ├── playlists.json
│   ├── utils/
│       ├── __init__.py
│       ├── common.py
│       ├── db.py
├── venv/
├── .env
├── main.py
├── readme.md
├── requirements.txt
├── Start.bat
```

## Tính năng

### Lệnh Quản trị viên
- `ban_unban.py`: Lệnh cấm và bỏ cấm người dùng.
- `clear.py`: Lệnh xóa tin nhắn.
- `mute_unmute.py`: Lệnh tắt và mở tiếng người dùng.
- `reaction_role.py`: Lệnh quản lý vai trò phản ứng.
- `setup.py`: Lệnh cài đặt ban đầu cho bot.
- `status.py`: Lệnh kiểm tra trạng thái của bot.
- `cuop_emoji.py`: Lệnh liên quan đến trộm emoji.
- `get_avatar.py`: Lệnh lấy avatar của người dùng.
- `help_command.py`: Lệnh trợ giúp tùy chỉnh.
- `info_server.py`: Lệnh lấy thông tin máy chủ.
- `info_user.py`: Lệnh lấy thông tin người dùng.
- `list_emoji.py`: Lệnh liệt kê tất cả emoji của máy chủ.
- `ping.py`: Lệnh kiểm tra độ trễ của bot.

### Sự kiện Listener
- `ban.py`: Listener cho sự kiện cấm người dùng.
- `booster_update.py`: Listener cho sự kiện tăng cường máy chủ.
- `bye.py`: Listener cho sự kiện người dùng rời đi.
- `counting.py`: Listener cho trò chơi đếm số.
- `member_update.py`: Listener cho sự kiện cập nhật thành viên.
- `message_update.py`: Listener cho sự kiện cập nhật tin nhắn.
- `server_update.py`: Listener cho sự kiện cập nhật máy chủ.
- `unban.py`: Listener cho sự kiện bỏ cấm người dùng.
- `welcome.py`: Listener chào mừng người dùng mới.

### Lệnh Tiện ích
- `common.py`: Các tiện ích chung được sử dụng trong bot.
- `db.py`: Các tiện ích cơ sở dữ liệu.

## Cài đặt và Thiết lập

1. **Clone repository:**
   ```sh
   git clone https://github.com/vnggodcreative/botdiscordpython.git
   cd botdiscordpython
   ```

2. **Tạo môi trường ảo:**
   ```sh
   python -m venv venv
   ```

3. **Kích hoạt môi trường ảo:**
   - Trên Windows:
     ```sh
     venv\Scripts\activate
     ```
   - Trên macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

4. **Cài đặt các gói phụ thuộc:**
   ```sh
   pip install -r requirements.txt
   ```

5. **Thiết lập các biến môi trường:**
   - Tạo tệp `.env` trong thư mục gốc của dự án và thêm các biến cấu hình của bạn (ví dụ: token bot, thông tin cơ sở dữ liệu).

6. **Chạy bot:**
   ```sh
   python main.py
   ```

## Quyền và Kiểm tra Vai trò

Bot sử dụng nhiều decorator để kiểm tra quyền và vai trò. Đảm bảo bạn đã thiết lập các vai trò và quyền cần thiết trong máy chủ Discord của bạn.

### Decorators
- `@commands.is_owner()`
- `@is_admin()`
- `@has_any_role(yeu_cau_roles)`
- `@has_any_role_or_owner(yeu_cau_roles)`
- `@has_permissions_or_owner(administrator=True)`
- `@commands.has_permissions(administrator=True)`
- `@commands.has_permissions(moderate_members=True)`
- `@commands.has_permissions(ban_members=True)`
- `@commands.has_permissions(kick_members=True)`
- `@commands.has_permissions(manage_emojis=True)`

### Hàm Kiểm tra Quyền
Đảm bảo các hàm sau được định nghĩa trong bot của bạn để xử lý kiểm tra quyền tùy chỉnh:

```python
def has_any_role_or_owner(role_ids):
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        for role_id in role_ids:
            role = discord.utils.get(ctx.author.roles, id=role_id)
            if role is không None:
                return True
        raise commands.MissingRole(role_ids)
    return commands.check(predicate)

def has_permissions_or_owner(**perms):
    async def predicate(ctx):
        if ctx.author.id == ctx.bot.owner_id:
            return True
        resolved = ctx.channel.permissions_for(ctx.author)
        return all(getattr(resolved, name, None) == value for name, value in perms.items())
    return commands.check(predicate)

def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)
```

## Đóng góp

Hãy thoải mái fork repository này, thực hiện các thay đổi, và gửi pull request. Mọi đóng góp đều được chào đón!

---

Cảm ơn bạn đã sử dụng DCS Creative BOT! Nếu bạn có bất kỳ câu hỏi nào hoặc cần trợ giúp, vui lòng liên hệ với [vnggodcreative@gmail.com](mailto:vnggodcreative@gmail.com).
