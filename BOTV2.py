import os
import json
import logging
from datetime import datetime, timedelta
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import threading
import time
import sys
import signal

# =====================================================
#           📋 কনফিগারেশন
# =====================================================

BOT_TOKEN = "8861425904:AAEFpWoal1ttkS0ot0I1TuVQ_dylSfTZo_Q"
ADMIN_ID = 7058712225
DB_FILE = "forward_bot.json"

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)

# ওয়েবহুক ডিলিট
try:
    bot.remove_webhook()
    logger.info("✅ ওয়েবহুক ডিলিট করা হয়েছে!")
except Exception as e:
    logger.error(f"ওয়েবহুক ডিলিট করতে ব্যর্থ: {e}")

# -------------------- ডেটাবেস --------------------
def get_default_db():
    return {
        "target_groups": [],
        "registered_users": [],
        "banned_users": [],
        "scheduled_forwards": [],
        "settings": {
            "forward_voice": True,
            "forward_photo": True,
            "forward_video": True,
            "forward_document": True,
            "forward_text": True,
            "reply_to_sender": False,
            "auto_forward": True
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
settings = db.get("settings", {})
scheduled_forwards = db.get("scheduled_forwards", [])

# -------------------- কিবোর্ড --------------------
def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📋 Group List"),
        KeyboardButton("➕ Add Group"),
        KeyboardButton("➖ Remove Group")
    )
    markup.add(
        KeyboardButton("⚙️ Settings"),
        KeyboardButton("📢 Broadcast"),
        KeyboardButton("📊 Stats"),
        KeyboardButton("⏰ Scheduled")
    )
    return markup

def get_group_select_keyboard(selected_groups=None, content_type=None, file_id=None, text=None, caption=None):
    if selected_groups is None:
        selected_groups = []
    
    markup = InlineKeyboardMarkup(row_width=1)
    
    all_selected = len(selected_groups) == len(target_groups) and len(target_groups) > 0
    markup.add(
        InlineKeyboardButton(
            f"{'✅' if all_selected else '⬜'} সব গ্রুপ {'সিলেক্ট' if not all_selected else 'ডিসিলেক্ট'} করুন",
            callback_data=f"select_all|{content_type}|{file_id}|{text}|{caption}"
        )
    )
    
    for gid in target_groups:
        try:
            chat = bot.get_chat(gid)
            name = chat.title or f"Group {gid}"
        except:
            name = f"Group {gid}"
        
        is_selected = gid in selected_groups
        markup.add(
            InlineKeyboardButton(
                f"{'✅' if is_selected else '⬜'} {name}",
                callback_data=f"toggle_group|{gid}|{content_type}|{file_id}|{text}|{caption}"
            )
        )
    
    if selected_groups:
        markup.add(
            InlineKeyboardButton(
                f"🚀 এখন ফরওয়ার্ড করুন ({len(selected_groups)} টি গ্রুপে)",
                callback_data=f"forward_selected|{content_type}|{file_id}|{text}|{caption}|{','.join(map(str, selected_groups))}"
            )
        )
        markup.add(
            InlineKeyboardButton(
                f"⏰ টাইম সেট করে ফরওয়ার্ড করুন",
                callback_data=f"set_time|{content_type}|{file_id}|{text}|{caption}|{','.join(map(str, selected_groups))}"
            )
        )
    
    markup.add(InlineKeyboardButton("❌ বাতিল করুন", callback_data="cancel_forward"))
    
    return markup

# -------------------- টাইম সেট কিবোর্ড --------------------
def get_time_select_keyboard(content_type, file_id, text, caption, group_ids):
    markup = InlineKeyboardMarkup(row_width=3)
    
    times = [
        ("1 মিনিট", 1),
        ("5 মিনিট", 5),
        ("10 মিনিট", 10),
        ("15 মিনিট", 15),
        ("30 মিনিট", 30),
        ("1 ঘন্টা", 60),
        ("2 ঘন্টা", 120),
        ("6 ঘন্টা", 360),
        ("12 ঘন্টা", 720),
        ("24 ঘন্টা", 1440),
        ("কাস্টম", "custom")
    ]
    
    for label, minutes in times:
        if minutes == "custom":
            markup.add(InlineKeyboardButton(
                f"✏️ {label}",
                callback_data=f"custom_time|{content_type}|{file_id}|{text}|{caption}|{','.join(map(str, group_ids))}"
            ))
        else:
            markup.add(InlineKeyboardButton(
                f"⏰ {label}",
                callback_data=f"time_select|{minutes}|{content_type}|{file_id}|{text}|{caption}|{','.join(map(str, group_ids))}"
            ))
    
    markup.add(InlineKeyboardButton("🔙 পিছনে যান", callback_data=f"back_to_select|{content_type}|{file_id}|{text}|{caption}|{','.join(map(str, group_ids))}"))
    markup.add(InlineKeyboardButton("❌ বাতিল করুন", callback_data="cancel_forward"))
    
    return markup

# -------------------- ফরওয়ার্ড ফাংশন --------------------
def forward_to_specific_groups(content_type, group_ids, file_id=None, text=None, caption=None):
    if not group_ids:
        return "❌ কোনো গ্রুপ সিলেক্ট করা নেই!"

    success_count = 0
    fail_count = 0
    failed_groups = []

    for group_id in group_ids:
        try:
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

# -------------------- শিডিউল ফরওয়ার্ড --------------------
def schedule_forward(content_type, group_ids, minutes, file_id=None, text=None, caption=None):
    forward_time = datetime.now() + timedelta(minutes=minutes)
    
    scheduled_item = {
        "content_type": content_type,
        "group_ids": group_ids,
        "file_id": file_id,
        "text": text,
        "caption": caption,
        "forward_time": forward_time.isoformat(),
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    scheduled_forwards.append(scheduled_item)
    db["scheduled_forwards"] = scheduled_forwards
    save_db(db)
    
    return forward_time

def check_scheduled_forwards():
    while True:
        try:
            now = datetime.now()
            to_remove = []
            
            for i, item in enumerate(scheduled_forwards):
                if item.get("status") == "pending":
                    forward_time = datetime.fromisoformat(item["forward_time"])
                    if now >= forward_time:
                        result = forward_to_specific_groups(
                            item["content_type"],
                            item["group_ids"],
                            item.get("file_id"),
                            item.get("text"),
                            item.get("caption")
                        )
                        logger.info(f"শিডিউল ফরওয়ার্ড সম্পন্ন: {result}")
                        item["status"] = "completed"
                        item["result"] = result
                        to_remove.append(i)
                        
                        try:
                            bot.send_message(
                                ADMIN_ID,
                                f"⏰ **শিডিউল ফরওয়ার্ড সম্পন্ন!**\n\n{result}",
                                parse_mode="Markdown"
                            )
                        except:
                            pass
            
            for i in sorted(to_remove, reverse=True):
                scheduled_forwards.pop(i)
            
            db["scheduled_forwards"] = scheduled_forwards
            save_db(db)
            
            time.sleep(30)
        except Exception as e:
            logger.error(f"শিডিউল চেক করতে ব্যর্থ: {e}")
            time.sleep(60)

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

    pending_count = len([s for s in scheduled_forwards if s.get("status") == "pending"])
    
    welcome_msg = (
        "🤖 **মাল্টি-গ্রুপ ফরওয়ার্ডার বট**\n\n"
        "📌 **কীভাবে ব্যবহার করবেন:**\n"
        "1️⃣ আমাকে আপনার গ্রুপগুলোর এডমিন বানান\n"
        "2️⃣ গ্রুপ যোগ করুন: `/addgroup` অথবা গ্রুপ থেকে মেসেজ ফরওয়ার্ড করুন\n"
        "3️⃣ প্রাইভেট চ্যাটে ফাইল/ভয়েস/ছবি/টেক্সট পাঠান\n"
        "4️⃣ কোন গ্রুপে ফরওয়ার্ড করবেন তা সিলেক্ট করুন\n"
        "5️⃣ ⏰ টাইম সেট করে ফরওয়ার্ড করুন অথবা এখনই ফরওয়ার্ড করুন\n\n"
        "📌 **ফিচারসমূহ:**\n"
        "✅ ফাইল, ভয়েস, ছবি, ভিডিও ফরওয়ার্ড\n"
        "✅ নির্দিষ্ট গ্রুপ সিলেক্ট করে ফরওয়ার্ড\n"
        "✅ ⏰ টাইম সেট করে ফরওয়ার্ড\n"
        "✅ একসাথে ৫+ গ্রুপে ফরওয়ার্ড\n\n"
        f"📋 **বর্তমান গ্রুপ:** {len(target_groups)} টি\n"
        f"⏰ **পেন্ডিং ফরওয়ার্ড:** {pending_count} টি\n"
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
        "/groups - গ্রুপ লিস্ট দেখে\n"
        "/addgroup - গ্রুপ যোগ করুন (আইডি দিয়ে)\n"
        "/removegroup - গ্রুপ বাদ দিন (আইডি দিয়ে)\n"
        "/broadcast - সব গ্রুপে মেসেজ পাঠান\n"
        "/settings - সেটিংস দেখুন\n"
        "/stats - পরিসংখ্যান\n"
        "/scheduled - পেন্ডিং ফরওয়ার্ড লিস্ট\n\n"
        "📌 **গ্রুপ যোগ করার নিয়ম:**\n"
        "1️⃣ `/addgroup -1001234567890` (আইডি দিয়ে)\n"
        "2️⃣ অথবা গ্রুপ থেকে যেকোনো মেসেজ ফরওয়ার্ড করুন"
    )

    bot.send_message(message.chat.id, help_msg, parse_mode="Markdown")

@bot.message_handler(commands=['addgroup'])
def add_group_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) > 1:
        try:
            group_id = int(args[1])
            if group_id not in target_groups:
                target_groups.append(group_id)
                db["target_groups"] = target_groups
                save_db(db)
                try:
                    chat = bot.get_chat(group_id)
                    name = chat.title or "Unknown"
                    bot.send_message(
                        message.chat.id,
                        f"✅ **{name}** গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                        parse_mode="Markdown"
                    )
                except:
                    bot.send_message(
                        message.chat.id,
                        f"✅ গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                        parse_mode="Markdown"
                    )
            else:
                bot.send_message(message.chat.id, "ℹ️ এই গ্রুপ ইতিমধ্যে যোগ করা আছে!")
        except:
            bot.send_message(message.chat.id, "❌ সঠিক গ্রুপ আইডি দিন! (যেমন: `/addgroup -1001234567890`)")
    else:
        bot.send_message(message.chat.id, "📌 গ্রুপ আইডি দিয়ে যোগ করুন: `/addgroup -1001234567890`")
        bot.send_message(message.chat.id, "📌 অথবা গ্রুপ থেকে একটি মেসেজ ফরওয়ার্ড করুন।")

@bot.message_handler(commands=['removegroup'])
def remove_group_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) > 1:
        try:
            group_id = int(args[1])
            if group_id in target_groups:
                target_groups.remove(group_id)
                db["target_groups"] = target_groups
                save_db(db)
                bot.send_message(
                    message.chat.id,
                    f"✅ গ্রুপ বাদ দেওয়া হয়েছে!\n🆔 `{group_id}`",
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(message.chat.id, "❌ এই গ্রুপ যোগ করা নেই!")
        except:
            bot.send_message(message.chat.id, "❌ সঠিক গ্রুপ আইডি দিন! (যেমন: `/removegroup -1001234567890`)")
    else:
        if not target_groups:
            bot.send_message(message.chat.id, "❌ কোনো গ্রুপ যোগ করা নেই!")
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for gid in target_groups:
            try:
                chat = bot.get_chat(gid)
                name = chat.title or f"Group {gid}"
                markup.add(InlineKeyboardButton(f"🗑️ {name}", callback_data=f"remove_{gid}"))
            except:
                markup.add(InlineKeyboardButton(f"🗑️ {gid}", callback_data=f"remove_{gid}"))

        bot.send_message(message.chat.id, "🗑️ বাদ দেওয়ার জন্য গ্রুপ সিলেক্ট করুন:", reply_markup=markup)

@bot.message_handler(commands=['groups'])
def show_groups_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not target_groups:
        bot.send_message(message.chat.id, "❌ কোনো গ্রুপ যোগ করা নেই!")
        return

    msg = "📋 **আপনার গ্রুপ লিস্ট:**\n\n"
    for i, gid in enumerate(target_groups, 1):
        try:
            chat = bot.get_chat(gid)
            name = chat.title or "Unknown"
            msg += f"{i}. {name}\n   🆔 `{gid}`\n\n"
        except:
            msg += f"{i}. Group ID: `{gid}`\n\n"

    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "📢 যে মেসেজ ব্রডকাস্ট করতে চান সেটি পাঠান।")

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
        InlineKeyboardButton("💬 Reply", callback_data="toggle_reply")
    )

    status = (
        "⚙️ **বর্তমান সেটিংস:**\n\n"
        f"🎤 Voice: {'✅ ON' if settings.get('forward_voice', True) else '❌ OFF'}\n"
        f"🖼️ Photo: {'✅ ON' if settings.get('forward_photo', True) else '❌ OFF'}\n"
        f"🎬 Video: {'✅ ON' if settings.get('forward_video', True) else '❌ OFF'}\n"
        f"📁 Document: {'✅ ON' if settings.get('forward_document', True) else '❌ OFF'}\n"
        f"📝 Text: {'✅ ON' if settings.get('forward_text', True) else '❌ OFF'}\n"
        f"💬 Reply: {'✅ ON' if settings.get('reply_to_sender', False) else '❌ OFF'}"
    )

    bot.send_message(message.chat.id, status, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    pending_count = len([s for s in scheduled_forwards if s.get("status") == "pending"])
    
    stats_msg = (
        f"📊 **পরিসংখ্যান:**\n\n"
        f"📋 মোট গ্রুপ: `{len(target_groups)}` টি\n"
        f"⏰ পেন্ডিং ফরওয়ার্ড: `{pending_count}` টি\n"
        f"📅 সর্বশেষ আপডেট: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
    )

    bot.send_message(message.chat.id, stats_msg, parse_mode="Markdown")

@bot.message_handler(commands=['scheduled'])
def show_scheduled(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    pending = [s for s in scheduled_forwards if s.get("status") == "pending"]
    
    if not pending:
        bot.send_message(message.chat.id, "⏰ কোনো পেন্ডিং ফরওয়ার্ড নেই!")
        return
    
    msg = "⏰ **পেন্ডিং ফরওয়ার্ড লিস্ট:**\n\n"
    for i, item in enumerate(pending, 1):
        forward_time = datetime.fromisoformat(item["forward_time"])
        time_left = forward_time - datetime.now()
        minutes_left = int(time_left.total_seconds() / 60)
        
        content_type = item["content_type"]
        group_count = len(item["group_ids"])
        msg += f"{i}. {content_type.capitalize()} → {group_count} টি গ্রুপে\n"
        msg += f"   ⏰ {forward_time.strftime('%Y-%m-%d %H:%M')} ({minutes_left} মিনিট বাকি)\n\n"
    
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# -------------------- মেসেজ হ্যান্ডলার --------------------
@bot.message_handler(func=lambda message: True, content_types=[
    'text', 'voice', 'audio', 'document', 'photo', 'video', 'sticker', 'animation'
])
def handle_messages(message):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ আপনি এই বট ব্যবহার করতে পারেন না!")
        return

    if message.chat.type != "private":
        return

    if message.forward_from_chat:
        group_id = message.forward_from_chat.id
        if group_id not in target_groups:
            target_groups.append(group_id)
            db["target_groups"] = target_groups
            save_db(db)
            try:
                chat = bot.get_chat(group_id)
                name = chat.title or "Unknown"
                bot.send_message(
                    message.chat.id,
                    f"✅ **{name}** গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                    parse_mode="Markdown"
                )
            except:
                bot.send_message(
                    message.chat.id,
                    f"✅ গ্রুপ যোগ করা হয়েছে!\n🆔 `{group_id}`",
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(message.chat.id, "ℹ️ এই গ্রুপ ইতিমধ্যে যোগ করা আছে!")
        return

    if message.text:
        text = message.text.lower()
        if text in ["📋 group list", "/groups"]:
            show_groups_cmd(message)
            return
        if text in ["📢 broadcast", "/broadcast"]:
            broadcast_cmd(message)
            return
        if text in ["⚙️ settings", "/settings"]:
            settings_cmd(message)
            return
        if text in ["📊 stats", "/stats"]:
            stats_cmd(message)
            return
        if text in ["⏰ scheduled", "/scheduled"]:
            show_scheduled(message)
            return

    if not target_groups:
        bot.send_message(message.chat.id, "❌ কোনো গ্রুপ যোগ করা নেই! প্রথমে `/addgroup` দিয়ে গ্রুপ যোগ করুন।")
        return

    content_type = None
    file_id = None
    text = None
    caption = None

    if message.voice:
        content_type = "voice"
        file_id = message.voice.file_id
        caption = message.caption
    elif message.audio:
        content_type = "audio"
        file_id = message.audio.file_id
        caption = message.caption
    elif message.document:
        content_type = "document"
        file_id = message.document.file_id
        caption = message.caption
    elif message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
        caption = message.caption
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id
        caption = message.caption
    elif message.sticker:
        content_type = "sticker"
        file_id = message.sticker.file_id
    elif message.animation:
        content_type = "animation"
        file_id = message.animation.file_id
        caption = message.caption
    elif message.text:
        content_type = "text"
        text = message.text

    if not content_type:
        bot.send_message(message.chat.id, "❌ এই ধরনের ফাইল ফরওয়ার্ড করা সম্ভব নয়!")
        return

    markup = get_group_select_keyboard([], content_type, file_id, text, caption)
    bot.send_message(
        message.chat.id,
        "📋 **কোন গ্রুপে ফরওয়ার্ড করবেন?**\n\n"
        "✅ চেক করে সিলেক্ট করুন, তারপর অপশন নির্বাচন করুন।",
        parse_mode="Markdown",
        reply_markup=markup
    )

# -------------------- ইনলাইন বাটন --------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ আপনি এই বট ব্যবহার করতে পারেন না!", show_alert=True)
        return

    if call.data.startswith("set_time|"):
        parts = call.data.split("|")
        content_type = parts[1] if len(parts) > 1 else None
        file_id = parts[2] if len(parts) > 2 and parts[2] != "None" else None
        text = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        caption = parts[4] if len(parts) > 4 and parts[4] != "None" else None
        group_ids_str = parts[5] if len(parts) > 5 else ""
        
        if not group_ids_str:
            bot.answer_callback_query(call.id, "❌ কোনো গ্রুপ সিলেক্ট করা নেই!", show_alert=True)
            return
        
        group_ids = [int(gid) for gid in group_ids_str.split(",") if gid]
        
        markup = get_time_select_keyboard(content_type, file_id, text, caption, group_ids)
        bot.edit_message_text(
            "⏰ **কতক্ষণ পর ফরওয়ার্ড করবেন?**\n\n"
            "নিচের বাটন থেকে সময় সিলেক্ট করুন:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("time_select|"):
        parts = call.data.split("|")
        minutes = int(parts[1])
        content_type = parts[2] if len(parts) > 2 else None
        file_id = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        text = parts[4] if len(parts) > 4 and parts[4] != "None" else None
        caption = parts[5] if len(parts) > 5 and parts[5] != "None" else None
        group_ids_str = parts[6] if len(parts) > 6 else ""
        
        group_ids = [int(gid) for gid in group_ids_str.split(",") if gid]
        
        forward_time = schedule_forward(content_type, group_ids, minutes, file_id, text, caption)
        
        bot.edit_message_text(
            f"✅ **ফরওয়ার্ড শিডিউল করা হয়েছে!**\n\n"
            f"⏰ সময়: {forward_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"📋 গ্রুপ: {len(group_ids)} টি\n"
            f"📂 টাইপ: {content_type.capitalize()}\n\n"
            f"আপনি `/scheduled` দিয়ে পেন্ডিং লিস্ট দেখতে পারেন।",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, f"✅ {minutes} মিনিট পর ফরওয়ার্ড হবে!")
        return

    if call.data.startswith("custom_time|"):
        parts = call.data.split("|")
        content_type = parts[1] if len(parts) > 1 else None
        file_id = parts[2] if len(parts) > 2 and parts[2] != "None" else None
        text = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        caption = parts[4] if len(parts) > 4 and parts[4] != "None" else None
        group_ids_str = parts[5] if len(parts) > 5 else ""
        
        group_ids = [int(gid) for gid in group_ids_str.split(",") if gid]
        
        bot.edit_message_text(
            "✏️ **কত মিনিট পর ফরওয়ার্ড করবেন?**\n\n"
            "মিনিট সংখ্যা টাইপ করে পাঠান (যেমন: 30, 60, 120)",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)
        
        user_states[call.from_user.id] = {
            "action": "custom_time",
            "content_type": content_type,
            "file_id": file_id,
            "text": text,
            "caption": caption,
            "group_ids": group_ids
        }
        return

    if call.data.startswith("back_to_select|"):
        parts = call.data.split("|")
        content_type = parts[1] if len(parts) > 1 else None
        file_id = parts[2] if len(parts) > 2 and parts[2] != "None" else None
        text = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        caption = parts[4] if len(parts) > 4 and parts[4] != "None" else None
        group_ids_str = parts[5] if len(parts) > 5 else ""
        
        group_ids = [int(gid) for gid in group_ids_str.split(",") if gid]
        
        markup = get_group_select_keyboard(group_ids, content_type, file_id, text, caption)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("remove_"):
        group_id = int(call.data.split("remove_")[1])
        if group_id in target_groups:
            target_groups.remove(group_id)
            db["target_groups"] = target_groups
            save_db(db)
            bot.answer_callback_query(call.id, f"✅ গ্রুপ বাদ দেওয়া হয়েছে!")
            bot.edit_message_text(f"✅ গ্রুপ বাদ দেওয়া হয়েছে!", call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ গ্রুপ পাওয়া যায়নি!")
        return

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
        elif key == "reply":
            settings["reply_to_sender"] = not settings.get("reply_to_sender", False)

        db["settings"] = settings
        save_db(db)
        settings_cmd(call.message)
        bot.answer_callback_query(call.id, f"✅ সেটিংস আপডেট করা হয়েছে!")
        return

    if call.data.startswith("select_all|"):
        parts = call.data.split("|")
        content_type = parts[1] if len(parts) > 1 else None
        file_id = parts[2] if len(parts) > 2 and parts[2] != "None" else None
        text = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        caption = parts[4] if len(parts) > 4 and parts[4] != "None" else None
        
        current_selected = []
        for row in call.message.reply_markup.keyboard:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("toggle_group|"):
                    if "✅" in btn.text:
                        gid = int(btn.callback_data.split("|")[1])
                        current_selected.append(gid)
        
        if len(current_selected) == len(target_groups):
            selected_groups = []
        else:
            selected_groups = target_groups.copy()
        
        markup = get_group_select_keyboard(selected_groups, content_type, file_id, text, caption)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, f"✅ {len(selected_groups)} টি গ্রুপ সিলেক্ট করা হয়েছে!")
        return

    if call.data.startswith("toggle_group|"):
        parts = call.data.split("|")
        group_id = int(parts[1])
        content_type = parts[2] if len(parts) > 2 else None
        file_id = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        text = parts[4] if len(parts) > 4 and parts[4] != "None" else None
        caption = parts[5] if len(parts) > 5 and parts[5] != "None" else None
        
        current_selected = []
        for row in call.message.reply_markup.keyboard:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("toggle_group|"):
                    if "✅" in btn.text:
                        gid = int(btn.callback_data.split("|")[1])
                        current_selected.append(gid)
        
        if group_id in current_selected:
            current_selected.remove(group_id)
        else:
            current_selected.append(group_id)
        
        markup = get_group_select_keyboard(current_selected, content_type, file_id, text, caption)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, f"{len(current_selected)} টি গ্রুপ সিলেক্ট করা হয়েছে!")
        return

    if call.data.startswith("forward_selected|"):
        parts = call.data.split("|")
        content_type = parts[1] if len(parts) > 1 else None
        file_id = parts[2] if len(parts) > 2 and parts[2] != "None" else None
        text = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        caption = parts[4] if len(parts) > 4 and parts[4] != "None" else None
        group_ids_str = parts[5] if len(parts) > 5 else ""
        
        if not group_ids_str:
            bot.answer_callback_query(call.id, "❌ কোনো গ্রুপ সিলেক্ট করা নেই!", show_alert=True)
            return
        
        group_ids = [int(gid) for gid in group_ids_str.split(",") if gid]
        
        result = forward_to_specific_groups(content_type, group_ids, file_id, text, caption)
        bot.edit_message_text(
            f"✅ **ফরওয়ার্ড সম্পন্ন!**\n\n{result}",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "✅ ফরওয়ার্ড সম্পন্ন!")
        return

    if call.data == "cancel_forward":
        bot.edit_message_text(
            "❌ ফরওয়ার্ড বাতিল করা হয়েছে!",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id, "❌ বাতিল!")
        return

    if call.data == "show_groups":
        show_groups_cmd(call.message)
        bot.answer_callback_query(call.id)
        return

    if call.data == "broadcast":
        bot.send_message(call.message.chat.id, "📢 যে মেসেজ ব্রডকাস্ট করতে চান সেটি পাঠান।")
        bot.answer_callback_query(call.id)
        return

    if call.data == "show_stats":
        stats_cmd(call.message)
        bot.answer_callback_query(call.id)
        return

    if call.data == "show_settings":
        settings_cmd(call.message)
        bot.answer_callback_query(call.id)
        return

    if call.data == "add_group":
        bot.send_message(call.message.chat.id, "📌 গ্রুপ থেকে একটি মেসেজ ফরওয়ার্ড করুন অথবা `/addgroup -100xxxxxx` দিন।")
        bot.answer_callback_query(call.id)
        return

    if call.data == "remove_group":
        remove_group_cmd(call.message)
        bot.answer_callback_query(call.id)
        return

# -------------------- ইউজার স্টেট --------------------
user_states = {}

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        return
    
    if user_id in user_states and user_states[user_id].get("action") == "custom_time":
        try:
            minutes = int(message.text.strip())
            if minutes <= 0:
                bot.send_message(message.chat.id, "❌ দয়া করে ০ এর বেশি সংখ্যা দিন!")
                return
            
            state = user_states[user_id]
            content_type = state.get("content_type")
            file_id = state.get("file_id")
            text = state.get("text")
            caption = state.get("caption")
            group_ids = state.get("group_ids", [])
            
            if not group_ids:
                bot.send_message(message.chat.id, "❌ কোনো গ্রুপ সিলেক্ট করা নেই!")
                return
            
            forward_time = schedule_forward(content_type, group_ids, minutes, file_id, text, caption)
            
            bot.send_message(
                message.chat.id,
                f"✅ **ফরওয়ার্ড শিডিউল করা হয়েছে!**\n\n"
                f"⏰ সময়: {forward_time.strftime('%Y-%m-%d %H:%M')}\n"
                f"📋 গ্রুপ: {len(group_ids)} টি\n"
                f"📂 টাইপ: {content_type.capitalize()}\n\n"
                f"আপনি `/scheduled` দিয়ে পেন্ডিং লিস্ট দেখতে পারেন।",
                parse_mode="Markdown"
            )
            
            del user_states[user_id]
        except ValueError:
            bot.send_message(message.chat.id, "❌ দয়া করে সঠিক সংখ্যা দিন! (যেমন: 30, 60, 120)")
        return

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
    print("🤖 মাল্টি-গ্রুপ ফরওয়ার্ডার বট (টাইম সেট ভার্সন)")
    print(f"👤 অ্যাডমিন আইডি: {ADMIN_ID}")
    print(f"📋 মোট গ্রুপ: {len(target_groups)} টি")
    print("=" * 50)
    print("💡 বট চালু আছে! Ctrl+C চাপলে বন্ধ হবে।")

    schedule_thread = threading.Thread(target=check_scheduled_forwards, daemon=True)
    schedule_thread.start()
    logger.info("✅ শিডিউল চেক থ্রেড স্টার্ট করা হয়েছে!")

    try:
        bot.infinity_polling(timeout=30)
    except Exception as e:
        logger.error(f"বট ক্র্যাশ: {e}")
        save_db(db)
        time.sleep(5)
