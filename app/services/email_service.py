
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    async def send_email(self, email_to: str, subject: str, content: str):
        # In a real application, you would use an SMTP server or an email API like SendGrid/SES
        logger.info(f"Sending email to {email_to} with subject '{subject}'")
        logger.info(f"Content: {content}")
        print(f"--- MOCK EMAIL ---")
        print(f"To: {email_to}")
        print(f"Subject: {subject}")
        print(f"Content: {content}")
        print(f"------------------")

    async def send_otp_email(self, email_to: str, otp: str, type: str):
        subject = f"Your OTP for {type} - {settings.PROJECT_NAME}"
        content = f"Your OTP is: {otp}. It expires in {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes."
        await self.send_email(email_to, subject, content)
