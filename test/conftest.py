import pytest
from ..models import Todo, Users
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from passlib.context import CryptContext
from fastapi.testclient import TestClient
from ..main import app
from ..routers.todos import get_current_user, get_db
#




TEST_SQLALCHEMY_DATABASE_URL = "postgresql://amiri:amiri1122@localhost/TestTodoApplicationDatabase"
test_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture
def client(db):
    
   
    
    # Override dependencies
    def override_get_db():
        yield db
        
    def override_get_current_user():
        return {"username": "testuser", "id": 1, "role": "admin"}
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture()
def db():
    
    Base.metadata.create_all(bind=test_engine)
    connection = test_engine.connect()
    transaction = connection.begin()
    db = TestSessionLocal(bind=connection)
    yield db
    db.close()
    transaction.rollback()
    connection.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def test_user(db):
    user = Users(
        username="testuser123",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("testpass"),
        is_active=True,
        phone_number="09123456789",
        role="user",
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def test_todo(db, test_user):
    todo = Todo(
        title="Test Todo",
        description="Test Description",
        priority=3,
        complete=False,
        owner_id=test_user.id,
    )
    db.add(todo)
    db.commit()
    return todo