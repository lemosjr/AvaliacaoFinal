# backend/model/product_model.py
"""
Product model representing items available for purchase.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class Product:
    """
    Product entity representing an item in the inventory.
    
    Attributes:
        id: Unique identifier
        description: Product description/name
        price: Unit price (> 0)
        quantity_available: Available stock (>= 0)
        user_id: ID of the user who created this product
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        description: str = '',
        price: float = 0.0,
        quantity_available: int = 0,
        user_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.description = description
        self.price = price
        self.quantity_available = quantity_available
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts product to dictionary.
        """
        return {
            'id': self.id,
            'description': self.description,
            'price': self.price,
            'quantity_available': self.quantity_available,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """
        Creates a Product instance from a dictionary.
        """
        return cls(
            id=data.get('id'),
            description=data.get('description', ''),
            price=float(data.get('price', 0.0)),
            quantity_available=int(data.get('quantity_available', 0)),
            user_id=data.get('user_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def has_stock(self, quantity: int) -> bool:
        """
        Checks if enough stock is available.
        
        Args:
            quantity: Requested quantity
        
        Returns:
            bool: True if enough stock available
        """
        return self.quantity_available >= quantity
    
    def reduce_stock(self, quantity: int) -> None:
        """
        Reduces available stock by the given quantity.
        
        Args:
            quantity: Quantity to reduce
        
        Raises:
            ValueError: If insufficient stock
        """
        if not self.has_stock(quantity):
            raise ValueError(f"Insufficient stock. Available: {self.quantity_available}, Requested: {quantity}")
        self.quantity_available -= quantity
        self.updated_at = datetime.now()
    
    def increase_stock(self, quantity: int) -> None:
        """
        Increases available stock by the given quantity.
        
        Args:
            quantity: Quantity to add (must be positive)
        
        Raises:
            ValueError: If quantity is negative
        """
        if quantity < 0:
            raise ValueError("Quantity must be positive")
        self.quantity_available += quantity
        self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, description='{self.description}', price={self.price}, stock={self.quantity_available})>"
    
    def __str__(self) -> str:
        return f"{self.description} - ${self.price:.2f} (Stock: {self.quantity_available})>"