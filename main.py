from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from models import Todo
from sqlalchemy.orm import Session
from database import engine, SessionLocal


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
# 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
def read_all_todos(db: db_dependency):
    todos = db.query(Todo).all()
    return todos

# Fetch Single Todo
@app.get("/todo/{todo_id}")
def read_single_todo(todo_id: int, db: db_dependency):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")