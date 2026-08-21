# frontend/src/connectors/order_connector.py
"""
Order Connector - Ponte entre a interface e o OrderController.
"""

from backend.controller.order_controller import OrderController
from frontend.src.connectors.base_connector import BaseConnector
from frontend.src.utils.session_manager import session
from frontend.src.utils.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)


class OrderConnector(BaseConnector):
    """Conector para operações de pedidos."""

    def __init__(self):
        self.controller = OrderController()

    def _get_user_id(self) -> int:
        """Obtém o ID do usuário da sessão."""
        user = session.get_user()
        if not user:
            raise ValueError("User not authenticated")
        return user['id']

    def create_order(self, customer: str, items: list) -> dict:
        """
        Cria um novo pedido.

        Args:
            customer: Nome do cliente
            items: Lista de itens [{'product_id': int, 'quantity': int}, ...]

        Returns:
            Dict com 'success' e 'data' (pedido) ou 'error'
        """
        user_id = self._get_user_id()
        logger.info(f"Creating order for customer: {customer}")

        result = self._handle_error(
            self.controller.create_order,
            {'customer': customer, 'items': items},
            user_id
        )

        if result['success']:
            event_bus.emit('order_created', result['data'].get('order', result['data']))
            logger.info(f"Order created successfully")

        return result

    def get_order(self, order_id: int) -> dict:
        """
        Obtém um pedido por ID.

        Args:
            order_id: ID do pedido

        Returns:
            Dict com 'success' e 'data' (pedido) ou 'error'
        """
        logger.debug(f"Getting order: {order_id}")

        return self._handle_error(
            self.controller.get_order,
            order_id
        )

    def list_orders(self, status: str = None) -> dict:
        """
        Lista pedidos do usuário, opcionalmente filtrados por status.

        Args:
            status: Filtro por status (opcional)

        Returns:
            Dict com 'success' e 'data' (lista de pedidos) ou 'error'
        """
        user_id = self._get_user_id()
        logger.debug(f"Listing orders with status: {status or 'all'}")

        result = self._handle_error(
            self.controller.list_orders,
            user_id=user_id,
            status=status
        )

        if result['success']:
            event_bus.emit('orders_loaded', result['data'].get('orders', []))

        return result

    def add_item_to_order(self, order_id: int, product_id: int, quantity: int) -> dict:
        """
        Adiciona um item a um pedido existente.

        Args:
            order_id: ID do pedido
            product_id: ID do produto
            quantity: Quantidade

        Returns:
            Dict com 'success' e 'data' (pedido atualizado) ou 'error'
        """
        user_id = self._get_user_id()
        logger.info(f"Adding item to order {order_id}: product {product_id}, quantity {quantity}")

        result = self._handle_error(
            self.controller.add_item_to_order,
            order_id,
            {
                'product_id': product_id,
                'quantity': quantity
            },
            user_id
        )

        if result['success']:
            event_bus.emit('order_updated', result['data'].get('order', result['data']))
            logger.info(f"Item added to order {order_id}")

        return result

    def update_order_status(self, order_id: int, status: str) -> dict:
        """
        Atualiza o status de um pedido.

        Args:
            order_id: ID do pedido
            status: Novo status ('created', 'processing', 'completed', 'cancelled')

        Returns:
            Dict com 'success' e 'data' (pedido atualizado) ou 'error'
        """
        user_id = self._get_user_id()
        logger.info(f"Updating order {order_id} status to: {status}")

        result = self._handle_error(
            self.controller.update_order_status,
            order_id,
            {
                'status': status
            },
            user_id
        )

        if result['success']:
            event_bus.emit('order_status_changed', {
                'order_id': order_id,
                'new_status': status,
                'order': result['data'].get('order', result['data'])
            })
            logger.info(f"Order {order_id} status updated to {status}")

        return result

    def calculate_order_total(self, order_id: int) -> dict:
        """
        Calcula e retorna o total de um pedido.

        Args:
            order_id: ID do pedido

        Returns:
            Dict com 'success' e 'data' (total) ou 'error'
        """
        user_id = self._get_user_id()
        logger.debug(f"Calculating total for order: {order_id}")

        return self._handle_error(
            self.controller.calculate_order_total,
            order_id,
            user_id
        )

    def delete_order(self, order_id: int) -> dict:
        """
        Deleta/cancela um pedido.

        Args:
            order_id: ID do pedido

        Returns:
            Dict com 'success' e 'message' ou 'error'
        """
        user_id = self._get_user_id()
        logger.info(f"Deleting order: {order_id}")

        result = self._handle_error(
            self.controller.delete_order,
            order_id,
            user_id
        )

        if result['success']:
            event_bus.emit('order_deleted', order_id)
            logger.info(f"Order deleted: {order_id}")

        return result

    def get_order_statuses(self) -> list:
        """
        Retorna a lista de status válidos para pedidos.

        Returns:
            list: Lista de status válidos
        """
        from frontend.src.utils.constants import ORDER_STATUSES
        return list(ORDER_STATUSES.keys())