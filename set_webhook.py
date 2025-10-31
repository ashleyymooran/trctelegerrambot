import requests

# توکن ربات شما
TELEGRAM_TOKEN = "8461212300:AAFmTxio3YON-C2FVOrnERS2cQErYO09Rms"

# نام اپلیکیشن Render
APP_NAME = "my-updownsug-umazat"

def set_webhook():
    webhook_url = f"https://{APP_NAME}.onrender.com/{TELEGRAM_TOKEN}"
    
    response = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
        params={"url": webhook_url}
    )
    
    print("✅ Webhook تنظیم شد!")
    print(f"📝 وضعیت: {response.json()}")

def get_webhook_info():
    response = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    )
    
    print("🔍 اطلاعات Webhook:")
    print(response.json())

if __name__ == '__main__':
    set_webhook()
    get_webhook_info()