from starlette import status
from ..models import Todo

def test_read_all_athenticated(client, test_todo, test_user):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "title": "Test Todo",
            "description": "Test Description",
            "priority": 3,
            "complete": False,
            "owner_id": test_user.id
        }
    ]

def test_read_single_todo_athenticated(client, test_todo, test_user):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() ==  {
            "id": 1,
            "title": "Test Todo",
            "description": "Test Description",
            "priority": 3,
            "complete": False,
            "owner_id": test_user.id
        }

def test_read_single_todo_not_found(client):
    response = client.get("/todo/100")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 100 not found"}


def test_create_todo_athenticated(client, test_user, db):
    
    request_data = {
        "title": "New Todo",
        "description": "This is a new todo",
        "priority": 5,
        "complete": False,
        "owner_id": test_user.id
    }
    response = client.post("/create-todo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail": "Todo created successfully"}

    todo = db.query(Todo).filter(Todo.id == 1).first()
    assert todo.title == request_data.get("title")
    assert todo.description == request_data.get("description")
    assert todo.priority == request_data.get("priority")
    assert todo.complete == request_data.get("complete")
    assert todo.owner_id == test_user.id


def test_update_todo_athenticated(client, test_todo, test_user):
    request_data = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 2,
        "complete": True,
    }
    response = client.put("/update-todo/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    updated_todo = client.get("/todo/1")
    assert updated_todo.status_code == status.HTTP_200_OK
    assert updated_todo.json() == {
        "id": 1,
        "title": request_data.get("title"),
        "description": request_data.get("description"),
        "priority": request_data.get("priority"),
        "complete": request_data.get("complete"),
        "owner_id": test_user.id
    }
    
def test_update_todo_not_found(client):
    request_data = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 2,
        "complete": True,
    }
    response = client.put("/update-todo/100", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 100 not found"}

def test_update_todo_with_invalid_data(client, test_todo):
    request_data = {
        "title": "",
        "description": "This is an updated todo",
        "priority": 2,
        "complete": True,
    }
    response = client.put("/update-todo/1", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    for error in response.json()["detail"]:
        assert error["msg"] == "String should have at least 3 characters"
    

def test_delete_todo_athenticated(client, test_todo, test_user):
    response = client.delete("/delete-todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted_todo = client.get("/todo/1")
    assert deleted_todo.status_code == status.HTTP_404_NOT_FOUND
    assert deleted_todo.json() == {"detail": "Todo with id 1 not found"}

def test_delete_todo_not_found(client):
    response = client.delete("/delete-todo/100")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 100 not found"}

def test_delete_todo_unauthenticated(client):
    response = client.delete("/delete-todo/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "User not authenticated"}