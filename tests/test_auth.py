"""Integration tests for token-based authentication and endpoint access."""

import io
import json


def test_upload_endpoint_unauthorized(client):
    """Verify that upload endpoint returns 401 without auth headers."""
    response = client.post(
        "/api/v1/upload",
        data={"file": (io.BytesIO(b""), "test.csv")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "token" in json_data["message"]


def test_upload_endpoint_invalid_key(client):
    """Verify that upload endpoint returns 401 with a bad API key."""
    response = client.post(
        "/api/v1/upload",
        data={"file": (io.BytesIO(b""), "test.csv")},
        content_type="multipart/form-data",
        headers={"X-API-Key": "wrong_key_123"}
    )
    assert response.status_code == 401


def test_movies_endpoint_unauthorized(client):
    """Verify that movies endpoint returns 401 without auth headers."""
    response = client.get("/api/v1/movies")
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["success"] is False


def test_movies_endpoint_invalid_key(client):
    """Verify that movies endpoint returns 401 with a bad API key."""
    response = client.get(
        "/api/v1/movies",
        headers={"Authorization": "Bearer wrong_bearer_token"}
    )
    assert response.status_code == 401


def test_auth_success_with_bearer_token(client):
    """Verify authentication succeeds with static Bearer token header."""
    response = client.get(
        "/api/v1/movies",
        headers={"Authorization": "Bearer test_secret_key"}
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True


def test_auth_success_with_x_api_key(client):
    """Verify authentication succeeds with static X-API-Key header."""
    response = client.get(
        "/api/v1/movies",
        headers={"X-API-Key": "test_secret_key"}
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True


# ================== Token Generation Tests ==================

def test_generate_token_success(client):
    """Verify that valid credentials generate a valid signed bearer token."""
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "test_admin", "password": "test_password"}
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "token" in json_data["data"]
    assert json_data["data"]["token_type"] == "Bearer"
    assert json_data["data"]["expires_in"] == 3600

    # Test using the newly generated token on the movies endpoint
    generated_token = json_data["data"]["token"]
    movies_response = client.get(
        "/api/v1/movies",
        headers={"Authorization": f"Bearer {generated_token}"}
    )
    assert movies_response.status_code == 200
    movies_json = movies_response.get_json()
    assert movies_json["success"] is True


def test_generate_token_invalid_credentials(client):
    """Verify that invalid credentials yield a 401 error."""
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "test_admin", "password": "wrong_password"}
    )
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Invalid username" in json_data["message"]


def test_generate_token_missing_params(client):
    """Verify that missing username or password yields a 400 error."""
    # Missing password
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "test_admin"}
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Missing" in json_data["message"]
