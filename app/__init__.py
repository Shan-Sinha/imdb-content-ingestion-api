import logging
import os

from flask import Flask
from pymongo import MongoClient

from app.config import Config

logger = logging.getLogger(__name__)

# Module-level MongoDB references — initialised in create_app()
mongo_client: MongoClient = None
db = None


def create_app(config_class=Config):
    """Flask application factory.

    Creates and configures the Flask app, connects to MongoDB,
    ensures required indexes exist, and registers API blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the temp upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ---- MongoDB connection ----
    global mongo_client, db
    mongo_client = MongoClient(
        app.config["MONGO_URI"],
        serverSelectionTimeoutMS=5000,  # fail fast during startup
    )
    db = mongo_client[app.config["DATABASE_NAME"]]

    # Store db reference on app for easy access in routes/services
    app.db = db

    # ---- Authenticator Setup (OOP dependency injection) ----
    from app.utils.auth import TokenAuthenticator
    app.authenticator = TokenAuthenticator(
        secret_key=app.config.get("SECRET_KEY", "imdb_super_secret_key_98765"),
        static_key=app.config.get("API_KEY", "default_secret_key_123")
    )

    # ---- Create indexes (idempotent, best-effort on startup) ----
    try:
        _ensure_indexes(db)
    except Exception as exc:
        logger.warning(
            "Could not create indexes on startup (MongoDB may not be available): %s",
            exc,
        )

    # ---- Register blueprints ----
    from app.routes.upload import upload_bp
    from app.routes.movies import movies_bp
    from app.routes.docs import docs_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(upload_bp, url_prefix="/api/v1")
    app.register_blueprint(movies_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(docs_bp)

    return app



def _ensure_indexes(database):
    """Create MongoDB indexes for efficient querying.

    Called on every startup; MongoDB ignores duplicate index creation.
    """
    movies = database["movies"]

    # Single-field indexes
    movies.create_index("year")
    movies.create_index("languages")
    movies.create_index("release_date")
    movies.create_index("vote_average")

    # Compound indexes for combined filter + sort
    movies.create_index([("year", 1), ("release_date", 1)])
    movies.create_index([("year", 1), ("vote_average", 1)])
    movies.create_index([("languages", 1), ("release_date", 1)])
    movies.create_index([("languages", 1), ("vote_average", 1)])
