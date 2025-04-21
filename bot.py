import os
import logging
import random
import string
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Paystack API key
PAYSTACK_SECRET_KEY = 'sk_live_9bfca73249f8e846633bd822e708ee9abfa9b1af'  # Replace with your Paystack secret key

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
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        # New user, register them
        users_data[user_id] = {
            'balance': 300,  # Starting balance
            'referral_code': generate_referral_code(),
            'referred_by': None,
            'referrals': 0
        }
        update.message.reply_text(f"Welcome! You have been registered. Your starting balance is ₦300.")
    else:
        update.message.reply_text(f"Welcome back, your current balance is: ₦{users_data[user_id]['balance']}")

# Command: /refer
def refer(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    referral_code = users_data[user_id]['referral_code']
    referral_link = f"https://t.me/{context.bot.username}?start={referral_code}"
    
    update.message.reply_text(f"Share this link with your friends to refer them and earn rewards:\n{referral_link}")

# Command: /deposit
def deposit(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        update.message.reply_text("You need to register first using /start.")
        return
    
    # Deposit amount (you can make it dynamic if needed)
    amount = 100  # Example amount for deposit
    
    # Create a Paystack payment link
    payment_url = create_paystack_payment_link(amount)
    
    if payment_url:
        update.message.reply_text(f"To deposit ₦{amount}, click the link below to proceed with your payment:\n{payment_url}")
    else:
        update.message.reply_text("An error occurred while creating the payment link. Please try again later.")

# Function to create Paystack payment link
def create_paystack_payment_link(amount: int) -> str:
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "amount": amount * 100,  # Convert to Kobo (1 Naira = 100 Kobo)
        "email": "user_email@example.com",  # Dynamically use user's email or Telegram ID
        "currency": "NGN",
        "callback_url": "https://yourwebsite.com/callback"  # Replace with your actual callback URL
    }
    
    try:
        # Make the request to Paystack to create a payment link
        response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=payload)
        response_data = response.json()

        if response.status_code == 200 and response_data["status"] == "success":
            payment_url = response_data["data"]["authorization_url"]
            return payment_url
        else:
            return None
    except Exception as e:
        logger.error(f"Error creating Paystack payment link: {e}")
        return None

# Command: /withdraw
def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        update.message.reply_text("You need to register first using /start.")
        return
    
    balance = users_data[user_id]['balance']
    
    if balance < 500:
        update.message.reply_text("Minimum withdrawal amount is ₦500.")
        return
    
    # Process withdrawal via Paystack (mocked here, you would replace with actual withdrawal logic)
    withdrawal_amount = 500
    success = initiate_paystack_withdrawal(user_id, withdrawal_amount)
    
    if success:
        users_data[user_id]['balance'] -= withdrawal_amount
        update.message.reply_text(f"Your withdrawal of ₦{withdrawal_amount} has been processed. Your remaining balance is ₦{users_data[user_id]['balance']}.")
    else:
        update.message.reply_text("An error occurred while processing the withdrawal. Please try again later.")

# Function to initiate Paystack withdrawal (you need a verified Paystack account for this)
def initiate_paystack_withdrawal(user_id: int, amount: int) -> bool:
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # Placeholder for actual withdrawal logic, requires Paystack account and user verification
    payload = {
        "source": "balance",
        "amount": amount * 100,  # Convert to Kobo
        "recipient": "recipient_account_id"  # Use actual recipient account ID, which must be verified
    }
    
    try:
        # Simulate Paystack API request for withdrawal
        response = requests.post("https://api.paystack.co/transfer", headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200 and response_data["status"] == "success":
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error initiating withdrawal via Paystack: {e}")
        return False

# Command: /my_balance
def my_balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in users_data:
        update.message.reply_text("You need to register first using /start.")
        return
    
    balance = users_data[user_id]['balance']
    update.message.reply_text(f"Your current balance is: ₦{balance}")

# Main function to start the bot
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    
    dp = updater.dispatcher
    
    # Commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("refer", refer))
    dp.add_handler(CommandHandler("deposit", deposit))
    dp.add_handler(CommandHandler("withdraw", withdraw))
    dp.add_handler(CommandHandler("my_balance", my_balance))
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
