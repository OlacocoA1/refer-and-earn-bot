import os
import time
import requests
import sqlite3
from flask import Flask, request, redirect
from threading import Thread
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = "7373949725:AAEh73YVcSeE2R0Cyp0Y3yuYci38dOx9-2Y"
AMMER_API_KEY = "5775769170:LIVE:TG_GCSu3Z2A9p9yMV1Nck9B8UAA"
BOT_USERNAME = "ReferGenieBot"
RENDER_BASE_URL = "https://refer-and-earn-bot-6npx.onrender.com"

# === INITIALIZE TELEGRAM ===
bot = Bot(token=TELEGRAM_BOT_TOKEN)
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# === FLASK SERVER FOR CALLBACK ===
app = Flask(__name__)

# === DATABASE SETUP ===
def init_db():
    conn = sqlite3.connect("refergenie.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            paid INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# === START HANDLER ===
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    telegram_id = user.id
    username = user.username

    # Save user to DB if not exists
    conn = sqlite3.connect("refergenie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (telegram_id, username) VALUES (?, ?)", (telegram_id, username))
    conn.commit()
    conn.close()

    # Show Pay button
    pay_button = InlineKeyboardButton("💳 Pay ₦1000", callback_data="pay_now")
    reply_markup = InlineKeyboardMarkup([[pay_button]])
    update.message.reply_text(
        "Welcome to ReferGenie! 🎉\nClick below to make your ₦1000 payment and unlock full access.",
        reply_markup=reply_markup
    )

# === CALLBACK QUERY HANDLER ===
def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    telegram_id = user.id

    if query.data == "pay_now":
        email = f"{user.username or 'refergenie'}@gmail.com"
        payment_url = f"https://ammerpay.com/pay?amount=1000&email={email}&key={AMMER_API_KEY}&callback={RENDER_BASE_URL}/payment_callback?user_id={telegram_id}"
        context.bot.send_message(
            chat_id=telegram_id,
            text=f"Click below to complete your payment:\n{payment_url}"
        )

# === PAYMENT CALLBACK ===
@app.route("/payment_callback", methods=["GET", "POST"])
def payment_callback():
    telegram_id = request.args.get("user_id")
    if telegram_id:
        conn = sqlite3.connect("refergenie.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET paid=1 WHERE telegram_id=?", (telegram_id,))
        conn.commit()
        conn.close()
        bot.send_message(chat_id=telegram_id, text="✅ Payment received! Welcome to ReferGenie Premium. 🎉")
        return "OK", 200
    return "User ID missing", 400

# === KEEP FLASK ALIVE ON RENDER ===
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# === LAUNCH EVERYTHING ===
if __name__ == "__main__":
    init_db()

    # Telegram handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback))

    # Launch Flask and Telegram Bot in parallel
    Thread(target=run_flask).start()
    updater.start_polling()
    updater.idle()
