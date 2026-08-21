# backend/repository/product_repository.py
"""
Product repository for database operations related to products.
"""

import logging
from typing import Optional, List

from backend.repository.base_repository import BaseRepository
from backend.model.product_model import Product
from backend.utils.exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class ProductRepository(BaseRepository[Product]):
    """
    Repository for Product entity with additional product-specific methods.
    """
    
    def __init__(self):
        super().__init__(Product, 'products', 'id')
    
    def get_by_user(self, user_id: int) -> List[Product]:
        """
        Retrieves all products belonging to a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            List[Product]: List of products
        """
        return self.get_by_field('user_id', user_id)
    
    def get_in_stock(self) -> List[Product]:
        """
        Retrieves all products with stock > 0.
        
        Returns:
            List[Product]: List of products in stock
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE quantity_available > 0 
            ORDER BY {self.id_field}
        """
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [self._from_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching in-stock products: {str(e)}")
            raise DatabaseError(f"Failed to fetch in-stock products: {str(e)}")
    
    def get_low_stock(self, threshold: int = 5) -> List[Product]:
        """
        Retrieves products with stock below a threshold.
        
        Args:
            threshold: Stock threshold (default: 5)
        
        Returns:
            List[Product]: List of low-stock products
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE quantity_available < %s 
            AND quantity_available > 0
            ORDER BY quantity_available ASC
        """
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, (threshold,))
                rows = cur.fetchall()
                return [self._from_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching low-stock products: {str(e)}")
            raise DatabaseError(f"Failed to fetch low-stock products: {str(e)}")
    
    def update_stock(self, product_id: int, quantity_change: int) -> Product:
        """
        Updates the stock of a product by adding or subtracting a quantity.
        
        Args:
            product_id: Product ID
            quantity_change: Positive to add, negative to subtract
        
        Returns:
            Product: Updated product instance
        
        Raises:
            ValueError: If resulting stock would be negative
            NotFoundError: If product not found
        """
        # Check if product exists
        product = self.get_by_id(product_id)
        
        new_quantity = product.quantity_available + quantity_change
        
        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock. Current: {product.quantity_available}, "
                f"Requested change: {quantity_change}"
            )
        
        return self.update(product_id, {'quantity_available': new_quantity})
    
    def search_by_description(self, search_term: str) -> List[Product]:
        """
        Searches products by description (case-insensitive partial match).
        
        Args:
            search_term: Search string
        
        Returns:
            List[Product]: List of matching products
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE LOWER(description) LIKE %s 
            ORDER BY {self.id_field}
        """
        search_pattern = f"%{search_term.lower()}%"
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, (search_pattern,))
                rows = cur.fetchall()
                return [self._from_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching products by description: {str(e)}")
            raise DatabaseError(f"Failed to search products: {str(e)}")
    
    def get_products_with_stats(self) -> List[dict]:
        """
        Retrieves products with order statistics (total ordered, revenue).
        
        Returns:
            List[dict]: List of product statistics
        """
        query = """
            SELECT 
                p.id,
                p.description,
                p.price,
                p.quantity_available,
                p.created_at,
                COUNT(oi.id) AS times_ordered,
                COALESCE(SUM(oi.quantity), 0) AS total_quantity_ordered,
                COALESCE(SUM(oi.subtotal), 0) AS total_revenue
            FROM products p
            LEFT JOIN order_items oi ON oi.product_id = p.id
            GROUP BY p.id
            ORDER BY p.id
        """
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error fetching products with stats: {str(e)}")
            raise DatabaseError(f"Failed to fetch product stats: {str(e)}")