# backend/model/order_item_model.py
"""
Order Item model representing individual items within an order.
Links orders and products with quantity and price snapshot.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class OrderItem:
    """
    OrderItem entity representing a product in an order.
    
    Attributes:
        id: Unique identifier
        order_id: ID of the parent order
        product_id: ID of the product
        quantity: Quantity ordered (> 0)
        unit_price: Price at time of order (snapshot)
        subtotal: Calculated (quantity * unit_price)
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        order_id: Optional[int] = None,
        product_id: Optional[int] = None,
        quantity: int = 0,
        unit_price: float = 0.0,
        subtotal: float = 0.0
    ):
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = int(quantity) if quantity is not None else 0
        self.unit_price = float(unit_price) if unit_price is not None else 0.0
        self.subtotal = float(subtotal) if subtotal else float(self.quantity * self.unit_price)
    
    def calculate_subtotal(self) -> float:
        """
        Calculates subtotal based on quantity and unit_price.
        
        Returns:
            float: Calculated subtotal
        """
        self.subtotal = self.quantity * self.unit_price
        return self.subtotal
    
    def update_quantity(self, new_quantity: int) -> None:
        """
        Updates quantity and recalculates subtotal.
        
        Args:
            new_quantity: New quantity (> 0)
        
        Raises:
            ValueError: If quantity is invalid
        """
        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        self.quantity = new_quantity
        self.calculate_subtotal()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts order item to dictionary.
        """
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderItem':
        """
        Creates an OrderItem instance from a dictionary.
        """
        return cls(
            id=data.get('id'),
            order_id=data.get('order_id'),
            product_id=data.get('product_id'),
            quantity=int(data.get('quantity', 0)),
            unit_price=float(data.get('unit_price', 0.0)),
            subtotal=float(data.get('subtotal', 0.0))
        )
    
    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, order={self.order_id}, product={self.product_id}, qty={self.quantity})>"
    
    def __str__(self) -> str:
        return f"Product {self.product_id} x {self.quantity} = ${self.subtotal:.2f}"