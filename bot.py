import sqlite3
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# === SETTINGS ===
BOT_TOKEN = "7373949725:AAEh73YVcSeE2R0Cyp0Y3yuYci38dOx9-2Y"
BOT_NAME = "CashFlexBot"
JOIN_FEE = 1000
REF_REWARD = 300
MIN_WITHDRAW = 1000
PAYSTACK_SECRET_KEY = "pk_live_b5fa4e730d9baa38f7ff012ad4d263d5d3459c5b"

# === DATABASE ===
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            referred_by INTEGER,
            balance INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def register_user(user_id, username, referred_by):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)",
              (user_id, username, referred_by))
    if referred_by:
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (REF_REWARD, referred_by))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def update_balance(user_id, amount):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_ref_count(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

# === PAYSTACK ===
def create_paystack_link(user_id, username):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": f"{username or 'user'}@cashflex.fake",
        "amount": JOIN_FEE * 100,
        "metadata": {"user_id": user_id}
    }
    res = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
    if res.status_code == 200:
        return res.json()['data']['authorization_url']
    else:
        return "⚠️ Error generating payment link."

# === BOT COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref_code = context.args[0] if context.args else None
    existing = get_user(user.id)

    if existing:
        await update.message.reply_text(
            f"👋 Welcome back to {BOT_NAME}!\nUse /balance, /refer or /withdraw."
        )
    else:
        register_user(user.id, user.username, ref_code)
        pay_url = create_paystack_link(user.id, user.username)
        await update.message.reply_text(
            f"👋 Welcome to {BOT_NAME}!\nTo activate your account, pay ₦{JOIN_FEE} below:\n{pay_url}"
        )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = get_balance(update.effective_user.id)
    await update.message.reply_text(f"💰 Your balance is ₦{bal}")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{BOT_NAME}?start={user_id}"
    count = get_ref_count(user_id)
    await update.message.reply_text(
        f"🔗 Your referral link:\n{link}\n\n👥 Referrals: {count}"
    )

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = get_balance(user_id)
    if bal < MIN_WITHDRAW:
        await update.message.reply_text("❌ You need at least ₦1000 to withdraw.")
    else:
        update_balance(user_id, -bal)
        await update.message.reply_text("✅ Withdrawal request sent. You'll be paid soon!")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command. Use /start /balance /refer /withdraw")

# === MAIN ===
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    app.run_polling()
