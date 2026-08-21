# backend/migrations/__init__.py
"""
Database migration management module.
Handles version control for database schema changes.
"""

from backend.migrations.manager import MigrationManager

__all__ = ['MigrationManager']