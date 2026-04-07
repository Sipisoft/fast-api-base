import os
from src.mailers.base_mailer import BaseMailer
from fastapi import Request
from fastapi_mail import MessageSchema
from typing import  TypeVar


T = TypeVar("T")
class PasswordResetMailer(BaseMailer):
    def __init__(self, account: T, password_token: str, new_password: bool = False, request: Request = None, mailer=None):
        super().__init__(mailer)
        print("Password token", password_token)
        self.account = account
        self.password_token = password_token
        self.request = request
        self.new_password = new_password
        self.template = self.env.get_template("password_reset.html")


    async def send(self):
        frontend_url = os.getenv('FRONTEND_URL')
        if not frontend_url and self.request:
            frontend_url = f"{self.request.base_url}"
        
        set_password_link = f"{frontend_url}set-password?token={ self.password_token }&new_password={self.new_password}"
        print("Link", set_password_link)
        html_content = self.template.render(account=self.account, link=set_password_link, request = self.request, new_password=self.new_password)

        message = MessageSchema(
            subject=f"Miverify - {'Set A' if self.new_password else 'Reset'} Password for your account ",
            recipients=[self.account.email],
            body=html_content,
            subtype="html"
        )
        await self.mailer.send_message(message)
        return {"message": "Email sent successfully!"}