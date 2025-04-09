from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user
from starlette import status
from fastapi.testclient import TestClient
import pytest
from ..models import Todo, Users

SQLALCHEMY_DATABASE_URL = "postgresql://amiri:amiri1122@localhost/TestTodoApplicationDatabase"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "amiri1122test", "id": 1, "role": "admin"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture

def test_todo():
    db = TestSessionLocal()
    
    test_user = Users(
        id=1, 
        username="testamiri1122",
        role="admin",
    )
    db.add(test_user)
    db.commit()

    todo = Todo(
        title="Learn fastAPI", 
        description="fastAPI is awesome", 
        priority=5, 
        complete=False, 
        owner_id=1,
        )
    
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


def test_read_all_athenticated(test_todo):
    response = client.get("/todos/")
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == test_todo.title
    assert response.json()[0]["description"] == test_todo.description
    assert response.json()[0]["priority"] == test_todo.priority
    assert response.json()[0]["complete"] == test_todo.complete
    assert response.json()[0]["owner_id"] == test_todo.owner_id
    assert response.json()[0]["id"] == test_todo.id


    