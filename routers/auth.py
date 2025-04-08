from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from ..models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..database import SessionLocal
from fastapi import Depends
from typing import Annotated
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import timedelta, datetime, timezone







router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "66a9349c91349a566620937520e450a83357cf3344eec82161a5a3cc21395f78"
ALGORITHM = "HS256"



bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def authenticate_user(db, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    to_encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    

class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str 


# Read all users
@router.get("/read_all", status_code=status.HTTP_200_OK)
async def read_all_users(db: db_dependency):
    users = db.query(Users).all()
    return users


# Create User
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_users(db: db_dependency, user_request: UserRequest):
    user_model = Users(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password), 
        role=user_request.role,
        is_active=True,
        phone_number = user_request.phone_number
    )
    db.add(user_model)
    db.commit()
    return {"detail": "User created successfully"}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
    db.delete(user)
    db.commit()
    return {"detail": f"User with id {user_id} deleted"}

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return "Failed to authenticate"
    jwt_token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {"access_token": jwt_token, "token_type": "bearer"}
    