from typing import List
from uuid import UUID
from src.models.admin import Admin, AdminRequest, AdminResponse, admin_actions, create as create_admin, get as get_admin, get_all as get_all_admin, update as update_admin
from src.db.database import get_db
from fastapi import APIRouter, Depends, status, Body, Request
from sqlalchemy.orm import Session
from src.utils.auth import  get_current_admin
from src.utils.models import PaginatedResponse, Pagination


router = APIRouter(prefix="/admins", dependencies=[], tags=["admins"],redirect_slashes=False)


@router.get("", response_model=PaginatedResponse[AdminResponse], status_code=status.HTTP_200_OK)
def  index (current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db), pagination: Pagination = Depends(Pagination)):
    return  get_all_admin(db, current_admin, pagination)
    


@router.post("", response_model=AdminResponse, status_code=status.HTTP_200_OK)
async def create(admin: AdminRequest = Body(), current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db), request: Request = None):
    print("Current Admin", current_admin)
    new_admin = await create_admin(db, admin, current_admin, request)
    return AdminResponse.model_validate(new_admin)

@router.put("/{id}", response_model=AdminResponse, status_code=status.HTTP_200_OK)
def update(id: UUID,request: Request, admin: AdminRequest = Body(), current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    print("Current Admin", current_admin)
    return update_admin(db, id, admin, current_admin )


@router.put("/{id}/{action_name}", response_model=AdminResponse, status_code=status.HTTP_200_OK)
async def update_action(id: UUID,action_name: str,  current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db), request: Request = None):
    return await admin_actions(db, id,  current_admin, action_name, request)


@router.get("/{id}", response_model=AdminResponse, status_code=status.HTTP_200_OK,)
def show(id: UUID, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return get_admin(db, id, current_admin)

    
