import uuid
import pytest
from fastapi.testclient import TestClient
from main import app
from src.db.database import get_db,Base
from src.utils.auth import get_current_admin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.auth import get_current_admin,get_current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.models.admin import Admin
from src.models.users import User

from fastapi import HTTPException, status

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
def override_get_current_admin():
    return Admin(
        id=uuid.uuid4(),
        email="test@test.com",
        role_id=uuid.uuid4(),
        username="testuser",
        name="Test User",
        active=True,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )

def override_get_current_user():
    return User(
        id=uuid.uuid4(),
        email="test@test.com",
        username="testuser",
        name="Test User",
        active=True,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )


def fake_current_admin_unauthenticated():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


@pytest.fixture(autouse=True)
def reset_auth_override():
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    app.dependency_overrides[get_current_user] = override_get_current_user

@contextmanager
def override_dependency(dep, new_dep):
    old_dep = app.dependency_overrides.get(dep)
    app.dependency_overrides[dep] = new_dep
    try:
        yield
    finally:
        if old_dep is not None:
            app.dependency_overrides[dep] = old_dep
        else:
            app.dependency_overrides.pop(dep, None)

@pytest.fixture
def client(db_session):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)
