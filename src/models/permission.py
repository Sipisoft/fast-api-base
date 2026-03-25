from typing import Annotated, Optional
import uuid
from src.models.association_tables import permissions_roles
from src.db.database import Base
from pydantic import BaseModel, Field, computed_field, ConfigDict
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from src.utils import app_permissions
from sqlalchemy.orm import relationship, Session

from src.utils.models import PaginatedResponse, Pagination



class Permission(Base):
    __tablename__ = "permissions"
    id = Column(pgUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    action = Column(String, unique=False, index=True)
    description = Column(String, unique=False, index=False, nullable=True)
    resource = Column(String, unique=False, index=False, nullable=True) 
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    roles = relationship('Role', secondary=permissions_roles, back_populates='permissions')
    model_config = ConfigDict(from_attributes=True)
    class Config:
        from_attributes = True
    


class PermissionRequest(BaseModel):
    action: str = Field(..., min_length=3, title= "Name", description= "Name of the Permission") 
    resource: str = Field(..., min_length=3, title= "Resource", description= "Resource of the Permission")
    description: Optional[str] = Field(None, min_length=3, title= "Description", description= "Description of the Permission")


class PermissionResponse(BaseModel):
    id: uuid.UUID
    action: str
    resource: str
    description: Optional[str]
    
    @computed_field
    def name(self)-> Annotated[str, property]:
         return f"{self.resource}:{self.action}"
    class Config:
        from_attributes = True

def populate_permissions(db):
    for key, value in app_permissions.APP_PERMISSIONS.items():
        for model_name in app_permissions.get_models(): 
            existing_permission = db.query(Permission).filter(Permission.action == key, Permission.resource== model_name).first()
            if existing_permission is not None:
                continue
            
            db.add(Permission(action=app_permissions.ActionsEnum(key), resource=model_name, description=value))
            db.commit()
            # db.refresh(db)
def get_all_permissions(db: Session, current_admin, pagination: Pagination) -> PaginatedResponse[PermissionResponse]: 

    data = db.query(Permission)
    total = data.count()
    if pagination.all is not True:
        data = data.offset(pagination.skip).limit(pagination.limit)
    
    data =  data.all()

    return PaginatedResponse[PermissionResponse].from_pagination(pagination=pagination, data=data, total = total)
    
