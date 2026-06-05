"""Shared pytest fixtures for the test suite."""

import os

import pytest
from pymongo import MongoClient

from app import create_app
from app.config import TestConfig


def _mongo_is_available() -> bool:
    """Quick check if MongoDB is reachable."""
    try:
        client = MongoClient(
            TestConfig.MONGO_URI,
            serverSelectionTimeoutMS=2000,
        )
        client.admin.command("ping")
        client.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def app():
    """Create a Flask application configured for testing.

    Skips the entire test suite if MongoDB is not available.
    """
    if not _mongo_is_available():
        pytest.skip(
            f"MongoDB is not available at {TestConfig.MONGO_URI}. "
            "Start MongoDB and re-run tests."
        )

    application = create_app(TestConfig)
    yield application

    # Teardown: drop the test database
    application.db.client.drop_database(application.db.name)


@pytest.fixture(scope="session")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def db(app):
    """Direct access to the test MongoDB database."""
    return app.db


@pytest.fixture(autouse=True)
def clean_movies(db):
    """Drop the movies collection before each test for isolation."""
    db["movies"].drop()
    yield
    db["movies"].drop()


@pytest.fixture()
def sample_csv(tmp_path):
    """Create a small CSV file for upload tests."""
    content = (
        "budget,homepage,original_language,original_title,overview,"
        "release_date,revenue,runtime,status,title,vote_average,"
        "vote_count,production_company_id,genre_id,languages\n"
        "30000000.0,,en,Toy Story,A toy story,1995-10-30,373554033.0,"
        "81,Released,Toy Story,7.7,5415.0,3,16,\"['English']\"\n"
        "65000000.0,,en,Jumanji,A board game,1995-12-15,262797249.0,"
        "104,Released,Jumanji,6.9,2413.0,559,12,\"['English', 'Français']\"\n"
        "0.0,,fr,La Haine,Hate,1995-05-31,0.0,98,Released,La Haine,"
        "7.9,695.0,802,18,\"['Français']\"\n"
        "1300000.0,,en,Taxi Driver,A taxi driver,1976-02-07,28262574.0,"
        "114,Released,Taxi Driver,8.1,2632.0,441,80,\"['English', 'Español']\"\n"
        "0.0,,de,Keiner liebt mich,,1994-11-07,0.0,104,Released,Nobody Loves Me,"
        "5.1,5.0,1,18,\"['Deutsch']\"\n"
    )
    csv_file = tmp_path / "test_movies.csv"
    csv_file.write_text(content, encoding="utf-8")
    return csv_file


@pytest.fixture()
def empty_csv(tmp_path):
    """Create a CSV file with only headers."""
    content = (
        "budget,homepage,original_language,original_title,overview,"
        "release_date,revenue,runtime,status,title,vote_average,"
        "vote_count,production_company_id,genre_id,languages\n"
    )
    csv_file = tmp_path / "empty_movies.csv"
    csv_file.write_text(content, encoding="utf-8")
    return csv_file


@pytest.fixture()
def non_csv_file(tmp_path):
    """Create a .txt file to test extension validation."""
    txt_file = tmp_path / "not_a_csv.txt"
    txt_file.write_text("hello world")
    return txt_file
