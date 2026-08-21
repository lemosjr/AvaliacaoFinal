# backend/repository/__init__.py
"""
Repository layer for database operations.
Provides CRUD and query methods for each entity.
"""

from backend.repository.base_repository import BaseRepository
from backend.repository.user_repository import UserRepository
from backend.repository.product_repository import ProductRepository
from backend.repository.order_repository import OrderRepository
from backend.repository.order_item_repository import OrderItemRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'ProductRepository',
    'OrderRepository',
    'OrderItemRepository'
]