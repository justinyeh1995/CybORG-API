from collections.abc import Generator
from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.networks import EmailStr
from pydantic import ValidationError

from sqlalchemy.orm import Session

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from FastAPI.database import SessionLocal
from api.v1.FastAPI import crud_user

from api.v1.FastAPI.api.core.security import get_password_hash, verify_password, create_access_token
 
from api.v1.FastAPI.api.core import security
from api.v1.FastAPI.api.core.config import settings

from api.v1.FastAPI.schemas import User, TokenPayload

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

def decode_token(token: str) -> User:
    # Decode the JWT token and extract the user details
    return User(
        username="user",
        email="user@example.com",
        full_name="User",
        is_admin=False
        )

async def get_current_user(token: str = TokenDep, db: Session = SessionDep):
    # Verify the JWT token using the token endpoint
    # If the token is valid, return the user details
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud_user.get_user_by_username(token_data.sub, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

@router.post("/token")
async def login(username: str, password: str):
    """Login Post"""
    return {"access_token": "user.username", "token_type": "bearer"}
