from typing import Generator
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from api.v1.FastAPI import app
from api.v1.FastAPI.database import SessionLocal

# Define the test client
client = TestClient(app)

# TestDB
## https://fastapi.tiangolo.com/advanced/testing-dependencies/#use-the-appdependency_overrides-attribute
def override_get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


