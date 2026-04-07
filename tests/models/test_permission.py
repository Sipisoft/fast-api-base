import pytest
from sqlalchemy.orm import Session
from src.models.permission import Permission, populate_permissions, get_all_permissions
from src.utils.models import Pagination

def test_populate_permissions(db_session: Session):
    db_session.query(Permission).delete()
    db_session.commit()

    populate_permissions(db_session)
    
    permissions = db_session.query(Permission).all()
    assert len(permissions) > 0
    
    actions = ["CREATE", "UPDATE", "DESTROY", "LIST", "GET"]
    for action in actions:
        assert any(p.action == action for p in permissions)

def test_get_all_permissions(db_session: Session):
    populate_permissions(db_session)
    
    pagination = Pagination(page=1, size=10, all=False, start_date=None, end_date=None)
    response = get_all_permissions(db_session, None, pagination)
    
    assert response.total > 0
    assert len(response.data) <= 10
    assert response.page == 1

def test_get_all_permissions_pagination(db_session: Session):
    populate_permissions(db_session)
    total_count = db_session.query(Permission).count()
    
    pagination = Pagination(page=1, size=5, all=False, start_date=None, end_date=None)
    response = get_all_permissions(db_session, None, pagination)
    assert len(response.data) == 5
    assert response.total == total_count

    pagination2 = Pagination(page=2, size=5, all=False, start_date=None, end_date=None)
    response2 = get_all_permissions(db_session, None, pagination2)
    assert len(response2.data) > 0
    assert response2.data[0].id != response.data[0].id
