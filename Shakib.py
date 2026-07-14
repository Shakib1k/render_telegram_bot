import os
import json
import logging
from datetime import datetime
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import threading
import time
import sys
import signal
import requests

# =====================================================
#           📋 কনফিগারেশন
# =====================================================

BOT_TOKEN = "8832122564:AAEHdFBqZxiMu3Y2m1SAAAjXymf2skLdksQ"
ADMIN_ID = 7058712225
DB_FILE = "forward_bot.json"

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)

# ওয়েবহুক ডিলিট - রেন্ডারে ওয়েবহুক ইস্যু সমাধান
try:
    # ওয়েবহুক ডিলিট করার চেষ্টা
    webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.get(webhook_url)
    if response.status_code == 200:
        logger.info("✅ ওয়েবহুক ডিলিট করা হয়েছে!")
    else:
        logger.warning(f"ওয়েবহুক ডিলিট করতে ব্যর্থ: {response.text}")
except Exception as e:
    logger.error(f"ওয়েবহুক ডিলিট করতে ব্যর্থ: {e}")

# -------------------- ডেটাবেস --------------------
def get_default_db():
    return {
        "target_groups": [],
        "source_groups": [],
        "registered_users": [],
        "banned_users": [],
        "settings": {
            "forward_voice": True,
            "forward_photo": True,
            "forward_video": True,
            "forward_document": True,
            "forward_text": True,
            "forward_sticker": True,
            "reply_to_sender": False,
            "auto_forward": True,
            "forward_from_source": True
        }
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
                return data
        except:
            return get_default_db()
    return get_default_db()

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info("ডেটাবেস সেভ করা হয়েছে")
    except Exception as e:
        logger.error(f"সেভ করতে ব্যর্থ: {e}")

db = load_db()
target_groups = db.get("target_groups", [])
source_groups = db.get("source_groups", [])
settings = db.get("settings", {})

# -------------------- কিবোর্ড --------------------
def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📋 Target Groups"),
        KeyboardButton("📋 Source Groups"),
        KeyboardButton("➕ Add Group"),
        KeyboardButton("➖ Remove Group")
    )
    markup.add(
        KeyboardButton("⚙️ Settings"),
        KeyboardButton("📢 Broadcast"),
        KeyboardButton("📊 Stats")
    )
    return markup

# -------------------- গ্রুপ যোগ/বাদ ফাংশন --------------------
def add_target_group(group_id):
    """টার্গেট গ্রুপ যোগ করে"""
    if group_id not in target_groups:
        target_groups.append(group_id)
        db["target_groups"] = target_groups
        save_db(db)
        return True
    return False

def remove_target_group(group_id):
    """টার্গেট গ্রুপ বাদ দেয়"""
    if group_id in target_groups:
        target_groups.remove(group_id)
        db["target_groups"] = target_groups
        save_db(db)
        return True
    return False

def add_source_group(group_id):
    """সোর্স গ্রুপ যোগ করে"""
    if group_id not in source_groups:
        source_groups.append(group_id)
        db["source_groups"] = source_groups
        save_db(db)
        return True
    return False

def remove_source_group(group_id):
    """সোর্স গ্রুপ বাদ দেয়"""
    if group_id in source_groups:
        source_groups.remove(group_id)
        db["source_groups"] = source_groups
        save_db(db)
        return True
    return False

# -------------------- ফরওয়ার্ড ফাংশন --------------------
def forward_to_groups(content_type, file_id=None, text=None, caption=None, from_chat_id=None, message_id=None):
    """সব টার্গেট গ্রুপে ফরওয়ার্ড করে"""
    if not target_groups:
        return "❌ কোনো টার্গেট গ্রুপ যোগ করা নেই!"

    success_count = 0
    fail_count = 0
    failed_groups = []

    for group_id in target_groups:
        try:
            if from_chat_id and message_id:
                bot.forward_message(group_id, from_chat_id, message_id)
            else:
                if content_type == "voice":
                    bot.send_voice(group_id, file_id, caption=caption)
                elif content_type == "audio":
                    bot.send_audio(group_id, file_id, caption=caption)
                elif content_type == "document":
                    bot.send_document(group_id, file_id, caption=caption)
                elif content_type == "photo":
                    bot.send_photo(group_id, file_id, caption=caption)
                elif content_type == "video":
                    bot.send_video(group_id, file_id, caption=caption)
                elif content_type == "text":
                    bot.send_message(group_id, text)
                elif content_type == "sticker":
                    bot.send_sticker(group_id, file_id)
                elif content_type == "animation":
                    bot.send_animation(group_id, file_id)
            success_count += 1
        except Exception as e:
            fail_count += 1
            failed_groups.append(str(group_id))
            logger.error(f"গ্রুপ {group_id} এ পাঠাতে ব্যর্থ: {e}")

    result = f"✅ {success_count} টি গ্রুপে পাঠানো হয়েছে"
    if fail_count > 0:
        result += f"\n❌ {fail_count} টি গ্রুপে ব্যর্থ: {', '.join(failed_groups[:5])}"
        if len(failed_groups) > 5:
            result += f" ... এবং {len(failed_groups)-5} টি"

    return result

# -------------------- বট কমান্ড --------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ আপনি এই বট ব্যবহার করতে পারেন না!")
        return

    if message.chat.type != "private":
        bot.send_message(message.chat.id, "👋 আমাকে প্রাইভেট চ্যাটে ব্যবহার করুন!")
        return

    welcome_msg = (
        "🤖 **মাল্টি-গ্রুপ ফরওয়ার্ডার বট**\n\n"
        "📌 **কীভাবে ব্যবহার করবেন:**\n\n"
        "🔹 **টার্গেট গ্রুপ** (যেখানে ফাইল যাবে):\n"
        "   `/addtarget -100xxxxxx`\n\n"
        "🔹 **সোর্স গ্রুপ** (যেখান থেকে ফাইল আসবে):\n"
        "   `/addsource -100xxxxxx`\n\n"
        "🔹 **অটো-ফরওয়ার্ড:**\n"
        "   সোর্স গ্রুপের যেকোনো মেসেজ স্বয়ংক্রিয়ভাবে টার্গেট গ্রুপে যাবে!\n\n"
        "🔹 **প্রাইভেট চ্যাট:**\n"
        "   সরাসরি ফাইল পাঠালেও টার্গেট গ্রুপে যাবে!\n\n"
        f"📋 **টার্গেট গ্রুপ:** {len(target_groups)} টি\n"
        f"📋 **সোর্স গ্রুপ:** {len(source_groups)} টি\n"
        "📌 **কমান্ড:** /help"
    )

    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(commands=['help'])
def send_help(message):
    if message.from_user.id != ADMIN_ID:
        return

    help_msg = (
        "📌 **বটের কমান্ডসমূহ:**\n\n"
        "/start - বট স্টার্ট\n"
        "/help - সাহায্য\n"
        "/targets - টার্গেট গ্রুপ লিস্ট দেখে\n"
        "/sources - সোর্স গ্রুপ লিস্ট দেখে\n"
        "/addtarget - টার্গেট গ্রুপ যোগ করুন\n"
        "/addsource - সোর্স গ্রুপ যোগ করুন\n"
        "/removetarget - টার্গেট গ্রুপ বাদ দিন\n"
        "/removesource - সোর্স গ্রুপ বাদ দিন\n"
        "/broadcast - সব গ্রুপে মেসেজ পাঠান\n"
        "/settings - সেটিংস দেখুন\n"
        "/stats - পরিসংখ্যান\n\n"
        "📌 **গ্রুপ যোগ করার নিয়ম:**\n"
        "1️⃣ `/addtarget -1001234567890` (আইডি দিয়ে)\n"
        "2️⃣ `/addsource -1001234567890` (আইডি দিয়ে)\n\n"
        "⚠️ **ফরওয়ার্ড করলে গ্রুপ অটো-অ্যাড হবে না!**"
    )

    bot.send_message(message.chat.id, help_msg, parse_mode="Markdown")

# -------------------- টার্গেট গ্রুপ যোগ/বাদ --------------------
@bot.message_handler(commands=['addtarget'])
def add_target_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) > 1:
        try:
            group_id = int(args[1])
            if add_target_group(group_id):
                try:
                    chat = bot.get_chat(group_id)
                    name = chat.title or "Unknown"
                    bot.send_message(
                        message.chat.id,
                        f"✅ **{name}** টার্গেট গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                        parse_mode="Markdown"
                    )
                except:
                    bot.send_message(
                        message.chat.id,
                        f"✅ টার্গেট গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                        parse_mode="Markdown"
                    )
            else:
                bot.send_message(message.chat.id, "ℹ️ এই গ্রুপ ইতিমধ্যে টার্গেট হিসেবে যোগ করা আছে!")
        except:
            bot.send_message(message.chat.id, "❌ সঠিক গ্রুপ আইডি দিন! (যেমন: `/addtarget -1001234567890`)")
    else:
        bot.send_message(message.chat.id, "📌 গ্রুপ আইডি দিয়ে যোগ করুন: `/addtarget -1001234567890`")

@bot.message_handler(commands=['removetarget'])
def remove_target_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not target_groups:
        bot.send_message(message.chat.id, "❌ কোনো টার্গেট গ্রুপ যোগ করা নেই!")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    for gid in target_groups:
        try:
            chat = bot.get_chat(gid)
            name = chat.title or f"Group {gid}"
            markup.add(InlineKeyboardButton(f"🗑️ {name}", callback_data=f"removetarget_{gid}"))
        except:
            markup.add(InlineKeyboardButton(f"🗑️ {gid}", callback_data=f"removetarget_{gid}"))

    bot.send_message(message.chat.id, "🗑️ বাদ দেওয়ার জন্য টার্গেট গ্রুপ সিলেক্ট করুন:", reply_markup=markup)

# -------------------- সোর্স গ্রুপ যোগ/বাদ --------------------
@bot.message_handler(commands=['addsource'])
def add_source_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) > 1:
        try:
            group_id = int(args[1])
            if add_source_group(group_id):
                try:
                    chat = bot.get_chat(group_id)
                    name = chat.title or "Unknown"
                    bot.send_message(
                        message.chat.id,
                        f"✅ **{name}** সোর্স গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                        parse_mode="Markdown"
                    )
                except:
                    bot.send_message(
                        message.chat.id,
                        f"✅ সোর্স গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                        parse_mode="Markdown"
                    )
            else:
                bot.send_message(message.chat.id, "ℹ️ এই গ্রুপ ইতিমধ্যে সোর্স হিসেবে যোগ করা আছে!")
        except:
            bot.send_message(message.chat.id, "❌ সঠিক গ্রুপ আইডি দিন! (যেমন: `/addsource -1001234567890`)")
    else:
        bot.send_message(message.chat.id, "📌 গ্রুপ আইডি দিয়ে যোগ করুন: `/addsource -1001234567890`")

@bot.message_handler(commands=['removesource'])
def remove_source_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not source_groups:
        bot.send_message(message.chat.id, "❌ কোনো সোর্স গ্রুপ যোগ করা নেই!")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    for gid in source_groups:
        try:
            chat = bot.get_chat(gid)
            name = chat.title or f"Group {gid}"
            markup.add(InlineKeyboardButton(f"🗑️ {name}", callback_data=f"removesource_{gid}"))
        except:
            markup.add(InlineKeyboardButton(f"🗑️ {gid}", callback_data=f"removesource_{gid}"))

    bot.send_message(message.chat.id, "🗑️ বাদ দেওয়ার জন্য সোর্স গ্রুপ সিলেক্ট করুন:", reply_markup=markup)

# -------------------- গ্রুপ লিস্ট দেখানো --------------------
@bot.message_handler(commands=['targets'])
def show_targets_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not target_groups:
        bot.send_message(message.chat.id, "❌ কোনো টার্গেট গ্রুপ যোগ করা নেই!")
        return

    msg = "📋 **টার্গেট গ্রুপ লিস্ট:**\n\n"
    for i, gid in enumerate(target_groups, 1):
        try:
            chat = bot.get_chat(gid)
            name = chat.title or "Unknown"
            msg += f"{i}. {name}\n   🆔 `{gid}`\n\n"
        except:
            msg += f"{i}. Group ID: `{gid}`\n\n"

    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['sources'])
def show_sources_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not source_groups:
        bot.send_message(message.chat.id, "❌ কোনো সোর্স গ্রুপ যোগ করা নেই!")
        return

    msg = "📋 **সোর্স গ্রুপ লিস্ট:**\n\n"
    for i, gid in enumerate(source_groups, 1):
        try:
            chat = bot.get_chat(gid)
            name = chat.title or "Unknown"
            msg += f"{i}. {name}\n   🆔 `{gid}`\n\n"
        except:
            msg += f"{i}. Group ID: `{gid}`\n\n"

    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# -------------------- ব্রডকাস্ট --------------------
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "📢 যে মেসেজ ব্রডকাস্ট করতে চান সেটি পাঠান।")

# -------------------- সেটিংস --------------------
@bot.message_handler(commands=['settings'])
def settings_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎤 Voice", callback_data="toggle_voice"),
        InlineKeyboardButton("🖼️ Photo", callback_data="toggle_photo"),
        InlineKeyboardButton("🎬 Video", callback_data="toggle_video"),
        InlineKeyboardButton("📁 Document", callback_data="toggle_document"),
        InlineKeyboardButton("📝 Text", callback_data="toggle_text"),
        InlineKeyboardButton("🔹 Sticker", callback_data="toggle_sticker"),
        InlineKeyboardButton("🔄 Source Fwd", callback_data="toggle_source_fwd")
    )

    status = (
        "⚙️ **বর্তমান সেটিংস:**\n\n"
        f"🎤 Voice: {'✅ ON' if settings.get('forward_voice', True) else '❌ OFF'}\n"
        f"🖼️ Photo: {'✅ ON' if settings.get('forward_photo', True) else '❌ OFF'}\n"
        f"🎬 Video: {'✅ ON' if settings.get('forward_video', True) else '❌ OFF'}\n"
        f"📁 Document: {'✅ ON' if settings.get('forward_document', True) else '❌ OFF'}\n"
        f"📝 Text: {'✅ ON' if settings.get('forward_text', True) else '❌ OFF'}\n"
        f"🔹 Sticker: {'✅ ON' if settings.get('forward_sticker', True) else '❌ OFF'}\n"
        f"🔄 Source Forward: {'✅ ON' if settings.get('forward_from_source', True) else '❌ OFF'}"
    )

    bot.send_message(message.chat.id, status, parse_mode="Markdown", reply_markup=markup)

# -------------------- স্ট্যাটাস --------------------
@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    stats_msg = (
        f"📊 **পরিসংখ্যান:**\n\n"
        f"📋 টার্গেট গ্রুপ: `{len(target_groups)}` টি\n"
        f"📋 সোর্স গ্রুপ: `{len(source_groups)}` টি\n"
        f"📅 সর্বশেষ আপডেট: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
    )

    bot.send_message(message.chat.id, stats_msg, parse_mode="Markdown")

# -------------------- মেইন মেসেজ হ্যান্ডলার --------------------
@bot.message_handler(func=lambda message: True, content_types=[
    'text', 'voice', 'audio', 'document', 'photo', 'video', 'sticker', 'animation'
])
def handle_all_messages(message):
    user_id = message.from_user.id
    
    # অ্যাডমিন চেক
    if user_id != ADMIN_ID:
        return
    
    # প্রাইভেট চ্যাটের মেসেজ হ্যান্ডেল
    if message.chat.type == "private":
        handle_private_messages(message)
        return
    
    # গ্রুপের মেসেজ হ্যান্ডেল (সোর্স গ্রুপ থেকে অটো-ফরওয়ার্ড)
    if message.chat.type in ['group', 'supergroup']:
        handle_group_messages(message)
        return

def handle_private_messages(message):
    """প্রাইভেট চ্যাটের মেসেজ হ্যান্ডেল"""
    
    # টেক্সট কমান্ড চেক
    if message.text:
        text = message.text.lower()
        if text == "📋 target groups" or text == "/targets":
            show_targets_cmd(message)
            return
        if text == "📋 source groups" or text == "/sources":
            show_sources_cmd(message)
            return
        if text == "➕ add group":
            bot.send_message(message.chat.id, "📌 `/addtarget` অথবা `/addsource` ব্যবহার করুন")
            return
        if text == "➖ remove group":
            bot.send_message(message.chat.id, "📌 `/removetarget` অথবা `/removesource` ব্যবহার করুন")
            return
        if text == "📢 broadcast" or text == "/broadcast":
            broadcast_cmd(message)
            return
        if text == "⚙️ settings" or text == "/settings":
            settings_cmd(message)
            return
        if text == "📊 stats" or text == "/stats":
            stats_cmd(message)
            return

    # ফরওয়ার্ড করা মেসেজ হ্যান্ডেল (শুধু ফাইল ফরওয়ার্ড করবে, গ্রুপ অ্যাড করবে না)
    if message.forward_from_chat:
        # গ্রুপ অটো-অ্যাড করা হচ্ছে না - শুধু ফাইল ফরওয়ার্ড হবে
        if target_groups:
            forward_file_from_message(message)
        else:
            bot.send_message(message.chat.id, "❌ কোনো টার্গেট গ্রুপ যোগ করা নেই! প্রথমে `/addtarget` দিয়ে গ্রুপ যোগ করুন।")
        return

    # প্রাইভেট চ্যাট থেকে সরাসরি ফাইল ফরওয়ার্ড
    if not target_groups:
        bot.send_message(message.chat.id, "❌ কোনো টার্গেট গ্রুপ যোগ করা নেই! প্রথমে `/addtarget` দিয়ে গ্রুপ যোগ করুন।")
        return
    
    forward_file_from_message(message)

def handle_group_messages(message):
    """গ্রুপের মেসেজ হ্যান্ডেল (সোর্স গ্রুপ থেকে অটো-ফরওয়ার্ড)"""
    
    chat_id = message.chat.id
    
    # চেক করুন এই গ্রুপটি সোর্স লিস্টে আছে কিনা
    if chat_id not in source_groups:
        return
    
    # সোর্স গ্রুপ থেকে ফরওয়ার্ড সক্রিয় আছে কিনা
    if not settings.get('forward_from_source', True):
        return
    
    # নিজের টার্গেট গ্রুপে ফরওয়ার্ড করুন (যে গ্রুপ থেকে এসেছে সেটি বাদে)
    for target_id in target_groups:
        if target_id != chat_id:
            try:
                bot.forward_message(target_id, chat_id, message.message_id)
                logger.info(f"মেসেজ ফরওয়ার্ড করা হয়েছে: {chat_id} -> {target_id}")
            except Exception as e:
                logger.error(f"ফরওয়ার্ড করতে ব্যর্থ {chat_id} -> {target_id}: {e}")

def forward_file_from_message(message):
    """মেসেজ থেকে ফাইল ফরওয়ার্ড করে"""
    
    # ভয়েস
    if message.voice and settings.get('forward_voice', True):
        result = forward_to_groups("voice", message.voice.file_id)
        bot.send_message(message.chat.id, result)
        return
    
    # অডিও
    if message.audio and settings.get('forward_voice', True):
        result = forward_to_groups("audio", message.audio.file_id)
        bot.send_message(message.chat.id, result)
        return
    
    # ডকুমেন্ট
    if message.document and settings.get('forward_document', True):
        result = forward_to_groups("document", message.document.file_id)
        bot.send_message(message.chat.id, result)
        return
    
    # ফটো
    if message.photo and settings.get('forward_photo', True):
        result = forward_to_groups("photo", message.photo[-1].file_id)
        bot.send_message(message.chat.id, result)
        return
    
    # ভিডিও
    if message.video and settings.get('forward_video', True):
        result = forward_to_groups("video", message.video.file_id)
        bot.send_message(message.chat.id, result)
        return
    
    # স্টিকার
    if message.sticker and settings.get('forward_sticker', True):
        result = forward_to_groups("sticker", message.sticker.file_id)
        bot.send_message(message.chat.id, result)
        return
    
    # অ্যানিমেশন
    if message.animation:
        result = forward_to_groups("animation", message.animation.file_id)
        bot.send_message(message.chat.id, result)
        return
    
    # টেক্সট
    if message.text and settings.get('forward_text', True):
        if message.text.startswith("/broadcast"):
            text = message.text.replace("/broadcast", "").strip()
            if text:
                result = forward_to_groups("text", text=text)
                bot.send_message(message.chat.id, result)
            else:
                bot.send_message(message.chat.id, "📢 ব্রডকাস্ট করার জন্য মেসেজ দিন।")
            return
        result = forward_to_groups("text", text=message.text)
        bot.send_message(message.chat.id, result)
        return
    
    bot.send_message(message.chat.id, "ℹ️ এই ধরনের ফাইল ফরওয়ার্ড করা সক্রিয় নেই।")

# -------------------- গ্রুপে বট যোগ হলে --------------------
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            chat_id = message.chat.id
            # টার্গেট গ্রুপ হিসেবে যোগ করুন
            if chat_id not in target_groups:
                target_groups.append(chat_id)
                db["target_groups"] = target_groups
                save_db(db)
                bot.send_message(
                    chat_id,
                    f"✅ বট সক্রিয়! আমি এই গ্রুপে ফাইল ফরওয়ার্ড করব।\n🆔 `{chat_id}`",
                    parse_mode="Markdown"
                )
                if message.from_user.id == ADMIN_ID:
                    bot.send_message(
                        ADMIN_ID,
                        f"✅ নতুন টার্গেট গ্রুপ যোগ করা হয়েছে!\n📛 {message.chat.title or 'Unknown'}\n🆔 `{chat_id}`",
                        parse_mode="Markdown"
                    )

# -------------------- ইনলাইন বাটন --------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ আপনি এই বট ব্যবহার করতে পারেন না!", show_alert=True)
        return

    # টার্গেট গ্রুপ রিমুভ
    if call.data.startswith("removetarget_"):
        group_id = int(call.data.split("removetarget_")[1])
        if group_id in target_groups:
            target_groups.remove(group_id)
            db["target_groups"] = target_groups
            save_db(db)
            bot.answer_callback_query(call.id, f"✅ টার্গেট গ্রুপ বাদ দেওয়া হয়েছে!")
            bot.edit_message_text(f"✅ টার্গেট গ্রুপ বাদ দেওয়া হয়েছে!", call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ গ্রুপ পাওয়া যায়নি!")
        return

    # সোর্স গ্রুপ রিমুভ
    if call.data.startswith("removesource_"):
        group_id = int(call.data.split("removesource_")[1])
        if group_id in source_groups:
            source_groups.remove(group_id)
            db["source_groups"] = source_groups
            save_db(db)
            bot.answer_callback_query(call.id, f"✅ সোর্স গ্রুপ বাদ দেওয়া হয়েছে!")
            bot.edit_message_text(f"✅ সোর্স গ্রুপ বাদ দেওয়া হয়েছে!", call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ গ্রুপ পাওয়া যায়নি!")
        return

    # সেটিংস টগল
    if call.data.startswith("toggle_"):
        key = call.data.replace("toggle_", "")
        if key == "voice":
            settings["forward_voice"] = not settings.get("forward_voice", True)
        elif key == "photo":
            settings["forward_photo"] = not settings.get("forward_photo", True)
        elif key == "video":
            settings["forward_video"] = not settings.get("forward_video", True)
        elif key == "document":
            settings["forward_document"] = not settings.get("forward_document", True)
        elif key == "text":
            settings["forward_text"] = not settings.get("forward_text", True)
        elif key == "sticker":
            settings["forward_sticker"] = not settings.get("forward_sticker", True)
        elif key == "source_fwd":
            settings["forward_from_source"] = not settings.get("forward_from_source", True)

        db["settings"] = settings
        save_db(db)
        settings_cmd(call.message)
        bot.answer_callback_query(call.id, f"✅ সেটিংস আপডেট করা হয়েছে!")

    # অন্যান্য কলব্যাক
    if call.data == "show_groups":
        show_targets_cmd(call.message)
        bot.answer_callback_query(call.id)

    if call.data == "broadcast":
        bot.send_message(call.message.chat.id, "📢 যে মেসেজ ব্রডকাস্ট করতে চান সেটি পাঠান।")
        bot.answer_callback_query(call.id)

    if call.data == "show_stats":
        stats_cmd(call.message)
        bot.answer_callback_query(call.id)

    if call.data == "show_settings":
        settings_cmd(call.message)
        bot.answer_callback_query(call.id)

    if call.data == "add_group":
        bot.send_message(call.message.chat.id, "📌 `/addtarget` অথবা `/addsource` ব্যবহার করুন")
        bot.answer_callback_query(call.id)

    if call.data == "remove_group":
        bot.send_message(call.message.chat.id, "📌 `/removetarget` অথবা `/removesource` ব্যবহার করুন")
        bot.answer_callback_query(call.id)

# -------------------- সিগন্যাল হ্যান্ডলার --------------------
def signal_handler(sig, frame):
    print("\n🛑 বট বন্ধ করা হচ্ছে...")
    save_db(db)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# -------------------- মেইন --------------------
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 মাল্টি-গ্রুপ ফরওয়ার্ডার বট (আপডেটেড)")
    print(f"👤 অ্যাডমিন আইডি: {ADMIN_ID}")
    print(f"📋 টার্গেট গ্রুপ: {len(target_groups)} টি")
    print(f"📋 সোর্স গ্রুপ: {len(source_groups)} টি")
    print("=" * 50)
    print("💡 বট চালু আছে! Ctrl+C চাপলে বন্ধ হবে।")
    print("📌 সোর্স গ্রুপের যেকোনো মেসেজ অটোমেটিক টার্গেট গ্রুপে যাবে!")
    print("⚠️ ফরওয়ার্ড করলে গ্রুপ অটো-অ্যাড হবে না!")

    try:
        # এখানে polling_start_time আর্গুমেন্ট দিয়ে টাইমআউট বাড়ানো
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"বট ক্র্যাশ: {e}")
        save_db(db)
        time.sleep(5)
