# frontend/src/dialogs/__init__.py
"""
Dialog windows for the application.
"""

from frontend.src.dialogs.add_product_dialog import AddProductDialog
from frontend.src.dialogs.create_order_dialog import CreateOrderDialog
from frontend.src.dialogs.add_item_dialog import AddItemDialog
from frontend.src.dialogs.confirmation_dialog import ConfirmationDialog
from frontend.src.dialogs.message_dialog import MessageDialog

__all__ = [
    'AddProductDialog',
    'CreateOrderDialog',
    'AddItemDialog',
    'ConfirmationDialog',
    'MessageDialog'
]