
from sqlalchemy import and_, or_
from src.db.database import get_db
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from src.models.admin import Admin
from sqlalchemy.orm import Session
from src.utils.auth import create_access_token
from src.utils.hash import Hash

router = APIRouter(prefix="/token", dependencies=[], tags=["token"], responses={401: {"description": "Unauthenticated"}  ,404: {"description": "Not Found"}})


@router.post("")
def show(request: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    
    
    model_class =  Admin
    user = db.query(model_class).filter(and_(or_(model_class.username == request.username, model_class.email == request.username), model_class.active == True)).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User with username {request.username} not found")
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Incorrect password")
        
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

