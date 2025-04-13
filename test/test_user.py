from fastapi import status



def test_read_all_users_authenticated(client, test_user):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user.username
    assert response.json()["email"] == test_user.email
    assert response.json()["first_name"] == test_user.first_name
    assert response.json()["last_name"] == test_user.last_name
    assert response.json()["id"] == test_user.id
    assert response.json()["phone_number"] == test_user.phone_number
    assert response.json()["role"] == test_user.role
    assert response.json()["is_active"] == test_user.is_active

def test_change_password_authenticated(client, test_user):
    response = client.put(
        "/update_password",
        json={
            "password": "testpass",
            "new_password": "newtestpass"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password changed successfully"}

def test_change_invalid_password_authenticated(client, test_user):
    response = client.put(
        "/update_password",
        json={
            "password": "wrongpass",
            "new_password": "newtestpass"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change"}

def test_change_phone_number_authenticated(client, test_user):
    response = client.put(
        "/phone_number/09123456789",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Phone number changed successfully"}