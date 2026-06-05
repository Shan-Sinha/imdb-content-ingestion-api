"""Integration tests for user registration, token-based authentication, and endpoint access."""

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


# ================== User Registration Tests ==================

def test_register_user_success(client):
    """Verify that registering a new user succeeds and hashes the password."""
    response = client.post(
        "/api/v1/users",
        json={"username": "new_user_123", "password": "secure_password"}
    )
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["username"] == "new_user_123"
    assert "id" in json_data["data"]


def test_register_user_duplicate_username(client):
    """Verify that registering an existing username returns a 400 error."""
    # First registration
    client.post(
        "/api/v1/users",
        json={"username": "duplicate_user", "password": "password1"}
    )
    # Duplicate registration
    response = client.post(
        "/api/v1/users",
        json={"username": "duplicate_user", "password": "password1"}
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "already exists" in json_data["message"]


def test_register_user_missing_params(client):
    """Verify that missing username or password yields a 400 error."""
    response = client.post(
        "/api/v1/users",
        json={"username": "only_username"}
    )
    assert response.status_code == 400


# ================== Token Generation Tests ==================

def test_generate_token_success(client):
    """Verify that a registered user can log in and generate a valid Bearer token."""
    # 1. Register user
    reg_response = client.post(
        "/api/v1/users",
        json={"username": "valid_user", "password": "valid_password"}
    )
    assert reg_response.status_code == 201

    # 2. Get token
    token_response = client.post(
        "/api/v1/auth/token",
        json={"username": "valid_user", "password": "valid_password"}
    )
    assert token_response.status_code == 200
    json_data = token_response.get_json()
    assert json_data["success"] is True
    assert "token" in json_data["data"]
    assert json_data["data"]["token_type"] == "Bearer"

    # 3. Test using the newly generated token on the movies endpoint
    generated_token = json_data["data"]["token"]
    movies_response = client.get(
        "/api/v1/movies",
        headers={"Authorization": f"Bearer {generated_token}"}
    )
    assert movies_response.status_code == 200
    movies_json = movies_response.get_json()
    assert movies_json["success"] is True


def test_generate_token_invalid_password(client):
    """Verify that logging in with incorrect password yields a 401 error."""
    # 1. Register user
    client.post(
        "/api/v1/users",
        json={"username": "some_user", "password": "good_password"}
    )

    # 2. Login with bad password
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "some_user", "password": "wrong_password"}
    )
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Invalid username" in json_data["message"]


def test_generate_token_missing_params(client):
    """Verify that missing credentials on token request yields a 400 error."""
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "some_user"}
    )
    assert response.status_code == 400
