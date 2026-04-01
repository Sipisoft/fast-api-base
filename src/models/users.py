from sqlalchemy import Index
from src.db.database import Base
from pydantic import Field, BaseModel, EmailStr,ConfigDict
from uuid import uuid4, UUID
from datetime import datetime,timedelta
from sqlalchemy.orm import Session, Query
from fastapi import Request,HTTPException, status
from src.utils.hash import Hash
from src.utils.password import generate_strong_password
from src.utils.models import PaginatedResponse, Pagination, set_field_values
from typing import Optional
from .account import AccountBase


class User(AccountBase):
    __tablename__ = "users"

class UserPasswordResetRequest(BaseModel):
    password: str = Field(..., min_length=6, title= "Password", description= "Password of the User")
    password_confirmation: str = Field(..., min_length=6, title= "Password Confirmation", description= "Password Confirmation of the User")
    password_token: str = Field(..., title= "Password Reset Token", description= "Password Reset Token of the User")

class UserRequest(BaseModel):
    username: str = Field(... , min_length=3, title= "Username", description= "Username of the User")
    email: EmailStr = Field(..., title= "Email", description= "Email of the User")

    name: str = Field(..., min_length=3, title= "Name", description= "Name of the User")

class UserProfileRequest(BaseModel):
    name: str = Field(..., min_length=3, title= "Name", description= "Name of the User")
    phone: Optional[str] = Field(None, min_length=3, title= "Phone", description= "Phone of the User")


class UserLoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    name: str = Field(...)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    name: str
    active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

def get_users(db: Session, current_user: User) -> Query[User]:
    return db.query(User)


async def create(db: Session, user: UserRequest, current_user: User , request: Request = None) -> User:
    from src.mailers.password_reset_mailer import PasswordResetMailer

    try:
        db_user = User()
        db_user = set_field_values(db_user, user)
        temp_password = generate_strong_password()
        db_user.password = Hash.encrypt(temp_password)
        password_token = Hash.generate_token()
        db_user.password_reset_token = password_token
        db_user.password_reset_token_expires_at = datetime.utcnow() + timedelta(minutes=15)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        if request is not None:
            try:
                await PasswordResetMailer(db_user, db_user.password_reset_token, True, request).send()
            except Exception as e2:
                print(f"Failed to send email for user: {db_user.email}")

        return db_user
    except Exception as e:
        db.rollback()  # Rollback the transaction on error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


def update_user(db: Session, id: UUID, user: UserRequest, current_user: User):
    db_user = get_users(db, current_user).filter(User.id == id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = set_field_values(db_user, user)

    db.commit()
    db.refresh(db_user)
    return db_user


async def user_actions(db: Session, id: UUID, current_user: User, action_name: str, request: Request = None) -> User:

    db_user = get_users(db, current_user).filter(User.id == id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if action_name == "deactivate":
        db_user.active = False
        db.commit()
        db.refresh(db_user)
        return db_user

    if action_name == "activate":
        db_user.active = True
        db.commit()
        db.refresh(db_user)
        return db_user

    if action_name == "reset_password":
        from src.mailers.password_reset_mailer import PasswordResetMailer
        token = Hash.generate_token()
        db_user.password_reset_token = token
        db_user.password_reset_token_expires_at = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
        db.refresh(db_user)

        await PasswordResetMailer(db_user, token,False, request).send()
        return db_user

def delete(db:Session, id: UUID, current_user: User):
    db_user = get_users(db, current_user).filter(User.id == id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    db.delete(db_user)
    db.commit()
    return db_user

def get(db: Session, id: UUID, current_user: User) -> User:
    return get_users(db, current_user).filter(User.id == id).first()


def get_all(db: Session, current_user: User, pagination: Pagination) -> PaginatedResponse[UserResponse]:
    data = get_users(db, current_user)
    if pagination.query:
        data = data.filter(User.name.ilike(f"%{pagination.query}%"))
    total = data.count()
    if pagination.all is not True:
        data = data.order_by(User.name.asc()).offset(pagination.skip).limit(pagination.limit)
    data =  data.all()
    return PaginatedResponse[UserResponse].from_pagination(pagination=pagination, data=data, total = total)


def set_new_password(db: Session, password_reset_request: UserPasswordResetRequest):
    if password_reset_request.password != password_reset_request.password_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    user = db.query(User).filter(User.password_reset_token == password_reset_request.password_token, User.password_reset_token_expires_at > datetime.utcnow()).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password reset token")
    user.password = Hash.encrypt(password_reset_request.password)
    db.commit()
    db.refresh(user)
    return user