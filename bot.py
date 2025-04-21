import os
import sqlite3
import logging
import requests
from flask import Flask, request
from telegram import (
    Bot, Update,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Dispatcher, CommandHandler, CallbackContext,
    CallbackQueryHandler
)

# === CONFIGURATION ===
TELEGRAM_TOKEN = "7373949725:AAEh73YVcSeE2R0Cyp0Y3yuYci38dOx9-2Y"
AMMERPAY_API_KEY = "5775769170:LIVE:TG_GCSu3Z2A9p9yMV1Nck9B8UAA"
BOT_USERNAME = "ReferGenieBot"
SITE_URL = "https://refer-and-earn-bot-6npx.onrender.com"  # Replace with actual Render URL

# === FLASK SETUP ===
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# === DB SETUP ===
def init_db():
    conn = sqlite3.connect("refergenie.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            paid INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# === START COMMAND ===
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name

    conn = sqlite3.connect("refergenie.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    c.execute("SELECT paid FROM users WHERE user_id = ?", (user_id,))
    paid = c.fetchone()[0]
    conn.close()

    if paid:
        show_dashboard(update, context)
    else:
        keyboard = [[InlineKeyboardButton("💳 Pay ₦1000 to Join", callback_data="pay")]]
        update.message.reply_text("Welcome to ReferGenie! To continue, please make payment:",
                                  reply_markup=InlineKeyboardMarkup(keyboard))

# === PAYMENT HANDLER ===
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name

    if query.data == "pay":
        # Generate AmmerPay link
        payload = {
            "amount": 1000,
            "email": f"{username}@gmail.com",
            "metadata": {"user_id": user_id},
            "redirect_url": f"{SITE_URL}/confirm/{user_id}"
        }
        headers = {"Authorization": f"Bearer {AMMERPAY_API_KEY}"}
        res = requests.post("https://api.ammerpay.com/initialize", json=payload, headers=headers)

        if res.status_code == 200 and res.json().get("status"):
            payment_url = res.json()["data"]["authorization_url"]
            query.edit_message_text("Click below to complete payment:",
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Pay Now", url=payment_url)]]))
        else:
            query.edit_message_text("Failed to generate payment link. Please try again later.")

# === CONFIRMATION ENDPOINT ===
@app.route("/confirm/<int:user_id>")
def confirm_payment(user_id):
    conn = sqlite3.connect("refergenie.db")
    c = conn.cursor()
    c.execute("UPDATE users SET paid = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    bot.send_message(chat_id=user_id, text="✅ Payment confirmed! You now have access.")
    return "Payment confirmed. You can now return to Telegram."

# === DASHBOARD ===
def show_dashboard(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = sqlite3.connect("refergenie.db")
    c = conn.cursor()
    c.execute("SELECT paid FROM users WHERE user_id = ?", (user_id,))
    paid = c.fetchone()[0]
    conn.close()

    if paid:
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data="dash")],
            [InlineKeyboardButton("👥 Referrals", callback_data="refs")],
            [InlineKeyboardButton("💼 Withdraw", callback_data="wd")]
        ]
        update.message.reply_text("Welcome back!", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text("Please complete payment first by clicking /start.")

# === EXTRA BUTTON LOGIC ===
def extra_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    conn = sqlite3.connect("refergenie.db")
    c = conn.cursor()
    c.execute("SELECT paid FROM users WHERE user_id = ?", (user_id,))
    paid = c.fetchone()[0]
    conn.close()

    if not paid:
        query.answer("Access denied. Payment required.")
        return

    if query.data == "dash":
        query.edit_message_text("📊 Your dashboard will go here.")
    elif query.data == "refs":
        query.edit_message_text("👥 Your referral system will go here.")
    elif query.data == "wd":
        query.edit_message_text("💼 Withdrawals system will go here.")

# === FLASK TELEGRAM HOOK ===
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# === SET WEBHOOK (Run Once on Startup) ===
@app.before_first_request
def set_webhook():
    webhook_url = f"{SITE_URL}/{TELEGRAM_TOKEN}"
    bot.set_webhook(webhook_url)

# === Dispatcher Setup ===
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button, pattern="^pay$"))
dispatcher.add_handler(CallbackQueryHandler(extra_buttons, pattern="^(dash|refs|wd)$"))

# === Start Flask App ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
