from typing import List, Optional, Annotated
import uuid
from src.models.permission import Permission, PermissionResponse
from src.models.association_tables import permissions_roles
from src.db.database import Base
from fastapi import HTTPException, Request, status
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from pydantic import BaseModel, Field, computed_field
from src.utils.models import PaginatedResponse, Pagination, set_field_values

class Role(Base):
    __tablename__ = "roles"
    id = Column(pgUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, index=True)
    description = Column(String, unique=False, index=False, nullable=True)
    admins = relationship("Admin", back_populates="role")
    permissions = relationship("Permission", back_populates="roles", secondary=permissions_roles)
    permission_ids: list[uuid.UUID] = []
    active = Column(Boolean, default=True)
    class Config:
      from_attributes = True
  


class RoleRequest(BaseModel):
    name: str = Field(..., min_length=3, title= "Name", description= "Name of the Role")
    description: Optional[str] = Field(None, min_length=3, title= "Description", description= "Description of the Role")
    permission_ids: List[uuid.UUID] = Field([], title="Permission IDs", description="Permission IDs of the Role")

class RoleResponse(BaseModel):
    
    id: uuid.UUID
    name: str
    description: Optional[str]
    active: bool
    permissions: list[PermissionResponse]
    @computed_field
    
    def permission_ids(self) -> Annotated[List[uuid.UUID], computed_field(...)]:
        return [perm.id for perm in self.permissions]
    class Config:
        from_attributes = True

def create(db: Session, role: RoleRequest):
    db_role = Role()
    db_role =set_field_values(db_role, role)
    
    db_role.permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all() if role.permission_ids is not None else []
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update(db:Session, id: uuid.UUID, role: RoleRequest):
    db_role = get_one(db, id)
    db_role = set_field_values(db_role, role)
    db_role.permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all() if role.permission_ids is not None else []
    db.commit()
    db.refresh(db_role)
    return db_role
def get_all(db:Session, pagination: Pagination) -> PaginatedResponse[RoleResponse]:

    data = db.query(Role)
    if pagination.query:
        data = data.filter(Role.name.ilike(f"%{pagination.query}%"))
    total = data.count()
    if pagination.all is not True:
        data = data.order_by(Role.name.asc()).offset(pagination.skip).limit(pagination.limit)
    
    data =  data.all()
    return PaginatedResponse[RoleResponse].from_pagination(pagination=pagination, data=data, total = total)
    


def get_one(db, id: uuid.UUID):
    db_role = db.query(Role).filter(Role.id == id).first()
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role

async def actions(db: Base, id: uuid.UUID,  action_name: str, request: Request) -> Role:
    db_role = db.query(Role).filter(Role.id == id).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Admin not found")    
    if action_name == "deactivate": 
        db_role.active = False
        db.commit() 
        db.refresh(db_role)
        return db_role 
    if action_name == "activate":
        db_role.active = True
        db.commit()
        db.refresh(db_role)
        return db_role

    else:
        raise HTTPException(status_code=400, detail="Invalid action")
   