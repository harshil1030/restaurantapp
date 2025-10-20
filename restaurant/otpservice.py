import random, string
from datetime import datetime, timedelta
import boto3
import os
from dotenv import load_dotenv

load_dotenv()   

# Initialize AWS SNS client
sns_client = boto3.client(
    "sns",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)


otp_db = {}  # In-memory store for OTPs; replace with Redis or DB in production


def generate_otp():
    """Generate a random 4-digit OTP"""
    return ''.join(random.choices(string.digits, k=4))

def send_otp(phone_number: str, otp: str):
    message = f"Tandoori Tadka Restaurant: \nYour verification OTP is: {otp}"
    try:
        response = sns_client.publish(
            PhoneNumber=phone_number,  # Must include +91 for India
            Message=message
        )
        print("✅ SMS sent successfully:", response)
        return True
    except Exception as e:
        print("❌ Error sending SMS:", str(e))
        return False
    
    
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