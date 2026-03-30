import uuid

import pytest
from fastapi.testclient import TestClient
from main import app
from src.db.database import get_db,Base
from src.utils.auth import get_current_admin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
    return {
        "id":uuid.uuid4(),
        "email":"test@test.com",
        "role_id":uuid.uuid4(),
    }

app.dependency_overrides[get_current_admin] = override_get_current_admin

@pytest.fixture
def client(db_session):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)