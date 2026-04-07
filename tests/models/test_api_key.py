import pytest
import uuid
from sqlalchemy.orm import Session
from src.models.api_key import ApiKey, ApiKeyRequest, create, get_all
from src.models.admin import Admin
from src.utils.models import Pagination

def test_create_api_key(db_session: Session):
    admin = Admin(id=uuid.uuid4(), email="admin@test.com", username="admin", name="Admin", role_id=uuid.uuid4(), type="internal")
    db_session.add(admin)
    db_session.commit()

    api_key_data = ApiKeyRequest(
        name="Test API Key",
        description="Test Description",
        callback_url="http://test.com"
    )
    
    api_key = create(db_session, api_key_data, admin)
    
    assert api_key.name == "Test API Key"
    assert api_key.description == "Test Description"
    assert api_key.admin_id == admin.id
    assert api_key.secret != "********"
    assert len(api_key.secret) > 0

def test_get_all_api_keys(db_session: Session):
    admin = Admin(id=uuid.uuid4(), email="admin2@test.com", username="admin2", name="Admin 2", role_id=uuid.uuid4(), type="internal")
    db_session.add(admin)
    db_session.commit()

    api_key1 = ApiKey(name="Key 1", description="Desc 1", admin_id=admin.id, secret="secret1", key_id=str(uuid.uuid4()))
    api_key2 = ApiKey(name="Key 2", description="Desc 2", admin_id=admin.id, secret="secret2", key_id=str(uuid.uuid4()))
    db_session.add_all([api_key1, api_key2])
    db_session.commit()

    pagination = Pagination(page=1, size=10, all=False, start_date=None, end_date=None)
    response = get_all(db_session, pagination)
    
    assert response.total >= 2
    assert any(k.name == "Key 1" for k in response.data)
    assert any(k.name == "Key 2" for k in response.data)
