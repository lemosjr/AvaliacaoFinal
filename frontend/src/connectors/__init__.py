# frontend/src/connectors/__init__.py
"""
Connectors module - Bridge between UI and backend controllers.
Each connector handles communication with a specific controller.
"""

from frontend.src.connectors.base_connector import BaseConnector
from frontend.src.connectors.auth_connector import AuthConnector
from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.connectors.order_connector import OrderConnector

__all__ = [
    'BaseConnector',
    'AuthConnector',
    'ProductConnector',
    'OrderConnector'
]