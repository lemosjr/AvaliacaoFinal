# backend/route/__init__.py
"""
Routes module for API endpoints.
Can be used with Flask, FastAPI, or other frameworks.
"""

from backend.route.auth_routes import auth_bp
from backend.route.product_routes import product_bp
from backend.route.order_routes import order_bp

__all__ = [
    'auth_bp',
    'product_bp',
    'order_bp'
]