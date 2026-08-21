# backend/validation/order_validator.py
"""
Validator for Order entity.
Handles validation of order creation, item addition, and status transitions.
"""

from typing import Optional, Dict, Any, List
from backend.utils.validators import (
    validate_non_empty_string,
    validate_length,
    validate_quantity,
    validate_price,
    validate_enum_value
)
from backend.utils.exceptions import ValidationError


class OrderValidator:
    """Validation methods for Order operations."""

    # Valid order statuses (matching database CHECK constraint)
    VALID_STATUSES = ['created', 'processing', 'completed', 'cancelled']

    # Allowed status transitions
    ALLOWED_TRANSITIONS = {
        'created': ['processing', 'cancelled'],
        'processing': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': []
    }

    @staticmethod
    def validate_create(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates order creation data.

        Required fields:
            - customer: non-empty string, max 100 chars
            - items: list of items (each with product_id and quantity)
            - user_id: required (implicitly from authenticated user)

        Args:
            data: Dictionary with order data

        Returns:
            Dict with validated data

        Raises:
            ValidationError: If any field is invalid
        """
        errors = []

        customer = data.get('customer', '').strip()
        items = data.get('items', [])
        user_id = data.get('user_id')

        # Validate customer
        try:
            customer = validate_non_empty_string(customer, 'Customer')
            customer = validate_length(customer, 2, 100, 'Customer')
        except ValueError as e:
            errors.append(str(e))

        # Validate user_id
        if not user_id:
            errors.append("User ID is required")
        elif not isinstance(user_id, int) or user_id <= 0:
            errors.append("User ID must be a positive integer")

        # Validate items
        try:
            OrderValidator._validate_items(items)
        except ValidationError as e:
            errors.extend(e.details or [str(e)])

        if errors:
            raise ValidationError("Validation failed for order creation", details=errors)

        return {
            'customer': customer,
            'items': items,
            'user_id': user_id
        }

    @staticmethod
    def _validate_items(items: List[Dict[str, Any]]) -> None:
        """
        Validates list of order items.
        Each item must have product_id and quantity > 0.
        """
        if not items:
            raise ValidationError("At least one item is required")

        errors = []
        for idx, item in enumerate(items):
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            if not product_id or not isinstance(product_id, int) or product_id <= 0:
                errors.append(f"Item #{idx+1}: Invalid product_id")

            try:
                validate_quantity(quantity)
            except ValueError as e:
                errors.append(f"Item #{idx+1}: {str(e)}")

        if errors:
            raise ValidationError("Invalid items", details=errors)

    @staticmethod
    def validate_add_item(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates adding an item to an existing order.

        Required fields:
            - product_id: positive integer
            - quantity: positive integer

        Returns:
            Dict with validated data
        """
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        errors = []

        if not product_id or not isinstance(product_id, int) or product_id <= 0:
            errors.append("product_id must be a positive integer")

        try:
            quantity = validate_quantity(quantity)
        except ValueError as e:
            errors.append(str(e))

        if errors:
            raise ValidationError("Invalid item data", details=errors)

        return {
            'product_id': product_id,
            'quantity': quantity
        }

    @staticmethod
    def validate_status_transition(current_status: str, new_status: str) -> None:
        """
        Validates if a status transition is allowed.

        Args:
            current_status: Current order status
            new_status: Desired new status

        Raises:
            ValidationError: If transition is not allowed
        """
        # Validate statuses are valid
        current_status = current_status.lower()
        new_status = new_status.lower()

        if current_status not in OrderValidator.VALID_STATUSES:
            raise ValidationError(f"Invalid current status: {current_status}")

        if new_status not in OrderValidator.VALID_STATUSES:
            raise ValidationError(f"Invalid new status: {new_status}")

        # Check if transition is allowed
        allowed = OrderValidator.ALLOWED_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValidationError(
                f"Cannot transition from '{current_status}' to '{new_status}'. "
                f"Allowed transitions: {allowed if allowed else 'none'}"
            )

    @staticmethod
    def validate_status(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates a status update request.

        Required fields:
            - status: valid status string

        Returns:
            Dict with validated status
        """
        status = data.get('status', '').strip().lower()

        if not status:
            raise ValidationError("Status is required")

        try:
            status = validate_enum_value(status, OrderValidator.VALID_STATUSES, 'Status')
        except ValueError as e:
            raise ValidationError(str(e))

        return {'status': status}

    @staticmethod
    def validate_order_can_be_modified(order_status: str, operation: str) -> None:
        """
        Validates that an order can be modified based on its status.

        Rules:
            - Completed orders cannot be modified
            - Cancelled orders cannot be modified
            - Created/Processing orders can be modified

        Args:
            order_status: Current order status
            operation: Description of the operation (for error message)

        Raises:
            ValidationError: If order cannot be modified
        """
        if order_status.lower() in ['completed', 'cancelled']:
            raise ValidationError(
                f"Cannot perform '{operation}' on a '{order_status}' order"
            )

    @staticmethod
    def validate_order_has_items(items: List) -> None:
        """
        Validates that an order has at least one item before completion.
        """
        if not items or len(items) == 0:
            raise ValidationError("Cannot complete order with no items")