from src.db.database import Base
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
# or your actual Base

permissions_roles = Table(
    'permissions_roles',
    Base.metadata,
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)