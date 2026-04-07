from src.mailers.base_mailer import BaseMailer
from fastapi_mail import MessageSchema
from datetime import datetime
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.admin import Admin


class OTPMailer(BaseMailer):
    def __init__(self, admin: "Admin", otp: str, magic_token: str, mailer=None):
        super().__init__(mailer)
        self.admin = admin
        self.otp = otp
        self.magic_token = magic_token

    async def send(self):
        base_url = os.getenv("FRONTEND_URL")
        magic_link = f"{base_url}?token={self.magic_token}"

        message = MessageSchema(
            subject="Security Verification Code",
            recipients=[self.admin.email],
            template_body={
                "user_name": self.admin.username,
                "otp": self.otp,
                "magic_link": magic_link,
                "current_year": datetime.now().year,
            },
            subtype="html",
        )

        await self.mailer.send_message(message, template_name="otp_email.html")
        return {"message": "Email sent successfully!"}