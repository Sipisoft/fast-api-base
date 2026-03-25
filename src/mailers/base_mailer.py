import os
from fastapi_mail import ConnectionConfig ,FastMail
from jinja2 import Environment, FileSystemLoader, select_autoescape
class BaseMailer:
    def __init__(self, mailer):
        self.conf = ConnectionConfig(
                MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
                MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
                MAIL_FROM=os.getenv("MAIL_FROM"),
                MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
                MAIL_SERVER=os.getenv("MAIL_SERVER"),
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=False
            )

        self.mailer = FastMail(self.conf)

        self.env = Environment(
            loader=FileSystemLoader("src/mailers/templates"),
            autoescape=select_autoescape(['html', 'xml'])
            )