from src.db.database import SessionLocal
from celery_app import celery_app
from fastapi import Request
from src.mailers.password_reset_mailer import PasswordResetMailer
from uuid import UUID
from enum import Enum

class AccountType(str, Enum):
    admin = "admin"
    user = "user"
@celery_app.task(name="send_password_reset_email_task")
def send_password_reset_email_task(admin_id: str, account_type: AccountType, new_password: bool) -> None:

    from src.models.admin import Admin
    db = SessionLocal()
    try:
        if account_type == AccountType.user:
            return
        account = db.query(Admin).filter(Admin.id == admin_id).first()
        if not account:
            return

        mailer = PasswordResetMailer(account, account.password_reset_token, new_password)
        import asyncio

        if asyncio.iscoroutinefunction(mailer.send):
            asyncio.run(mailer.send())
        else:
            mailer.send()
    finally:
        db.close()
