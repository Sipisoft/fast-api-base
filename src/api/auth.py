from src.models.admin import AdminPasswordResetRequest, set_new_password, EmailOtpRequest, EmailOtpVerifyRequest
from src.db.database import get_db
from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from src.utils.auth import send_otp_email, verify_email_otp, create_access_token


router = APIRouter(prefix="/auth", dependencies=[], tags=["auth"],redirect_slashes=False)

@router.post("/set-password", description= "Reset Password", response_description="Reset Password", status_code=status.HTTP_200_OK)
def reset_password(password_reset_request: AdminPasswordResetRequest, db: Session = Depends(get_db)):
    set_new_password(db, password_reset_request)
    
    return {"message": "Password reset successfully!"}



@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def get_auth_otp(request: EmailOtpRequest, db: Session = Depends(get_db)):

    await send_otp_email(request.email, db)
    return {"message": "OTP sent successfully!"}

@router.post("/verify-otp", description="Verify OTP for email-based authentication", status_code=status.HTTP_200_OK)
async def verify_auth_otp(request: EmailOtpVerifyRequest, db: Session = Depends(get_db)):

    admin = await verify_email_otp(request.email, request.otp, db)
    access_token = create_access_token({"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}
