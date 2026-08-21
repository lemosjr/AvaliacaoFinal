# backend/service/product_service.py
"""
Product service handles business rules for products.
"""

from typing import List, Optional, Dict, Any
from backend.repository.product_repository import ProductRepository
from backend.model.product_model import Product
from backend.service.validation_service import ValidationService
from backend.utils.validators import (
    validate_non_empty_string,
    validate_price,
    validate_non_negative_number
)
from backend.utils.exceptions import NotFoundError, ValidationError, BusinessRuleError
from backend.utils.logger import logger


class ProductService:
    """
    Service for product operations with business rules.
    """

    def __init__(self):
        self.product_repo = ProductRepository()
        self.validator = ValidationService()

    def create_product(self, description: str, price: float, quantity_available: int, user_id: int) -> Product:
        """
        Creates a new product.
        """
        # Validate
        validated = self.validator.validate_product_data(description, price, quantity_available)
        
        # Create product (only real database columns)
        created = self.product_repo.create({
            'description': validated['description'],
            'price': validated['price'],
            'quantity_available': validated['quantity_available'],
            'user_id': user_id
        })
        logger.info(f"Product created: {created.id} - {created.description}")
        return created

    def get_product(self, product_id: int) -> Product:
        """
        Gets a product by ID, raises NotFoundError if not found.
        """
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product", product_id)
        return product

    def get_all_products(self, user_id: Optional[int] = None) -> List[Product]:
        """
        Gets all products, optionally filtered by user.
        """
        if user_id:
            return self.product_repo.get_by_user(user_id)
        return self.product_repo.get_all()

    def update_product(self, product_id: int, data: Dict[str, Any]) -> Product:
        """
        Updates a product.
        """
        product = self.get_product(product_id)
        
        # Validate fields that are provided
        validated_data = {}
        if 'description' in data:
            validated_data['description'] = validate_non_empty_string(data['description'], "Description")
        if 'price' in data:
            validated_data['price'] = validate_price(data['price'])
        if 'quantity_available' in data:
            validated_data['quantity_available'] = int(validate_non_negative_number(data['quantity_available'], "Quantity"))
        
        if not validated_data:
            raise ValidationError("No valid fields to update")
        
        # Update product
        updated = self.product_repo.update(product_id, validated_data)
        if not updated:
            raise NotFoundError("Product", product_id)
        
        logger.info(f"Product updated: {updated.id}")
        return updated

    def delete_product(self, product_id: int) -> bool:
        """
        Deletes a product.
        """
        product = self.get_product(product_id)
        # You might want to check if product is referenced in orders before deletion
        # For now, we'll let the repository handle it (cascade)
        result = self.product_repo.delete(product_id)
        if result:
            logger.info(f"Product deleted: {product_id}")
        return result

    def check_stock(self, product_id: int, requested_quantity: int) -> bool:
        """
        Checks if stock is sufficient.
        """
        product = self.get_product(product_id)
        return product.quantity_available >= requested_quantity

    def reserve_stock(self, product_id: int, quantity: int) -> None:
        """
        Reserves stock (decreases quantity).
        Used when adding items to an order.
        """
        product = self.get_product(product_id)
        if quantity > product.quantity_available:
            raise BusinessRuleError(
                f"Insufficient stock. Available: {product.quantity_available}, requested: {quantity}",
                rule="INSUFFICIENT_STOCK"
            )
        self.product_repo.update(product_id, {
            'quantity_available': product.quantity_available - quantity
        })
        logger.info(f"Reserved {quantity} of product {product_id}")

    def release_stock(self, product_id: int, quantity: int) -> None:
        """
        Releases stock (increases quantity).
        Used when order is cancelled or items removed.
        """
        product = self.get_product(product_id)
        new_qty = product.quantity_available + quantity
        self.product_repo.update(product_id, {
            'quantity_available': new_qty
        })
        logger.info(f"Released {quantity} of product {product_id}")

    def search_products(self, query: str) -> List[Product]:
        """
        Searches products by description.
        """
        return self.product_repo.search_by_description(query)