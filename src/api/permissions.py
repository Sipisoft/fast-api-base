from fastapi import APIRouter, status
from src.models.permission import PermissionResponse
from src.models.admin import Admin
from src.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from src.utils.auth import get_current_admin
from src.utils.models import PaginatedResponse, Pagination
router = APIRouter(prefix="/permissions", tags=["Permissions"],redirect_slashes=False)

@router.get("", response_model=PaginatedResponse[PermissionResponse], status_code=status.HTTP_200_OK)
def get_permissions(db: Session = Depends(get_db),pagination: Pagination = Depends(Pagination), current_admin: Admin = Depends(get_current_admin)):
    from src.models.permission import PermissionResponse, get_all_permissions
    return get_all_permissions(db, current_admin, pagination)
    