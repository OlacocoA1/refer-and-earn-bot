import logging
import sqlite3
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# === CONFIGURATION ===
BOT_TOKEN = "7373949725:AAEh73YVcSeE2R0Cyp0Y3yuYci38dOx9-2Y"
PAYSTACK_KEY = "pk_live_b5fa4e730d9baa38f7ff012ad4d263d5d3459c5b"
BOT_USERNAME = "ReferGenieBot"  # exact Telegram username (with Bot suffix)

# === LOGGING ===
logging.basicConfig(level=logging.INFO)

# === DATABASE CONNECTION ===
def init_db():
    conn = sqlite3.connect("refergenie.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            referrer_id INTEGER,
            FOREIGN KEY (referrer_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

# === MAIN MENU KEYBOARD ===
def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("💰 Check Balance"), KeyboardButton("👥 Get Referral Link")],
        [KeyboardButton("💵 Withdraw")]
    ], resize_keyboard=True)

# === /start COMMAND ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or f"user{user_id}"
    
    # Connect to DB and check if the user already exists
    conn = sqlite3.connect("refergenie.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
    
    # Handle referral if link has start arg
    if context.args:
        referrer = int(context.args[0])
        if referrer != user_id:
            cursor.execute("UPDATE users SET referrer_id = ? WHERE user_id = ?", (referrer, user_id))
            cursor.execute("UPDATE users SET balance = balance + 300 WHERE user_id = ?", (referrer,))
            conn.commit()

    conn.close()
    
    keyboard = [[InlineKeyboardButton("💳 Pay ₦1000 to Join", callback_data="pay")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome to *ReferGenie!*\n\n"
        "Pay ₦1000 to activate your account and start earning ₦300 per referral.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    await update.message.reply_text("👇 Use the menu below to access other features.", reply_markup=main_menu())

# === INLINE BUTTON HANDLER ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or f"user{user_id}"

    payload = {
        "email": f"{username}@gmail.com",
        "amount": 100000,  # in kobo (₦1000)
        "metadata": {"user_id": user_id}
    }

    headers = {
        "Authorization": f"Bearer {PAYSTACK_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=payload)
        data = res.json()

        if data.get("status"):
            payment_url = data["data"]["authorization_url"]
            await query.message.reply_text(f"💳 Click below to pay:\n{payment_url}")
        else:
            await query.message.reply_text(f"❌ Error: {data.get('message', 'Failed to create payment link')}")
    except Exception as e:
        logging.error(f"Paystack error: {e}")
        await query.message.reply_text("⚠️ Payment failed due to server error.")

# === COMMAND: /balance or 💰 Check Balance ===
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("refergenie.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()

    conn.close()

    if balance:
        await update.message.reply_text(f"💰 Your balance: ₦{balance[0]}")
    else:
        await update.message.reply_text("❌ You are not registered yet. Please try again later.")

# === COMMAND: /refer or 👥 Get Referral Link ===
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"🔗 Your referral link:\n{link}")

# === COMMAND: /withdraw or 💵 Withdraw ===
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("refergenie.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()

    if balance and balance[0] >= 1000:
        cursor.execute("UPDATE users SET balance = balance - 1000 WHERE user_id = ?", (user_id,))
        conn.commit()
        await update.message.reply_text("✅ Withdrawal of ₦1000 requested. Admin will process it shortly.")
    else:
        await update.message.reply_text("❌ Minimum balance for withdrawal is ₦1000.")

    conn.close()

# === HANDLE BUTTONS (Text Messages from Keyboard) ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "💰 Check Balance":
        await show_balance(update, context)
    elif text == "👥 Get Referral Link":
        await referral(update, context)
    elif text == "💵 Withdraw":
        await withdraw(update, context)
    else:
        await update.message.reply_text("❓ Unknown option. Please use the buttons below.", reply_markup=main_menu())

# === MAIN ===
if __name__ == '__main__':
    init_db()  # Initialize the DB on startup

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ ReferGenie is running...")
    app.run_polling()
