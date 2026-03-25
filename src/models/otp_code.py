from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from src.db.database import Base


class OtpPurpose:
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    admin_id = Column(pgUUID(as_uuid=True), ForeignKey("admins.id"), index=True, nullable=False)
    code_hash = Column(String, nullable=False)
    purpose = Column(String, nullable=False, default=OtpPurpose.LOGIN)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=5)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    used_at = Column(DateTime, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    def is_expired(self, now: datetime | None = None) -> bool:
        now = now or datetime.utcnow()
        return self.expires_at < now

    def is_locked(self, now: datetime | None = None) -> bool:
        now = now or datetime.utcnow()
        return self.locked_until is not None and self.locked_until > now

    def register_failed_attempt(self, now: datetime, lockout_minutes: int) -> None:
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.locked_until = now + timedelta(minutes=lockout_minutes)

    def mark_used(self, now: datetime) -> None:
        self.used_at = now
        self.active = False
