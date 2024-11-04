from typing import Generator
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from api.v1.FastAPI.database import SessionLocal
from FastAPI.fastapi_index import app
from FastAPI.api.deps import get_db

# Define the test client
client = TestClient(app)

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

# Build the database URL
TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:postgres@postgres:5432/cyborg_app"

engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # The ORM’s “handle” to the database is the Session.

# TestDB
## https://fastapi.tiangolo.com/advanced/testing-dependencies/#use-the-appdependency_overrides-attribute
def override_get_db() -> Generator[Session, None, None]:
    try:
        db = TestingSessionLocal() # TODO we have to use the test database instead
        yield db
    finally:
        db.close()
        
@pytest.fixture
def test_db():
    yield override_get_db()

app.dependency_overrides[get_db] = override_get_db # https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#pytest-fixtures

@pytest.fixture
def valid_user():
    return {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com",
    }

# test create user
@pytest.mark.parametrize("username, password, email", ["username", "password", "email"])
def test_create_user(username, password, email, **kwargs):
    pass
    response = client.post("/api/users/create",
                           json={})
