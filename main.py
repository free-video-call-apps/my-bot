import telebot
import random
import time
from threading import Thread
from flask import Flask

# আপনার নতুন টোকেন ও আইডি (আমি আপডেট করে দিয়েছি)
TOKEN = '8709397620:AAEgvEbgxcbDQ3p0jIYYUyeHRRHNSjBfHrY'
ADMIN = 8049927326

bot = telebot.TeleBot(TOKEN)

# ডাটা রাখার জন্য ডিকশনারি
active_sessions = {} # {user_id: timer_message_id}

# Render Server সচল রাখার জন্য Flask
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run_flask(): app.run(host='0.0.0.0', port=8080)

# সেকেন্ডে সেকেন্ডে কাউন্টডাউন ফাংশন
def countdown(chat_id, msg_id, sub_id):
    total_seconds = 300 # ৫ মিনিট = ৩০০ সেকেন্ড
    while total_seconds > 0:
        # চেক করা: অ্যাডমিন ফাইল পাঠিয়ে দিলে এই লুপ বন্ধ হবে
        if chat_id not in active_sessions or active_sessions[chat_id] != msg_id:
            return 

        mins, secs = divmod(total_seconds, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        
        try:
            # প্রতি ১ সেকেন্ডে টাইম আপডেট হবে
            bot.edit_message_text(
                f"Your apk is being processed...\n\n"
                f"⌛ Estimated time left: {time_format}\n"
                f"🆔 Submission ID: {sub_id}",
                chat_id, msg_id
            )
        except Exception:
            # যদি মেসেজ ডিলিট হয়ে যায় তবে লুপ থামবে
            break
        
        time.sleep(1) # ১ সেকেন্ড অপেক্ষা
        total_seconds -= 1

@bot.message_handler(commands=['start'])
def start(m): 
    bot.reply_to(m, "👋 Welcome! Send your APK to protect it.")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    global active_sessions
    
    if not message.document.file_name.endswith('.apk'):
        return

    # ১. অ্যাডমিন (আপনি) ফাইল পাঠালে সরাসরি ইউজারকে যাবে
    if message.chat.id == ADMIN:
        target_user_id = None
        # বর্তমানে যে ইউজার ওয়েটিং এ আছে তাকে খুঁজে বের করা
        for uid in list(active_sessions.keys()):
            target_user_id = uid
            break
        
        if target_user_id:
            # আগের টাইমার মেসেজটি সাথে সাথে ডিলিট করে দেওয়া
            try:
                bot.delete_message(target_user_id, active_sessions[target_user_id])
            except:
                pass
            
            # ইউজারকে মডিফাইড ফাইল পাঠানো
            bot.send_document(target_user_id, message.document.file_id, caption="✅ Your APK has been processed! Here it is.")
            bot.reply_to(message, f"✅ সফল! ইউজার {target_user_id} এর টাইমার রিমুভ করা হয়েছে এবং ফাইল পাঠানো হয়েছে।")
            
            # সেশন ক্লিয়ার করা (যাতে লুপ বন্ধ হয়)
            del active_sessions[target_user_id]
        else:
            bot.reply_to(message, "❌ এই মুহূর্তে কোনো রিকোয়েস্ট পেন্ডিং নেই।")
        return

    # ২. সাধারণ ইউজার ফাইল পাঠালে
    user_id = message.chat.id
    sid = random.randint(100000, 999999)
    
    # অ্যাডমিনকে ফাইল পাঠানো
    bot.send_document(ADMIN, message.document.file_id, caption=f"📁 New APK!\nFrom: {message.from_user.first_name}\nID: {user_id}")
    
    # ইউজারের পাঠানো মেসেজ ডিলিট করা (চ্যাট পরিষ্কার রাখতে)
    try:
        bot.delete_message(user_id, message.message_id)
    except:
        pass

    # নতুন টাইমার মেসেজ পাঠানো
    sent_msg = bot.send_message(user_id, f"Your apk has been queued.\n\n⌛ Estimated time left: 05:00\n🆔 Submission ID: {sid}")
    
    # এই ইউজারের মেসেজ আইডি সেভ করা
    active_sessions[user_id] = sent_msg.message_id
    
    # ১ সেকেন্ড পর পর কাউন্টডাউন শুরু করা
    Thread(target=countdown, args=(user_id, sent_msg.message_id, sid)).start()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()    bot.infinity_polling()
