import pytest
from fastapi.testclient import TestClient

@pytest.mark.parametrize(
    "full_name, password, email, is_active, is_superuser",
    [("test_user", "password", "email@example.com", True, False)]
)
def test_create_user(client: TestClient, full_name, password, email, is_active, is_superuser):
    response = client.post(
        "/api/users/create",
        json={
            "full_name": full_name,
            "password": password,
            "email": email,
            "is_active": is_active,
            "is_superuser": is_superuser,
        }
    )
    
    data = response.json()
    
    assert response.status_code == 200  # Updated to match the endpoint's status code
    assert data["full_name"] == full_name
    assert data["email"] == email
    assert data["is_active"] == is_active
    assert data["is_superuser"] == is_superuser
    assert "user_id" in data  # Ensure user_id is present
 
                           
