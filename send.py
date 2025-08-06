from twilio.rest import Client
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Twilio Setup
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
recipient_number = os.getenv("ALERT_RECIPIENT_NUMBER")
client = Client(account_sid, auth_token)

# Cloudinary Setup
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Upload image
def upload_to_cloudinary(image_path):
    try:
        upload_result = cloudinary.uploader.upload(image_path)
        print(f"✅ Image uploaded: {upload_result['secure_url']}")
        return upload_result["secure_url"]
    except Exception as e:
        print(f"❌ Failed to upload image: {e}")
        return None

# Send SMS with link
def sendSmsWithImage(image_url):
    try:
        body = f"🚨 Alert: Intruder Detected! See the screenshot: {image_url}"
        message = client.messages.create(
            from_=twilio_number,
            to=recipient_number,
            body=body
        )
        print(f"✅ SMS sent with SID: {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")
