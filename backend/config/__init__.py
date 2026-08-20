# backend/config/__init__.py
"""
Configuration module for the application.
Contains database connection and application settings.
"""

from backend.config.database import Database, db
from backend.config.settings import Settings

__all__ = ['Database', 'db', 'Settings']