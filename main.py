from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session
import models
from models import Todo
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from starlette import status
from pydantic import BaseModel, Field



app = FastAPI()

models.Base.metadata.create_all(bind=engine)
# create everyhing from database.py file and models.py file to be able to 
# create a new database that has a new table called todos with all the columns
# that we have specified in the models.py file

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=6)
    completed: bool



@app.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(db: db_dependency):
    todos = db.query(Todo).all()
    return todos

# Fetch Single Todo
@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_single_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')

# Create Todo 
@app.post("/create-todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo = Todo(**todo_request.model_dump())
    db.add(todo)
    db.commit()
    return {"detail": f"Todo created successfully"}


# Update Todo
@app.put("/update-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.completed = todo_request.completed

    db.add(todo)
    db.commit()
    return {"detail": f"Todo with id {todo_id} updated"}

# Delete Todo
@app.delete("/delete-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')
    db.delete(todo)
    db.commit()
    return {"detail": f"Todo deleted successfully"}