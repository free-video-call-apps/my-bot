import telebot
import random
import time
from threading import Thread
from flask import Flask
import os

# আপনার নতুন টোকেন ও আইডি
TOKEN = '8709397620:AAEgvEbgxcbDQ3p0jIYYUyeHRRHNSjBfHrY'
ADMIN = 8049927326

bot = telebot.TeleBot(TOKEN)
active_sessions = {}

# Render সার্ভারকে জাগিয়ে রাখার জন্য Flask
app = Flask('')
@app.route('/')
def home():
    return "Bot is Live 24/7"

def run_flask():
    # Render-এর জন্য নির্দিষ্ট পোর্ট ধরা
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# কাউন্টডাউন ফাংশন
def countdown(chat_id, msg_id, sub_id):
    total_seconds = 300 
    while total_seconds > 0:
        if chat_id not in active_sessions or active_sessions[chat_id] != msg_id:
            return 
        mins, secs = divmod(total_seconds, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        try:
            bot.edit_message_text(
                f"Your apk is being processed...\n\n⌛ Estimated time left: {time_format}\n🆔 Submission ID: {sub_id}",
                chat_id, msg_id
            )
        except:
            break
        time.sleep(1)
        total_seconds -= 1

@bot.message_handler(commands=['start'])
def start(m): 
    bot.reply_to(m, "👋 Welcome! Our protection service is active 24/7.")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    global active_sessions
    if not message.document.file_name.endswith('.apk'):
        return

    if message.chat.id == ADMIN:
        target_user_id = next(iter(active_sessions), None)
        if target_user_id:
            try:
                bot.delete_message(target_user_id, active_sessions[target_user_id])
            except: pass
            bot.send_document(target_user_id, message.document.file_id, caption="✅ Your APK has been processed!")
            bot.reply_to(message, "✅ সফল!")
            del active_sessions[target_user_id]
        else:
            bot.reply_to(message, "❌ পেন্ডিং নেই।")
        return

    user_id = message.chat.id
    sid = random.randint(100000, 999999)
    bot.send_document(ADMIN, message.document.file_id, caption=f"📁 New APK!\nFrom: {message.from_user.first_name}\nID: {user_id}")
    sent_msg = bot.send_message(user_id, f"Your apk has been queued.\n\n⌛ Estimated time left: 05:00\n🆔 Submission ID: {sid}")
    active_sessions[user_id] = sent_msg.message_id
    Thread(target=countdown, args=(user_id, sent_msg.message_id, sid)).start()

# এই অংশটুকু আপনার ফাইলে আছে কি না চেক করুন
if __name__ == "__main__":
    # Flask সার্ভার চালু করা (থ্রেড দিয়ে)
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    # বট পোলিং শুরু যাতে অলটাইম কানেক্টেড থাকে
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
