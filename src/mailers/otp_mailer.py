from src.mailers.base_mailer import BaseMailer
from src.models.admin import Admin
from fastapi_mail import MessageSchema
from datetime import datetime
class OTPMailer(BaseMailer):
    def __init__(self, admin:Admin, otp:str,mailer=None):
        super().__init__(mailer)
        self.admin = admin
        self.otp = otp


    async def send(self):
        message = MessageSchema(
            subject=f"Security Verification Code",
            recipients=[self.admin.email],
            template_body={
                "user_name":self.admin.username,
                "otp":self.otp,
                "current_year":datetime.now().year
            },
            subtype="html"
        )
        await self.mailer.send_message(message,template_name="otp_email.html")
        return {"message": "Email sent successfully!"}