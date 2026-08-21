# backend/middleware/__init__.py
"""
Middleware modules for authentication and logging.
Used to protect routes and log requests/responses.
"""

from backend.middleware.auth_middleware import AuthMiddleware
from backend.middleware.log_middleware import LogMiddleware

__all__ = [
    'AuthMiddleware',
    'LogMiddleware'
]