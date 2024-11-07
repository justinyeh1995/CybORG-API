import pytest
from api.v1.FastAPI.crud import crud_user
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.FastAPI import models, schemas
from api.v1.FastAPI.api.core.config import settings

"""
Test cleint sent a form submission and response a token
"""

@pytest.fixture
def test_user(db_session: Session):
    user_in = schemas.UserCreate(
        full_name="test_user_login",
        email="email@example.com",
        password="password",
        is_active=True,
        is_superuser=False,
    )
    user = crud_user.create_user(db_session, user_in)
    return user

def test_get_access_token(client: TestClient, test_user: models.User) -> None:
    login_data = {
        "username": test_user.full_name, 
        "password": "password"
    }
    r = client.post(f"/api/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]