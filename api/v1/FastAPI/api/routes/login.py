from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from api.v1.FastAPI.models import User
from api.v1.FastAPI.api.core.config import settings
from api.v1.FastAPI.api.core import security
from api.v1.FastAPI.api.deps import SessionDep
from api.v1.FastAPI.crud import crud_login as crud
from api.v1.FastAPI.schemas import Token, TokenPayload

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user: User | None = crud.authenticate(
        db_session=session, username=form_data.username, password=form_data.password
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
    
### TODO Add SSO login like Google account login support 