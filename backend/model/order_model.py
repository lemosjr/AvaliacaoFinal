# backend/model/order_model.py
"""
Order model representing customer orders.
Manages order lifecycle and status transitions.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class OrderStatus(str, Enum):
    """
    Valid order statuses (values must match the database CHECK constraint).
    Orders follow a lifecycle: created -> processing -> completed (or cancelled).
    """
    CREATED = 'created'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    @classmethod
    def get_valid_transitions(cls, current_status: str) -> List[str]:
        """
        Returns valid next statuses for a given current status.
        
        Args:
            current_status: Current order status
        
        Returns:
            List[str]: List of valid next statuses
        """
        transitions = {
            cls.CREATED.value: [cls.PROCESSING.value, cls.CANCELLED.value],
            cls.PROCESSING.value: [cls.COMPLETED.value, cls.CANCELLED.value],
            cls.COMPLETED.value: [],
            cls.CANCELLED.value: []
        }
        return transitions.get(current_status, [])
    
    @classmethod
    def can_transition(cls, current_status: str, new_status: str) -> bool:
        """
        Checks if a transition from current_status to new_status is valid.
        
        Args:
            current_status: Current order status
            new_status: Desired new status
        
        Returns:
            bool: True if transition is valid
        """
        valid_transitions = cls.get_valid_transitions(current_status)
        return new_status in valid_transitions


class Order:
    """
    Order entity representing a customer order.
    
    Attributes:
        id: Unique identifier
        customer: Customer name
        status: Current order status (OrderStatus)
        total_amount: Total order amount (sum of items)
        user_id: ID of the user who created this order
        created_at: Creation timestamp
        updated_at: Last update timestamp
        items: List of OrderItems (not stored in database directly)
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        customer: str = '',
        status: str = OrderStatus.CREATED.value,
        total_amount: float = 0.0,
        user_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        items: Optional[List['OrderItem']] = None
    ):
        self.id = id
        self.customer = customer
        self.status = status
        self.total_amount = total_amount
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.items = items or []
    
    def add_item(self, item: 'OrderItem') -> None:
        """
        Adds an item to the order and recalculates total.
        
        Args:
            item: OrderItem to add
        
        Raises:
            ValueError: If order is finalized or canceled
        """
        if self.status in [OrderStatus.COMPLETED.value, OrderStatus.CANCELLED.value]:
            raise ValueError(f"Cannot add items to a {self.status} order")
        
        self.items.append(item)
        self._recalculate_total()
        self.updated_at = datetime.now()
    
    def remove_item(self, item_id: int) -> None:
        """
        Removes an item from the order and recalculates total.
        
        Args:
            item_id: ID of the item to remove
        
        Raises:
            ValueError: If order is finalized or canceled
            ValueError: If item not found
        """
        if self.status in [OrderStatus.COMPLETED.value, OrderStatus.CANCELLED.value]:
            raise ValueError(f"Cannot remove items from a {self.status} order")
        
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                self._recalculate_total()
                self.updated_at = datetime.now()
                return
        
        raise ValueError(f"Item with id {item_id} not found in order")
    
    def _recalculate_total(self) -> None:
        """
        Recalculates total_amount based on items.
        """
        self.total_amount = sum(item.subtotal for item in self.items)
    
    def change_status(self, new_status: str) -> None:
        """
        Changes the order status if transition is valid.
        
        Args:
            new_status: New order status
        
        Raises:
            ValueError: If transition is invalid
            ValueError: If trying to finalize without items
        """
        # Validate transition
        if not OrderStatus.can_transition(self.status, new_status):
            raise ValueError(
                f"Cannot transition from '{self.status}' to '{new_status}'. "
                f"Valid transitions: {OrderStatus.get_valid_transitions(self.status)}"
            )
        
        # Business rule: Can't finalize without items
        if new_status == OrderStatus.COMPLETED.value and not self.items:
            raise ValueError("Cannot finalize order without items")
        
        self.status = new_status
        self.updated_at = datetime.now()
    
    def get_item_count(self) -> int:
        """
        Returns the number of items in the order.
        """
        return len(self.items)
    
    def get_total_quantity(self) -> int:
        """
        Returns the total quantity of all items in the order.
        """
        return sum(item.quantity for item in self.items)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts order to dictionary.
        """
        return {
            'id': self.id,
            'customer': self.customer,
            'status': self.status,
            'total_amount': self.total_amount,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    def to_dict_basic(self) -> Dict[str, Any]:
        """
        Converts order to dictionary without items (for listings).
        """
        return {
            'id': self.id,
            'customer': self.customer,
            'status': self.status,
            'total_amount': self.total_amount,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'item_count': self.get_item_count(),
            'total_quantity': self.get_total_quantity()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """
        Creates an Order instance from a dictionary.
        Items are not loaded automatically.
        """
        return cls(
            id=data.get('id'),
            customer=data.get('customer', ''),
            status=data.get('status', OrderStatus.CREATED.value),
            total_amount=float(data.get('total_amount', 0.0)),
            user_id=data.get('user_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, customer='{self.customer}', status='{self.status}', total={self.total_amount})>"
    
    def __str__(self) -> str:
        return f"Order #{self.id} - {self.customer} - {self.status} - ${self.total_amount:.2f}"