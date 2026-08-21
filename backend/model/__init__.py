# backend/model/__init__.py
"""
Data models for the application.
Defines the structure of core entities: User, Product, Order, OrderItem.
"""

from backend.model.user_model import User
from backend.model.product_model import Product
from backend.model.order_model import Order, OrderStatus
from backend.model.order_item_model import OrderItem

__all__ = [
    'User',
    'Product',
    'Order',
    'OrderStatus',
    'OrderItem'
]