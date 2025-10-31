# src/bot.py
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import requests
from flask import Flask, request, jsonify

# ----------------------------------------------------------------------
# 1. تنظیمات Flask (برای health-check و webhook)
# ----------------------------------------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
    return "ربات Truecaller در حال اجراست! /start را در تلگرام بزنید."


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    return Response("ol", status=200)
    data = request.get_json()
    logger.info(f"Callback received: {data}")
    return jsonify({"status": "success"})


# ----------------------------------------------------------------------
# 2. تنظیمات لاگ
# ----------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# 3. توکن‌ها – فقط از متغیرهای محیطی
# ----------------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
TRUECALLER_API_KEY = os.getenv("TRUECALLER_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN در متغیرهای محیطی تنظیم نشده است.")
if not TRUECALLER_API_KEY:
    raise RuntimeError("TRUECALLER_API_KEY در متغیرهای محیطی تنظیم نشده است.")


# ----------------------------------------------------------------------
# 4. دستور /start
# ----------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name}!\n\n"
        "من ربات جستجوی شماره تلفن هستم.\n\n"
        "لطفاً شماره تلفن را به فرمت بین‌المللی ارسال کنید:\n"
        "مثال: +989123456789"
    )


# ----------------------------------------------------------------------
# 5. جستجوی شماره تلفن
# ----------------------------------------------------------------------
async def search_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone_number = update.message.text.strip()

    # ----- اعتبارسنجی -----
    if not phone_number.startswith("+"):
        await update.message.reply_text(
            "شماره باید با + شروع شود!\n"
            "مثال صحیح: +989123456789"
        )
        return

    if len(phone_number) < 10:
        await update.message.reply_text("شماره بسیار کوتاه است!")
        return

    await update.message.reply_text("در حال جستجو...")

    # ----- فراخوانی API Truecaller -----
    url = f"https://api.truecaller.com/v2/search?phone={phone_number}"
    headers = {
        "Authorization": f"Bearer {TRUECALLER_API_KEY}",
        "User-Agent": "TelegramTruecallerBot/1.0",
        "Accept": "application/json",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Truecaller API status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            if data.get("data"):
                info = data["data"][0]
                name = info.get("name", "نام یافت نشد")
                city = info.get("city", "شهر یافت نشد")
                carrier = info.get("carrier", "اپراتور یافت نشد")
                country = info.get("country", "کشور یافت نشد")

                message = f"""
نتایج جستجو:
**شماره:** # src/bot.py
impo# src/bot{name}bot.py
imp{city}bot.py
impo{country}.py
import os
{carrier}
"""
            else:
                message = "هیچ اطلاعاتی برای این شماره یافت نشد."
        elif resp.status_code == 401:
            message = "خطای API Key! لطفاً کلید را بررسی کنید."
        elif resp.status_code == 429:
            message = "محدودیت درخواست! چند لحظه صبر کنید."
        else:
            message = f"خطای API: کد {resp.status_code}"

    except requests.exceptions.Timeout:
        message = "timeout! دوباره تلاش کنید."
    except requests.exceptions.ConnectionError:
        message = "خطای اتصال به اینترنت!"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        message = "خطای ناشناخته! بعداً تلاش کنید."

    await update.message.reply_text(message)


# ----------------------------------------------------------------------
# 6. هندلر خطا
# ----------------------------------------------------------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


# ----------------------------------------------------------------------
# 7. تابع اصلی (Webhook + Flask)
# ----------------------------------------------------------------------
def main() -> None:
    # ---- ساخت اپلیکیشن telegram-bot (python-telegram-bot v20+) ----
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # ---- اضافه کردن هندلرها ----
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search_phone_number)
    )
    application.add_error_handler(error_handler)

    # ---- تنظیمات webhook برای Render ----
    PORT = int(os.getenv("PORT", 5000))
    APP_NAME = os.getenv("RENDER_APP_NAME", "my-updownsug-umazat")  # در Render تنظیم کنید
    webhook_url = f"https://{APP_NAME}.onrender.com/webhook"

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=webhook_url,
    )

    logger.info(f"ربات با webhook راه‌اندازی شد: {webhook_url}")


# ----------------------------------------------------------------------
# 8. اجرا (Flask + Bot)
# ----------------------------------------------------------------------
if    __name__ == "__main__":
    # در Render فقط Flask اجرا می‌شود؛ bot داخل webhook کار می‌کند
    # اما برای تست محلی می‌توانید main() را مستقیم صدا بزنید
    import sys

    if "run_bot" in sys.argv:
        main()
    else:
        # Flask برای health-check
        from werkzeug.serving import run_simple

        run_simple("0.0.0.0", int(os.getenv("PORT", 5000)), app)



