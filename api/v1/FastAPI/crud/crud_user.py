from http.client import HTTPException
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.v1.FastAPI import models, schemas
from api.v1.FastAPI.schemas import User
from api.v1.FastAPI.api.core.security import get_password_hash
import uuid

def create_user(db_session: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user_in.password)
    user = models.User(user_id=str(uuid.uuid4()),
                email=user_in.email, 
                full_name=user_in.full_name, 
                hashed_password=hashed_password,
                is_active=user_in.is_active,
                is_superuser=user_in.is_superuser)
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def update_user(username, db):
    pass

def delete_user(username, db):
    pass

def get_user_by_email(session: Session, email: str) -> models.User | None:
    statement = select(models.User).where(models.User.email == email)
    result = session.execute(statement)
    user = result.scalars().first()
    return user

def get_user_by_username(session: Session, username: str) -> models.User | None:
    statement = select(models.User).where(models.User.full_name == username)
    result = session.execute(statement)
    user = result.scalars().first()
    return user

def get_user_by_id(session: Session, user_id: str) -> models.User | None:
    statement = select(models.User).where(models.User.user_id == user_id)
    result = session.execute(statement)
    user = result.scalars().first()
    return user

def authenticate_user(email, password, db):
    pass
