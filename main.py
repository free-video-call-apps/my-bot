import telebot
import random
import time
from threading import Thread
from flask import Flask
import os

# আপনার তথ্য
API_TOKEN = '8615930482:AAGmrjUMvQn1iUIne4rljpRI0lG4jaRNUWc'
ADMIN_ID = 8049927326 

bot = telebot.TeleBot(API_TOKEN)
last_user_id = None 

# Render-এর জন্য ওয়েব সার্ভার
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def start_countdown(user_id, message_id, sub_id):
    minutes_left = 5
    while minutes_left > 0:
        time.sleep(60)
        minutes_left -= 1
        try:
            new_text = (
                f"Your apk is being processed...\n\n"
                f"Estimated time left: {minutes_left} minutes.\n"
                f"Submission ID: {sub_id}"
            )
            bot.edit_message_text(new_text, user_id, message_id)
        except:
            break
    if minutes_left == 0:
        try:
            bot.send_message(user_id, "⌛ Your APK is almost ready. Admin is sending it now!")
        except:
            pass

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Welcome! Send your APK to protect it.")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    global last_user_id
    if message.document.file_name.endswith('.apk'):
        if message.chat.id == ADMIN_ID:
            if last_user_id:
                bot.send_message(last_user_id, "✅ Your APK has been processed! Here is your file:")
                bot.send_document(last_user_id, message.document.file_id)
                bot.reply_to(message, f"✅ সফল! ইউজার {last_user_id} এর কাছে পাঠানো হয়েছে।")
                last_user_id = None
            else:
                bot.reply_to(message, "❌ কোনো রিকোয়েস্ট পেন্ডিং নেই।")
            return

        last_user_id = message.chat.id
        sub_id = random.randint(100000, 999999)
        initial_response = (
            f"Your apk has been queued. Generally the server can process one apk within 5 minutes.\n\n"
            f"Submission ID: {sub_id}\n"
            f"Queue position: 1"
        )
        sent_msg = bot.reply_to(message, initial_response)
        
        try:
            bot.send_document(ADMIN_ID, message.document.file_id, caption=f"📁 New APK!\nFrom: {message.from_user.first_name}\nID: {message.chat.id}")
        except:
            pass
            
        Thread(target=start_countdown, args=(message.chat.id, sent_msg.message_id, sub_id)).start()

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("বটটি চালু হচ্ছে...")
    bot.infinity_polling()
