from typing import List
from src.db.database import get_db
from fastapi import APIRouter, Depends, status, Body
from src.models.user import User
from src.models.user import  UserRequest, UserResponse, get_all as get_all_users,update as update_user, user_actions
from sqlalchemy.orm import Session
from src.utils.auth import get_current_admin as get_current_user, oauth2_schema
from src.models.user import get as get_user

router = APIRouter(prefix="/users", dependencies=[], tags=["users"])

@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def index ( db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_users(db, current_user)

@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user(db, current_user, id)

@router.put("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update(id: int,  current_user: User = Depends(get_current_user), user: UserRequest = Body(), db: Session = Depends(get_db)):
    return update_user(db, id,  current_user, user)

@router.put("/{id}/{action_name}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_action(id: int,action_name: str,  current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_actions(db, id,  current_user, action_name)
