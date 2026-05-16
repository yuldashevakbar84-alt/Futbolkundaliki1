"""
⚽ Futbol Mashg'ulot Bot
Jamoa uchun kundalik mashg'ulotni kuzatib boruvchi Telegram bot

O'rnatish:
    pip install python-telegram-bot==20.7

Ishlatish:
    1. BotFather dan token oling
    2. BOT_TOKEN ni o'zgartiring
    3. python futbol_bot.py
"""

import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ========================
# SOZLAMALAR
# ========================
BOT_TOKEN = 8627118427:AAF7zjvJL7BbHPpQ1BZyg5n4vF-eX6GBfYs
DATA_FILE = "mashgulot_data.json"

# Haftalik mashg'ulot dasturi
HAFTALIK_DASTUR = {
    0: {"kun": "Dushanba", "mavzu": "Asos — Dribbling", "emoji": "⚽", "dam": False},
    1: {"kun": "Seshanba", "mavzu": "Aldash harakatlari", "emoji": "🔥", "dam": False},
    2: {"kun": "Chorshanba", "mavzu": "Tezlik dribblingi", "emoji": "⚡", "dam": False},
    3: {"kun": "Payshanba", "mavzu": "Dam olish", "emoji": "😴", "dam": True},
    4: {"kun": "Juma", "mavzu": "1v1 mashq", "emoji": "🥊", "dam": False},
    5: {"kun": "Shanba", "mavzu": "O'yin kuni", "emoji": "🏆", "dam": False},
    6: {"kun": "Yakshanba", "mavzu": "To'liq dam", "emoji": "🛌", "dam": True},
}


# ========================
# MA'LUMOTLAR SAQLASH
# ========================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id, name):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "ism": name,
            "jami": 0,
            "bu_hafta": 0,
            "streak": 0,
            "oxirgi_kun": None,
            "tarix": []
        }
    return data[uid]


# ========================
# BUYRUQLAR
# ========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    get_user(data, user.id, user.first_name)
    save_data(data)

    matn = (
        f"⚽ *Assalomu alaykum, {user.first_name}!*\n\n"
        "Bu bot jamoangiz uchun futbol mashg'ulotlarini kuzatib boradi.\n\n"
        "*Buyruqlar:*\n"
        "✅ /bajardim — bugungi mashg'ulotni belgilash\n"
        "📊 /reyting — jamoa reytingini ko'rish\n"
        "📅 /dastur — haftalik mashg'ulot dasturi\n"
        "👤 /mening — mening statistikam\n"
        "ℹ️ /yordam — barcha buyruqlar\n\n"
        "Mashg'ulotni boshlaymizmi? 💪"
    )
    await update.message.reply_text(matn, parse_mode="Markdown")


async def bajardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bugun = datetime.now().strftime("%Y-%m-%d")
    hafta_kuni = datetime.now().weekday()
    kun_info = HAFTALIK_DASTUR[hafta_kuni]

    # Dam olish kuni
    if kun_info["dam"]:
        await update.message.reply_text(
            f"{kun_info['emoji']} Bugun *{kun_info['kun']}* — dam olish kuni!\n\n"
            "Hozir dam oling, ertaga yanada kuchli bo'lib kelasiz 💪",
            parse_mode="Markdown"
        )
        return

    data = load_data()
    foydalanuvchi = get_user(data, user.id, user.first_name)

    # Bugun allaqachon belgilangan
    if foydalanuvchi["oxirgi_kun"] == bugun:
        await update.message.reply_text(
            "✅ Siz bugungi mashg'ulotni allaqachon belgilagansiz!\n\n"
            f"*{kun_info['emoji']} {kun_info['mavzu']}* — bajarildi!\n\n"
            "Ertangi mashg'ulotni ham o'tkazib yubormang 🔥",
            parse_mode="Markdown"
        )
        return

    # Streak hisoblash
    kecha = datetime.now()
    streak = foydalanuvchi["streak"]
    if foydalanuvchi["oxirgi_kun"]:
        from datetime import timedelta
        oxirgi = datetime.strptime(foydalanuvchi["oxirgi_kun"], "%Y-%m-%d")
        farq = (datetime.now() - oxirgi).days
        if farq == 1:
            streak += 1
        elif farq > 1:
            streak = 1
    else:
        streak = 1

    # Yangilash
    foydalanuvchi["jami"] += 1
    foydalanuvchi["bu_hafta"] += 1
    foydalanuvchi["streak"] = streak
    foydalanuvchi["oxirgi_kun"] = bugun
    foydalanuvchi["tarix"].append(bugun)
    save_data(data)

    # Streak xabari
    streak_matn = ""
    if streak >= 7:
        streak_matn = f"\n🔥 *{streak} kunlik seriya!* Ajoyib!"
    elif streak >= 3:
        streak_matn = f"\n⚡ *{streak} kun ketma-ket!* Davom et!"

    matn = (
        f"✅ *Bajarildi! Zo'r, {user.first_name}!*\n\n"
        f"{kun_info['emoji']} Bugungi mashg'ulot: *{kun_info['mavzu']}*\n\n"
        f"📊 Jami: *{foydalanuvchi['jami']} kun*\n"
        f"🗓 Bu hafta: *{foydalanuvchi['bu_hafta']} kun*"
        f"{streak_matn}\n\n"
        "Mashg'ulotni davom ettiring! 💪"
    )
    await update.message.reply_text(matn, parse_mode="Markdown")


async def reyting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    if not data:
        await update.message.reply_text("Hali hech kim ro'yxatga kirmagan.")
        return

    # Jami bo'yicha saralash
    tartiblangan = sorted(
        data.items(),
        key=lambda x: x[1].get("jami", 0),
        reverse=True
    )

    matn = "🏆 *JAMOA REYTINGI*\n"
    matn += "━━━━━━━━━━━━━━━━\n\n"

    medallar = ["🥇", "🥈", "🥉"]

    for i, (uid, info) in enumerate(tartiblangan):
        medal = medallar[i] if i < 3 else f"{i+1}."
        streak = info.get("streak", 0)
        streak_ico = f" 🔥{streak}" if streak >= 3 else ""
        matn += (
            f"{medal} *{info['ism']}*{streak_ico}\n"
            f"   Jami: {info['jami']} kun | Bu hafta: {info['bu_hafta']} kun\n\n"
        )

    matn += "━━━━━━━━━━━━━━━━\n"
    matn += f"👥 Jamoa a'zolari: {len(data)} ta"

    await update.message.reply_text(matn, parse_mode="Markdown")


async def dastur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bugun = datetime.now().weekday()
    matn = "📅 *HAFTALIK MASHG'ULOT DASTURI*\n"
    matn += "━━━━━━━━━━━━━━━━\n\n"

    for kuni, info in HAFTALIK_DASTUR.items():
        belgi = "👉 " if kuni == bugun else "   "
        dam_matn = " *(Dam)*" if info["dam"] else ""
        matn += f"{belgi}{info['emoji']} *{info['kun']}* — {info['mavzu']}{dam_matn}\n"

    matn += "\n━━━━━━━━━━━━━━━━\n"
    matn += "⏱ Har mashg'ulot: 1 soat\n"
    matn += "🎯 Texnika: Dribbling"

    await update.message.reply_text(matn, parse_mode="Markdown")


async def mening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    info = get_user(data, user.id, user.first_name)
    save_data(data)

    streak = info.get("streak", 0)
    streak_bar = "🔥" * min(streak, 10)

    matn = (
        f"👤 *{info['ism']} — Statistika*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"📊 Jami mashg'ulotlar: *{info['jami']} kun*\n"
        f"🗓 Bu hafta: *{info['bu_hafta']} kun*\n"
        f"⚡ Ketma-ket seriya: *{streak} kun*\n"
        f"{streak_bar}\n\n"
    )

    # Oxirgi 5 kun
    if info["tarix"]:
        matn += "📆 *Oxirgi mashg'ulotlar:*\n"
        for sana in info["tarix"][-5:][::-1]:
            matn += f"  ✅ {sana}\n"

    await update.message.reply_text(matn, parse_mode="Markdown")


async def yordam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = (
        "⚽ *FUTBOL BOT — BUYRUQLAR*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "✅ /bajardim — bugungi mashg'ulotni belgilash\n"
        "📊 /reyting — jamoa reytingini ko'rish\n"
        "📅 /dastur — haftalik jadval\n"
        "👤 /mening — o'z statistikam\n"
        "🚀 /start — botni qayta ishga tushirish\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "💡 *Maslahat:* Har kuni /bajardim deb yozing!\n"
        "Jamoangizni guruhga qo'shing va raqobatlashing 🏆"
    )
    await update.message.reply_text(matn, parse_mode="Markdown")


async def noma_lum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Buyruq tanilmadi.\n/yordam deb yozing — barcha buyruqlar ro'yxati.",
    )


# ========================
# ASOSIY FUNKSIYA
# ========================

def main():
    print("⚽ Futbol Bot ishga tushmoqda...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Buyruqlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bajardim", bajardim))
    app.add_handler(CommandHandler("reyting", reyting))
    app.add_handler(CommandHandler("dastur", dastur))
    app.add_handler(CommandHandler("mening", mening))
    app.add_handler(CommandHandler("yordam", yordam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, noma_lum))

    print("✅ Bot tayyor! To'xtatish uchun Ctrl+C bosing.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
