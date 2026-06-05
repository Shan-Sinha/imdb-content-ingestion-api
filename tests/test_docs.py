"""Tests for the Swagger API documentation routes."""

import json


def test_root_redirect(client):
    """Verify that visiting root redirects to the /docs endpoint."""
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/docs"


def test_docs_page(client):
    """Verify that the Swagger UI docs page is served correctly."""
    response = client.get("/docs")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "swagger-ui" in html
    assert "swagger-ui-bundle.js" in html


def test_swagger_json(client):
    """Verify that the swagger.json endpoint returns valid OpenAPI 3 spec."""
    response = client.get("/api/v1/swagger.json")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    
    data = json.loads(response.data.decode("utf-8"))
    assert data["openapi"] == "3.0.0"
    assert "paths" in data
    assert "/api/v1/upload" in data["paths"]
    assert "/api/v1/movies" in data["paths"]
