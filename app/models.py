"""
User model: Wraps MongoDB document in a Flask-Login compatible class.
Flask-Login requires is_authenticated, is_active, is_anonymous, get_id.
"""

from __future__ import annotations
import logging
from bson import ObjectId
from flask_login import UserMixin
from .database import get_db

logger = logging.getLogger(__name__)


class User(UserMixin):
    """
    Lightweight user object that maps MongoDB fields to Flask-Login interface.
    We intentionally avoid heavy ORM abstractions to keep the code simple
    and MongoDB-idiomatic.
    """

    def __init__(self, user_doc: dict):
        self._id = str(user_doc['_id'])
        self.name = user_doc['name']
        self.email = user_doc['email']
        self.password_hash = user_doc.get('password_hash', '')
        self.created_at = user_doc.get('created_at')

    def get_id(self) -> str:
        return self._id

    @property
    def id(self) -> str:
        return self._id

    def to_dict(self) -> dict:
        return {
            'id': self._id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at,
        }

    @staticmethod
    def find_by_email(email: str) -> User | None:
        try:
            db = get_db()
            doc = db.users.find_one({'email': email.lower().strip()})
            return User(doc) if doc else None
        except Exception as e:
            logger.error(f"find_by_email error: {e}")
            return None

    @staticmethod
    def find_by_id(user_id: str) -> User | None:
        try:
            db = get_db()
            doc = db.users.find_one({'_id': ObjectId(user_id)})
            return User(doc) if doc else None
        except Exception as e:
            logger.error(f"find_by_id error: {e}")
            return None

    @staticmethod
    def create(name: str, email: str, password_hash: str) -> User | None:
        from datetime import datetime, timezone
        try:
            db = get_db()
            result = db.users.insert_one({
                'name': name.strip(),
                'email': email.lower().strip(),
                'password_hash': password_hash,
                'created_at': datetime.now(timezone.utc),
            })
            return User.find_by_id(str(result.inserted_id))
        except Exception as e:
            logger.error(f"User.create error: {e}")
            return None


class UserLoader:
    """Separates the Flask-Login loading concern from the User model."""

    @staticmethod
    def load(user_id: str) -> User | None:
        return User.find_by_id(user_id)
