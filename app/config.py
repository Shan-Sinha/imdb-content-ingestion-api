import os
import tempfile

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "imdb")
    API_KEY = os.getenv("API_KEY", "default_secret_key_123")
    SECRET_KEY = os.getenv("SECRET_KEY", "imdb_super_secret_key_98765")
    AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "password123")

    # 1.5 GB — enough headroom for a 1 GB CSV plus multipart overhead
    MAX_CONTENT_LENGTH = int(1.5 * 1024 * 1024 * 1024)

    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "imdb_uploads")

    # CSV processing
    CSV_CHUNK_SIZE = 5000  # rows per batch for chunked insert


class TestConfig(Config):
    """Overrides for the test suite — uses a separate database."""

    TESTING = True
    DATABASE_NAME = "imdb_test"
    API_KEY = "test_secret_key"
    SECRET_KEY = "test_secret_key"
    AUTH_USERNAME = "test_admin"
    AUTH_PASSWORD = "test_password"
