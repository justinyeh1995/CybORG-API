"""
To share fixtures across multiple test files in pytest, 
you should place them in a file named conftest.py, not configtest.py. 
The conftest.py file is a special configuration file for pytest, 
and pytest will automatically recognize and load fixtures defined in it.
"""

from typing import Generator
import pytest
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

from fastapi.testclient import TestClient

from api.v1.FastAPI.fastapi_index import app
from api.v1.FastAPI.api.deps import get_db
from api.v1.FastAPI.database import Base
from api.v1.FastAPI.crud import crud_user
from api.v1.FastAPI import schemas, models

# Load environment variables from .env file
load_dotenv()

# Get the database connection details from the environment variables
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = "test_database"
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

@pytest.fixture(name="db_session", scope="session") # you can give a fixture a name so that it can be injected into the test
def session_fixture():
    engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        db_session: Session = TestSessionLocal() # TODO we have to use the test database instead
        yield db_session
    finally:
        statement = delete(models.GameConfiguration)
        db_session.execute(statement)
        db_session.commit()

        # statement = delete(models.User)
        # db_session.execute(statement)
        # db_session.commit()
        
        db_session.close()
        
@pytest.fixture(name="client", scope="module")
def client_fixture(db_session):
    def override_get_db_session() -> Generator[Session, None, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db_session # https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#pytest-fixtures
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user", scope="session")
def test_user(db_session: Session):
    user_in = schemas.UserCreate(
        full_name="test_user_login",
        email="email@example.com",
        password="password",
        is_active=True,
        is_superuser=False,
    )
    user = crud_user.create_user(db_session, user_in)
    yield user
    
@pytest.fixture(name="test_user_jwt_token", scope="module")
def normal_user_token_headers(client: TestClient, test_user: models.User):
    r = client.post(
        "/api/login/access-token",
        data={"username": test_user.full_name, "password": "password"} # TODO: this is tight-coupuled here
        )
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    yield headers