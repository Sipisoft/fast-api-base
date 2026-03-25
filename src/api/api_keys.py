from fastapi import APIRouter, Depends, status
from src.models.api_key import  ApiKeyRequest, ApiKeyResponse,ApiKeyWithSecretResponse,  create, get_all
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.models.admin import Admin
from src.utils.auth import get_current_admin
from src.utils.models import Pagination, PaginatedResponse
router = APIRouter(prefix="/api-keys", tags=["API Keys"],redirect_slashes=False)


@router.get("", response_model=PaginatedResponse[ApiKeyResponse], status_code=status.HTTP_200_OK)
async def list_api_keys(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin), pagination: Pagination = Depends(Pagination)) -> PaginatedResponse[ApiKeyResponse]:
    return get_all(db, pagination)

@router.post("", response_model=ApiKeyWithSecretResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(api_key: ApiKeyRequest, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return create(db, api_key, current_admin)