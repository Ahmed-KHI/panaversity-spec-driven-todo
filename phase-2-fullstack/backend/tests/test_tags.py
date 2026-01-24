"""
Unit tests for Phase V tag endpoints.
[Task]: T-B-011 (Tag API Tests)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.2,
        specs/005-phase-v-cloud/phase5-cloud.tasks.md §B.11
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from src.main import app
from src.database import get_session
from src.models import User, Tag
from src.utils.auth import create_access_token


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with dependency override."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash="$2b$12$test_hash",
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Create authentication headers."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


# ===== Tag Creation Tests =====

def test_create_tag(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating a tag."""
    response = client.post(
        f"/api/{test_user.id}/tags",
        json={
            "name": "Work",
            "color": "#3B82F6"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Work"
    assert data["color"] == "#3B82F6"
    assert "id" in data
    assert "created_at" in data


def test_create_tag_with_default_color(client: TestClient, test_user: User, auth_headers: dict):
    """Test creating tag without specifying color (should use default)."""
    response = client.post(
        f"/api/{test_user.id}/tags",
        json={"name": "Personal"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Personal"
    assert data["color"] == "#3B82F6"  # Default blue


def test_create_tag_duplicate_name_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that duplicate tag names are rejected."""
    # Create first tag
    client.post(
        f"/api/{test_user.id}/tags",
        json={"name": "Work"},
        headers=auth_headers
    )
    
    # Try to create duplicate
    response = client.post(
        f"/api/{test_user.id}/tags",
        json={"name": "Work"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_tag_invalid_color_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that invalid hex color is rejected."""
    response = client.post(
        f"/api/{test_user.id}/tags",
        json={
            "name": "InvalidColor",
            "color": "not-a-hex-color"
        },
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


# ===== Tag Listing Tests =====

def test_list_tags_empty(client: TestClient, test_user: User, auth_headers: dict):
    """Test listing tags when none exist."""
    response = client.get(
        f"/api/{test_user.id}/tags",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["tags"] == []


def test_list_tags(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test listing all user's tags."""
    # Create test tags
    tags = [
        Tag(name="Work", color="#3B82F6", created_by=test_user.id),
        Tag(name="Personal", color="#10B981", created_by=test_user.id),
        Tag(name="Urgent", color="#EF4444", created_by=test_user.id),
    ]
    session.add_all(tags)
    session.commit()
    
    response = client.get(
        f"/api/{test_user.id}/tags",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    tag_names = [t["name"] for t in data["tags"]]
    assert "Work" in tag_names
    assert "Personal" in tag_names
    assert "Urgent" in tag_names


# ===== Get Single Tag Tests =====

def test_get_tag_by_id(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test getting a specific tag by ID."""
    tag = Tag(name="TestTag", color="#FF0000", created_by=test_user.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    response = client.get(
        f"/api/{test_user.id}/tags/{tag.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tag.id
    assert data["name"] == "TestTag"
    assert data["color"] == "#FF0000"


def test_get_nonexistent_tag_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that getting non-existent tag returns 404."""
    response = client.get(
        f"/api/{test_user.id}/tags/99999",
        headers=auth_headers
    )
    assert response.status_code == 404


# ===== Tag Update Tests =====

def test_update_tag_name(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test updating tag name."""
    tag = Tag(name="OldName", color="#3B82F6", created_by=test_user.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    response = client.put(
        f"/api/{test_user.id}/tags/{tag.id}",
        json={"name": "NewName"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NewName"
    assert data["color"] == "#3B82F6"  # Color unchanged


def test_update_tag_color(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test updating tag color."""
    tag = Tag(name="ColorTag", color="#3B82F6", created_by=test_user.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    response = client.put(
        f"/api/{test_user.id}/tags/{tag.id}",
        json={"color": "#FF0000"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["color"] == "#FF0000"
    assert data["name"] == "ColorTag"  # Name unchanged


def test_update_tag_duplicate_name_fails(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test that updating to duplicate name fails."""
    tag1 = Tag(name="Tag1", color="#3B82F6", created_by=test_user.id)
    tag2 = Tag(name="Tag2", color="#10B981", created_by=test_user.id)
    session.add_all([tag1, tag2])
    session.commit()
    session.refresh(tag2)
    
    response = client.put(
        f"/api/{test_user.id}/tags/{tag2.id}",
        json={"name": "Tag1"},  # Trying to rename to existing name
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# ===== Tag Deletion Tests =====

def test_delete_tag(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """Test deleting a tag."""
    tag = Tag(name="ToDelete", color="#3B82F6", created_by=test_user.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    response = client.delete(
        f"/api/{test_user.id}/tags/{tag.id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify tag is deleted
    get_response = client.get(
        f"/api/{test_user.id}/tags/{tag.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_tag_fails(client: TestClient, test_user: User, auth_headers: dict):
    """Test that deleting non-existent tag returns 404."""
    response = client.delete(
        f"/api/{test_user.id}/tags/99999",
        headers=auth_headers
    )
    assert response.status_code == 404


# ===== Authorization Tests =====

def test_tag_requires_authentication(client: TestClient):
    """Test that tag endpoints require authentication."""
    fake_user_id = str(uuid4())
    
    # Try to list tags without auth
    response = client.get(f"/api/{fake_user_id}/tags")
    assert response.status_code == 401


def test_cannot_access_other_user_tags(client: TestClient, session: Session):
    """Test that users cannot access other users' tags."""
    # Create two users
    user1 = User(id=uuid4(), email="user1@example.com", password_hash="hash1", full_name="User 1")
    user2 = User(id=uuid4(), email="user2@example.com", password_hash="hash2", full_name="User 2")
    session.add_all([user1, user2])
    session.commit()
    
    # User1 creates a tag
    tag = Tag(name="User1Tag", color="#3B82F6", created_by=user1.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    # User2 tries to access User1's tag
    user2_token = create_access_token({"sub": str(user2.id)})
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    response = client.get(
        f"/api/{user1.id}/tags/{tag.id}",
        headers=user2_headers
    )
    assert response.status_code == 404  # Should appear as not found for security
