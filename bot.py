import os
import logging
import random
import string
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Paystack API key
PAYSTACK_SECRET_KEY = 'sk_live_9bfca73249f8e846633bd822e708ee9abfa9b1af'  # Replace with your Paystack key

# Telegram Bot Token
TELEGRAM_TOKEN = '7373949725:AAEh73YVcSeE2R0Cyp0Y3yuYci38dOx9-2Y'  # Replace with your Telegram bot token

# In-memory storage for users (this can be replaced with a database later)
users_data = {}

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions to manage users
def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Command: /start
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        # New user, register them
        users_data[user_id] = {
            'balance': 300,  # Starting balance
            'referral_code': generate_referral_code(),
            'referred_by': None,
            'referrals': 0
        }
        await update.message.reply_text(f"Welcome! You have been registered. Your starting balance is ₦300.")
    else:
        await update.message.reply_text(f"Welcome back, your current balance is: ₦{users_data[user_id]['balance']}")

# Command: /refer
async def refer(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    referral_code = users_data[user_id]['referral_code']
    referral_link = f"https://t.me/{context.bot.username}?start={referral_code}"
    
    await update.message.reply_text(f"Share this link with your friends to refer them and earn rewards:\n{referral_link}")

# Command: /deposit
async def deposit(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        await update.message.reply_text("You need to register first using /start.")
        return
    
    # Create a Paystack payment link for deposit (mocked, use Paystack API for real integration)
    amount = 100  # Example amount for deposit
    paystack_url = f"https://paystack.com/pay/{PAYSTACK_SECRET_KEY}"  # This would need to be replaced with actual Paystack API

    await update.message.reply_text(f"To deposit ₦{amount}, click the link below:\n{paystack_url}")

# Command: /withdraw
async def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        await update.message.reply_text("You need to register first using /start.")
        return
    
    balance = users_data[user_id]['balance']
    
    if balance < 500:
        await update.message.reply_text("Minimum withdrawal amount is ₦500.")
        return
    
    # Process withdrawal via Paystack (mocked here)
    # Replace this with real Paystack API withdrawal logic
    withdrawal_amount = 500
    users_data[user_id]['balance'] -= withdrawal_amount
    await update.message.reply_text(f"Your withdrawal of ₦{withdrawal_amount} has been processed. Your remaining balance is ₦{users_data[user_id]['balance']}.")

# Command: /my_balance
async def my_balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        await update.message.reply_text("You need to register first using /start.")
        return
    
    balance = users_data[user_id]['balance']
    await update.message.reply_text(f"Your current balance is: ₦{balance}")

# Main function to start the bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("refer", refer))
    application.add_handler(CommandHandler("deposit", deposit))
    application.add_handler(CommandHandler("withdraw", withdraw))
    application.add_handler(CommandHandler("my_balance", my_balance))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
