from http.client import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.v1.FastAPI import models, schemas

def create_user(username, password, db):
    pass

def update_user(username, db):
    pass

def delete_user(username, db):
    pass

def get_user_by_email(email, db):
    pass

def get_user_by_username(username, db):
    pass

def authenticate_user(email, password, db):
    pass
