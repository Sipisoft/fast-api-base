import src.models
from src.mailers.otp_mailer import OTPMailer
from src.models.admin import Admin
from src.db.database import SessionLocal
from celery_app import celery_app


@celery_app.task(name="send_otp_email_task")
def send_otp_email_task(admin_id: int, otp: str, magic_token: str) -> None:

    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return

        mailer = OTPMailer(admin, otp, magic_token)
        import asyncio

        if asyncio.iscoroutinefunction(mailer.send):
            asyncio.run(mailer.send())
        else:
            mailer.send()
    finally:
        db.close()
