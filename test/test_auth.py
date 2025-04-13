from fastapi import status
from ..routers.auth import authenticate_user 


def test_authenticate_user(db, test_user):
    authenticated_user = authenticate_user(db, test_user.username, "testpass")
    assert authenticated_user is not False
    assert authenticated_user.username == "testuser123"

    none_existing_user = authenticate_user(db, "wronguser", "testpass")
    assert none_existing_user is False

    wrong_password_user = authenticate_user(db, test_user.username, "wrongpass")
    assert wrong_password_user is False
    
    