# frontend/src/widgets/__init__.py
"""
Widgets - Componentes reutilizáveis da interface.
"""

from frontend.src.widgets.product_widget import ProductWidget
from frontend.src.widgets.order_widget import OrderWidget
from frontend.src.widgets.table_widget import TableWidget
from frontend.src.widgets.status_badge import StatusBadge
from frontend.src.widgets.search_bar import SearchBar

__all__ = [
    'ProductWidget',
    'OrderWidget',
    'TableWidget',
    'StatusBadge',
    'SearchBar'
]