
from src.models.admin import Admin
from src.db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.models.role import Role, RoleRequest, RoleResponse, create, get_all, get_one, update, actions as role_actions
from uuid import UUID

from sqlalchemy.orm import Session
from src.utils.models import PaginatedResponse, Pagination
from src.utils.auth import get_current_admin
router = APIRouter(prefix='/roles', tags=["Roles"])

@router.get("", response_model=PaginatedResponse[RoleResponse], status_code=status.HTTP_200_OK)
def get_roles(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin), pagination: Pagination = Depends(Pagination)):
    return get_all(db, pagination)

@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleRequest,db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    return create(db, role)

@router.get("/{id}", response_model=RoleResponse)
def get_role(id: UUID, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    return get_one(db, id)

@router.put("/{id}", response_model=RoleResponse)
def update_role(id: UUID,  role: RoleRequest,db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    return update(db, id, role)

@router.put("/{id}/{action_name}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def update_action(id: UUID,action_name: str,  current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db), request: Request = None):
    return await role_actions(db, id,   action_name, request)