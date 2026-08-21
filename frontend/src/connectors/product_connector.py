# frontend/src/connectors/product_connector.py
"""
Product Connector - Ponte entre a interface e o ProductController.
"""

from backend.controller.product_controller import ProductController
from frontend.src.connectors.base_connector import BaseConnector
from frontend.src.utils.session_manager import session
from frontend.src.utils.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)


class ProductConnector(BaseConnector):
    """Conector para operações de produtos."""

    def __init__(self):
        self.controller = ProductController()

    def _get_user_id(self) -> int:
        """Obtém o ID do usuário da sessão."""
        user = session.get_user()
        if not user:
            raise ValueError("User not authenticated")
        return user['id']

    def create_product(self, description: str, price: float, quantity_available: int) -> dict:
        """
        Cria um novo produto.

        Args:
            description: Descrição do produto
            price: Preço do produto
            quantity_available: Quantidade disponível

        Returns:
            Dict com 'success' e 'data' (produto) ou 'error'
        """
        user_id = self._get_user_id()
        logger.info(f"Creating product: {description}")

        result = self._handle_error(
            self.controller.create_product,
            {
                'description': description,
                'price': price,
                'quantity_available': quantity_available
            },
            user_id
        )

        if result['success']:
            event_bus.emit('product_created', result['data']['product'])
            logger.info(f"Product created: {description}")

        return result

    def get_product(self, product_id: int) -> dict:
        """
        Obtém um produto por ID.

        Args:
            product_id: ID do produto

        Returns:
            Dict com 'success' e 'data' (produto) ou 'error'
        """
        logger.debug(f"Getting product: {product_id}")

        return self._handle_error(
            self.controller.get_product,
            product_id
        )

    def list_products(self) -> dict:
        """
        Lista todos os produtos do usuário.

        Returns:
            Dict com 'success' e 'data' (lista de produtos) ou 'error'
        """
        user_id = self._get_user_id()
        logger.debug("Listing products")

        result = self._handle_error(
            self.controller.list_products,
            user_id
        )

        if result['success']:
            # Atualiza a lista no cache do evento
            event_bus.emit('products_loaded', result['data']['products'])

        return result

    def update_product(self, product_id: int, data: dict) -> dict:
        """
        Atualiza um produto existente.

        Args:
            product_id: ID do produto
            data: Dicionário com campos a atualizar

        Returns:
            Dict com 'success' e 'data' (produto atualizado) ou 'error'
        """
        user_id = self._get_user_id()
        logger.info(f"Updating product: {product_id}")

        result = self._handle_error(
            self.controller.update_product,
            product_id,
            data,
            user_id
        )

        if result['success']:
            event_bus.emit('product_updated', result['data']['product'])
            logger.info(f"Product updated: {product_id}")

        return result

    def delete_product(self, product_id: int) -> dict:
        """
        Deleta um produto.

        Args:
            product_id: ID do produto

        Returns:
            Dict com 'success' e 'message' ou 'error'
        """
        user_id = self._get_user_id()
        logger.info(f"Deleting product: {product_id}")

        result = self._handle_error(
            self.controller.delete_product,
            product_id,
            user_id
        )

        if result['success']:
            event_bus.emit('product_deleted', product_id)
            logger.info(f"Product deleted: {product_id}")

        return result

    def check_stock(self, product_id: int, requested_quantity: int) -> dict:
        """
        Verifica disponibilidade de estoque.

        Args:
            product_id: ID do produto
            requested_quantity: Quantidade solicitada

        Returns:
            Dict com 'success' e dados de disponibilidade
        """
        logger.debug(f"Checking stock for product {product_id}: {requested_quantity}")

        return self._handle_error(
            self.controller.check_stock,
            product_id,
            requested_quantity
        )