from collections.abc import Generator
from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, Depends, HTTPException, status
from pydantic.networks import EmailStr
from pydantic import ValidationError

from sqlalchemy.orm import Session

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

import redis.asyncio as redis

from api.v1.FastAPI.database import SessionLocal
from api.v1.FastAPI.crud import crud_user

from api.v1.FastAPI.api.core.security import get_password_hash, verify_password, create_access_token
 
from api.v1.FastAPI.api.core import security
from api.v1.FastAPI.api.core.config import settings

from api.v1.FastAPI.schemas import User, TokenPayload
from api.v1.FastAPI import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/access-token")

def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_redis_client(request: Request):
    return request.app.state.redis_client

# RedisClientDep = Annotated[redis.Redis, Depends(get_redis_client)]
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(token: TokenDep, db: SessionDep) -> User:
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
    user = crud_user.get_user_by_id(db, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return User.from_orm(user)

CurrentUserDep = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user