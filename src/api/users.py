from typing import List
from src.db.database import get_db
from fastapi import APIRouter, Depends, status, Body
from src.models.admin import Admin
from src.models.user import UserAdminRequest, UserRequest, UserResponse, get_all_users, update_user, user_actions
from sqlalchemy.orm import Session
from src.utils.auth import get_current_admin, oauth2_schema
from src.models.user import get_user, update_user

router = APIRouter(prefix="/users", dependencies=[], tags=["users"])

@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def index ( db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return get_all_users(db, current_admin)

@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get(id: int, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return get_user(db, current_admin, id)

@router.put("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update(id: int,  current_admin: Admin = Depends(get_current_admin), user: UserAdminRequest = Body(), db: Session = Depends(get_db)):
    return update_user(db, id,  current_admin, user)

@router.put("/{id}/{action_name}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_action(id: int,action_name: str,  current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return user_actions(db, id,  current_admin, action_name)

# async def get_users(db: Session = Depends(get_db)):
#     return db.query(User).all()