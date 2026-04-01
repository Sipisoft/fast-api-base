
from datetime import datetime, timedelta
from email.policy import default
from enum import Enum
from typing import Optional
from uuid import UUID


from src.models.role import RoleResponse
from src.db.database import Base
from sqlalchemy import Column,ForeignKey, Enum as SQLAlchemyEnum
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session, relationship
from fastapi import HTTPException, status, Request
from src.utils.hash import Hash
from src.utils.password import generate_strong_password
from sqlalchemy.dialects.postgresql import UUID as pgUUId
from src.utils.models import PaginatedResponse, Pagination, set_field_values

from .account import AccountBase

class AdminType(str, Enum):
    internal = "internal"
    external = "external"
    
class Admin(AccountBase):
    __tablename__ = "admins"

    type= Column(SQLAlchemyEnum(AdminType), index=True,  nullable=False, unique=False )
    role_id = Column(pgUUId(as_uuid=True), ForeignKey('roles.id'), index=True, nullable=True)
    role = relationship("Role", back_populates="admins")
    api_keys = relationship("ApiKey", back_populates="admin")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class AdminPasswordResetRequest(BaseModel):
    password: str = Field(..., min_length=6, title= "Password", description= "Password of the User")
    password_confirmation: str = Field(..., min_length=6, title= "Password Confirmation", description= "Password Confirmation of the User")
    password_token: str = Field(..., title= "Password Reset Token", description= "Password Reset Token of the User")

class AdminRequest(BaseModel):
    username: str = Field(... , min_length=3, title= "Username", description= "Username of the User")
    email: EmailStr = Field(..., title= "Email", description= "Email of the User")
    
    name: str = Field(..., min_length=3, title= "Name", description= "Name of the User")
    type: AdminType = Field(default=AdminType.external, title="Admin Type", description="Type of Admin")
    role_id: UUID = Field(..., title="Role ID", description="Role ID of the Admin")

class AdminProfileRequest(BaseModel):
    name: str = Field(..., min_length=3, title= "Name", description= "Name of the User")
    phone: Optional[str] = Field(None, min_length=3, title= "Phone", description= "Phone of the User")
    

class AdminLoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    name: str = Field(...)
    role: Optional[RoleResponse] = None
class AdminResponse(BaseModel):
    id: UUID
    username: str
    email: str
    name: str
    active: bool
    role_id: UUID
    role: Optional[RoleResponse] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

async def create(db: Session, admin: AdminRequest, current_admin: Admin , request: Request = None) -> Admin:
    from src.mailers.password_reset_mailer import PasswordResetMailer
    
    try:
        db_admin = Admin()
        db_admin = set_field_values(db_admin, admin)
        db_admin.type = AdminType.internal
        temp_password = generate_strong_password()
        db_admin.password = Hash.encrypt(temp_password)
        password_token = Hash.generate_token()
        db_admin.password_reset_token = password_token
        db_admin.password_reset_token_expires_at = datetime.utcnow() + timedelta(minutes=15)
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        if request is not None:
            try: 
                await PasswordResetMailer(db_admin, db_admin.password_reset_token, True, request).send()
            except Exception as e2:
                print(f"Failed to send email for admin: {db_admin.email}")
        
        return db_admin
    except Exception as e:
        db.rollback()  # Rollback the transaction on error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create admin: {str(e)}"
        )

def update(db: Session, id: int, admin: AdminRequest, current_admin: Admin):
    db_admin = get_admins(db, current_admin).filter(Admin.id == id).first()
    
    if db_admin is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_admin = set_field_values(db_admin, admin)
   
    db.commit()
    db.refresh(db_admin)
    return db_admin


async def admin_actions(db: Session, id: int, current_admin: Admin, action_name: str, request: Request) -> Admin:
    #PLUG ACCESS CONTROL
    db_admin = get_admins(db, current_admin).filter(Admin.id == id).first()

    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")    
    if action_name == "deactivate": 
        db_admin.active = False
        db.commit() 
        db.refresh(db_admin)
        return db_admin 
    if action_name == "activate":
        db_admin.active = True
        db.commit()
        db.refresh(db_admin)
        return db_admin 
    if action_name == "reset_password": 
        from src.mailers.password_reset_mailer import PasswordResetMailer
        token = Hash.generate_token()
        #Send password via email 
        print("This is toke", token)
        db_admin.password_reset_token = token
        db_admin.password_reset_token_expires_at = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
        db.refresh(db_admin)
        
        await PasswordResetMailer(db_admin, token,False, request).send()
        return db_admin

def delete(db:Session, id: int, current_admin: Admin):
    db_admin = get_admins(db, current_admin).filter(Admin.id == id).first()
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    db.delete(db_admin)
    db.commit()
    return db_admin
def get(db: Session, id: int, current_admin: Admin) -> Admin:
    return get_admins(db, current_admin).filter(Admin.id == id).first()
    

def get_all(db: Session, current_admin: Admin, pagination: Pagination) -> PaginatedResponse[AdminResponse]:
    data = get_admins(db, current_admin)
    if pagination.query:
        data = data.filter(Admin.name.ilike(f"%{pagination.query}%"))
    total = data.count()
    if pagination.all is not True:
        data = data.order_by(Admin.name.asc()).offset(pagination.skip).limit(pagination.limit)
    data =  data.all()
    return PaginatedResponse[AdminResponse].from_pagination(pagination=pagination, data=data, total = total)

def get_admins(db: Session, current_admin: Admin) -> list[Admin]: 
        return db.query(Admin)


def set_new_password(db: Session, password_reset_request: AdminPasswordResetRequest):
    if password_reset_request.password != password_reset_request.password_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    admin = db.query(Admin).filter(Admin.password_reset_token == password_reset_request.password_token, Admin.password_reset_token_expires_at > datetime.utcnow()).first()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password reset token")
    admin.password = Hash.encrypt(password_reset_request.password)
    db.commit()
    db.refresh(admin)
    return admin