from typing import List
from src.db.database import get_db
from fastapi import APIRouter, Depends, status, Body
from src.models.users import User
from src.models.users import  UserRequest, UserResponse, get_all,update , user_actions
from sqlalchemy.orm import Session
from src.utils.auth import  get_current_user
from src.models.users import get as get_user
from uuid import UUID
from src.utils.models import PaginatedResponse, Pagination, set_field_values
router = APIRouter(prefix="/users", dependencies=[], tags=["users"])

@router.get("", response_model=PaginatedResponse[UserResponse], status_code=status.HTTP_200_OK)
def index ( db: Session = Depends(get_db), current_user: User = Depends(get_current_user), pagination: Pagination = Depends(Pagination)):
    return get_all(db, current_user, pagination)

@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get(id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user(db, id, current_user)

@router.put("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update(id: UUID,  current_user: User = Depends(get_current_user), user: UserRequest = Body(), db: Session = Depends(get_db)):
    from src.models.users import update as update_user
    return update_user(db, id, user, current_user)

@router.put("/{id}/{action_name}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_action(id: UUID,action_name: str,  current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_actions(db, id,  current_user, action_name, None)
