#!/usr/bin/env python3
import telebot
import subprocess
import sys
import time

# ================== CẤU HÌNH ==================
BOT_TOKEN = "7657683464:AAFRJkE2iuClkecQTZgwpBj8G9LB8oAsnyU"

# ADMIN GỐC (ID Telegram của bạn)
ADMIN_IDS = {
    7497594902,   # <-- thay bằng ID của bạn
}

MAX_LIMIT = 2          # số lần tối đa
DEFAULT_LIMIT = 2      # số lần mặc định
COOLDOWN_SECONDS = 120 # 2 phút
# ==============================================

bot = telebot.TeleBot(BOT_TOKEN)

# Lưu thời gian dùng /bgmi lần cuối của từng admin
last_used = {}

# ---------- HÀM TIỆN ÍCH ----------
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def not_admin_reply(message):
    bot.reply_to(
        message,
        "Bot chỉ hoạt động với admin.\nBạn không có quyền sử dụng."
    )
# ---------------------------------

@bot.message_handler(commands=["start"])
def start_cmd(message):
    if not is_admin(message.from_user.id):
        not_admin_reply(message)
        return

    bot.reply_to(
        message,
        "Bot FAKE spam SMS (chỉ học tập)\n\n"
        "Lệnh:\n"
        "/bgmi <sdt> <so_lan>\n"
        "/add <telegram_id>\n\n"
        "Giới hạn: tối đa 2 lần\n"
        "Cooldown: 2 phút / mỗi admin"
    )

@bot.message_handler(commands=["add"])
def add_admin_cmd(message):
    if not is_admin(message.from_user.id):
        not_admin_reply(message)
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Cú pháp đúng:\n/add <telegram_id>")
        return

    try:
        new_admin = int(parts[1])
    except ValueError:
        bot.reply_to(message, "ID không hợp lệ.")
        return

    if new_admin in ADMIN_IDS:
        bot.reply_to(message, "ID này đã là admin.")
        return

    ADMIN_IDS.add(new_admin)
    bot.reply_to(message, f"Đã thêm admin: {new_admin}")

@bot.message_handler(commands=["bgmi"])
def bgmi_cmd(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        not_admin_reply(message)
        return

    now = time.time()

    # -------- COOLDOWN 2 PHÚT --------
    last = last_used.get(user_id, 0)
    remain = COOLDOWN_SECONDS - (now - last)
    if remain > 0:
        bot.reply_to(
            message,
            f"Vui lòng chờ {int(remain)} giây nữa mới dùng lại."
        )
        return
    # --------------------------------

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(
            message,
            "Ví dụ:\n/bgmi 0987654321 2"
        )
        return

    phone = parts[1]

    try:
        times = int(parts[2]) if len(parts) >= 3 else DEFAULT_LIMIT
    except ValueError:
        times = DEFAULT_LIMIT

    if times < 1:
        times = 1
    if times > MAX_LIMIT:
        times = MAX_LIMIT

    last_used[user_id] = now

    bot.reply_to(
        message,
        f"FAKE spam\nSố: {phone}\nSố lần: {times}"
    )

    try:
        result = subprocess.run(
            [sys.executable, "bgmi.py", phone, str(times)],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout.strip() or "Không có output"

        bot.reply_to(
            message,
            f"Kết quả:\n{output}"
        )

    except Exception as e:
        bot.reply_to(message, f"Lỗi khi chạy script:\n{e}")

print("Bot đang chạy...")
bot.infinity_polling()
