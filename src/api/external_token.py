
from fastapi import APIRouter, status, Depends
from src.models.api_client_token import ApiClientTokenResponse
from src.utils.auth import get_current_api_key
from src.models.api_key import ApiKey
from sqlalchemy.orm import Session 
from src.db.database import get_db
from src.models.api_client_token import   create as create_api_token
router = APIRouter(prefix='/token', tags=["token"],redirect_slashes=False)


@router.post("", response_model=ApiClientTokenResponse, status_code=status.HTTP_201_CREATED)
def create( current_api_key: ApiKey = Depends(get_current_api_key), db: Session = Depends(get_db)):
    return create_api_token(db, current_api_key)