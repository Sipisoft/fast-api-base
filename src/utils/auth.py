import base64
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from typing import Optional
from src.models.admin import Admin, AdminType
from src.models.users import User
from src.models.api_key import ApiKey
from src.db.database import get_db
from fastapi.security import OAuth2PasswordBearer

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from src.db.database import get_db
from src.mailers.otp_mailer import OTPMailer
from src.models.admin import Admin, get_admin_by_email
from src.models.api_client_token import ApiClientToken
from src.models.api_key import ApiKey
from src.models.otp_code import OtpCode, OtpPurpose
from src.utils.hash import Hash
from src.workers.tasks import send_otp_email_task
from typing import TypeVar,Type
from src.models.account import AccountBase

T = TypeVar("T", bound=AccountBase)
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OTP configuration (can be overridden via environment variables)
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
OTP_LOCKOUT_MINUTES = int(os.getenv("OTP_LOCKOUT_MINUTES", "10"))
OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "60"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




def get_account(account:Type[T],token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username = payload.get("sub")
        
        if not username:

            raise credentials_exception
        if not account:
            raise credentials_exception
        user = db.query(account).filter(account.username == username).first()
        if not user or user is None:
            raise credentials_exception
        return user
    except Exception as e:
        print(f"Error: {e}")
        raise credentials_exception


def get_current_admin(
        token: str = Depends(oauth2_schema),
        db: Session = Depends(get_db)
) -> Admin:
    return get_account(Admin, token, db)


def get_current_user(
        token: str = Depends(oauth2_schema),
        db: Session = Depends(get_db)
) -> User:
    return get_account(User, token, db)

def get_current_api_key(authorization: str = Header(...) , db: Session = Depends(get_db)) -> ApiKey:
    print("AUTHORIZATION", authorization)
    try:
        scheme, _, encryted_credentials = authorization.partition(" ")
        scheme = scheme.lower()
        if scheme not in  ["bearer", "bearerx"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")
        print("ENCRYPTED CREDENTIALS", encryted_credentials)
        credentials = encryted_credentials if  scheme == "bearer" else  base64.b64decode(encryted_credentials)
        key_id, secret = [credentials, _] if scheme == 'bearer' else credentials.decode().split(":")
        api_key = db.query(ApiClientToken).filter(ApiClientToken.id == key_id).filter(ApiClientToken.expires_at > datetime.now()).first().api_key if scheme == "bearer" else   db.query(ApiKey).filter(ApiKey.key_id == key_id).first()
        print("API KEY QUERY", api_key)
        if not api_key or api_key is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
        
        if not api_key.active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key is inactive.")
        if True if scheme == "bearer" else Hash.verify(secret, api_key.secret):
            return api_key
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")



def encode_basic_auth(username: str, password: str) -> str: 
    crecentials = f"{username}:{password}"
    encoded_bytes = base64.b64encode(crecentials.encode("utf-8"))
    encoded_str = encoded_bytes.decode("utf-8")
    return f"Basic {encoded_str}"

def generate_otp()->str:
    return "".join(str(secrets.randbelow(10)) for _ in range(6))


def generate_magic_link_token() -> str:
    return str(uuid4())


def send_otp_email(email:EmailStr,db: Session):

    try:
        admin = get_admin_by_email(db,email=email)
        now = datetime.utcnow()

        recent_active = (
            db.query(OtpCode)
            .filter(
                OtpCode.admin_id == admin.id,
                OtpCode.purpose == OtpPurpose.LOGIN,
                OtpCode.active == True,  # noqa: E712
                OtpCode.created_at > now - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS),
            )
            .order_by(OtpCode.created_at.desc())
            .first()
        )
        if recent_active is not None:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OTP was recently sent. Please wait before requesting a new code."
            )

        otp = generate_otp()
        magic_token = generate_magic_link_token()
        otp_code = OtpCode(
            admin_id=admin.id,
            code=Hash.encrypt(otp),
            secret=magic_token,
            purpose=OtpPurpose.LOGIN,
            expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
            max_attempts=OTP_MAX_ATTEMPTS,
        )
        db.add(otp_code)
        db.commit()
        db.refresh(otp_code)

        try:
            send_otp_email_task.delay(admin_id=admin.id, otp=otp, magic_token=magic_token)
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enqueue OTP email. Please try again later."
            )

        return
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again later."
        )


def verify_magic_link(token: str, db: Session) -> Admin:

    now = datetime.utcnow()
    otp_code = (
        db.query(OtpCode)
        .filter(
            OtpCode.secret == token,
            OtpCode.purpose == OtpPurpose.LOGIN,
            OtpCode.active == True,  # noqa: E712
        )
        .order_by(OtpCode.created_at.desc())
        .first()
    )
    if otp_code is None or otp_code.is_expired(now):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Magic link is invalid or has expired. Please request a new one."
        )

    admin = db.query(Admin).filter(Admin.id == otp_code.admin_id).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Magic link is invalid."
        )

    # Mark magic link as used and inactive (single-use)
    otp_code.mark_used(now)
    db.add(otp_code)
    db.commit()

    return admin


def verify_email_otp(email: EmailStr, otp: str, db: Session) -> Admin:

    admin = get_admin_by_email(db, email=email)
    now = datetime.utcnow()

    otp_code = (
        db.query(OtpCode)
        .filter(
            OtpCode.admin_id == admin.id,
            OtpCode.purpose == OtpPurpose.LOGIN,
            OtpCode.active == True,  # noqa: E712
        )
        .order_by(OtpCode.created_at.desc())
        .first()
    )

    if otp_code is None or otp_code.is_expired(now):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP is invalid or has expired. Please request a new code."
        )

    if otp_code.is_locked(now):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many invalid attempts. Please try again later."
        )

    # Verify OTP
    if not Hash.verify(otp, otp_code.code):
        otp_code.register_failed_attempt(now, OTP_LOCKOUT_MINUTES)
        db.add(otp_code)
        db.commit()
        db.refresh(otp_code)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP."
        )

    otp_code.mark_used(now)
    db.add(otp_code)
    db.commit()

    return admin


