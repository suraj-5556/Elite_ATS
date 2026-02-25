"""
Database module: MongoDB connection via PyMongo.
Uses Flask app context so the same client is reused across requests.
"""

import logging
from flask import Flask, g
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)
_client: MongoClient = None


def init_db(app: Flask) -> None:
    """Initialize MongoDB client and attach teardown."""
    global _client
    try:
        _client = MongoClient(app.config['MONGODB_URI'], serverSelectionTimeoutMS=5000)
        # Verify connection
        _client.admin.command('ping')
        logger.info("MongoDB connected successfully.")
    except ConnectionFailure as e:
        logger.warning(f"MongoDB connection failed: {e}. Using fallback.")
        # Allow app to start even without DB (useful for local dev)
        _client = MongoClient(app.config['MONGODB_URI'], serverSelectionTimeoutMS=5000)

    @app.teardown_appcontext
    def close_db(exception):
        pass  # PyMongo manages its own connection pool


def get_db():
    """Return the database instance. Callable from anywhere in the app."""
    if _client is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    # Extract DB name from URI or default to 'talentai'
    db_name = _client.get_default_database().name if '/' in str(_client) else 'talentai'
    try:
        return _client.get_default_database()
    except Exception:
        return _client['talentai']
