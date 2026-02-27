import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print(f"Token (First 10 chars): {TELEGRAM_BOT_TOKEN[:10]}..." if TELEGRAM_BOT_TOKEN else "Token: MISSING")
print(f"Chat ID: {TELEGRAM_CHAT_ID}" if TELEGRAM_CHAT_ID else "Chat ID: MISSING")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("Cannot test without token and chat ID.")
    exit(1)

# Check bot info
print("\n--- Testing Bot Token ---")
try:
    info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    info_res = requests.get(info_url)
    print(f"Status Code: {info_res.status_code}")
    print(f"Response: {info_res.json()}")
except Exception as e:
    print(f"Error checking bot: {e}")

# Send test message
print("\n--- Sending Test Message ---")
try:
    msg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': "🤖 Hello! This is a test message from your News Tracker setup script to confirm the connection works."
    }
    msg_res = requests.post(msg_url, json=payload)
    print(f"Status Code: {msg_res.status_code}")
    print(f"Response: {msg_res.json()}")
    
    if msg_res.status_code == 200:
        print("\n✅ SUCCESS! The message was sent to Telegram.")
    else:
        print("\n❌ FAILED! Telegram rejected the message.")
except Exception as e:
    print(f"Error sending message: {e}")
