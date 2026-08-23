import telebot
import requests
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread

# ১. আপনার টেলিগ্রাম বোটের টোকেন
API_TOKEN = '8902395736:AAEv-wNNitsdZZd2noWosTE9dBMlMqQt9Zo' 
bot = telebot.TeleBot(API_TOKEN)

# ২. GameSkinBo API Key
GAME_API_KEY = '2ehSS19Ys1yc4rUzcJf5GRLwgYMCz6ESeiCrU0rB45o'

# রেন্ডারে পোর্ট ধরে রাখার জন্য ছোট ফ্লাস্ক সার্ভার (Render Port Binding Fix)
app = Flask('')

@app.route('/')
def home():
    return "TY INFO CHECKER Bot is Active 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ডেট ফরম্যাট করার ফাংশন
def format_date(unix_timestamp):
    if not unix_timestamp:
        return 'N/A'
    try:
        date = datetime.fromtimestamp(int(unix_timestamp))
        return date.strftime('%b %d, %Y')
    except:
        return 'N/A'

user_state = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🔍 CHECK PLAYER INFO", callback_data="start_info"),
        InlineKeyboardButton("👑 OWNER PROFILE", url="https://t.me/MrTripleR_YT")
    )
    
    welcome_text = (
        "┏━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃    💎 TY INFO CHECKER 💎    ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "⚡ 𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝙋𝙍𝙀𝙈𝙄𝙐𝙈 𝘽𝙊𝙏 ⚡\n\n"
        "Welcome to the ultimate Free Fire Profile Checker bot. "
        "Click the button below to check any player profile instantly with professional stats!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👑 Owner: @MrTripleR_YT\n"
        "⚡ Powered by: TYNEX OFFICIAL"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_info")
def callback_query(call):
    user_state[call.message.chat.id] = "waiting_for_uid"
    bot.answer_callback_query(call.id, "Please enter the Player UID now!")
    bot.send_message(
        call.message.chat.id, 
        "✍️ **Please send the Free Fire UID below:**\n*(Example: 2287422745)*", 
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['info'])
def info_command(message):
    user_state[message.chat.id] = "waiting_for_uid"
    bot.reply_to(
        message, 
        "✍️ **Please send the Free Fire UID below:**\n*(Example: 2287422745)*", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_uid")
def process_uid(message):
    uid = message.text.strip()
    
    if not uid.isdigit() or len(uid) < 5 or len(uid) > 12:
        bot.reply_to(message, "❌ **Invalid UID!** Please enter a valid Free Fire UID (Numbers only).", parse_mode="Markdown")
        return
    
    user_state[message.chat.id] = None
    process_msg = bot.reply_to(message, "⚡ [ ᴄ𝙊𝙉𝙉𝙀𝘾𝙏𝙄𝙉𝙂 𝙏𝙊 𝙎𝙀𝙍𝙑𝙀𝙍... ]\n🔍 Fetching professional stats...")

    api_url = f"https://api.gameskinbo.com/ff-info/get?uid={uid}"
    headers = {'x-api-key': GAME_API_KEY}

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        
        try:
            data = response.json()
        except:
            data = {}

        if response.status_code == 200 and 'AccountInfo' in data and data.get('AccountInfo'):
            acc = data.get('AccountInfo', {})
            prof = data.get('AccountProfileInfo', {})
            guild = data.get('GuildInfo', {})
            social = data.get('SocialInfo', {})
            pet = data.get('PetInfo', {})
            credit = data.get('CreditScoreInfo', {})
            eq = data.get('EquippedItemsInfo', {})

            def val(v, default="N/A"):
                return v if v is not None and v != "" else default

            created_date = format_date(acc.get('AccountCreateTime'))
            last_login_date = format_date(acc.get('AccountLastLogin'))

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔄 CHECK ANOTHER UID", callback_data="start_info"))

            result_text = (
                "┏━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃     💎 TY INFO CHECKER       ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"👤 Nickname      :  {val(acc.get('AccountName'))}\n"
                f"🆔 UID           :  {uid}\n"
                f"🌍 Region        :  {val(acc.get('AccountRegion'))}\n"
                f"⭐ Level         :  LV. {val(acc.get('AccountLevel'))}\n"
                f"❤️ Total Likes   :  {val(acc.get('AccountLikes'))}\n"
                f"🔥 Total EXP     :  {val(acc.get('AccountEXP'))}\n"
                f"🛡️ Credit Score  :  {val(credit.get('creditScore'))}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "       📅 ACCOUNT TIMELINE       \n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📅 Created Date  :  {created_date}\n"
                f"🕒 Last Login    :  {last_login_date}\n"
                f"🎮 Game Version  :  {val(data.get('ReleaseVersion'))}\n"
                f"🏆 Current Season:  {val(acc.get('AccountSeasonId'))}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "       🏆 RANK STATISTICS       \n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🎖️ BR Max Rank   :  {val(prof.get('BrMaxRank'))}\n"
                f"⭐ BR Points     :  {val(prof.get('BrRankPoint'))}\n"
                f"🎯 CS Max Rank   :  {val(prof.get('CsMaxRank'))}\n"
                f"⭐ CS Points     :  {val(prof.get('CsRankPoint'))}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "       🛡️ GUILD DETAILS       \n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🏰 Guild Name    :  {val(guild.get('GuildName'))}\n"
                f"🆔 Guild ID      :  {val(guild.get('GuildID'))}\n"
                f"👥 Members       :  {val(guild.get('GuildMember'))} / {val(guild.get('GuildCapacity'))}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "       📌 OTHERS & ASSETS       \n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🐾 Pet Level     :  {val(pet.get('level'))}\n"
                f"🎟️ Elite Badges  :  {val(eq.get('EquippedBPBadges'))}\n"
                f"✍️ Signature     :  {val(social.get('signature'))}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👑 Owner: @MrTripleR_YT\n"
                "⚡ Powered by: TYNEX OFFICIAL"
            )
            bot.edit_message_text(result_text, message.chat.id, process_msg.message_id, reply_markup=markup)
        else:
            bot.edit_message_text(
                "┏━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃     ❌ INVALID UID          ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"🆔 UID: `{uid}`\n\n"
                "⚠️ **Player not found!** Please check the UID and try again with a correct Free Fire UID.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👑 Owner: @MrTripleR_YT\n"
                "⚡ Powered by: TYNEX OFFICIAL",
                message.chat.id,
                process_msg.message_id,
                parse_mode="Markdown"
            )

    except Exception:
        bot.edit_message_text(
            "❌ **Connection Error!** Unable to reach the server right now. Please try again later.",
            message.chat.id,
            process_msg.message_id
        )

if __name__ == "__main__":
    keep_alive()
    print("🤖 TY INFO CHECKER Bot সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()