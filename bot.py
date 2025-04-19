import sqlite3
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a secret key for session management

PAYSTACK_KEY = "pk_live_b5fa4e730d9baa38f7ff012ad4d263d5d3459c5b"
BOT_USERNAME = "ReferGenieBot"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("refergenie.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            referrer_id INTEGER,
            paid INTEGER DEFAULT 0,  -- 0 for not paid, 1 for paid
            FOREIGN KEY (referrer_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

# === Home Page ===
@app.route('/')
def home():
    user_id = session.get("user_id")
    if user_id:
        conn = sqlite3.connect("refergenie.db")
        cursor = conn.cursor()
        cursor.execute("SELECT paid FROM users WHERE user_id=?", (user_id,))
        paid = cursor.fetchone()
        conn.close()

        if paid and paid[0] == 0:  # If not paid
            return redirect(url_for('pay'))
        else:
            return render_template('dashboard.html')

    return render_template('index.html')

# === Paystack Payment Page ===
@app.route('/pay', methods=['GET', 'POST'])
def pay():
    user_id = session.get("user_id")
    if request.method == 'POST':
        username = request.form.get("username")
        # Initialize the Paystack payment link
        payload = {
            "email": f"{username}@gmail.com",
            "amount": 100000,  # ₦1000 is 1000 kobo
            "metadata": {"user_id": user_id},
            "callback_url": "https://yourwebsite.com/callback"
        }
        headers = {
            "Authorization": f"Bearer {PAYSTACK_KEY}",
            "Content-Type": "application/json"
        }
        res = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=payload)
        data = res.json()

        if data.get("status"):
            payment_url = data["data"]["authorization_url"]
            return redirect(payment_url)
        else:
            return "Error: Failed to generate payment link"

    return render_template('pay.html')

# === Callback for Paystack ===
@app.route('/callback', methods=['GET'])
def callback():
    user_id = session.get("user_id")
    # Assuming Paystack sends data back to this endpoint upon successful payment
    if user_id:
        conn = sqlite3.connect("refergenie.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET paid = 1 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    return "Error: User ID not found"

# === User Registration (Temporary for this demo) ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        user_id = request.form.get("user_id")  # This would be dynamically handled in a real system
        conn = sqlite3.connect("refergenie.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        conn.close()

        session['user_id'] = user_id
        return redirect(url_for('home'))
    
    return render_template('register.html')

# === Main ===
if __name__ == "__main__":
    init_db()  # Ensure the database is initialized
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
