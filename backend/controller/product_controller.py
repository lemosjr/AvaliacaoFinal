# backend/controller/product_controller.py
"""
Product Controller.
Handles product CRUD operations.
"""

import logging
from typing import Dict, Any, Optional

from backend.service.product_service import ProductService
from backend.validation.product_validator import ProductValidator
from backend.utils.exceptions import ValidationError, NotFoundError, AppException

logger = logging.getLogger(__name__)


class ProductController:
    """Controller for product-related operations."""

    def __init__(self):
        self.product_service = ProductService()

    def create_product(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Create a new product.

        Args:
            data: Dict with description, price, quantity_available
            user_id: ID of authenticated user creating the product

        Returns:
            Dict with created product data

        Raises:
            ValidationError: If input data is invalid
            AppException: If creation fails
        """
        try:
            # 1. Validate input
            validated = ProductValidator.validate_create(data)

            # 2. Call service
            product = self.product_service.create_product(
                description=validated['description'],
                price=validated['price'],
                quantity_available=validated['quantity_available'],
                user_id=user_id
            )

            logger.info(f"Product created: {product.description} (ID: {product.id}) by user {user_id}")

            return {
                'success': True,
                'product': product.to_dict()
            }

        except (ValidationError, AppException) as e:
            logger.warning(f"Product creation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during product creation: {str(e)}")
            raise AppException("Product creation failed due to internal error")

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """
        Get a single product by ID.

        Args:
            product_id: Product ID

        Returns:
            Dict with product data

        Raises:
            NotFoundError: If product not found
        """
        try:
            product = self.product_service.get_product(product_id)
            if not product:
                raise NotFoundError('Product', product_id)

            return {'success': True, 'product': product.to_dict()}

        except NotFoundError as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting product {product_id}: {str(e)}")
            raise AppException("Failed to retrieve product")

    def list_products(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        List products, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter products by owner

        Returns:
            Dict with list of products
        """
        try:
            products = self.product_service.get_all_products(user_id=user_id)
            return {
                'success': True,
                'products': [p.to_dict() for p in products],
                'count': len(products)
            }
        except Exception as e:
            logger.error(f"Unexpected error listing products: {str(e)}")
            raise AppException("Failed to list products")

    def update_product(self, product_id: int, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Update an existing product.

        Args:
            product_id: Product ID
            data: Dict with fields to update
            user_id: ID of authenticated user (for ownership check)

        Returns:
            Dict with updated product data

        Raises:
            NotFoundError: If product not found
            AuthorizationError: If user doesn't own the product
            ValidationError: If input data is invalid
        """
        try:
            # 1. Validate input
            validated = ProductValidator.validate_update(data)

            # 2. Call service
            product = self.product_service.update_product(
                product_id=product_id,
                data=validated
            )

            logger.info(f"Product updated: {product.description} (ID: {product.id}) by user {user_id}")

            return {
                'success': True,
                'product': product.to_dict()
            }

        except (NotFoundError, ValidationError, AppException) as e:
            logger.warning(f"Product update failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating product {product_id}: {str(e)}")
            raise AppException("Product update failed due to internal error")

    def delete_product(self, product_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete a product.

        Args:
            product_id: Product ID
            user_id: ID of authenticated user (for ownership check)

        Returns:
            Dict with success message

        Raises:
            NotFoundError: If product not found
            AuthorizationError: If user doesn't own the product
        """
        try:
            self.product_service.delete_product(product_id=product_id)
            logger.info(f"Product deleted: ID {product_id} by user {user_id}")
            return {'success': True, 'message': 'Product deleted successfully'}

        except (NotFoundError, AppException) as e:
            logger.warning(f"Product deletion failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting product {product_id}: {str(e)}")
            raise AppException("Product deletion failed")

    def check_stock(self, product_id: int, requested_quantity: int) -> Dict[str, Any]:
        """
        Check if requested quantity is available.

        Args:
            product_id: Product ID
            requested_quantity: Quantity requested

        Returns:
            Dict with availability info
        """
        try:
            product = self.product_service.get_product(product_id)
            if not product:
                raise NotFoundError('Product', product_id)

            available = product.quantity_available >= requested_quantity

            return {
                'success': True,
                'product_id': product_id,
                'available': available,
                'stock': product.quantity_available,
                'requested': requested_quantity
            }

        except NotFoundError as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking stock: {str(e)}")
            raise AppException("Failed to check stock")