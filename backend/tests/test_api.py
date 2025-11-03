import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Category, GmailAccount
from app.auth import create_access_token

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    db = TestingSessionLocal()
    user = User(
        google_id="test123",
        email="test@example.com",
        name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create a Gmail account for the user
    gmail_account = GmailAccount(
        user_id=user.id,
        email="test@example.com",
        access_token="test_token",
        refresh_token="test_refresh",
        is_primary=True
    )
    db.add(gmail_account)
    db.commit()
    
    yield user
    db.close()

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(data={"user_id": test_user.id})
    return {"Authorization": f"Bearer {token}"}

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Email Sorter API" in response.json()["message"]

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_category(client, auth_headers):
    response = client.post(
        "/categories/",
        json={"name": "Test Category", "description": "A test category"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "A test category"
    assert "id" in data

def test_list_categories(client, auth_headers):
    # Create a category first
    client.post(
        "/categories/",
        json={"name": "Test Category", "description": "A test category"},
        headers=auth_headers
    )
    
    response = client.get("/categories/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Category"

def test_get_category(client, auth_headers):
    # Create a category
    create_response = client.post(
        "/categories/",
        json={"name": "Test Category", "description": "A test category"},
        headers=auth_headers
    )
    category_id = create_response.json()["id"]
    
    # Get the category
    response = client.get(f"/categories/{category_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"

def test_update_category(client, auth_headers):
    # Create a category
    create_response = client.post(
        "/categories/",
        json={"name": "Test Category", "description": "A test category"},
        headers=auth_headers
    )
    category_id = create_response.json()["id"]
    
    # Update the category
    response = client.put(
        f"/categories/{category_id}",
        json={"name": "Updated Category"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"

def test_delete_category(client, auth_headers):
    # Create a category
    create_response = client.post(
        "/categories/",
        json={"name": "Test Category", "description": "A test category"},
        headers=auth_headers
    )
    category_id = create_response.json()["id"]
    
    # Delete the category
    response = client.delete(f"/categories/{category_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(f"/categories/{category_id}", headers=auth_headers)
    assert response.status_code == 404

def test_unauthorized_access(client):
    response = client.get("/categories/")
    assert response.status_code == 403

def test_duplicate_category_name(client, auth_headers):
    # Create first category
    client.post(
        "/categories/",
        json={"name": "Test Category", "description": "First"},
        headers=auth_headers
    )
    
    # Try to create duplicate
    response = client.post(
        "/categories/",
        json={"name": "Test Category", "description": "Second"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_list_gmail_accounts(client, auth_headers):
    response = client.get("/accounts/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["email"] == "test@example.com"

