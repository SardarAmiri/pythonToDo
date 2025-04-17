from fastapi import status
from ..routers.auth import authenticate_user, create_access_token, get_current_user, SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import timedelta
from fastapi import HTTPException


def test_authenticate_user(db, test_user):
    authenticated_user = authenticate_user(db, test_user.username, "testpass")
    assert authenticated_user is not False
    assert authenticated_user.username == "testuser123"

    none_existing_user = authenticate_user(db, "wronguser", "testpass")
    assert none_existing_user is False

    wrong_password_user = authenticate_user(db, test_user.username, "wrongpass")
    assert wrong_password_user is False

    
def test_create_access_token():
    username  = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)
    token = create_access_token(username, user_id, role, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role
    assert "exp" in decoded_token

def test_get_current_user():
    token = jwt.encode({"sub": "testuser", "id": 1, "role": "user"}, SECRET_KEY, algorithm=ALGORITHM)
    user = get_current_user(token)
    assert user["username"] == "testuser"
    assert user["id"] == 1
    assert user["role"] == "user"
    
def test_get_current_user_invalid_token():
    token = jwt.encode({"sub": "testuser"}, SECRET_KEY, algorithm=ALGORITHM)
    try:
        user = get_current_user(token)
    except HTTPException as e:
        assert e.status_code == status.HTTP_401_UNAUTHORIZED
        assert e.detail == "Could not validate credentials"
    
    


    