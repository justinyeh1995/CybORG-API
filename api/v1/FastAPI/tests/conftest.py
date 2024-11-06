"""
To share fixtures across multiple test files in pytest, 
you should place them in a file named conftest.py, not configtest.py. 
The conftest.py file is a special configuration file for pytest, 
and pytest will automatically recognize and load fixtures defined in it.
"""

from typing import Generator
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from api.v1.FastAPI.fastapi_index import app
from api.v1.FastAPI.api.deps import get_db
from api.v1.FastAPI.database import Base
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
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
