import logging
import os
import requests
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import MessageHandler, filters
from telegram.ext import Updater
import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your Telegram bot token and Paystack API key
TOKEN = "7373949725:AAEh73YVcSeE2R0Cyp0Y3yuYci38dOx9-2Y"  # Your Telegram Bot API key
PAYSTACK_API_KEY = "pk_live_b5fa4e730d9baa38f7ff012ad4d263d5d3459c5b"  # Paystack API Key

# Initialize the bot
bot = Bot(token=TOKEN)

# A simple in-memory user store (For production, use a database like PostgreSQL)
users = {}

# Paystack Verification URL
PAYSTACK_VERIFICATION_URL = "https://api.paystack.co/transaction/verify/"

# Initialize logging
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users:
        users[user_id] = {'balance': 0, 'referred': []}
    update.message.reply_text(f"Welcome to ReferGenie! Use the commands below to manage your account:\n\n"
                              "/balance - Check your balance\n"
                              "/refer - Get your referral link\n"
                              "/withdraw - Request a withdrawal\n")


def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in users:
        balance = users[user_id]['balance']
        update.message.reply_text(f"Your current balance is: {balance} Naira.")
    else:
        update.message.reply_text("You haven't started using the bot yet. Please type /start to begin.")


def refer(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
    update.message.reply_text(f"Share this link with your friends to refer them: {ref_link}")


def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in users:
        balance = users[user_id]['balance']
        if balance >= 1000:
            # Simulate withdrawal process (you'll integrate Paystack withdrawal here)
            update.message.reply_text(f"Your withdrawal request of {balance} Naira is being processed.")
            # Reset the user's balance after withdrawal
            users[user_id]['balance'] = 0
        else:
            update.message.reply_text("You must have a minimum of 1000 Naira to withdraw.")
    else:
        update.message.reply_text("You haven't started using the bot yet. Please type /start to begin.")


def process_payment(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users:
        users[user_id] = {'balance': 0, 'referred': []}
    
    # Simulate the user making the initial payment
    users[user_id]['balance'] = 1000
    update.message.reply_text(f"Your payment of 1000 Naira has been received. You are now eligible for referrals.")

# Handle referral bonus
def handle_referral(user_id, referred_user_id):
    if user_id in users:
        # Add bonus to the referring user
        users[user_id]['balance'] += 300
        if referred_user_id not in users[user_id]['referred']:
            users[user_id]['referred'].append(referred_user_id)
            print(f"Referral bonus added to {user_id}'s account. Total balance: {users[user_id]['balance']} Naira.")
    else:
        print(f"User {user_id} not found for referral.")

def verify_paystack_transaction(transaction_reference: str) -> bool:
    # Verify the transaction on Paystack's servers
    headers = {
        'Authorization': f'Bearer {PAYSTACK_API_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.get(f"{PAYSTACK_VERIFICATION_URL}{transaction_reference}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['data']['status'] == 'success':
            return True
    return False

def main() -> None:
    updater = Updater(TOKEN)

    # Register handlers for commands
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("refer", refer))
    dp.add_handler(CommandHandler("withdraw", withdraw))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_payment))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
