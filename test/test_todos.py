from starlette import status

def test_read_all_athenticated(client, test_todo, test_user):
    print("===================>  test_read_all_athenticated")
    print(test_user.id)
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
    print(response.json())
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


def test_create_todo_athenticated(client, test_user):
    
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