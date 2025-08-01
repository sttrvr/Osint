import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
import threading

# Flask keep-alive
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# --- API KEYS ---
BOT_TOKEN = os.environ.get("8173476361:AAFK7a0A_hw9lnYLWU4qrCYVkK5PiQgsGHE")
SHODAN_API_KEY = os.environ.get("7L1aiYw3vR65CdGfpgiy7bU3BDvJSqsW")
INTELX_API_KEY = os.environ.get("40a346fb-bb26-4780-a80f-0e669f37c331")

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Это OSINT Бот. Используй команды /ip, /email, /phone, /leak и т.д.")

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи IP: /ip 8.8.8.8")
        return
    ip = context.args[0]
    url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        reply = f"🌍 IP: {ip}\nОрганизация: {data.get('org')}\nГород: {data.get('city')}\nОткрытые порты: {data.get('ports')}"
    else:
        reply = "❌ Не удалось получить данные."
    await update.message.reply_text(reply)

async def email_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи email: /email test@example.com")
        return
    email = context.args[0]
    headers = {
        "x-key": INTELX_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "term": email,
        "maxresults": 1,
        "media": 0
    }
    r = requests.post("https://2.intelx.io/phonebook/search", headers=headers, json=data)
    if r.status_code == 200:
        res = r.json()
        total = res.get("selectors", [])
        reply = f"🔍 Email найден в {len(total)} источниках (если доступно)."
    else:
        reply = "❌ Ошибка при поиске email."
    await update.message.reply_text(reply)

async def phone_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи номер телефона: /phone +79991234567")
        return
    phone = context.args[0]
    # Для OSINT Industries нужно будет сделать реальный запрос, если есть API
    reply = f"📞 Поиск по номеру: {phone}\n(интеграция в разработке)"
    await update.message.reply_text(reply)

async def leak_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи email или username: /leak test@example.com")
        return
    term = context.args[0]
    headers = {
        "x-key": INTELX_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "term": term,
        "maxresults": 5,
        "media": 0
    }
    r = requests.post("https://2.intelx.io/phonebook/search", headers=headers, json=data)
    if r.status_code == 200:
        reply = f"🕵️ Данные о {term} найдены! Возможно, присутствует в утечках."
    else:
        reply = "❌ Ничего не найдено."
    await update.message.reply_text(reply)

# --- MAIN ---
def main():
    app_tg = Application.builder().token(BOT_TOKEN).build()

    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("ip", ip_lookup))
    app_tg.add_handler(CommandHandler("email", email_lookup))
    app_tg.add_handler(CommandHandler("phone", phone_lookup))
    app_tg.add_handler(CommandHandler("leak", leak_lookup))

    threading.Thread(target=run_flask).start()  # Keep-alive thread
    app_tg.run_polling()

if __name__ == "__main__":
    main()

