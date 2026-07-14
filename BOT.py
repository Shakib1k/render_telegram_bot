import os
import time
import uuid
import json
import logging
from datetime import datetime, timedelta
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import threading
import random
import sys
import signal
import hashlib

# =====================================================
#           🔐 এডমিন পাসওয়ার্ড সিস্টেম - অটো লগইন
# =====================================================

ADMIN_PASSWORD = "admin123"
ADMIN_PASSWORD_HASH = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()

SESSION_FILE = "admin_session.json"

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_session(data):
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

def verify_admin_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH

def is_admin_logged_in(user_id):
    if user_id in user_sessions:
        session = user_sessions[user_id]
        if session.get("logged_in", False):
            if session.get("remember", False):
                if datetime.now() - session["login_time"] <= timedelta(days=7):
                    return True
            elif datetime.now() - session["login_time"] <= timedelta(hours=1):
                return True

    saved = load_session()
    if str(user_id) in saved:
        session_data = saved[str(user_id)]
        if session_data.get("logged_in", False):
            login_time = datetime.fromisoformat(session_data["login_time"])
            if datetime.now() - login_time <= timedelta(days=7):
                user_sessions[user_id] = {
                    "logged_in": True,
                    "login_time": login_time,
                    "remember": True,
                    "auto_login": True
                }
                return True
    return False

def login_admin(user_id, password, remember=False):
    if verify_admin_password(password):
        user_sessions[user_id] = {
            "logged_in": True,
            "login_time": datetime.now(),
            "remember": remember,
            "auto_login": remember
        }
        if remember:
            saved = load_session()
            saved[str(user_id)] = {
                "logged_in": True,
                "login_time": datetime.now().isoformat(),
                "remember": True
            }
            save_session(saved)
        return True
    return False

def logout_admin(user_id):
    if user_id in user_sessions:
        user_sessions[user_id] = {"logged_in": False, "login_time": None, "remember": False, "auto_login": False}
    saved = load_session()
    if str(user_id) in saved:
        del saved[str(user_id)]
        save_session(saved)
    return True

user_sessions = {}

BOT_NAME = "SHAKIB"
BOT_NAME_STYLE = "✨ 𝐒𝐇𝐀𝐊𝐈𝐁 ✨"

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logging.warning("gTTS ইনস্টল নেই।")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("Pillow ইনস্টল নেই।")

# =====================================================
#           🎬 প্রিমিয়াম অ্যানিমেশন ফাংশন
# =====================================================

def premium_loading_animation(duration=3):
    """প্রিমিয়াম লোডিং অ্যানিমেশন"""
    chars = ["✦", "✧", "⭐", "🌟", "✨", "💫"]
    colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
    reset = '\033[0m'
    bold = '\033[1m'

    os.system('clear' if os.name == 'posix' else 'cls')

    for i in range(duration * 10):
        color = colors[i % len(colors)]
        char = chars[i % len(chars)]
        progress = "█" * (i % 10) + "░" * (10 - (i % 10))
        sys.stdout.write(f'\r{color}{bold}╔═══════════════════════════════════════╗{reset}')
        sys.stdout.write(f'\n\r{color}{bold}║  {char} {BOT_NAME} BOT LOADING {char}  ║{reset}')
        sys.stdout.write(f'\n\r{color}{bold}║  [{progress}] {i*10}%        ║{reset}')
        sys.stdout.write(f'\n\r{color}{bold}╚═══════════════════════════════════════╝{reset}')
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\r\033[K')
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()

def premium_rose_animation():
    """প্রিমিয়াম গোলাপ অ্যানিমেশন"""
    roses = [
        "  🌹  ",
        " 🌹🌹 ",
        "🌹🌹🌹",
        " 🌹🌹 ",
        "  🌹  "
    ]
    colors = ['\033[91m', '\033[93m', '\033[95m', '\033[96m', '\033[94m']
    reset = '\033[0m'
    bold = '\033[1m'

    for _ in range(3):
        for j, rose in enumerate(roses):
            color = colors[j % len(colors)]
            sys.stdout.write(f'\r{color}{bold}  ✨ {rose} ✨  {reset}')
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 20 + '\r')
    sys.stdout.flush()

def premium_sparkle_effect():
    """প্রিমিয়াম স্পার্কল এফেক্ট"""
    sparkles = ["✨", "⭐", "🌟", "💫", "🔥"]
    colors = ['\033[93m', '\033[96m', '\033[94m', '\033[95m', '\033[91m']
    reset = '\033[0m'
    bold = '\033[1m'

    for i in range(6):
        sparkle = sparkles[i % len(sparkles)]
        color = colors[i % len(colors)]
        text = f"{sparkle}  {BOT_NAME} BOT ACTIVE  {sparkle}"
        sys.stdout.write(f'\r{color}{bold}{text.center(50)}{reset}')
        sys.stdout.flush()
        time.sleep(0.15)
    sys.stdout.write('\r' + ' ' * 50 + '\r')
    sys.stdout.flush()

def premium_bot_off():
    """প্রিমিয়াম বট অফ অ্যানিমেশন"""
    os.system('clear' if os.name == 'posix' else 'cls')

    for i in range(3):
        emojis = ["🔴", "🟡", "🟢"]
        sys.stdout.write(f'\r\033[91m● {emojis[i]} SHAKIB BOT STOPPING {emojis[i]} ●\033[0m')
        sys.stdout.flush()
        time.sleep(0.3)

    print("\n")

    final_msg = f"""
\033[96m╔═══════════════════════════════════════╗
║                                           ║
║        ✨ \033[93m{BOT_NAME} Bot Off ✨\033[96m              ║
║                                           ║
║     \033[91m● Bot Stopped Successfully ●\033[96m       ║
║     \033[92m● Thanks for using {BOT_NAME} Bot ●\033[96m    ║
║                                           ║
╠═══════════════════════════════════════╣
║                                           ║
║   \033[93m🔴 Bot is currently OFF\033[96m                ║
║                                           ║
║   \033[95m🚀 To Start Bot Again, Type:\033[96m           ║
║   \033[93m   python3 bot.py\033[96m                      ║
║   \033[95m   OR\033[96m                                  ║
║   \033[93m   python bot.py\033[96m                       ║
║                                           ║
║   \033[92m💡 Or just type: ON\033[96m                    ║
║                                           ║
╚═══════════════════════════════════════╝\033[0m
"""
    print(final_msg)
    print(f"\n\033[92m✅ Bot Off Successfully!\033[0m")
    print(f"\033[96m📌 To restart, type: \033[93mpython3 bot.py\033[0m")
    print(f"\033[96m💡 Or type \033[92mON\033[96m to restart automatically\033[0m")
    print(f"\n\033[93m⏳ Waiting for command...\033[0m")

    while True:
        try:
            cmd = input(f"\n\033[96m➜ Enter command (ON to start): \033[0m").strip().upper()
            if cmd == "ON":
                restart_bot()
                break
            elif cmd == "EXIT" or cmd == "QUIT":
                print(f"\n\033[91m❌ Exiting...\033[0m")
                sys.exit(0)
            else:
                print(f"\033[91m❌ Unknown command! Type 'ON' to start the bot or 'EXIT' to quit.\033[0m")
        except KeyboardInterrupt:
            print(f"\n\033[91m❌ Exited.\033[0m")
            sys.exit(0)
        except Exception as e:
            print(f"\033[91m❌ Error: {e}\033[0m")

def restart_bot():
    print(f"\n\033[92m🚀 Restarting {BOT_NAME} Bot...\033[0m")
    time.sleep(1)
    python = sys.executable
    os.execl(python, python, *sys.argv)

def signal_handler(sig, frame):
    premium_bot_off()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# -------------------- কনফিগারেশন --------------------
BOT_TOKEN = "8864999864:AAGuROjCe5Fx44yFfe6Lxy-IRX0ppcEZ4MY"
ADMIN_ID = 7058712225
DB_FILE = "bot_database.json"
LOG_FILE = "bot_activity.log"
BACKUP_INTERVAL = 300  # প্রতি ৫ মিনিটে ব্যাকআপ

# রেন্ডারের জন্য পোর্ট সেটআপ
PORT = int(os.environ.get('PORT', 8080))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RED = '\033[91m'
PURPLE = '\033[95m'

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    premium_rose_animation()
    time.sleep(0.3)
    premium_loading_animation(2)
    time.sleep(0.3)
    premium_sparkle_effect()
    time.sleep(0.3)

    print(f"{PURPLE}{BOLD}")
    print("╔═══════════════════════════════════════╗")
    print("║                                       ║")
    print("║      ✨ 𝐒 𝐇 𝐀 𝐊 𝐈 𝐁 ✨            ║")
    print("║                                       ║")
    print("║    🚀 PREMIUM BOT v3.0               ║")
    print("║    ☑ API Layer 214 Compatible        ║")
    print("║    🔐 Auto Login System Active       ║")
    print("║    📁 File Name Feature Active       ║")
    print("║    ✨ Premium UI & Animations        ║")
    print("║                                       ║")
    print("╚═══════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"\n{GREEN}✅ Bot is Ready!{RESET}")
    print(f"{YELLOW}🔐 Admin Password: {ADMIN_PASSWORD}{RESET}")
    print(f"{CYAN}💡 Press Ctrl+C to stop{RESET}\n")

bot = telebot.TeleBot(BOT_TOKEN)

# -------------------- ডেটাবেস ম্যানেজমেন্ট --------------------
def get_default_db():
    return {
        "file_database": {},
        "registered_users": [],
        "banned_users": [],
        "user_activity": {},
        "user_ranks": {},
        "bot_settings": {
            "force_join": True,
            "chat_link_1": "https://t.me/your_group_1",
            "chat_link_2": "https://t.me/your_group_2",
            "dynamic_channels": {},
            "custom_commands": {},
            "maintenance_mode": False,
            "welcome_message": f"✨ Welcome to {BOT_NAME} Premium Bot! ✨",
            "auto_delete": False,
            "delete_after": 60,
            "log_channel": None,
            "auto_reply": {},
            "referral_bonus": 5,
            "daily_reward": 10,
            "sub_admins": [],
            "admin_password": ADMIN_PASSWORD_HASH
        },
        "scheduled_messages": [],
        "giveaway": {"active": False, "prize": "", "participants": [], "end_time": None, "winners": []},
        "poll_data": {},
        "referrals": {},
        "user_wallets": {},
        "pending_approvals": []
    }

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_db = get_default_db()

                for key in default_db:
                    if key not in data:
                        data[key] = default_db[key]
                for key in default_db["bot_settings"]:
                    if key not in data["bot_settings"]:
                        data["bot_settings"][key] = default_db["bot_settings"][key]
                for key in default_db["giveaway"]:
                    if key not in data["giveaway"]:
                        data["giveaway"][key] = default_db["giveaway"][key]
                return data
        except Exception as e:
            logger.error(f"ডেটাবেস লোড করতে ব্যর্থ: {e}")
            # ব্যাকআপ থেকে রিস্টোর করার চেষ্টা
            if os.path.exists(f"{DB_FILE}.backup"):
                try:
                    with open(f"{DB_FILE}.backup", "r", encoding="utf-8") as f:
                        return json.load(f)
                except:
                    pass
            return get_default_db()
    return get_default_db()

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # ব্যাকআপ ফাইল সেভ
        with open(f"{DB_FILE}.backup", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logger.info("ডেটাবেস সেভ করা হয়েছে")
    except Exception as e:
        logger.error(f"ডেটাবেস সেভ করতে ব্যর্থ: {e}")

db = load_db()
file_database = db["file_database"]
registered_users = set(db["registered_users"])
banned_users = set(db.get("banned_users", []))
user_activity = db.get("user_activity", {})
user_ranks = db.get("user_ranks", {})
bot_settings = db["bot_settings"]
scheduled_messages = db.get("scheduled_messages", [])
giveaway = db.get("giveaway", {"active": False, "prize": "", "participants": [], "end_time": None, "winners": []})
user_wallets = db.get("user_wallets", {})
referrals = db.get("referrals", {})
pending_approvals = db.get("pending_approvals", [])
user_states = {}

data_lock = threading.Lock()

def sync_db():
    with data_lock:
        db["file_database"] = file_database
        db["registered_users"] = list(registered_users)
        db["banned_users"] = list(banned_users)
        db["user_activity"] = user_activity
        db["user_ranks"] = user_ranks
        db["bot_settings"] = bot_settings
        db["scheduled_messages"] = scheduled_messages
        db["giveaway"] = giveaway
        db["user_wallets"] = user_wallets
        db["referrals"] = referrals
        db["pending_approvals"] = pending_approvals
        save_db(db)

def auto_backup():
    """স্বয়ংক্রিয় ব্যাকআপ থ্রেড"""
    while True:
        try:
            time.sleep(BACKUP_INTERVAL)
            sync_db()
            logger.info("Auto-backup completed")
        except Exception as e:
            logger.error(f"Auto-backup error: {e}")

def log_user_activity(user_id, action):
    with data_lock:
        if user_id not in user_activity:
            user_activity[user_id] = {"total_actions": 0, "last_active": None, "actions": [], "points": 0, "rank": "Member"}

        user_activity[user_id]["total_actions"] += 1
        user_activity[user_id]["last_active"] = datetime.now().isoformat()

        if len(user_activity[user_id]["actions"]) >= 50:
            user_activity[user_id]["actions"].pop(0)
        user_activity[user_id]["actions"].append({
            "action": action,
            "time": datetime.now().isoformat()
        })

        if "points" not in user_activity[user_id]:
            user_activity[user_id]["points"] = 0

        if action not in ["voice_generated", "daily_reward"]:
            user_activity[user_id]["points"] += 1

        points = user_activity[user_id]["points"]
        if points >= 100:
            user_activity[user_id]["rank"] = "💎 Diamond"
        elif points >= 50:
            user_activity[user_id]["rank"] = "🥇 Gold"
        elif points >= 25:
            user_activity[user_id]["rank"] = "🥈 Silver"
        elif points >= 10:
            user_activity[user_id]["rank"] = "🥉 Bronze"

    sync_db()

    log_channel = bot_settings.get("log_channel")
    if log_channel:
        try:
            bot.send_message(
                log_channel,
                f"📝 **Activity Log**\n👤 User: `{user_id}`\n⚡ Action: `{action}`\n🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="Markdown"
            )
        except:
            pass

def is_user_banned(user_id):
    return user_id in banned_users

def check_user_membership(user_id):
    if not bot_settings["force_join"]:
        return True

    links_to_check = [bot_settings["chat_link_1"], bot_settings["chat_link_2"]]

    if "dynamic_channels" in bot_settings:
        for ch_id, ch_info in bot_settings["dynamic_channels"].items():
            links_to_check.append(ch_info["link"])

    for channel in links_to_check:
        if not channel or "your_group" in channel:
            continue
        try:
            chat_target = channel
            if "t.me/" in channel:
                parts = channel.split("t.me/")[-1].replace("+", "").split("/")
                chat_target = "@" + parts[0] if parts[0] else channel

            member = bot.get_chat_member(chat_target, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logger.error(f"চ্যানেল চেক করতে সমস্যা: {e}")
            return False
    return True

# -------------------- কিবোর্ড --------------------
def get_join_keyboard(file_id_param=None):
    markup = InlineKeyboardMarkup(row_width=2)
    join_buttons = []

    if bot_settings["chat_link_1"]:
        join_buttons.append(InlineKeyboardButton(text="📢 Join Channel 1", url=bot_settings["chat_link_1"]))
    if bot_settings["chat_link_2"]:
        join_buttons.append(InlineKeyboardButton(text="📢 Join Channel 2", url=bot_settings["chat_link_2"]))

    if join_buttons:
        markup.row(*join_buttons)

    if "dynamic_channels" in bot_settings:
        for ch_id, ch_info in bot_settings["dynamic_channels"].items():
            markup.add(InlineKeyboardButton(
                text=f"📢 {ch_info['name']}",
                url=ch_info["link"]
            ))

    callback_data = f"verify_{file_id_param}" if file_id_param else "check_verification"
    markup.add(InlineKeyboardButton(text="✅ Verify & Continue", callback_data=callback_data))

    return markup

def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🎙️ Voice"),
        KeyboardButton("📊 Stats"),
        KeyboardButton("🎁 Daily Reward")
    )
    markup.add(
        KeyboardButton("ℹ️ Help"),
        KeyboardButton("👤 Profile"),
        KeyboardButton("🏆 Leaderboard")
    )
    return markup

def get_login_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔑 Login as Admin", callback_data="admin_login"),
        InlineKeyboardButton("👤 Continue as User", callback_data="continue_as_user")
    )
    markup.add(
        InlineKeyboardButton("💾 Save & Auto-Login", callback_data="admin_login_save")
    )
    return markup

def get_admin_panel_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    auto_status = "🔄 Auto-Login: ✅ ON" if is_admin_logged_in(ADMIN_ID) else "🔄 Auto-Login: ❌ OFF"
    markup.add(InlineKeyboardButton(text=auto_status, callback_data="auto_login_status"))

    status_text = "✅ Force Join: ON" if bot_settings["force_join"] else "❌ Force Join: OFF"
    markup.add(InlineKeyboardButton(text=status_text, callback_data="toggle_force_join"))
    maint_status = "🛠️ Maintenance: ON" if bot_settings.get("maintenance_mode", False) else "🛠️ Maintenance: OFF"
    markup.add(InlineKeyboardButton(text=maint_status, callback_data="toggle_maintenance"))
    auto_delete_status = "🗑️ Auto-Delete: ON" if bot_settings.get("auto_delete", False) else "🗑️ Auto-Delete: OFF"
    markup.add(InlineKeyboardButton(text=auto_delete_status, callback_data="toggle_auto_delete"))
    markup.add(
        InlineKeyboardButton("🔗 Change Link 1", callback_data="change_link_1"),
        InlineKeyboardButton("🔗 Change Link 2", callback_data="change_link_2")
    )
    markup.add(
        InlineKeyboardButton("➕ Add Channel", callback_data="admin_add_dynamic_channel"),
        InlineKeyboardButton("📋 Manage Channels", callback_data="admin_manage_dynamic_channels")
    )
    markup.add(
        InlineKeyboardButton("🔑 Create Secret Key", callback_data="admin_create_key"),
        InlineKeyboardButton("📋 View Files", callback_data="admin_view_files"),
        InlineKeyboardButton("🗑️ Delete File", callback_data="admin_delete_file"),
        InlineKeyboardButton("🔑 View Keys Count", callback_data="admin_view_keys_count")
    )
    markup.add(
        InlineKeyboardButton("🛠️ Custom Commands", callback_data="admin_custom_commands")
    )
    markup.add(
        InlineKeyboardButton("👥 View Users", callback_data="admin_view_users"),
        InlineKeyboardButton("⛔ Ban User", callback_data="admin_ban_user"),
        InlineKeyboardButton("✅ Unban User", callback_data="admin_unban_user")
    )
    markup.add(
        InlineKeyboardButton("🎁 Giveaway", callback_data="admin_giveaway"),
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton("📝 Auto Reply", callback_data="admin_auto_reply"),
        InlineKeyboardButton("📅 Schedule Message", callback_data="admin_schedule")
    )
    markup.add(
        InlineKeyboardButton("📊 Bot Stats", callback_data="view_stats"),
        InlineKeyboardButton("📋 Settings", callback_data="view_settings"),
        InlineKeyboardButton("📝 Set Log Channel", callback_data="admin_set_log_channel"),
        InlineKeyboardButton("👑 Manage Admins", callback_data="admin_manage_admins")
    )
    markup.add(
        InlineKeyboardButton("🚪 Logout", callback_data="admin_logout"),
        InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")
    )
    return markup

def get_user_panel_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
        InlineKeyboardButton("🎁 Daily Reward", callback_data="daily_reward"),
        InlineKeyboardButton("ℹ️ Help", callback_data="user_help"),
        InlineKeyboardButton("🔗 Referral Link", callback_data="get_referral")
    )
    return markup

# -------------------- ফাইল সেন্ডিং ফাংশন --------------------
def send_target_file(chat_id, file_key):
    if file_key in file_database:
        data_item = file_database[file_key]

        if data_item.get("is_text_key"):
            panel_name = data_item.get("panel_name", "CUSTOM PANEL")
            secret_value = data_item.get("secret_value", "NO KEY SET")

            custom_panel_msg = (
                "╔════════════════════════════╗\n"
                f"║  🔐 {panel_name} 🔐\n"
                "╠════════════════════════════╣\n"
                "║  ✅ Verification Successful!\n"
                "║  Your Secret Key:\n"
                "║\n"
                f"║  `{secret_value}`\n"
                "║\n"
                "║  📋 Tap the button below to copy\n"
                "╚════════════════════════════╝"
            )

            copy_markup = InlineKeyboardMarkup()
            copy_markup.add(InlineKeyboardButton("📋 Click to Copy Secret Key", callback_data=f"copy_val|{secret_value}"))

            sent_msg = bot.send_message(chat_id, custom_panel_msg, parse_mode="Markdown", reply_markup=copy_markup)
            log_user_activity(chat_id, "secret_key_accessed")

            if bot_settings.get("auto_delete", False):
                delete_after = bot_settings.get("delete_after", 60)
                threading.Timer(delete_after, lambda: delete_message_safe(chat_id, sent_msg.message_id)).start()
            return True
        else:
            f_id = data_item["file_id"]
            f_type = data_item["file_type"]
            file_name = data_item.get("file_name", f"file_{file_key[:8]}")

            success_msg = (
                "╔════════════════════════════╗\n"
                "║  ✅ Verification Successful!\n"
                f"║  📁 File: {file_name}\n"
                "║  Your file is ready\n"
                "╚════════════════════════════╝"
            )
            sent_msg = bot.send_message(chat_id, success_msg, reply_markup=get_main_keyboard())

            try:
                if f_type == 'document':
                    bot.send_document(chat_id, f_id)
                elif f_type == 'photo':
                    bot.send_photo(chat_id, f_id)
                elif f_type == 'video':
                    bot.send_video(chat_id, f_id)
                elif f_type == 'audio':
                    bot.send_audio(chat_id, f_id)

                log_user_activity(chat_id, f"file_accessed_{f_type}")

                if bot_settings.get("auto_delete", False):
                    delete_after = bot_settings.get("delete_after", 60)
                    threading.Timer(delete_after, lambda: delete_message_safe(chat_id, sent_msg.message_id)).start()
                return True
            except Exception as e:
                logger.error(f"ফাইল সেন্ডিং এরর: {e}")
                bot.send_message(chat_id, "❌ ফাইল পাঠাতে সমস্যা হয়েছে।")
    else:
        bot.send_message(
            chat_id,
            "❌ এই লিংকটি সচল নয় অথবা ফাইলটি ডেটাবেজ থেকে মুছে ফেলা হয়েছে।",
            reply_markup=get_main_keyboard()
        )
    return False

def delete_message_safe(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

def check_giveaway():
    if giveaway.get("active") and giveaway.get("end_time"):
        try:
            end_time = datetime.fromisoformat(giveaway["end_time"])
            if datetime.now() >= end_time:
                participants = giveaway.get("participants", [])
                if participants:
                    winner = random.choice(participants)
                    prize = giveaway.get("prize", "Prize")

                    if "winners" not in giveaway:
                        giveaway["winners"] = []
                    giveaway["winners"].append({"user_id": winner, "prize": prize, "time": datetime.now().isoformat()})

                    bot.send_message(
                        ADMIN_ID,
                        f"🎉 **Giveaway Ended!**\n🏆 Winner: `{winner}`\n🎁 Prize: {prize}"
                    )

                    try:
                        bot.send_message(
                            winner,
                            f"🎉 **Congratulations!**\nYou won the giveaway!\n🎁 Prize: {prize}\nContact admin to claim."
                        )
                    except:
                        pass

                giveaway["active"] = False
                giveaway["participants"] = []
                giveaway["end_time"] = None
                sync_db()
        except Exception as e:
            logger.error(f"Giveaway check error: {e}")

# =====================================================
#           📝 বট কমান্ড হ্যান্ডলার
# =====================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    if is_user_banned(user_id):
        bot.send_message(chat_id, "⛔ You have been banned from using this bot!")
        return

    if user_id != ADMIN_ID and bot_settings.get("maintenance_mode", False):
        bot.send_message(chat_id, "🔧 Bot is under maintenance. Please try again later.")
        return

    user_states[chat_id] = None

    command_args = message.text.split()
    if len(command_args) > 1 and command_args[1].startswith("ref_"):
        try:
            referrer_id = int(command_args[1].replace("ref_", ""))
            if referrer_id != user_id and user_id not in registered_users:
                if "referrals" not in db:
                    db["referrals"] = {}
                if str(referrer_id) not in db["referrals"]:
                    db["referrals"][str(referrer_id)] = []
                if user_id not in db["referrals"][str(referrer_id)]:
                    db["referrals"][str(referrer_id)].append(user_id)
                    sync_db()
                    bot.send_message(referrer_id, f"🎉 New referral! {first_name} used your link.")
        except:
            pass

    if user_id not in registered_users:
        registered_users.add(user_id)
        log_user_activity(user_id, "registered")
        sync_db()

    file_key = command_args[1] if len(command_args) > 1 and not command_args[1].startswith("ref_") else None

    if user_id == ADMIN_ID:
        if is_admin_logged_in(user_id):
            admin_msg = (
                "╔════════════════════════════╗\n"
                f"║  👋 Welcome {BOT_NAME} Admin!\n"
                "║  🛠️ Bot Control Panel\n"
                "╠════════════════════════════╣\n"
                "║  🔑 Create Secret Keys\n"
                "║  📁 Manage Files\n"
                "║  👥 Manage Users\n"
                "║  📊 View Stats\n"
                "║  🔄 Auto-Login Active\n"
                "╚════════════════════════════╝"
            )
            bot.send_message(chat_id, admin_msg, parse_mode="Markdown", reply_markup=get_admin_panel_keyboard())
        else:
            login_msg = (
                "╔════════════════════════════╗\n"
                "║  🔐 Admin Login Required!\n"
                "╠════════════════════════════╣\n"
                "║  Please login to access\n"
                "║  the admin panel.\n"
                "║  Use the buttons below:\n"
                "║  • Normal Login (1 hour)\n"
                "║  • Save & Auto-Login (7 days)\n"
                "╚════════════════════════════╝"
            )
            bot.send_message(chat_id, login_msg, parse_mode="Markdown", reply_markup=get_login_keyboard())
        return

    if check_user_membership(user_id):
        if file_key:
            send_target_file(chat_id, file_key)
        else:
            welcome_msg = bot_settings.get("welcome_message", f"Welcome to {BOT_NAME} Premium Bot!")
            bot.send_message(
                chat_id,
                f"╔════════════════════════════╗\n"
                f"║  ✨ {welcome_msg}\n"
                f"║  Hello {first_name}! 👋\n"
                f"║  How can I help you today?\n"
                f"╚════════════════════════════╝",
                reply_markup=get_main_keyboard()
            )
    else:
        bot.send_message(
            chat_id,
            f"╔════════════════════════════╗\n"
            f"║  🔒 Access Restricted!\n"
            f"║  Please join our channels\n"
            f"║  to use this bot.\n"
            f"╚════════════════════════════╝",
            parse_mode="Markdown",
            reply_markup=get_join_keyboard(file_key)
        )

# -------------------- ইনলাইন বাটন হ্যান্ডলার --------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    message_id = call.message.message_id

    if is_user_banned(user_id) and user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ You are banned!", show_alert=True)
        return

    if call.data.startswith("copy_val|"):
        text_to_copy = call.data.split("copy_val|", 1)[1]
        bot.answer_callback_query(call.id, text=f"✅ Copied to clipboard!\n\n{text_to_copy}", show_alert=True)
        return

    if call.data == "admin_login":
        user_states[chat_id] = "waiting_for_admin_password"
        bot.send_message(chat_id, "🔑 Enter admin password (1 hour session):")
        bot.answer_callback_query(call.id)
        return

    if call.data == "admin_login_save":
        user_states[chat_id] = "waiting_for_admin_password_save"
        bot.send_message(chat_id, "🔑 Enter admin password (Saved for 7 days):")
        bot.answer_callback_query(call.id)
        return

    if call.data == "auto_login_status":
        status = "🔄 Auto-Login is ✅ ON\n⏰ Valid for 7 days" if is_admin_logged_in(user_id) else "🔄 Auto-Login is ❌ OFF"
        bot.answer_callback_query(call.id, status, show_alert=True)
        return

    if call.data == "continue_as_user":
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, "👤 You are continuing as a regular user.", reply_markup=get_main_keyboard())
        bot.answer_callback_query(call.id)
        return

    if call.data == "admin_logout":
        if logout_admin(user_id):
            bot.answer_callback_query(call.id, "✅ Logged out! Auto-login cleared.")
            bot.edit_message_text(
                "🚪 You have been logged out.\n🔐 Auto-login session cleared.",
                chat_id,
                message_id
            )
        else:
            bot.answer_callback_query(call.id, "❌ You were not logged in!")
        return

    if call.data.startswith("verify_"):
        file_key = call.data.split("verify_")[-1]
        if check_user_membership(user_id):
            bot.delete_message(chat_id, message_id)
            if file_key and file_key != "None":
                send_target_file(chat_id, file_key)
            else:
                bot.send_message(chat_id, "✅ Verification Successful! You can now use the bot.", reply_markup=get_main_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Please join all channels first!", show_alert=True)
        return

    if call.data == "check_verification":
        if check_user_membership(user_id):
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, "✅ Verification Successful!", reply_markup=get_main_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ Please join all channels first!", show_alert=True)
        return

    if call.data == "my_stats":
        if user_id in user_activity:
            stats = user_activity[user_id]
            points = stats.get("points", 0)
            rank = stats.get("rank", "Member")
            msg = (
                f"📊 **Your Stats:**\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🔄 Total Actions: `{stats['total_actions']}`\n"
                f"⭐ Points: `{points}`\n"
                f"🏅 Rank: `{rank}`\n"
                f"📅 Last Active: `{stats['last_active'][:10] if stats['last_active'] else 'N/A'}`"
            )
        else:
            msg = "📊 No activity recorded yet."
        bot.send_message(chat_id, msg, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if call.data == "daily_reward":
        today = datetime.now().date().isoformat()
        if "last_daily" in user_activity.get(user_id, {}):
            last_daily = user_activity[user_id].get("last_daily", "")
            if last_daily == today:
                bot.answer_callback_query(call.id, "❌ You already claimed today's reward!", show_alert=True)
                return

        if user_id not in user_activity:
            user_activity[user_id] = {"points": 0}
        user_activity[user_id]["points"] = user_activity[user_id].get("points", 0) + bot_settings.get("daily_reward", 10)
        user_activity[user_id]["last_daily"] = today
        sync_db()
        log_user_activity(user_id, "daily_reward")
        bot.answer_callback_query(call.id, f"🎁 You got {bot_settings.get('daily_reward', 10)} points!")
        return

    if call.data == "get_referral":
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        ref_count = len(db.get("referrals", {}).get(str(user_id), []))
        bonus = bot_settings.get("referral_bonus", 5)
        msg = (
            f"🔗 **Your Referral Link:**\n"
            f"`{ref_link}`\n\n"
            f"📊 Total Referrals: `{ref_count}`\n"
            f"🎁 Bonus per Referral: `{bonus}` points"
        )
        bot.send_message(chat_id, msg, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if call.data == "user_help":
        help_msg = (
            "╔════════════════════════════╗\n"
            f"║  ✨ {BOT_NAME} Bot Commands\n"
            "╠════════════════════════════╣\n"
            "║  🎙️ Voice - Text to Voice\n"
            "║  📊 Stats - Your activity\n"
            "║  🎁 Daily Reward - Get points\n"
            "║  🏆 Leaderboard - Top users\n"
            "║  👤 Profile - Your info\n"
            "║  🔗 Referral - Invite friends\n"
            "╚════════════════════════════╝"
        )
        bot.send_message(chat_id, help_msg)
        bot.answer_callback_query(call.id)
        return

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
        return

    if not is_admin_logged_in(user_id):
        bot.answer_callback_query(call.id, "🔐 Please login first!", show_alert=True)
        bot.send_message(chat_id, "🔐 Please login to access admin features.", reply_markup=get_login_keyboard())
        return

    # -------------------- অ্যাডমিন কমান্ডস --------------------
    if call.data == "toggle_force_join":
        bot_settings["force_join"] = not bot_settings["force_join"]
        sync_db()
        status = "ON" if bot_settings["force_join"] else "OFF"
        bot.answer_callback_query(call.id, f"Force Join turned {status}!")
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_admin_panel_keyboard())

    elif call.data == "toggle_maintenance":
        bot_settings["maintenance_mode"] = not bot_settings.get("maintenance_mode", False)
        sync_db()
        status = "ON" if bot_settings["maintenance_mode"] else "OFF"
        bot.answer_callback_query(call.id, f"Maintenance mode turned {status}!")
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_admin_panel_keyboard())

    elif call.data == "toggle_auto_delete":
        bot_settings["auto_delete"] = not bot_settings.get("auto_delete", False)
        sync_db()
        status = "ON" if bot_settings["auto_delete"] else "OFF"
        bot.answer_callback_query(call.id, f"Auto-Delete turned {status}!")
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_admin_panel_keyboard())

    elif call.data == "admin_view_keys_count":
        bot.answer_callback_query(call.id)
        secret_keys = {k: v for k, v in file_database.items() if v.get("is_text_key", False)}

        if not secret_keys:
            bot.send_message(chat_id, "🔑 **No Secret Keys found!**", parse_mode="Markdown")
            return

        total = len(secret_keys)
        bot.send_message(chat_id, f"🔑 **Total Secret Keys:** `{total}`", parse_mode="Markdown")

        bot_info = bot.get_me()
        for key, data in secret_keys.items():
            share_link = f"https://t.me/{bot_info.username}?start={key}"
            info_text = (
                f"🔑 **{data.get('panel_name', 'Unnamed')}**\n"
                f"🆔 ID: `{key}`\n"
                f"🔗 Link: `{share_link}`"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🗑️ Delete", callback_data=f"inline_delete_{key}"))
            bot.send_message(chat_id, info_text, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)
        return

    elif call.data == "admin_giveaway":
        bot.answer_callback_query(call.id)
        markup = InlineKeyboardMarkup(row_width=2)
        if giveaway.get("active"):
            markup.add(InlineKeyboardButton("🛑 End Giveaway", callback_data="admin_end_giveaway"))
            status = f"🟢 Active\n🎁 Prize: {giveaway.get('prize', 'N/A')}\n👥 Participants: {len(giveaway.get('participants', []))}"
        else:
            markup.add(
                InlineKeyboardButton("🎁 Start Giveaway", callback_data="admin_start_giveaway"),
                InlineKeyboardButton("📋 List Winners", callback_data="admin_list_winners")
            )
            status = "🔴 Inactive"
        bot.edit_message_text(
            f"🎁 **Giveaway Management**\n\nStatus: {status}",
            chat_id,
            message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif call.data == "admin_list_winners":
        bot.answer_callback_query(call.id)
        winners = giveaway.get("winners", [])
        if not winners:
            bot.send_message(chat_id, "❌ No winners yet!")
            return

        msg = "🏆 **Previous Winners:**\n━━━━━━━━━━━━━━━━\n"
        for i, w in enumerate(winners[-10:], 1):
            msg += f"{i}. User: `{w.get('user_id', 'Unknown')}`\n   🎁 {w.get('prize', 'Prize')}\n"

        bot.send_message(chat_id, msg, parse_mode="Markdown")

    elif call.data == "admin_start_giveaway":
        user_states[chat_id] = "waiting_for_giveaway_prize"
        bot.send_message(chat_id, "🎁 Enter the prize for giveaway:")
        bot.answer_callback_query(call.id)

    elif call.data == "admin_end_giveaway":
        if giveaway.get("active"):
            participants = giveaway.get("participants", [])
            if participants:
                winner = random.choice(participants)
                prize = giveaway.get("prize", "Prize")

                if "winners" not in giveaway:
                    giveaway["winners"] = []
                giveaway["winners"].append({"user_id": winner, "prize": prize, "time": datetime.now().isoformat()})

                bot.send_message(
                    chat_id,
                    f"🎉 **Giveaway Ended!**\n🏆 Winner: `{winner}`\n🎁 Prize: {prize}"
                )
                try:
                    bot.send_message(
                        winner,
                        f"🎉 **Congratulations!**\nYou won the giveaway!\n🎁 Prize: {prize}\nContact admin to claim."
                    )
                except:
                    pass
                giveaway["active"] = False
                giveaway["participants"] = []
                giveaway["end_time"] = None
                sync_db()
                bot.answer_callback_query(call.id, "✅ Giveaway ended!")
            else:
                giveaway["active"] = False
                giveaway["participants"] = []
                giveaway["end_time"] = None
                sync_db()
                bot.answer_callback_query(call.id, "❌ No participants!")

    elif call.data == "admin_auto_reply":
        bot.answer_callback_query(call.id)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("➕ Add Auto Reply", callback_data="admin_add_auto_reply"),
            InlineKeyboardButton("📋 List Auto Replies", callback_data="admin_list_auto_reply"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
        )
        bot.edit_message_text("📝 **Auto Reply Management**", chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "admin_add_auto_reply":
        user_states[chat_id] = "waiting_for_auto_reply_keyword"
        bot.send_message(chat_id, "📝 Enter the keyword for auto-reply:")
        bot.answer_callback_query(call.id)

    elif call.data == "admin_list_auto_reply":
        auto_reply = bot_settings.get("auto_reply", {})
        if not auto_reply:
            bot.send_message(chat_id, "❌ No auto-replies set.")
            bot.answer_callback_query(call.id)
            return

        for keyword, reply in auto_reply.items():
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_auto_reply|{keyword}"))
            bot.send_message(chat_id, f"🔹 `{keyword}`\n📝 {reply}", parse_mode="Markdown", reply_markup=markup)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("delete_auto_reply|"):
        keyword = call.data.split("delete_auto_reply|")[-1]
        if "auto_reply" in bot_settings and keyword in bot_settings["auto_reply"]:
            del bot_settings["auto_reply"][keyword]
            sync_db()
            bot.answer_callback_query(call.id, f"✅ Auto-reply `{keyword}` deleted!")
            bot.delete_message(chat_id, message_id)

    elif call.data == "admin_schedule":
        bot.answer_callback_query(call.id)
        user_states[chat_id] = "waiting_for_schedule_message"
        bot.send_message(chat_id, "📅 Enter scheduled message:\nFormat: `message|YYYY-MM-DD HH:MM`\nExample: Hello|2026-06-24 14:30")

    elif call.data == "admin_manage_admins":
        bot.answer_callback_query(call.id)
        admins = bot_settings.get("sub_admins", [])
        admins_list = "\n".join([f"• `{admin}`" for admin in admins]) if admins else "None"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("➕ Add Admin", callback_data="admin_add_admin"),
            InlineKeyboardButton("🗑️ Remove Admin", callback_data="admin_remove_admin"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
        )
        bot.edit_message_text(
            f"👑 **Admin Management**\n\n**Current Admins:**\n{admins_list}",
            chat_id,
            message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif call.data == "admin_add_admin":
        user_states[chat_id] = "waiting_for_add_admin"
        bot.send_message(chat_id, "👑 Enter user ID to add as admin:")
        bot.answer_callback_query(call.id)

    elif call.data == "admin_remove_admin":
        user_states[chat_id] = "waiting_for_remove_admin"
        bot.send_message(chat_id, "👑 Enter user ID to remove from admin:")
        bot.answer_callback_query(call.id)

    elif call.data in ["change_link_1", "change_link_2", "admin_create_key",
                      "admin_delete_file", "admin_broadcast", "admin_add_dynamic_channel",
                      "admin_ban_user", "admin_unban_user", "admin_set_log_channel"]:
        mapping = {
            "change_link_1": ("waiting_for_link_1", "📝 Enter new Group Link 1:"),
            "change_link_2": ("waiting_for_link_2", "📝 Enter new Group Link 2:"),
            "admin_create_key": ("waiting_for_panel_name", "📝 Enter panel name:"),
            "admin_delete_file": ("waiting_for_delete_key", "🗑️ Enter file ID to delete:"),
            "admin_broadcast": ("waiting_for_broadcast", "📢 Enter broadcast message:"),
            "admin_add_dynamic_channel": ("waiting_for_dynamic_ch_name", "📝 Enter channel name:"),
            "admin_ban_user": ("waiting_for_ban_user", "⛔ Enter user ID to ban:"),
            "admin_unban_user": ("waiting_for_unban_user", "✅ Enter user ID to unban:"),
            "admin_set_log_channel": ("waiting_for_log_channel", "📝 Enter channel ID or username for logs:")
        }
        state, msg = mapping[call.data]
        user_states[chat_id] = state
        bot.send_message(chat_id, msg)
        bot.answer_callback_query(call.id)

    # কাস্টম কমান্ড ম্যানেজমেন্ট
    elif call.data == "admin_custom_commands":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("➕ Add Custom Command", callback_data="admin_add_custom_cmd"),
            InlineKeyboardButton("📋 List Custom Commands", callback_data="admin_list_custom_cmd"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
        )
        bot.edit_message_text("🛠️ **Custom Commands Management**", chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
        bot.answer_callback_query(call.id)

    elif call.data == "admin_add_custom_cmd":
        user_states[chat_id] = "waiting_for_custom_cmd_name"
        bot.send_message(chat_id, "📝 Enter the command word (without '/'):\n(e.g., `hello`)")
        bot.answer_callback_query(call.id)

    elif call.data == "admin_list_custom_cmd":
        cmds = bot_settings.get("custom_commands", {})
        if not cmds:
            bot.send_message(chat_id, "❌ No custom commands added yet.")
            bot.answer_callback_query(call.id)
            return

        for cmd, resp in cmds.items():
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_custom_cmd|{cmd}"))
            bot.send_message(chat_id, f"🔹 `/{cmd}`\n📝 {resp}", parse_mode="Markdown", reply_markup=markup)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("delete_custom_cmd|"):
        cmd = call.data.split("delete_custom_cmd|")[-1]
        if "custom_commands" in bot_settings and cmd in bot_settings["custom_commands"]:
            del bot_settings["custom_commands"][cmd]
            sync_db()
            bot.answer_callback_query(call.id, f"✅ Command `{cmd}` deleted!")
            bot.delete_message(chat_id, message_id)
        else:
            bot.answer_callback_query(call.id, "❌ Command not found!")

    elif call.data == "admin_manage_dynamic_channels":
        bot.answer_callback_query(call.id)
        if not bot_settings.get("dynamic_channels"):
            bot.send_message(chat_id, "❌ No custom channels found!")
            return

        bot.send_message(chat_id, "📋 **Your Custom Channels:**")
        for ch_id, ch_info in bot_settings["dynamic_channels"].items():
            info_text = f"📛 **Name:** {ch_info['name']}\n🔗 **Link:** {ch_info['link']}"
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("✏️ Edit Link", callback_data=f"edit_dyn_link_{ch_id}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_dyn_ch_{ch_id}")
            )
            bot.send_message(chat_id, info_text, reply_markup=markup)

    elif call.data == "admin_view_users":
        bot.answer_callback_query(call.id)
        users_list = list(registered_users)
        if not users_list:
            bot.send_message(chat_id, "❌ No registered users!")
            return

        msg = f"👥 **Total Users:** `{len(users_list)}`\n\n"
        for i, uid in enumerate(users_list[:20], 1):
            try:
                user = bot.get_chat(uid)
                name = user.first_name or "Unknown"
                msg += f"{i}. {name} - `{uid}`\n"
            except:
                msg += f"{i}. Unknown - `{uid}`\n"

        if len(users_list) > 20:
            msg += f"\n... and {len(users_list) - 20} more"

        bot.send_message(chat_id, msg, parse_mode="Markdown")

    elif call.data == "admin_view_files":
        bot.answer_callback_query(call.id)
        if not file_database:
            bot.send_message(chat_id, "❌ No files in database!")
            return

        bot_info = bot.get_me()
        bot.send_message(chat_id, "📋 **Stored Files & Keys:**")

        for key, data in file_database.items():
            share_link = f"https://t.me/{bot_info.username}?start={key}"
            if data.get("is_text_key"):
                info_text = f"🔑 **Secret Key Panel**\n📛 Name: {data['panel_name']}\n🆔 ID: `{key}`\n🔗 Link: `{share_link}`"
            else:
                file_name = data.get("file_name", f"file_{key[:8]}")
                info_text = f"📁 **File**\n📛 Name: `{file_name}`\n🆔 ID: `{key}`\n🔗 Link: `{share_link}`"

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🗑️ Delete", callback_data=f"inline_delete_{key}"))
            bot.send_message(chat_id, info_text, parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("inline_delete_"):
        target_key = call.data.split("inline_delete_")[-1]
        if target_key in file_database:
            del file_database[target_key]
            sync_db()
            bot.answer_callback_query(call.id, "✅ File deleted!")
            bot.delete_message(chat_id, message_id)
        else:
            bot.answer_callback_query(call.id, "❌ File not found!")

    elif call.data.startswith("edit_dyn_link_"):
        ch_id = call.data.split("edit_dyn_link_")[-1]
        user_states[chat_id] = f"waiting_for_edit_dyn_link||{ch_id}"
        bot.send_message(chat_id, "✏️ Enter the new link for this channel:")
        bot.answer_callback_query(call.id)

    elif call.data.startswith("delete_dyn_ch_"):
        ch_id = call.data.split("delete_dyn_ch_")[-1]
        if "dynamic_channels" in bot_settings and ch_id in bot_settings["dynamic_channels"]:
            del bot_settings["dynamic_channels"][ch_id]
            sync_db()
            bot.answer_callback_query(call.id, "✅ Channel deleted!")
            bot.delete_message(chat_id, message_id)
        else:
            bot.answer_callback_query(call.id, "❌ Channel not found!")

    elif call.data == "view_stats":
        dyn_count = len(bot_settings.get("dynamic_channels", {}))
        cmd_count = len(bot_settings.get("custom_commands", {}))
        keys_count = sum(1 for v in file_database.values() if v.get("is_text_key", False))
        sub_admins = len(bot_settings.get("sub_admins", []))
        total_points = sum(u.get("points", 0) for u in user_activity.values())
        stats_text = (
            f"📊 **Bot Statistics:**\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👥 Total Users: `{len(registered_users)}`\n"
            f"📁 Total Files: `{len(file_database)}`\n"
            f"🔑 Secret Keys: `{keys_count}`\n"
            f"🔗 Custom Channels: `{dyn_count}`\n"
            f"🛠️ Custom Commands: `{cmd_count}`\n"
            f"⛔ Banned Users: `{len(banned_users)}`\n"
            f"👑 Sub-Admins: `{sub_admins}`\n"
            f"⭐ Total Points: `{total_points}`"
        )
        bot.send_message(chat_id, stats_text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    elif call.data == "view_settings":
        status_join = "✅ ON" if bot_settings["force_join"] else "❌ OFF"
        settings_text = (
            f"📋 **Current Settings:**\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🔐 Force Join: {status_join}\n"
            f"🛠️ Maintenance: {'ON' if bot_settings.get('maintenance_mode', False) else 'OFF'}\n"
            f"🗑️ Auto-Delete: {'ON' if bot_settings.get('auto_delete', False) else 'OFF'}\n"
            f"⏱️ Delete After: {bot_settings.get('delete_after', 60)} seconds\n"
            f"🔗 Link 1: {bot_settings['chat_link_1']}\n"
            f"🔗 Link 2: {bot_settings['chat_link_2']}\n"
            f"💬 Welcome Message: {bot_settings.get('welcome_message', 'Default')}\n"
            f"📝 Log Channel: {bot_settings.get('log_channel', 'Not set')}\n"
            f"🎁 Daily Reward: {bot_settings.get('daily_reward', 10)} points\n"
            f"🔗 Referral Bonus: {bot_settings.get('referral_bonus', 5)} points"
        )

        if bot_settings.get("dynamic_channels"):
            settings_text += "\n\n➕ **Extra Channels:**"
            for ch_id, ch_info in bot_settings["dynamic_channels"].items():
                settings_text += f"\n🔹 {ch_info['name']}: {ch_info['link']}"

        if bot_settings.get("custom_commands"):
            settings_text += "\n\n🛠️ **Custom Commands:**"
            for cmd, resp in bot_settings["custom_commands"].items():
                settings_text += f"\n🔹 /{cmd} → {resp[:50]}{'...' if len(resp)>50 else ''}"

        if bot_settings.get("auto_reply"):
            settings_text += "\n\n📝 **Auto Replies:**"
            for keyword, reply in bot_settings["auto_reply"].items():
                settings_text += f"\n🔹 {keyword} → {reply[:30]}{'...' if len(reply)>30 else ''}"

        bot.send_message(chat_id, settings_text, disable_web_page_preview=True)
        bot.answer_callback_query(call.id)

    elif call.data == "back_to_main":
        if user_id == ADMIN_ID and is_admin_logged_in(user_id):
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_admin_panel_keyboard())
        else:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_user_panel_keyboard())
        bot.answer_callback_query(call.id)

# -------------------- ফাইল আপলোড হ্যান্ডলার --------------------
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'voice'])
def handle_admin_files(message):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to upload files!")
        return

    if not is_admin_logged_in(user_id):
        bot.send_message(message.chat.id, "🔐 Please login first!", reply_markup=get_login_keyboard())
        return

    file_id, file_type, file_name = None, None, None

    if message.document:
        file_id = message.document.file_id
        file_type = 'document'
        file_name = message.document.file_name or f"document_{uuid.uuid4().hex[:6]}"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'photo'
        file_name = f"image_{uuid.uuid4().hex[:6]}.jpg"
    elif message.video:
        file_id = message.video.file_id
        file_type = 'video'
        file_name = message.video.file_name or f"video_{uuid.uuid4().hex[:6]}.mp4"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = 'audio'
        file_name = message.audio.file_name or f"audio_{uuid.uuid4().hex[:6]}.mp3"

    if file_id:
        unique_key = "file_" + str(uuid.uuid4().hex[:8])
        file_database[unique_key] = {
            "file_id": file_id,
            "file_type": file_type,
            "file_name": file_name,
            "is_text_key": False,
            "uploaded_at": datetime.now().isoformat()
        }
        sync_db()

        bot_info = bot.get_me()
        share_link = f"https://t.me/{bot_info.username}?start={unique_key}"

        success_msg = (
            "╔════════════════════════════╗\n"
            "║  ✅ File Uploaded!\n"
            "╠════════════════════════════╣\n"
            f"║  📁 Name: `{file_name}`\n"
            f"║  📂 Type: {file_type.capitalize()}\n"
            f"║  🆔 ID: `{unique_key}`\n"
            "║  📋 Link:\n"
            f"║  `{share_link}`\n"
            "╚════════════════════════════╝"
        )

        copy_markup = InlineKeyboardMarkup()
        copy_markup.add(InlineKeyboardButton("📋 Click to Copy Link", callback_data=f"copy_val|{share_link}"))

        bot.send_message(message.chat.id, success_msg, parse_mode="Markdown", reply_markup=copy_markup)
        logger.info(f"ফাইল আপলোড: {file_name} ({unique_key}) by admin")

# -------------------- টেক্সট মেসেজ হ্যান্ডলার --------------------
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    if is_user_banned(user_id):
        bot.send_message(chat_id, "⛔ You are banned from using this bot!")
        return

    if user_id != ADMIN_ID and bot_settings.get("maintenance_mode", False):
        bot.send_message(chat_id, "🔧 Bot is under maintenance. Please try again later.")
        return

    if user_id not in registered_users:
        registered_users.add(user_id)
        log_user_activity(user_id, "registered")
        sync_db()

    # অটো রিপ্লাই চেক
    if text:
        auto_reply = bot_settings.get("auto_reply", {})
        for keyword, reply in auto_reply.items():
            if keyword.lower() in text.lower():
                bot.send_message(chat_id, reply)
                return

    # অ্যাডমিন স্টেট হ্যান্ডলিং
    if user_id == ADMIN_ID:
        current_state = user_states.get(chat_id)

        if current_state == "waiting_for_admin_password":
            password = text.strip()
            if login_admin(user_id, password, remember=False):
                user_states[chat_id] = None
                bot.delete_message(chat_id, message.message_id - 1)
                bot.delete_message(chat_id, message.message_id)
                admin_msg = (
                    "╔════════════════════════════╗\n"
                    "║  ✅ Login Successful!\n"
                    "║  👋 Welcome Admin!\n"
                    "║  🛠️ Bot Control Panel\n"
                    "╠════════════════════════════╣\n"
                    "║  🔑 Create Secret Keys\n"
                    "║  📁 Manage Files\n"
                    "║  👥 Manage Users\n"
                    "║  📊 View Stats\n"
                    "║  ⏰ Session: 1 Hour\n"
                    "╚════════════════════════════╝"
                )
                bot.send_message(chat_id, admin_msg, parse_mode="Markdown", reply_markup=get_admin_panel_keyboard())
                logger.info(f"Admin logged in: {user_id}")
            else:
                user_states[chat_id] = "waiting_for_admin_password"
                bot.send_message(chat_id, "❌ Invalid password! Please try again:")
            return

        if current_state == "waiting_for_admin_password_save":
            password = text.strip()
            if login_admin(user_id, password, remember=True):
                user_states[chat_id] = None
                bot.delete_message(chat_id, message.message_id - 1)
                bot.delete_message(chat_id, message.message_id)
                admin_msg = (
                    "╔════════════════════════════╗\n"
                    "║  ✅ Login Successful!\n"
                    "║  👋 Welcome Admin!\n"
                    "║  🛠️ Bot Control Panel\n"
                    "╠════════════════════════════╣\n"
                    "║  🔑 Create Secret Keys\n"
                    "║  📁 Manage Files\n"
                    "║  👥 Manage Users\n"
                    "║  📊 View Stats\n"
                    "║  💾 Password Saved!\n"
                    "║  🔄 Auto-Login Active (7 Days)\n"
                    "╚════════════════════════════╝"
                )
                bot.send_message(chat_id, admin_msg, parse_mode="Markdown", reply_markup=get_admin_panel_keyboard())
                logger.info(f"Admin logged in with save: {user_id}")
            else:
                user_states[chat_id] = "waiting_for_admin_password_save"
                bot.send_message(chat_id, "❌ Invalid password! Please try again:")
            return

        if current_state == "waiting_for_giveaway_prize":
            giveaway["prize"] = text.strip()
            giveaway["active"] = True
            giveaway["participants"] = []
            giveaway["end_time"] = (datetime.now() + timedelta(hours=24)).isoformat()
            sync_db()
            user_states[chat_id] = None
            bot.send_message(chat_id, f"🎁 Giveaway started!\nPrize: {text.strip()}\nEnds in 24 hours!")
            return

        if current_state == "waiting_for_schedule_message":
            try:
                parts = text.split("|")
                if len(parts) != 2:
                    bot.send_message(chat_id, "❌ Invalid format! Use: `message|YYYY-MM-DD HH:MM`")
                    return
                msg, time_str = parts
                schedule_time = datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M")

                scheduled_messages.append({
                    "message": msg,
                    "time": schedule_time.isoformat(),
                    "sent": False
                })
                sync_db()
                user_states[chat_id] = None
                bot.send_message(chat_id, f"✅ Message scheduled for {time_str}!")
            except Exception as e:
                bot.send_message(chat_id, f"❌ Error: {e}")
            return

        if current_state == "waiting_for_add_admin":
            try:
                admin_id = int(text.strip())
                if "sub_admins" not in bot_settings:
                    bot_settings["sub_admins"] = []
                if admin_id not in bot_settings["sub_admins"] and admin_id != ADMIN_ID:
                    bot_settings["sub_admins"].append(admin_id)
                    sync_db()
                    bot.send_message(chat_id, f"✅ Admin `{admin_id}` added!")
                else:
                    bot.send_message(chat_id, "❌ User already admin or is the main admin!")
                user_states[chat_id] = None
            except:
                bot.send_message(chat_id, "❌ Invalid user ID!")
            return

        if current_state == "waiting_for_remove_admin":
            try:
                admin_id = int(text.strip())
                if "sub_admins" in bot_settings and admin_id in bot_settings["sub_admins"]:
                    bot_settings["sub_admins"].remove(admin_id)
                    sync_db()
                    bot.send_message(chat_id, f"✅ Admin `{admin_id}` removed!")
                else:
                    bot.send_message(chat_id, "❌ Admin not found!")
                user_states[chat_id] = None
            except:
                bot.send_message(chat_id, "❌ Invalid user ID!")
            return

        if current_state == "waiting_for_auto_reply_keyword":
            user_states[chat_id] = f"waiting_for_auto_reply_response||{text.strip()}"
            bot.send_message(chat_id, f"✏️ Enter reply for `{text.strip()}`:")
            return

        if current_state and current_state.startswith("waiting_for_auto_reply_response||"):
            keyword = current_state.split("waiting_for_auto_reply_response||")[-1]
            response = text.strip()
            if not response:
                bot.send_message(chat_id, "❌ Reply cannot be empty!")
                return

            if "auto_reply" not in bot_settings:
                bot_settings["auto_reply"] = {}
            bot_settings["auto_reply"][keyword] = response
            sync_db()
            user_states[chat_id] = None
            bot.send_message(chat_id, f"✅ Auto-reply for `{keyword}` added!")
            return

        if current_state == "waiting_for_link_1":
            bot_settings["chat_link_1"] = text.strip()
            sync_db()
            user_states[chat_id] = None
            bot.send_message(chat_id, "✅ Link 1 updated!", reply_markup=get_admin_panel_keyboard())
            return

        if current_state == "waiting_for_link_2":
            bot_settings["chat_link_2"] = text.strip()
            sync_db()
            user_states[chat_id] = None
            bot.send_message(chat_id, "✅ Link 2 updated!", reply_markup=get_admin_panel_keyboard())
            return

        if current_state == "waiting_for_dynamic_ch_name":
            user_states[chat_id] = f"waiting_for_dynamic_ch_link||{text.strip()}"
            bot.send_message(chat_id, f"🔗 Enter invite link for **{text.strip()}**:")
            return

        if current_state and current_state.startswith("waiting_for_dynamic_ch_link||"):
            ch_name = current_state.split("waiting_for_dynamic_ch_link||")[-1]
            ch_link = text.strip()
            user_states[chat_id] = None

            ch_id = "ch_" + str(uuid.uuid4().hex[:6])
            if "dynamic_channels" not in bot_settings:
                bot_settings["dynamic_channels"] = {}

            bot_settings["dynamic_channels"][ch_id] = {"name": ch_name, "link": ch_link}
            sync_db()
            bot.send_message(chat_id, f"✅ **{ch_name}** added successfully!", reply_markup=get_admin_panel_keyboard())
            return

        if current_state and current_state.startswith("waiting_for_edit_dyn_link||"):
            ch_id = current_state.split("waiting_for_edit_dyn_link||")[-1]
            user_states[chat_id] = None

            if "dynamic_channels" in bot_settings and ch_id in bot_settings["dynamic_channels"]:
                bot_settings["dynamic_channels"][ch_id]["link"] = text.strip()
                sync_db()
                bot.send_message(chat_id, "✅ Link updated!", reply_markup=get_admin_panel_keyboard())
            return

        if current_state == "waiting_for_ban_user":
            user_states[chat_id] = None
            try:
                target_id = int(text.strip())
                banned_users.add(target_id)
                sync_db()
                bot.send_message(chat_id, f"✅ User `{target_id}` banned!", parse_mode="Markdown", reply_markup=get_admin_panel_keyboard())
            except:
                bot.send_message(chat_id, "❌ Invalid user ID!")
            return

        if current_state == "waiting_for_unban_user":
            user_states[chat_id] = None
            try:
                target_id = int(text.strip())
                if target_id in banned_users:
                    banned_users.remove(target_id)
                    sync_db()
                    bot.send_message(chat_id, f"✅ User `{target_id}` unbanned!", parse_mode="Markdown", reply_markup=get_admin_panel_keyboard())
                else:
                    bot.send_message(chat_id, "❌ User not found in ban list!")
            except:
                bot.send_message(chat_id, "❌ Invalid user ID!")
            return

        if current_state == "waiting_for_panel_name":
            user_states[chat_id] = f"waiting_for_secret_value||{text.strip()}"
            bot.send_message(chat_id, "🔑 Enter the Secret Key value:")
            return

        if current_state and current_state.startswith("waiting_for_secret_value||"):
            panel_name = current_state.split("waiting_for_secret_value||")[-1]
            secret_value = text.strip()
            user_states[chat_id] = None

            unique_key = "key_" + str(uuid.uuid4().hex[:8])
            file_database[unique_key] = {
                "is_text_key": True,
                "panel_name": panel_name,
                "secret_value": secret_value,
                "uploaded_at": datetime.now().isoformat()
            }
            sync_db()

            bot_info = bot.get_me()
            share_link = f"https://t.me/{bot_info.username}?start={unique_key}"

            success_msg = (
                "╔════════════════════════════╗\n"
                "║  ✅ Secret Key Created!\n"
                "╠════════════════════════════╣\n"
                f"║  📋 Panel: {panel_name}\n"
                f"║  🆔 ID: `{unique_key}`\n"
                "║  🔗 Link:\n"
                f"║  `{share_link}`\n"
                "╚════════════════════════════╝"
            )

            copy_markup = InlineKeyboardMarkup()
            copy_markup.add(InlineKeyboardButton("📋 Click to Copy Link", callback_data=f"copy_val|{share_link}"))

            bot.send_message(chat_id, success_msg, parse_mode="Markdown", reply_markup=copy_markup)
            logger.info(f"Secret key created: {unique_key} - {panel_name}")
            return

        if current_state == "waiting_for_delete_key":
            target_key = text.strip()
            user_states[chat_id] = None
            if target_key in file_database:
                del file_database[target_key]
                sync_db()
                bot.send_message(chat_id, f"✅ File `{target_key}` deleted!", parse_mode="Markdown", reply_markup=get_admin_panel_keyboard())
            else:
                bot.send_message(chat_id, "❌ File ID not found!", reply_markup=get_admin_panel_keyboard())
            return

        if current_state == "waiting_for_broadcast":
            user_states[chat_id] = None
            success_count = 0
            status_msg = bot.send_message(chat_id, "📢 Sending broadcast...")

            for u_id in list(registered_users):
                if u_id == ADMIN_ID:
                    continue
                try:
                    bot.send_message(
                        u_id,
                        f"📢 **Broadcast Message:**\n\n{text}",
                        parse_mode="Markdown"
                    )
                    success_count += 1
                    time.sleep(0.05)
                except Exception as e:
                    logger.error(f"Broadcast failed to {u_id}: {e}")

            bot.edit_message_text(
                f"✅ Broadcast completed!\n🎯 Sent to `{success_count}` users",
                chat_id,
                status_msg.message_id,
                parse_mode="Markdown"
            )
            logger.info(f"Broadcast sent to {success_count} users")
            return

        if current_state == "waiting_for_custom_cmd_name":
            cmd_word = text.strip().lower()
            if not cmd_word:
                bot.send_message(chat_id, "❌ Command cannot be empty!")
                return
            user_states[chat_id] = f"waiting_for_custom_cmd_response||{cmd_word}"
            bot.send_message(chat_id, f"✏️ Enter the response for `/{cmd_word}`:")
            return

        if current_state and current_state.startswith("waiting_for_custom_cmd_response||"):
            cmd_word = current_state.split("waiting_for_custom_cmd_response||")[-1]
            response = text.strip()
            if not response:
                bot.send_message(chat_id, "❌ Response cannot be empty!")
                return

            if "custom_commands" not in bot_settings:
                bot_settings["custom_commands"] = {}
            bot_settings["custom_commands"][cmd_word] = response
            sync_db()
            user_states[chat_id] = None
            bot.send_message(chat_id, f"✅ Command `/{cmd_word}` added successfully!", reply_markup=get_admin_panel_keyboard())
            return

        if current_state == "waiting_for_log_channel":
            user_states[chat_id] = None
            log_channel = text.strip()
            if log_channel:
                bot_settings["log_channel"] = log_channel
                sync_db()
                bot.send_message(chat_id, f"✅ Log channel set to `{log_channel}`!", reply_markup=get_admin_panel_keyboard())
            else:
                bot.send_message(chat_id, "❌ Invalid channel!", reply_markup=get_admin_panel_keyboard())
            return

    # ফোর্স জয়েন চেক
    if user_id != ADMIN_ID and not check_user_membership(user_id):
        bot.send_message(
            chat_id,
            "🔒 Please join all channels to use this bot!",
            reply_markup=get_join_keyboard()
        )
        return

    # কাস্টম কমান্ড চেক
    if text and text.startswith("/"):
        cmd = text[1:].strip().lower()
        custom_cmds = bot_settings.get("custom_commands", {})
        if cmd in custom_cmds:
            bot.send_message(chat_id, custom_cmds[cmd])
            log_user_activity(user_id, f"custom_command_{cmd}")
            return

    # ইউজার কমান্ডস
    if text == "🎙️ Voice" or text == "/voice":
        if not GTTS_AVAILABLE:
            bot.send_message(chat_id, "❌ Voice feature is not available. gTTS not installed!")
            return
        user_states[chat_id] = "waiting_for_voice_text"
        bot.send_message(chat_id, "🎤 Send your text for voice generation:", reply_markup=types.ReplyKeyboardRemove())

    elif text == "📊 Stats" or text == "/stats":
        if user_id in user_activity:
            stats = user_activity[user_id]
            points = stats.get("points", 0)
            rank = stats.get("rank", "Member")
            msg = (
                f"📊 **Your Stats:**\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🔄 Total Actions: `{stats['total_actions']}`\n"
                f"⭐ Points: `{points}`\n"
                f"🏅 Rank: `{rank}`\n"
                f"📅 Last Active: `{stats['last_active'][:10] if stats['last_active'] else 'N/A'}`"
            )
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "📊 No activity recorded yet.")

    elif text == "🎁 Daily Reward" or text == "/daily":
        today = datetime.now().date().isoformat()
        if "last_daily" in user_activity.get(user_id, {}):
            last_daily = user_activity[user_id].get("last_daily", "")
            if last_daily == today:
                bot.send_message(chat_id, "❌ You already claimed today's reward! Come back tomorrow.")
                return

        if user_id not in user_activity:
            user_activity[user_id] = {"points": 0}
        user_activity[user_id]["points"] = user_activity[user_id].get("points", 0) + bot_settings.get("daily_reward", 10)
        user_activity[user_id]["last_daily"] = today
        sync_db()
        log_user_activity(user_id, "daily_reward")
        bot.send_message(chat_id, f"🎁 You got {bot_settings.get('daily_reward', 10)} points!")

    elif text == "🏆 Leaderboard" or text == "/leaderboard":
        if not user_activity:
            bot.send_message(chat_id, "❌ No users found!")
            return

        sorted_users = sorted(user_activity.items(), key=lambda x: x[1].get("points", 0), reverse=True)[:10]
        msg = "🏆 **Top 10 Users:**\n━━━━━━━━━━━━━━━━\n"
        for i, (uid, data) in enumerate(sorted_users, 1):
            try:
                user = bot.get_chat(int(uid))
                name = user.first_name or "Unknown"
            except:
                name = "Unknown"
            points = data.get("points", 0)
            rank = data.get("rank", "Member")
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            msg += f"{medal} {name} - `{points}` pts ({rank})\n"

        bot.send_message(chat_id, msg, parse_mode="Markdown")

    elif text == "ℹ️ Help" or text == "/help":
        help_msg = (
            "╔════════════════════════════╗\n"
            f"║  ✨ {BOT_NAME} Bot Commands\n"
            "╠════════════════════════════╣\n"
            "║  🎙️ Voice - Text to Voice\n"
            "║  📊 Stats - View stats\n"
            "║  🎁 Daily Reward - Get points\n"
            "║  🏆 Leaderboard - Top users\n"
            "║  👤 Profile - User info\n"
            "║  🔗 Referral - Invite friends\n"
            "╚════════════════════════════╝"
        )
        bot.send_message(chat_id, help_msg)

    elif text == "👤 Profile" or text == "/profile":
        user = message.from_user
        points = user_activity.get(user_id, {}).get("points", 0)
        rank = user_activity.get(user_id, {}).get("rank", "Member")
        ref_count = len(db.get("referrals", {}).get(str(user_id), []))
        profile_msg = (
            f"👤 **Your Profile:**\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📛 Name: {user.first_name or 'N/A'}\n"
            f"🆔 ID: `{user.id}`\n"
            f"⭐ Points: `{points}`\n"
            f"🏅 Rank: `{rank}`\n"
            f"🔗 Referrals: `{ref_count}`\n"
            f"📅 Joined: {datetime.fromtimestamp(user.date).strftime('%Y-%m-%d') if hasattr(user, 'date') else 'N/A'}"
        )
        bot.send_message(chat_id, profile_msg, parse_mode="Markdown")

    # ভয়েস জেনারেশন
    elif user_states.get(chat_id) == "waiting_for_voice_text":
        if not GTTS_AVAILABLE:
            bot.send_message(chat_id, "❌ Voice feature not available!")
            user_states[chat_id] = None
            return

        user_states[chat_id] = None
        status_message = bot.send_message(chat_id, "🎵 Generating voice...")
        file_path = f"voice_{chat_id}_{int(time.time())}.mp3"

        try:
            tts = gTTS(text=text, lang='bn', slow=False)
            tts.save(file_path)

            with open(file_path, 'rb') as audio:
                bot.send_audio(
                    chat_id,
                    audio,
                    caption="🎵 Here is your voice message!",
                    reply_markup=get_main_keyboard()
                )
            bot.delete_message(chat_id, status_message.message_id)
            log_user_activity(user_id, "voice_generated")

        except Exception as e:
            logger.error(f"Voice generation error: {e}")
            bot.send_message(chat_id, f"❌ Voice generation failed: {str(e)[:100]}", reply_markup=get_main_keyboard())
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    else:
        bot.send_message(chat_id, "❌ Unknown command. Use /help for available commands.", reply_markup=get_main_keyboard())

# -------------------- শিডিউল মেসেজ চেক --------------------
def check_scheduled_messages():
    while True:
        try:
            now = datetime.now()
            for msg in scheduled_messages:
                if not msg.get("sent"):
                    msg_time = datetime.fromisoformat(msg["time"])
                    if now >= msg_time:
                        for user_id in list(registered_users):
                            try:
                                bot.send_message(user_id, f"📅 **Scheduled Message:**\n\n{msg['message']}", parse_mode="Markdown")
                            except:
                                pass
                        msg["sent"] = True
                        sync_db()
            time.sleep(60)
        except Exception as e:
            logger.error(f"Scheduled message error: {e}")
            time.sleep(60)

# -------------------- গিভঅ্যাওয়ে চেক --------------------
def check_giveaway_loop():
    while True:
        try:
            check_giveaway()
            time.sleep(60)
        except Exception as e:
            logger.error(f"Giveaway check error: {e}")
            time.sleep(60)

# -------------------- রেন্ডারের জন্য ওয়েবহুক সেটআপ --------------------
def setup_webhook():
    try:
        bot.remove_webhook()
        logger.info("Webhook removed, using polling mode")
        return True
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        return False

# -------------------- গ্লোবাল এরর হ্যান্ডলার --------------------
def global_exception_handler(exc_type, exc_value, exc_traceback):
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = global_exception_handler

# -------------------- মেইন --------------------
if __name__ == "__main__":
    # Render-এর জন্য Flask ওয়েব সার্ভার
    try:
        from flask import Flask
        app_flask = Flask(__name__)

        @app_flask.route('/')
        def home():
            return "SHAKIB Bot is running!"

        @app_flask.route('/health')
        def health():
            return "OK"

        def run_bot():
            print_banner()
            logger.info(f"🤖 {BOT_NAME} Bot is starting...")
            logger.info(f"👤 Admin ID: {ADMIN_ID}")
            logger.info(f"🔐 Admin Password: {ADMIN_PASSWORD}")
            logger.info(f"📁 Database: {DB_FILE}")
            logger.info(f"📝 Log File: {LOG_FILE}")

            # অটো-ব্যাকআপ থ্রেড স্টার্ট
            backup_thread = threading.Thread(target=auto_backup, daemon=True)
            backup_thread.start()
            logger.info("✅ Auto-backup thread started")

            schedule_thread = threading.Thread(target=check_scheduled_messages, daemon=True)
            schedule_thread.start()

            giveaway_thread = threading.Thread(target=check_giveaway_loop, daemon=True)
            giveaway_thread.start()

            logger.info(f"✅ {BOT_NAME} Bot is running on Render...")

            try:
                bot.infinity_polling(timeout=30, long_polling_timeout=20)
            except Exception as e:
                logger.error(f"Bot crashed: {e}")
                sync_db()
                time.sleep(5)

        # বট থ্রেডে চালান
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()

        # Flask সার্ভার চালান (Render-এর জন্য)
        port = int(os.environ.get("PORT", 5000))
        app_flask.run(host="0.0.0.0", port=port)

    except ImportError:
        # Flask ইনস্টল না থাকলে সরাসরি বট চালান
        print_banner()
        logger.info(f"🤖 {BOT_NAME} Bot is starting...")
        logger.info(f"👤 Admin ID: {ADMIN_ID}")
        logger.info(f"🔐 Admin Password: {ADMIN_PASSWORD}")
        logger.info(f"📁 Database: {DB_FILE}")
        logger.info(f"📝 Log File: {LOG_FILE}")

        # অটো-ব্যাকআপ থ্রেড স্টার্ট
        backup_thread = threading.Thread(target=auto_backup, daemon=True)
        backup_thread.start()
        logger.info("✅ Auto-backup thread started")

        schedule_thread = threading.Thread(target=check_scheduled_messages, daemon=True)
        schedule_thread.start()

        giveaway_thread = threading.Thread(target=check_giveaway_loop, daemon=True)
        giveaway_thread.start()

        logger.info(f"✅ {BOT_NAME} Bot is running...")

        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20)
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            sync_db()
            time.sleep(5)
