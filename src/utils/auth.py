from datetime import datetime, timedelta, timezone
import base64
from typing import Optional
from src.models.admin import Admin, AdminType
from src.models.users import User
from src.models.api_key import ApiKey
from src.db.database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Header
from src.models.api_client_token import ApiClientToken
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from jose import jwt
from src.utils.hash import Hash
from typing import TypeVar,Type
from src.models.account import AccountBase

T = TypeVar("T", bound=AccountBase)
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta: 
        expire = datetime.now(timezone.utc) + expires_delta
    else: 
        expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
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