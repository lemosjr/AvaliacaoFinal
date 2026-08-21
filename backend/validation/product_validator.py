# backend/validation/product_validator.py
"""
Validator for Product entity.
Handles validation of product creation and updates.
"""

from typing import Optional, Dict, Any
from backend.utils.validators import (
    validate_non_empty_string,
    validate_length,
    validate_price,
    validate_quantity,
    validate_non_negative_number
)
from backend.utils.exceptions import ValidationError


class ProductValidator:
    """Validation methods for Product operations."""

    @staticmethod
    def validate_create(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates product creation data.

        Required fields:
            - description: non-empty string, max 200 chars
            - price: positive number with at most 2 decimals
            - quantity_available: non-negative integer

        Args:
            data: Dictionary with product data

        Returns:
            Dict with validated and sanitized data

        Raises:
            ValidationError: If any field is invalid
        """
        errors = []

        description = data.get('description', '').strip()
        price = data.get('price')
        quantity = data.get('quantity_available')

        # Validate description
        try:
            description = validate_non_empty_string(description, 'Description')
            description = validate_length(description, 3, 200, 'Description')
        except ValueError as e:
            errors.append(str(e))

        # Validate price
        try:
            if price is None:
                raise ValueError("Price is required")
            price = validate_price(price)
        except ValueError as e:
            errors.append(str(e))

        # Validate quantity
        try:
            if quantity is None:
                raise ValueError("Quantity is required")
            quantity = validate_non_negative_number(quantity, 'Quantity')
            quantity = int(quantity)  # Ensure integer
        except ValueError as e:
            errors.append(str(e))

        if errors:
            raise ValidationError("Validation failed for product creation", details=errors)

        return {
            'description': description,
            'price': price,
            'quantity_available': quantity
        }

    @staticmethod
    def validate_update(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates product update.

        Only validates fields that are present.
        """
        validated = {}
        errors = []

        # Validate description if provided
        if 'description' in data:
            try:
                description = validate_non_empty_string(data['description'], 'Description')
                description = validate_length(description, 3, 200, 'Description')
                validated['description'] = description
            except ValueError as e:
                errors.append(str(e))

        # Validate price if provided
        if 'price' in data:
            try:
                validated['price'] = validate_price(data['price'])
            except ValueError as e:
                errors.append(str(e))

        # Validate quantity if provided
        if 'quantity_available' in data:
            try:
                qty = validate_non_negative_number(data['quantity_available'], 'Quantity')
                validated['quantity_available'] = int(qty)
            except ValueError as e:
                errors.append(str(e))

        if errors:
            raise ValidationError("Validation failed for product update", details=errors)

        return validated

    @staticmethod
    def validate_quantity_for_order(product_id: int, quantity: int) -> int:
        """
        Validates that a quantity is positive and valid for an order.
        This is typically called before adding to cart/order.
        """
        try:
            return validate_quantity(quantity)
        except ValueError as e:
            raise ValidationError(f"Invalid quantity for product {product_id}: {str(e)}")

    @staticmethod
    def validate_stock_availability(available: int, requested: int) -> None:
        """
        Validates that requested quantity does not exceed available stock.
        """
        if requested > available:
            raise ValidationError(
                f"Insufficient stock. Available: {available}, Requested: {requested}",
                details={'available': available, 'requested': requested}
            )