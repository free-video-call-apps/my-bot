import telebot
import random
import time
import os
from threading import Thread
from flask import Flask

# আপনার টোকেন ও আইডি
TOKEN = '8615930482:AAGmrjUMvQn1iUIne4rljpRI0lG4jaRNUWc'
ADMIN = 8049927326

bot = telebot.TeleBot(TOKEN)
last_user_id = None

# Render Server সচল রাখার জন্য
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run_flask(): app.run(host='0.0.0.0', port=8080)

# সেকেন্ডে সেকেন্ডে কাউন্টডাউন ফাংশন
def countdown(chat_id, msg_id, sub_id):
    total_seconds = 300 # ৫ মিনিট = ৩০০ সেকেন্ড
    
    while total_seconds > 0:
        mins, secs = divmod(total_seconds, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        
        try:
            # প্রতি ৫ সেকেন্ড পর পর মেসেজ আপডেট হবে (টেলিগ্রাম লিমিট রক্ষার জন্য)
            # আপনি চাইলে ৫ এর জায়গায় ১ দিতে পারেন, তবে ৫ দিলে বট ব্যান হওয়ার ভয় থাকে না
            if total_seconds % 5 == 0: 
                bot.edit_message_text(
                    f"Your apk is being processed...\n\n"
                    f"⌛ Estimated time left: {time_format}\n"
                    f"🆔 Submission ID: {sub_id}",
                    chat_id, msg_id
                )
        except:
            break
            
        time.sleep(1)
        total_seconds -= 1
        
    try:
        bot.send_message(chat_id, "⌛ Your APK is almost ready! Please wait, Admin is sending it.")
    except:
        pass

@bot.message_handler(commands=['start'])
def start(m): 
    bot.reply_to(m, "👋 Welcome! Send your APK to protect it.")

@bot.message_handler(content_types=['document'])
def handle(m):
    global last_user_id
    if not m.document.file_name.endswith('.apk'):
        bot.reply_to(m, "❌ Please send a valid APK file.")
        return
    
    if m.chat.id == ADMIN:
        if last_user_id:
            bot.send_document(last_user_id, m.document.file_id, caption="✅ Your APK has been processed!")
            bot.reply_to(m, f"✅ সফল! ইউজার {last_user_id} কে পাঠানো হয়েছে।")
            last_user_id = None
        else:
            bot.reply_to(m, "❌ কোনো রিকোয়েস্ট পেন্ডিং নেই।")
        return

    last_user_id = m.chat.id
    sid = random.randint(100000, 999999)
    
    res = bot.reply_to(m, f"Your apk has been queued.\n\n⌛ Estimated time left: 05:00\n🆔 Submission ID: {sid}")
    
    # অ্যাডমিনকে জানানো
    bot.send_document(ADMIN, m.document.file_id, caption=f"📁 New APK!\nFrom: {m.from_user.first_name}\nID: {m.chat.id}")
    
    # কাউন্টডাউন শুরু
    Thread(target=countdown, args=(m.chat.id, res.message_id, sid)).start()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
