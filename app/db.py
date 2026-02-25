"""
MongoDB connection helper.
Reads MONGO_URI from environment (set in your .env file).
"""
import os
from pymongo import MongoClient
from flask import g, current_app


def get_db():
    """Return the database handle, reusing the connection within a request."""
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client[current_app.config['MONGO_DB_NAME']]
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    # MongoClient is thread-safe; individual handles don't need explicit close.


def init_app(app):
    app.teardown_appcontext(close_db)
    # Create indexes on first run
    with app.app_context():
        try:
            db = get_db()
            db['users'].create_index('email', unique=True)
            db['resumes'].create_index('user_id')
        except Exception as exc:
            app.logger.warning(f'DB index creation skipped: {exc}')
