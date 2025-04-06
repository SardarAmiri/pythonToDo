from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from models import Todo
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user



router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="User not authenticated")
    todos = db.query(Todo).all()
    return todos

@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="User not authenticated")
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        db.delete(todo)
        db.commit()
        return {"detail": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')