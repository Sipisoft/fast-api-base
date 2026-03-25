from src.db.database import get_db
from fastapi import APIRouter, Depends, status
from src.models.admin import Admin, AdminProfileRequest, AdminRequest, AdminResponse, update as update_admin
from sqlalchemy.orm import Session
from src.utils.auth import get_current_admin
router = APIRouter(prefix="/profile", dependencies=[], tags=["profile"])

@router.get("", response_model=AdminResponse, status_code=status.HTTP_200_OK)
def index(current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return current_admin

@router.put("", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def update(admin: AdminProfileRequest, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return update_admin(db, current_admin.id, admin, current_admin)