# backend/controller/__init__.py
"""
Controllers module.
Orchestrates requests, validation, and service calls.
"""

from backend.controller.auth_controller import AuthController
from backend.controller.product_controller import ProductController
from backend.controller.order_controller import OrderController

__all__ = [
    'AuthController',
    'ProductController',
    'OrderController'
]