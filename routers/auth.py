from fastapi import APIRouter
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi import Depends
from typing import Annotated
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm



router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(db, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return True

class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

# Read all users
@router.get("/auth_all", status_code=status.HTTP_200_OK)
async def read_all_users(db: db_dependency):
    users = db.query(Users).all()
    return users


# Create User
@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_users(db: db_dependency, user_request: UserRequest):
    user_model = Users(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password), 
        role=user_request.role,
        is_active=True
    )
    db.add(user_model)
    db.commit()
    return {"detail": "User created successfully"}


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return "Failed to authenticate"
    return "Authenticated successfully"
    