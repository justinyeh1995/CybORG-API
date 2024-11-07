from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.networks import EmailStr
from fastapi.security import OAuth2PasswordBearer
import passlib

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from api.v1.FastAPI.api.core.security import get_password_hash, verify_password, create_access_token

from api.v1.FastAPI.schemas import User, UserCreate
import api.v1.FastAPI.crud.crud_user as crud

from api.v1.FastAPI.api.deps import SessionDep

router = APIRouter()

### create a user
@router.post("/create")
async def create_user(user_in: UserCreate,
                      db_session: SessionDep):
    user = crud.create_user(db_session, user_in)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return user
    
### update user password, email, username 
### delete user



# @router.post("/token")
# async def login(username: str, password: str):
#     """Login Post"""
#     return {"access_token": "user.username", "token_type": "bearer"}
