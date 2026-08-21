# backend/controller/order_controller.py
"""
Order Controller.
Handles order creation, item management, status updates, and queries.
"""

import logging
from typing import Dict, Any, Optional

from backend.service.order_service import OrderService
from backend.validation.order_validator import OrderValidator
from backend.utils.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleError,
    StateError,
    AppException
)

logger = logging.getLogger(__name__)


class OrderController:
    """Controller for order-related operations."""

    def __init__(self):
        self.order_service = OrderService()

    def create_order(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Create a new order.

        Args:
            data: Dict with customer, items (list of product_id/quantity)
            user_id: ID of authenticated user

        Returns:
            Dict with created order data

        Raises:
            ValidationError: If input data is invalid
            BusinessRuleError: If business rules violated
        """
        try:
            # 1. Validate input
            validated = OrderValidator.validate_create({**data, 'user_id': user_id})

            # 2. Call service
            order = self.order_service.create_order(
                customer=validated['customer'],
                items=validated['items'],
                user_id=validated['user_id']
            )

            logger.info(f"Order created: ID {order.id} for customer {order.customer} by user {user_id}")

            return {
                'success': True,
                'order': order.to_dict()
            }

        except (ValidationError, BusinessRuleError) as e:
            logger.warning(f"Order creation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during order creation: {str(e)}")
            raise AppException("Order creation failed due to internal error")

    def get_order(self, order_id: int) -> Dict[str, Any]:
        """
        Get a single order by ID.

        Args:
            order_id: Order ID

        Returns:
            Dict with order data

        Raises:
            NotFoundError: If order not found
        """
        try:
            order = self.order_service.get_order_by_id(order_id)
            if not order:
                raise NotFoundError('Order', order_id)

            return {'success': True, 'order': order.to_dict()}

        except NotFoundError as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting order {order_id}: {str(e)}")
            raise AppException("Failed to retrieve order")

    def list_orders(self, user_id: Optional[int] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List orders, optionally filtered by user and status.

        Args:
            user_id: Optional user ID to filter by owner
            status: Optional status filter

        Returns:
            Dict with list of orders
        """
        try:
            if status:
                # Validate status
                OrderValidator.validate_enum_value(status, OrderValidator.VALID_STATUSES, 'Status')

            orders = self.order_service.list_orders(user_id=user_id, status=status)
            return {
                'success': True,
                'orders': [o.to_dict() for o in orders],
                'count': len(orders)
            }
        except ValidationError as e:
            logger.warning(f"Invalid status filter: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing orders: {str(e)}")
            raise AppException("Failed to list orders")

    def add_item_to_order(self, order_id: int, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Add an item to an existing order.

        Args:
            order_id: Order ID
            data: Dict with product_id and quantity
            user_id: ID of authenticated user (for ownership check)

        Returns:
            Dict with updated order data

        Raises:
            NotFoundError: If order or product not found
            ValidationError: If input data is invalid
            StateError: If order status doesn't allow modification
            BusinessRuleError: If stock insufficient
        """
        try:
            # 1. Validate input
            validated = OrderValidator.validate_add_item(data)

            # 2. Call service
            order = self.order_service.add_item_to_order(
                order_id=order_id,
                product_id=validated['product_id'],
                quantity=validated['quantity'],
                user_id=user_id
            )

            logger.info(f"Item added to order {order_id} by user {user_id}")

            return {
                'success': True,
                'order': order.to_dict()
            }

        except (NotFoundError, ValidationError, StateError, BusinessRuleError) as e:
            logger.warning(f"Add item to order {order_id} failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding item to order {order_id}: {str(e)}")
            raise AppException("Failed to add item to order")

    def update_order_status(self, order_id: int, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Update the status of an order.

        Args:
            order_id: Order ID
            data: Dict with new status
            user_id: ID of authenticated user (for ownership check)

        Returns:
            Dict with updated order data

        Raises:
            NotFoundError: If order not found
            ValidationError: If status is invalid or transition not allowed
            StateError: If operation incompatible with current state
        """
        try:
            # 1. Validate input
            validated = OrderValidator.validate_status(data)

            # 2. Call service
            order = self.order_service.update_order_status(
                order_id=order_id,
                new_status=validated['status'],
                user_id=user_id
            )

            logger.info(f"Order {order_id} status updated to '{order.status}' by user {user_id}")

            return {
                'success': True,
                'order': order.to_dict()
            }

        except (NotFoundError, ValidationError, StateError) as e:
            logger.warning(f"Status update for order {order_id} failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating status of order {order_id}: {str(e)}")
            raise AppException("Failed to update order status")

    def calculate_order_total(self, order_id: int, user_id: int) -> Dict[str, Any]:
        """
        Calculate and return the total of an order (recalculates from items).

        Args:
            order_id: Order ID
            user_id: ID of authenticated user (for ownership check)

        Returns:
            Dict with order total

        Raises:
            NotFoundError: If order not found
        """
        try:
            total = self.order_service.calculate_order_total(order_id=order_id, user_id=user_id)
            return {
                'success': True,
                'order_id': order_id,
                'total': total
            }
        except NotFoundError as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating total for order {order_id}: {str(e)}")
            raise AppException("Failed to calculate order total")

    def delete_order(self, order_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete/cancel an order (only if in created/processing state).

        Args:
            order_id: Order ID
            user_id: ID of authenticated user (for ownership check)

        Returns:
            Dict with success message

        Raises:
            NotFoundError: If order not found
            StateError: If order cannot be deleted
        """
        try:
            self.order_service.delete_order(order_id=order_id, user_id=user_id)
            logger.info(f"Order {order_id} deleted by user {user_id}")
            return {'success': True, 'message': 'Order deleted successfully'}

        except (NotFoundError, StateError) as e:
            logger.warning(f"Delete order {order_id} failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting order {order_id}: {str(e)}")
            raise AppException("Failed to delete order")