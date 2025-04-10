from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from ..models import Todo
from sqlalchemy.orm import Session
from ..database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user




router = APIRouter(
    tags=["todos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=6)
    complete: bool



@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    todos = db.query(Todo).filter(Todo.owner_id == user.get("id")).all()
    return todos

# Fetch Single Todo
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_single_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')

# Create Todo 
@router.post("/create-todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    todo = Todo(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo)
    db.commit()
    return {"detail": f"Todo created successfully"}


# Update Todo
@router.put("/update-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.add(todo)
    db.commit()
    return {"detail": f"Todo with id {todo_id} updated"}

# Delete Todo
@router.delete("/delete-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')
    db.delete(todo)
    db.commit()
    return {"detail": f"Todo deleted successfully"}