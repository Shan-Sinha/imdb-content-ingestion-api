"""Unit tests for the refactored Object-Oriented Programming (OOP) classes."""

from datetime import datetime, timezone
import pytest
from app.models.movie import Movie
from app.utils.auth import TokenAuthenticator
from app.services.movie_service import MovieService


def test_movie_class_instantiation():
    """Verify that the Movie model class instantiates and serialize fields correctly."""
    movie_doc = {
        "_id": "65bfa78a2e1d7a8d54231b23",
        "title": "Toy Story",
        "budget": "30000000.0",
        "homepage": "http://toystory.com",
        "release_date": datetime(1995, 10, 30, tzinfo=timezone.utc),
        "languages": ["English"],
    }
    
    movie = Movie.from_mongo(movie_doc)
    assert movie.title == "Toy Story"
    assert movie.budget == 30000000.0
    assert movie.id == "65bfa78a2e1d7a8d54231b23"
    
    serialized = movie.to_dict()
    assert serialized["id"] == "65bfa78a2e1d7a8d54231b23"
    assert serialized["budget"] == 30000000.0
    assert serialized["release_date"] == "1995-10-30T00:00:00+00:00"


def test_token_authenticator_lifecycle():
    """Verify TokenAuthenticator signs, verifies, and rejects tokens correctly."""
    authenticator = TokenAuthenticator(
        secret_key="secret_sig_123",
        static_key="static_key_123"
    )
    
    # Generate token
    token = authenticator.generate_token("admin_user")
    assert token is not None
    assert isinstance(token, str)
    
    # Verify token
    username = authenticator.verify_token(token)
    assert username == "admin_user"
    
    # Fallback static key verification
    static_username = authenticator.verify_token("static_key_123")
    assert static_username == "api_client"
    
    # Rejection of invalid token
    assert authenticator.verify_token("invalid_token_xyz") is None


def test_movie_service_querying(db, client, sample_csv):
    """Verify that MovieService queries correctly."""
    # Seed the DB
    from app.services.csv_service import CSVService
    csv_service = CSVService(db["movies"])
    csv_service.process(sample_csv)
    
    # Query via MovieService
    service = MovieService(db["movies"])
    result = service.get_movies(
        page=1,
        per_page=2,
        sort_field="vote_average",
        sort_direction=-1,
        original_title="Toy"
    )
    
    assert len(result["movies"]) == 1
    assert result["movies"][0]["title"] == "Toy Story"
    assert result["pagination"]["total_records"] == 1
