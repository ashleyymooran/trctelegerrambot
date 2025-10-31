import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن‌ها از متغیرهای محیطی
TELEGRAM_TOKEN = os.environ.get('BOT_TOKEN', '8461212300:AAFmTxio3YON-C2FVOrnERS2cQErYO09Rms')
TRUECALLER_API_KEY = os.environ.get('TRUECALLER_API_KEY')

# صفحه اصلی برای چک کردن سلامت ربات
@app.route('/')
def home():
    return "✅ ربات Truecaller در حال اجراست! /start را در تلگرام بزنید."

# کال‌بک برای Truecaller (ضروری)
@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    logger.info(f"Callback received: {data}")
    return jsonify({"status": "success"})

# دستور /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f"👋 سلام {user.first_name}!\n\n"
        "🤖 من ربات جستجوی شماره تلفن هستم.\n\n"
        "📞 لطفاً شماره تلفن را به فرمت بین‌المللی ارسال کنید:\n"
        "مثال: +989123456789"
    )

# پردازش شماره تلفن
def search_phone_number(update: Update, context: CallbackContext) -> None:
    phone_number = update.message.text.strip()
    
    # اعتبارسنجی شماره
    if not phone_number.startswith('+'):
        update.message.reply_text(
            "❌ شماره باید با + شروع شود!\n"
            "✅ مثال صحیح: +989123456789"
        )
        return
    
    if len(phone_number) < 10:
        update.message.reply_text("❌ شماره بسیار کوتاه است!")
        return

    update.message.reply_text("🔍 در حال جستجو...")

    # فراخوانی API Truecaller
    url = f"https://api.truecaller.com/v2/search?phone={phone_number}"
    headers = {
        "Authorization": f"Bearer {TRUECALLER_API_KEY}",
        "User-Agent": "TelegramTruecallerBot/1.0",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Truecaller API Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                info = data['data'][0]
                name = info.get('name', '📛 نام یافت نشد')
                city = info.get('city', '🏙 شهر یافت نشد')
                carrier = info.get('carrier', '📡 اپراتور یافت نشد')
                country = info.get('country', '🌍 کشور یافت نشد')
                
                message = (
                    f"📊 **نتایج جستجو:**\n"
                    f"📞 **شماره:** `{phone_number}`\n"
                    f"👤t Update
f{name}\n"
                    f"🏙gram impor{city}\n"
                    f"🌍gram import{country}\n"
                    f"📡m import Updat{carrier}"
                )
            else:
                message = "❌ هیچ اطلاعاتی برای این شماره یافت نشد."
        elif response.status_code == 401:
            message = "🔑 خطای API Key! لطفا Truecaller API Key را بررسی کنید."
        elif response.status_code == 429:
            message = "⏳ محدودیت درخواست! لطفا چند لحظه صبر کنید."
        else:
            message = f"❌ خطای API: کد {response.status_code}"
            
    except requests.exceptions.Timeout:
        message = "⏰ timeout! لطفا دوباره تلاش کنید."
    except requests.exceptions.ConnectionError:
        message = "🌐 خطای اتصال به اینترنت!"
    except Exception as e:
        logger.error(f"Error: {e}")
        message = "⚠️ خطای ناشناخته! لطفا بعدا تلاش کنید."

    update.message.reply_text(message)

# هندلر خطا
def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f"Update {update} caused error {context.error}")

def main():
    # ایجاد updater و dispatcher
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # اضافه کردن هندلرها
    dispatcher.
add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search_phone_number))
    dispatcher.add_error_handler(error_handler)

    # تنظیمات webhook برای Render
    PORT = int(os.environ.get('PORT', 5000))
    
    # 🔥 IMPORTANT: نام اپلیکیشن Render خودت رو اینجا بذار
    APP_NAME = "my-updownsug-umazat"  # از لاگ‌ها گرفتم
    
    webhook_url = f"https://{APP_NAME}.onrender.com/{TELEGRAM_TOKEN}"
    
    # راه‌اندازی webhook
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )
    
    logger.info(f"🤖 ربات راه‌اندازی شد! Webhook: {webhook_url}")
    updater.idle()

ifs://api.tr== '__main__':
    main()