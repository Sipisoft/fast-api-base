import pytest
import uuid
from sqlalchemy.orm import Session
from src.models.api_client_token import ApiClientToken, create, get
from src.models.api_key import ApiKey

from datetime import datetime, timedelta

def test_create_api_client_token(db_session: Session):
    api_key = ApiKey(id=uuid.uuid4(), name="Token Test Key", description="Test", admin_id=uuid.uuid4(), secret="secret", key_id=str(uuid.uuid4()))
    db_session.add(api_key)
    db_session.commit()

    token_obj = ApiClientToken(
        api_key_id=api_key.id,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db_session.add(token_obj)
    db_session.commit()
    db_session.refresh(token_obj)
    
    assert token_obj.api_key_id == api_key.id
    assert isinstance(token_obj.id, uuid.UUID)
    assert token_obj.token == str(token_obj.id)
    assert token_obj.expires_at is not None

def test_get_api_client_token(db_session: Session):
    api_key = ApiKey(id=uuid.uuid4(), name="Get Token Test Key", description="Test", admin_id=uuid.uuid4(), secret="secret", key_id=str(uuid.uuid4()))
    db_session.add(api_key)
    db_session.commit()

    token_obj = ApiClientToken(
        id=uuid.uuid4(), 
        api_key_id=api_key.id,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db_session.add(token_obj)
    db_session.commit()

    fetched_token = get(db_session, token_obj.id)
    assert fetched_token is not None
    assert fetched_token.id == token_obj.id
