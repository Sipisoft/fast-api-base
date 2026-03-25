from typing import Optional
from uuid import uuid4, UUID
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from src.db.database import Base
from src.utils.hash import Hash
from pydantic import BaseModel, Field, field_serializer
from src.models.admin import Admin
from src.utils.models import PaginatedResponse, Pagination, set_field_values
class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(pgUUID(as_uuid=True), default=uuid4, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    key_id = Column(String, unique=True, nullable=False, index=True, server_default=uuid4().hex)
    description = Column(String, unique=False, nullable=False, index=False)
    secret = Column(String, nullable=False, index=False)
    admin_id = Column(pgUUID(as_uuid=True), ForeignKey('admins.id'), nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False, server_default='true')
    callback_url = Column(String,default="",nullable=True)
    callback_username = Column(String,default="",nullable=True)
    callback_password = Column(String,default="",nullable=True)
    admin = relationship("Admin", back_populates="api_keys")
    api_client_tokens = relationship("ApiClientToken", back_populates="api_key")

class ApiKeyRequest(BaseModel):
    name: str = Field(..., min_length=3, title="Name", description="Name of the API Key")
    description: str = Field(..., min_length=3, title="Description", description="Description of the API Key")
    callback_url: str = Field("",  title="Callback URL", description="Callback URL of the API Key")
    callback_username: str = Field("",  title="Callback Username", description="Callback Username of the API Key")
    callback_password: str = Field("",  title="Callback Password", description="Callback Password of the API Key")
    
class ApiKeyWithSecretResponse(BaseModel):
    id: UUID
    name: str
    description: str
    # active: bool
    secret: str
    key_id: UUID
    callback_url: Optional[str]
    admin_id: UUID
    class Config:
        from_attributes = True
class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    description: str
    key_id: UUID
    # active: bool
    secret: str
    callback_url: Optional[str]
    admin_id: UUID
    class Config:
        from_attributes = True
    @field_serializer("secret")
    def mask_secret(self, value: str) -> str:
        return "********"

def get_all(db: Base, pagination: Pagination)  -> PaginatedResponse[ApiKeyResponse]:
    data =  db.query(ApiKey)
    total = data.count()
    if pagination.all is not True:
        data = data.offset(pagination.skip).limit(pagination.limit)
    
    data =  data.all()
    return PaginatedResponse[ApiKeyResponse].from_pagination(pagination=pagination, data=data, total = total)


def create(db: Base, api_key: ApiKeyRequest, current_admin: Admin) -> ApiKey:
    db_api_key = ApiKey()
    db_api_key = set_field_values(db_api_key, api_key)
    token = Hash.generate_api_key()
    db_api_key.admin_id = current_admin.id
    db_api_key.secret = Hash.encrypt(token) 
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    db_api_key.secret = token  # Return the plain token only once upon creation
    return db_api_key
