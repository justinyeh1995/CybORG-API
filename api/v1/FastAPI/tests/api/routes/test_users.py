from typing import Generator
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from api.v1.FastAPI.fastapi_index import app
from api.v1.FastAPI.api.deps import get_db
from api.v1.FastAPI.database import Base
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get the database connection details from the environment variables
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = "test_database"
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

@pytest.fixture(name="db_session") # you can give a fixture a name so that it can be injected into the test
def session_fixture():
    engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        db_session: Session = TestSessionLocal() # TODO we have to use the test database instead
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)

        
@pytest.fixture(name="client")
def client_fixture(db_session):
    def override_get_db_session() -> Generator[Session, None, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db_session # https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#pytest-fixtures
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# test create user
@pytest.mark.parametrize(
    "full_name, password, email, is_active, is_superuser",
    [("test_user", "password", "email@example.com", True, False)]
)
def test_create_user(client: TestClient, full_name, password, email, is_active, is_superuser):
    response = client.post(
        "/api/users/create",
        json={
            "full_name": full_name,
            "password": password,
            "email": email,
            "is_active": is_active,
            "is_superuser": is_superuser,
        }
    )
    
    data = response.json()
    
    assert response.status_code == 200  # Updated to match the endpoint's status code
    assert data["full_name"] == full_name
    assert data["email"] == email
    assert data["is_active"] == is_active
    assert data["is_superuser"] == is_superuser
    assert "user_id" in data  # Ensure user_id is present
 
                           
