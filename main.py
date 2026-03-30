import telebot
import random
import time
from threading import Thread
from flask import Flask

# ১. আপনার বটের তথ্য (এখানেই সব ঠিক থাকবে)
API_TOKEN = '8615930482:AAGmrjUMvQn1iUIne4rljpRI0lG4jaRNUWc'
ADMIN_ID = 8049927326 

bot = telebot.TeleBot(API_TOKEN)
last_user_id = None # সর্বশেষ ইউজারের আইডি মনে রাখার জন্য

# ২. Render সার্ভারে বটটি ২৪ ঘণ্টা চালু রাখার জন্য একটি ছোট ওয়েব সার্ভার
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running"

def run():
    app.run(host='0.0.0.0', port=8080)

# ৩. টাইমার বা কাউন্টডাউন ফাংশন (যা ৫ মিনিট থেকে কমতে থাকবে)
def start_countdown(user_id, message_id, sub_id):
    minutes_left = 5
    while minutes_left > 0:
        time.sleep(60) # ১ মিনিট অপেক্ষা
        minutes_left -= 1
        try:
            new_text = (
                f"Your apk is being processed...\n\n"
                f"Estimated time left: {minutes_left} minutes.\n"
                f"Submission ID: {sub_id}"
            )
            bot.edit_message_text(new_text, user_id, message_id)
        except:
            break # যদি মেসেজ ডিলিট হয়ে যায় তবে লুপ বন্ধ হবে
            
    if minutes_left == 0:
        try:
            bot.send_message(user_id, "⌛ Your APK is almost ready. Admin is sending it now!")
        except:
            pass

# ৪. বটের মেইন কাজ শুরু
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "স্বাগতম মালিক! ইউজাররা অ্যাপ পাঠালে আমি আপনাকে দেব। আপনি শুধু ফাইলটি এখানে সেন্ড করবেন।")
    else:
        bot.reply_to(message, "👋 Welcome! Send your APK to protect or bypass it with our secure server.")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    global last_user_id
    
    # ফাইলটি এপিকে কি না চেক করা
    if message.document.file_name.endswith('.apk'):
        
        # অ্যাডমিন (আপনি) যদি ফাইল সেন্ড করেন (কোনো রিপ্লাই ছাড়াই)
        if message.chat.id == ADMIN_ID:
            if last_user_id:
                bot.send_message(last_user_id, "✅ Your APK has been processed and protected! Here is your file:")
                bot.send_document(last_user_id, message.document.file_id)
                bot.reply_to(message, f"✅ সফল! অ্যাপটি ইউজারের (ID: {last_user_id}) কাছে পাঠানো হয়েছে।")
                last_user_id = None # কাজ শেষ হলে আইডি ক্লিয়ার
            else:
                bot.reply_to(message, "❌ এই মুহূর্তে কোনো ইউজারের রিকোয়েস্ট পেন্ডিং নেই।")
            return

        # সাধারণ ইউজার যদি এপিকে পাঠায়
        last_user_id = message.chat.id # ইউজারের আইডি সেভ করা হলো
        sub_id = random.randint(100000, 999999)
        
        # ইউজারকে কিউ মেসেজ দেওয়া (টাইমার সহ)
        initial_response = (
            f"Your apk has been queued. Generally the server can process one apk within 5 minutes.\n\n"
            f"Submission ID: {sub_id}\n"
            f"Queue position: 1"
        )
        sent_msg = bot.reply_to(message, initial_response)
        
        # অ্যাডমিনকে (আপনাকে) ফাইলটি পাঠানো
        admin_info = f"📁 New APK for Bypass!\nUser: {message.from_user.first_name}\nID: {message.chat.id}\n\nআপনি শুধু মডিফাইড ফাইলটি এখানে সেন্ড করুন, আমি ইউজারের কাছে পৌঁছে দেব।"
        bot.send_document(ADMIN_ID, message.document.file_id, caption=admin_info)

        # কাউন্টডাউন শুরু করা (ব্যাকগ্রাউন্ড থ্রেড)
        Thread(target=start_countdown, args=(message.chat.id, sent_msg.message_id, sub_id)).start()

    else:
        bot.reply_to(message, "❌ Please send a valid APK file.")

# ৫. সার্ভার এবং বট একসাথে চালু করা
if __name__ == "__main__":
    Thread(target=run).start() # ওয়েব সার্ভার চালু
    print("বটটি এখন অনলাইন সার্ভারে চালু হচ্ছে...")
    bot.polling(none_stop=True)
