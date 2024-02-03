from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

phone_number=os.getenv("PHONE_NUMBER")
account_sid=os.getenv("TWILIO_ACCOUNT_SID")
auth_token=os.getenv("TWILIO_AUTH_TOKEN")
verify_sid=os.getenv("VERIFY_SID")


client=Client(account_sid,auth_token)

otp_verification=client.verify.v2.services(verify_sid).verifications.create(
    to=phone_number,channel="sms"
)

print(otp_verification.status)

otp_code=input("Please enter the otp sent to you :")

otp_vcheck = client.verify.v2.services(verify_sid).verification_checks.create(
    to=phone_number, code=otp_code
)

print("Verification Status:", otp_vcheck.status)


