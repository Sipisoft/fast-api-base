from uuid import uuid4, UUID
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from src.db.database import Base
from src.models.api_key import ApiKey
from pydantic import BaseModel
import datetime
from datetime import datetime

class ApiClientToken(Base):
    __tablename__ = "api_client_tokens"
    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    api_key_id = Column(pgUUID(as_uuid=True), ForeignKey('api_keys.id'), nullable=False, index=True)
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default="(now() + interval '30 minutes')"
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")
    api_key = relationship("ApiKey", back_populates="api_client_tokens")

    @property
    def token(self):
        return str(self.id)

class ApiClientTokenResponse(BaseModel): 
    token: str
    expires_at: datetime

    class Config:
        orm_mode = True

def create(db: Base, api_key: ApiKey) -> ApiClientToken: 
    token = ApiClientToken(api_key_id= api_key.id)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

def get(db: Base, id: UUID)-> ApiClientToken: 
    token = db.query(ApiClientToken).filter(ApiClientToken.id == id).first()