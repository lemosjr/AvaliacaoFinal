# backend/service/order_service.py
"""
Order service handles business rules for orders.
Integrates with product service for stock management.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal

from backend.repository.order_repository import OrderRepository
from backend.repository.order_item_repository import OrderItemRepository
from backend.repository.product_repository import ProductRepository
from backend.model.order_model import Order, OrderItem
from backend.model.product_model import Product
from backend.service.validation_service import ValidationService
from backend.service.state_service import StateService
from backend.service.product_service import ProductService
from backend.utils.exceptions import NotFoundError, ValidationError, BusinessRuleError, StateError
from backend.utils.logger import logger


class OrderService:
    """
    Service for order operations with business rules.
    """

    def __init__(self):
        self.order_repo = OrderRepository()
        self.order_item_repo = OrderItemRepository()
        self.product_service = ProductService()
        self.validator = ValidationService()

    def create_order(self, customer: str, user_id: int) -> Order:
        """
        Creates a new order with status 'created'.
        """
        validated = self.validator.validate_order_creation(customer, user_id)
        
        order = Order(
            customer=validated['customer'],
            user_id=validated['user_id'],
            status='created'
        )
        
        created = self.order_repo.create(order)
        logger.info(f"Order created: {created.id} for customer {created.customer}")
        return created

    def get_order(self, order_id: int) -> Order:
        """
        Gets an order by ID with its items.
        """
        order = self.order_repo.get_by_id_with_items(order_id)
        if not order:
            raise NotFoundError("Order", order_id)
        return order

    def get_orders_by_user(self, user_id: int) -> List[Order]:
        """
        Gets all orders for a user.
        """
        return self.order_repo.get_by_user(user_id)

    def get_all_orders(self) -> List[Order]:
        """
        Gets all orders.
        """
        return self.order_repo.get_all_with_items()

    def add_item_to_order(self, order_id: int, product_id: int, quantity: int) -> Order:
        """
        Adds a product to an existing order.
        """
        # Get order
        order = self.get_order(order_id)
        
        # Validate operation is allowed
        StateService.validate_operation(order.status, 'add_item')
        
        # Validate item
        item_data = self.validator.validate_order_item(product_id, quantity, self.product_service.product_repo)
        product = item_data['product']
        qty = item_data['quantity']
        
        # Check if product already in order, update quantity
        existing_items = self.order_item_repo.get_by_order(order_id)
        for existing in existing_items:
            if existing.product_id == product_id:
                # Update quantity (will also adjust stock)
                new_qty = existing.quantity + qty
                # Check stock again (total quantity)
                if new_qty > product.quantity_available:
                    raise BusinessRuleError(
                        f"Insufficient stock. Available: {product.quantity_available}, requested: {new_qty}",
                        rule="INSUFFICIENT_STOCK"
                    )
                # Reserve additional stock
                self.product_service.reserve_stock(product_id, qty)
                # Update item
                self.order_item_repo.update(existing.id, {'quantity': new_qty, 'subtotal': new_qty * product.price})
                logger.info(f"Updated item {existing.id} in order {order_id}")
                # Recalculate total
                self.calculate_total(order_id)
                return self.get_order(order_id)
        
        # New item: reserve stock
        self.product_service.reserve_stock(product_id, qty)
        
        # Create order item
        order_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=qty,
            unit_price=product.price,
            subtotal=qty * product.price
        )
        self.order_item_repo.create(order_item)
        logger.info(f"Added item to order {order_id}: product {product_id}, qty {qty}")
        
        # Recalculate total
        self.calculate_total(order_id)
        return self.get_order(order_id)

    def remove_item_from_order(self, order_id: int, item_id: int) -> Order:
        """
        Removes an item from an order.
        """
        order = self.get_order(order_id)
        StateService.validate_operation(order.status, 'remove_item')
        
        # Get item
        item = self.order_item_repo.get_by_id(item_id)
        if not item or item.order_id != order_id:
            raise NotFoundError("OrderItem", item_id)
        
        # Release stock
        self.product_service.release_stock(item.product_id, item.quantity)
        
        # Delete item
        self.order_item_repo.delete(item_id)
        logger.info(f"Removed item {item_id} from order {order_id}")
        
        # Recalculate total
        self.calculate_total(order_id)
        return self.get_order(order_id)

    def update_item_quantity(self, order_id: int, item_id: int, new_quantity: int) -> Order:
        """
        Updates quantity of an item in the order.
        """
        order = self.get_order(order_id)
        StateService.validate_operation(order.status, 'update_item')
        
        # Get item
        item = self.order_item_repo.get_by_id(item_id)
        if not item or item.order_id != order_id:
            raise NotFoundError("OrderItem", item_id)
        
        # Get product
        product = self.product_service.get_product(item.product_id)
        
        # Calculate difference
        diff = new_quantity - item.quantity
        
        if diff > 0:
            # Need more stock
            self.product_service.reserve_stock(item.product_id, diff)
        elif diff < 0:
            # Release excess stock
            self.product_service.release_stock(item.product_id, -diff)
        
        # Update item
        new_subtotal = new_quantity * product.price
        self.order_item_repo.update(item_id, {
            'quantity': new_quantity,
            'subtotal': new_subtotal
        })
        logger.info(f"Updated item {item_id} quantity to {new_quantity}")
        
        # Recalculate total
        self.calculate_total(order_id)
        return self.get_order(order_id)

    def calculate_total(self, order_id: int) -> float:
        """
        Calculates and updates the order total.
        """
        items = self.order_item_repo.get_by_order(order_id)
        total = sum(item.subtotal for item in items)
        
        # Update order total
        self.order_repo.update_total(order_id, total)
        logger.debug(f"Order {order_id} total updated: {total}")
        return total

    def change_order_status(self, order_id: int, new_status: str) -> Order:
        """
        Changes the status of an order with validation.
        """
        order = self.get_order(order_id)
        
        # Validate transition
        StateService.validate_transition(order.status, new_status)
        
        # Special rule: cannot finalize if no items
        if new_status == 'completed':
            items = self.order_item_repo.get_by_order(order_id)
            self.validator.validate_order_can_be_finalized(order, len(items))
        
        # Update status
        self.order_repo.update_status(order_id, new_status)
        logger.info(f"Order {order_id} status changed to {new_status}")
        
        return self.get_order(order_id)

    def cancel_order(self, order_id: int) -> Order:
        """
        Cancels an order and releases all stock.
        """
        order = self.get_order(order_id)
        
        # Validate can cancel
        StateService.validate_transition(order.status, 'cancelled')
        
        # Release all stock
        items = self.order_item_repo.get_by_order(order_id)
        for item in items:
            self.product_service.release_stock(item.product_id, item.quantity)
        
        # Update status
        self.order_repo.update_status(order_id, 'cancelled')
        logger.info(f"Order {order_id} cancelled, stock released")
        
        return self.get_order(order_id)

    def get_order_summary(self, order_id: int) -> Dict[str, Any]:
        """
        Returns a summary of the order with totals and items.
        """
        order = self.get_order(order_id)
        items = self.order_item_repo.get_by_order(order_id)
        
        return {
            'order': order.to_dict(),
            'items': [item.to_dict() for item in items],
            'item_count': len(items),
            'total_quantity': sum(item.quantity for item in items),
            'total_value': order.total_amount
        }

    def get_orders_by_status(self, status: str) -> List[Order]:
        """
        Gets orders filtered by status.
        """
        return self.order_repo.get_by_status(status)

    def get_order_history(self, user_id: int) -> List[Order]:
        """
        Gets order history for a user.
        """
        return self.order_repo.get_by_user(user_id, include_cancelled=True)