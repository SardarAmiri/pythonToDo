from fastapi import status
from ..models import Todo




def test_read_all_todos_authenticated(client, test_todo, test_user):
   
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == test_todo.title
    assert response.json()[0]["description"] == test_todo.description
    assert response.json()[0]["priority"] == test_todo.priority
    assert response.json()[0]["complete"] == test_todo.complete
    assert response.json()[0]["owner_id"] == test_user.id
    assert response.json()[0]["id"] == test_todo.id


    
def test_admin_todo_authenticated(client, test_todo, db):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model is None

def test_admin_todo_not_found(client):
    response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}
    
    
   