import random, string
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()   

twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
otp_db = {}  # In-memory store for OTPs; replace with Redis or DB in production

def generate_otp():
    return ''.join(random.choices(string.digits, k=4))

def send_otp(phone_number: str, otp: str):
    message = f"Your verification OTP is: {otp}"
    twilio_client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_FROM_NUMBER"),
        to=phone_number
    )

def store_otp(phone: str, otp: str):
    expiry = datetime.now() + timedelta(minutes=int(os.getenv("OTP_EXPIRY_MINUTES", 5)))
    otp_db[phone] = {"otp": otp, "expires": expiry}
 
def verify_otp(phone: str, otp: str):
    entry = otp_db.get(phone)
    if not entry:
        return False, "OTP not found"
    if datetime.now() > entry["expires"]:
        return False, "OTP expired"
    if entry["otp"] != otp:
        return False, "Invalid OTP"
    return True, "OTP verified"