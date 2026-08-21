# backend/repository/order_item_repository.py
"""
Order item repository for database operations related to order items.
"""

import logging
from typing import Optional, List, Dict, Any

from backend.repository.base_repository import BaseRepository
from backend.model.order_item_model import OrderItem
from backend.utils.exceptions import NotFoundError, DatabaseError
from backend.config.database import db

logger = logging.getLogger(__name__)


class OrderItemRepository(BaseRepository[OrderItem]):
    """
    Repository for OrderItem entity with additional order-item-specific methods.
    """
    
    def __init__(self):
        super().__init__(OrderItem, 'order_items', 'id')
    
    def get_by_order(self, order_id: int) -> List[OrderItem]:
        """
        Retrieves all items belonging to a specific order.
        
        Args:
            order_id: Order ID
        
        Returns:
            List[OrderItem]: List of order items
        """
        return self.get_by_field('order_id', order_id)
    
    def get_by_product(self, product_id: int) -> List[OrderItem]:
        """
        Retrieves all items containing a specific product.
        
        Args:
            product_id: Product ID
        
        Returns:
            List[OrderItem]: List of order items
        """
        return self.get_by_field('product_id', product_id)
    
    def delete_by_order(self, order_id: int) -> int:
        """
        Deletes all items belonging to an order.
        
        Args:
            order_id: Order ID
        
        Returns:
            int: Number of deleted items
        
        Raises:
            DatabaseError: If deletion fails
        """
        query = "DELETE FROM order_items WHERE order_id = %s"
        
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (order_id,))
                    deleted_count = cur.rowcount
                    conn.commit()
                    return deleted_count
        except Exception as e:
            logger.error(f"Error deleting items for order {order_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete order items: {str(e)}")
    
    def get_items_with_details(self, order_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves order items with product details for a specific order.
        
        Args:
            order_id: Order ID
        
        Returns:
            List[Dict]: Items with product details
        """
        query = """
            SELECT 
                oi.id,
                oi.order_id,
                oi.product_id,
                oi.quantity,
                oi.unit_price,
                oi.subtotal,
                p.description AS product_description,
                p.price AS current_price,
                p.quantity_available AS current_stock
            FROM order_items oi
            LEFT JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = %s
            ORDER BY oi.id
        """
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, (order_id,))
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error fetching items with details for order {order_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch items with details: {str(e)}")
    
    def create_multiple(self, items_data: List[Dict[str, Any]]) -> List[OrderItem]:
        """
        Creates multiple order items in a single transaction.
        
        Args:
            items_data: List of dictionaries with order item data
        
        Returns:
            List[OrderItem]: List of created order items
        
        Raises:
            DatabaseError: If creation fails
        """
        if not items_data:
            return []
        
        created_items = []
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    for item in items_data:
                        # Remove id if present
                        item_copy = item.copy()
                        item_copy.pop('id', None)
                        
                        columns = list(item_copy.keys())
                        placeholders = [f"%s"] * len(columns)
                        values = list(item_copy.values())
                        
                        query = f"""
                            INSERT INTO order_items ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                            RETURNING id
                        """
                        cur.execute(query, values)
                        new_id = cur.fetchone()[0]
                        
                        # Fetch the created item
                        cur.execute("SELECT * FROM order_items WHERE id = %s", (new_id,))
                        row = cur.fetchone()
                        # Convert to dict for model creation
                        # Since we don't have dict_cursor here, we need to get column names
                        col_names = [desc[0] for desc in cur.description]
                        row_dict = dict(zip(col_names, row))
                        created_items.append(self._from_dict(row_dict))
                    
                    conn.commit()
                    return created_items
        except Exception as e:
            logger.error(f"Error creating multiple order items: {str(e)}")
            raise DatabaseError(f"Failed to create order items: {str(e)}")
    
    def update_order_item_subtotals(self, order_id: int) -> bool:
        """
        Recalculates subtotal for all items of a given order
        (assuming quantity or unit_price changed).
        
        Args:
            order_id: Order ID
        
        Returns:
            bool: True if updated successfully
        """
        query = """
            UPDATE order_items
            SET subtotal = quantity * unit_price
            WHERE order_id = %s
        """
        
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (order_id,))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Error updating subtotals for order {order_id}: {str(e)}")
            raise DatabaseError(f"Failed to update subtotals: {str(e)}")