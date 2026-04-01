from src.db.database import Base
from sqlalchemy import Column, DateTime, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID as pgUUId
from uuid import uuid4


class AccountBase(Base):
    __abstract__ = True

    id = Column(pgUUId(as_uuid=True), default=uuid4,primary_key=True)
    username = Column(String, unique=True)
    name=Column(String, unique=False, nullable=True)
    password = Column(String)
    email = Column(String, unique=True)

    password_reset_token = Column(String, unique=True, nullable=True)
    password_reset_token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), nullable=True)
    active = Column(Boolean, default=True)