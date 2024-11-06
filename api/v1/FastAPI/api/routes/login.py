from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from FastAPI.schemas import User
from FastAPI.api.core.config import settings
from FastAPI.api.core import security
from FastAPI.api.deps import SessionDep
from FastAPI.crud import crud_login as crud
from FastAPI.schemas import Token, TokenPayload

router = APIRouter()

@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user: User | None = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.user_id, expires_delta=access_token_expires
        )
    )

# @router.post('/login')
# async def login(username: str, password: str):
#     # Check if the user exists in the database
#     # If the user exists, verify the password using passlib
#     # If the password is correct, generate a JWT token and return it to the user
#     # If the password is incorrect, return an error message
#     return {"message": "Login successful"}

# @router.post('/register')