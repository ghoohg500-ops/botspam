#!/usr/bin/env python3
import telebot
import subprocess
import sys
import time

# ================== CẤU HÌNH ==================
BOT_TOKEN = "7718251438:AAHtLy-axP3jLq1ce2JaTaCGhjgbRcNZV1A"

ADMIN_IDS = {
    123456789  # THAY ID TELEGRAM CỦA BẠN
}

COOLDOWN_SECONDS = 120
DEFAULT_LIMIT = 2
MAX_LIMIT = 2

BGMI_FILE = "bgmi.py"

bot = telebot.TeleBot(BOT_TOKEN)
last_used = {}

# ================== HÀM PHỤ ==================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def cooldown_left(user_id: int) -> int:
    if user_id not in last_used:
        return 0
    remain = COOLDOWN_SECONDS - int(time.time() - last_used[user_id])
    return max(0, remain)

# ================== /start ==================
@bot.message_handler(commands=["start"])
def start_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Bạn không có quyền sử dụng bot này.")
        return
    bot.reply_to(message, "✅ Bot đang hoạt động.")

# ================== /add ==================
@bot.message_handler(commands=["add"])
def add_admin(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Chỉ admin mới dùng được lệnh này.")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "❌ Dùng: /add <user_id>")
        return

    try:
        new_id = int(args[1])
    except ValueError:
        bot.reply_to(message, "❌ ID không hợp lệ.")
        return

    ADMIN_IDS.add(new_id)
    bot.reply_to(message, f"✅ Đã thêm admin: `{new_id}`")

# ================== /bgmi ==================
@bot.message_handler(commands=["bgmi"])
def bgmi_cmd(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.reply_to(message, "⛔ Bạn không phải admin.")
        return

    wait = cooldown_left(user_id)
    if wait > 0:
        bot.reply_to(message, f"⏳ Vui lòng chờ {wait}s trước khi dùng lại.")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Dùng: /bgmi <sdt> [số_lần]")
        return

    phone = args[1]

    try:
        times = int(args[2]) if len(args) >= 3 else DEFAULT_LIMIT
    except ValueError:
        bot.reply_to(message, "❌ Số lần phải là số.")
        return

    if times > MAX_LIMIT:
        times = MAX_LIMIT

    last_used[user_id] = time.time()

    bot.reply_to(
        message,
        f"🚀 Bắt đầu chạy `{BGMI_FILE}`\n"
        f"📱 SĐT: {phone}\n"
        f"🔁 Số lần: {times}"
    )

    # ========== THEO DÕI bgmi.py ==========
    try:
        process = subprocess.run(
            [sys.executable, BGMI_FILE, phone, str(times)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if process.returncode == 0:
            output = process.stdout.strip()
            bot.reply_to(
                message,
                "✅ HOÀN THÀNH\n"
                + (f"📄 Output:\n{output}" if output else "📄 Không có output.")
            )
        else:
            bot.reply_to(
                message,
                "❌ THẤT BẠI\n"
                f"⚠️ Lỗi:\n{process.stderr.strip()}"
            )

    except subprocess.TimeoutExpired:
        bot.reply_to(message, "❌ THẤT BẠI: bgmi.py chạy quá lâu (timeout).")
    except Exception as e:
        bot.reply_to(message, f"❌ THẤT BẠI: {e}")

# ================== CHẠY BOT ==================
print("Bot is running...")
bot.infinity_polling(skip_pending=True)
