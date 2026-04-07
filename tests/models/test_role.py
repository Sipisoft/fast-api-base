import pytest
import uuid
from sqlalchemy.orm import Session
from src.models.role import Role, RoleRequest, create, update, get_all, get_one, actions
from src.models.permission import Permission
from datetime import date
from src.utils.models import Pagination

def test_create_role(db_session: Session):
    permission1 = Permission(id=uuid.uuid4(), action="CREATE", resource="test", description="Test Create")
    permission2 = Permission(id=uuid.uuid4(), action="UPDATE", resource="test", description="Test Update")
    db_session.add(permission1)
    db_session.add(permission2)
    db_session.commit()

    role_data = RoleRequest(
        name="Test Role",
        description="Test Description",
        permission_ids=[permission1.id, permission2.id]
    )
    
    role = create(db_session, role_data)
    
    assert role.name == "Test Role"
    assert role.description == "Test Description"
    assert len(role.permissions) == 2
    assert permission1 in role.permissions
    assert permission2 in role.permissions

def test_update_role(db_session: Session):
    permission1 = Permission(id=uuid.uuid4(), action="CREATE", resource="test", description="Test Create")
    db_session.add(permission1)
    db_session.commit()

    role = Role(name="Old Name", description="Old Desc")
    db_session.add(role)
    db_session.commit()

    update_data = RoleRequest(
        name="New Name",
        description="New Desc",
        permission_ids=[permission1.id]
    )
    
    updated_role = update(db_session, role.id, update_data)
    
    assert updated_role.name == "New Name"
    assert updated_role.description == "New Desc"
    assert len(updated_role.permissions) == 1
    assert updated_role.permissions[0].id == permission1.id

def test_get_one_role(db_session: Session):
    role = Role(name="Get One Role")
    db_session.add(role)
    db_session.commit()

    fetched_role = get_one(db_session, role.id)
    assert fetched_role.id == role.id
    assert fetched_role.name == "Get One Role"

def test_get_one_role_not_found(db_session: Session):
    with pytest.raises(Exception) as excinfo:
        get_one(db_session, uuid.uuid4())
    assert "404" in str(excinfo.value)

def test_get_all_roles(db_session: Session):
    db_session.query(Role).delete()
    db_session.commit()

    db_session.add(Role(name="Role A"))
    db_session.add(Role(name="Role B"))
    db_session.commit()

    pagination = Pagination(page=1, size=10, all=True)
    response = get_all(db_session, pagination)
    
    assert response.total >= 2
    assert any(r.name == "Role A" for r in response.data)
    assert any(r.name == "Role B" for r in response.data)

def test_get_all_roles_with_query(db_session: Session):
    db_session.add(Role(name="Admin Role"))
    db_session.add(Role(name="User Role"))
    db_session.commit()

    pagination = Pagination(page=1, size=10, all=True, query="Admin")
    response = get_all(db_session, pagination)
    
    assert response.total == 1
    assert response.data[0].name == "Admin Role"

@pytest.mark.anyio
async def test_role_actions_activate_deactivate(db_session: Session):
    role = Role(name="Action Role", active=True)
    db_session.add(role)
    db_session.commit()

    # Deactivate
    updated_role = await actions(db_session, role.id, "deactivate", None)
    assert updated_role.active is False

    # Activate
    updated_role = await actions(db_session, role.id, "activate", None)
    assert updated_role.active is True

@pytest.mark.anyio
async def test_role_actions_invalid(db_session: Session):
    role = Role(name="Invalid Action Role")
    db_session.add(role)
    db_session.commit()

    with pytest.raises(Exception) as excinfo:
        await actions(db_session, role.id, "invalid_action", None)
    assert "400" in str(excinfo.value)
