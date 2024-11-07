from sqlalchemy.orm import Session
from api.v1.FastAPI.schemas import User
from api.v1.FastAPI.crud_user import get_user_by_email, get_user_by_username
from api.v1.FastAPI.api.core.security import verify_password

def authenticate(db_session: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db_session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user