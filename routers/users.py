from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from ..models import Users
from sqlalchemy.orm import Session
from ..database import SessionLocal
from fastapi import status
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from ..routers.todos import get_current_user, get_db



router = APIRouter(
    tags=["users"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

class UserPhoneNumber(BaseModel):
    phone_number : str 
    new_phone_number: str

@router.get("/users", status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    users = db.query(Users).filter(Users.id == user.get('id')).first()
    return users

@router.put("/update_password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return {"message": "Password changed successfully"}

@router.put("/phone_number/{phone_number}", status_code=status.HTTP_200_OK)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
    return {"message": "Phone number changed successfully"}