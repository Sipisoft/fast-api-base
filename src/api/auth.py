from src.models.admin import AdminPasswordResetRequest, set_new_password
from src.db.database import get_db
from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", dependencies=[], tags=["auth"],redirect_slashes=False)

@router.post("/set-password", description= "Reset Password", response_description="Reset Password", status_code=status.HTTP_200_OK)
def reset_password(password_reset_request: AdminPasswordResetRequest, db: Session = Depends(get_db)):
    set_new_password(db, password_reset_request)
    
    return {"message": "Password reset successfully!"}


        