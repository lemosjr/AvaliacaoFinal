# backend/service/validation_service.py
"""
Reusable business validations.
These are called by services to ensure business rules are followed.
"""

from typing import Optional, List, Dict, Any
from backend.utils.validators import (
    validate_non_empty_string,
    validate_positive_number,
    validate_non_negative_number,
    validate_price,
    validate_quantity,
    validate_email,
    validate_password_strength
)
from backend.utils.exceptions import ValidationError, BusinessRuleError


class ValidationService:
    """
    Centralized validation for business rules.
    """

    @staticmethod
    def validate_product_data(description: str, price: float, quantity_available: int) -> Dict[str, Any]:
        """
        Validates product creation/update data.
        """
        errors = []
        
        try:
            description = validate_non_empty_string(description, "Product description")
        except ValueError as e:
            errors.append(str(e))
        
        try:
            price = validate_price(price)
        except ValueError as e:
            errors.append(str(e))
        
        try:
            quantity_available = validate_non_negative_number(quantity_available, "Quantity available")
            # Ensure it's integer
            quantity_available = int(quantity_available)
        except ValueError as e:
            errors.append(str(e))
        
        if errors:
            raise ValidationError("Invalid product data", details={"errors": errors})
        
        return {
            "description": description,
            "price": price,
            "quantity_available": quantity_available
        }

    @staticmethod
    def validate_order_creation(customer: str, user_id: int) -> Dict[str, Any]:
        """
        Validates data for creating a new order.
        """
        try:
            customer = validate_non_empty_string(customer, "Customer name")
        except ValueError as e:
            raise ValidationError(str(e))
        
        if not user_id or user_id <= 0:
            raise ValidationError("Valid user ID is required")
        
        return {"customer": customer, "user_id": user_id}

    @staticmethod
    def validate_order_item(product_id: int, quantity: int, product_repo) -> Dict[str, Any]:
        """
        Validates adding an item to an order.
        Checks product exists, quantity > 0, and stock availability.
        """
        # Get product
        product = product_repo.get_by_id(product_id)
        if not product:
            raise ValidationError(f"Product with ID {product_id} not found")
        
        try:
            quantity = validate_quantity(quantity)
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Check stock
        if quantity > product.quantity_available:
            raise BusinessRuleError(
                f"Insufficient stock. Available: {product.quantity_available}, requested: {quantity}",
                rule="INSUFFICIENT_STOCK"
            )
        
        return {
            "product": product,
            "quantity": quantity,
            "unit_price": product.price,
            "subtotal": quantity * product.price
        }

    @staticmethod
    def validate_order_status_transition(current_status: str, new_status: str) -> None:
        """
        Validates if a status transition is allowed.
        """
        allowed_transitions = {
            "created": ["processing", "cancelled"],
            "processing": ["completed", "cancelled"],
            "completed": [],
            "cancelled": []
        }
        
        if new_status not in allowed_transitions.get(current_status, []):
            raise BusinessRuleError(
                f"Cannot transition from '{current_status}' to '{new_status}'",
                rule="INVALID_STATUS_TRANSITION"
            )

    @staticmethod
    def validate_order_can_add_items(order) -> None:
        """
        Validates if items can be added to the order.
        """
        if order.status in ["completed", "cancelled"]:
            raise BusinessRuleError(
                f"Cannot add items to a {order.status} order",
                rule="ORDER_FINALIZED"
            )

    @staticmethod
    def validate_order_can_be_finalized(order, items_count: int) -> None:
        """
        Validates if order can be finalized (must have at least one item).
        """
        if items_count == 0:
            raise BusinessRuleError(
                "Order must have at least one item before finalizing",
                rule="ORDER_EMPTY"
            )
        if order.status in ["completed", "cancelled"]:
            raise BusinessRuleError(
                f"Order is already {order.status}",
                rule="ORDER_FINALIZED"
            )

    @staticmethod
    def validate_user_registration(email: str, password: str, name: str) -> Dict[str, Any]:
        """
        Validates user registration data.
        """
        errors = []
        try:
            email = validate_email(email)
        except ValueError as e:
            errors.append(str(e))
        
        try:
            password = validate_password_strength(password)
        except ValueError as e:
            errors.append(str(e))
        
        try:
            name = validate_non_empty_string(name, "Name")
        except ValueError as e:
            errors.append(str(e))
        
        if errors:
            raise ValidationError("Invalid registration data", details={"errors": errors})
        
        return {"email": email, "password": password, "name": name}