# backend/repository/order_repository.py
"""
Order repository for database operations related to orders.
"""

import logging
from typing import Optional, List, Dict, Any

from backend.repository.base_repository import BaseRepository
from backend.model.order_model import Order
from backend.utils.exceptions import NotFoundError, DatabaseError
from backend.config.database import db

logger = logging.getLogger(__name__)


class OrderRepository(BaseRepository[Order]):
    """
    Repository for Order entity with additional order-specific methods.
    """
    
    def __init__(self):
        super().__init__(Order, 'orders', 'id')
    
    def get_by_user(self, user_id: int) -> List[Order]:
        """
        Retrieves all orders belonging to a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            List[Order]: List of orders
        """
        return self.get_by_field('user_id', user_id)
    
    def get_by_status(self, status: str) -> List[Order]:
        """
        Retrieves all orders with a specific status.
        
        Args:
            status: Order status ('created', 'processing', 'completed', 'cancelled')
        
        Returns:
            List[Order]: List of orders
        """
        return self.get_by_field('status', status)
    
    def get_active_orders(self) -> List[Order]:
        """
        Retrieves all non-completed and non-cancelled orders.
        
        Returns:
            List[Order]: List of active orders
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE status NOT IN ('completed', 'cancelled')
            ORDER BY created_at DESC
        """
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [self._from_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching active orders: {str(e)}")
            raise DatabaseError(f"Failed to fetch active orders: {str(e)}")
    
    def get_recent_orders(self, limit: int = 10) -> List[Order]:
        """
        Retrieves the most recent orders.
        
        Args:
            limit: Maximum number of orders to return
        
        Returns:
            List[Order]: List of recent orders
        """
        return self.get_all(limit=limit, offset=0)
    
    def update_status(self, order_id: int, new_status: str) -> Order:
        """
        Updates the status of an order.
        
        Args:
            order_id: Order ID
            new_status: New status value
        
        Returns:
            Order: Updated order instance
        
        Raises:
            NotFoundError: If order not found
        """
        # Validate status (will be caught by database CHECK constraint)
        return self.update(order_id, {'status': new_status})
    
    def update_total_amount(self, order_id: int) -> Order:
        """
        Recalculates and updates the total_amount of an order
        based on its items.
        
        Args:
            order_id: Order ID
        
        Returns:
            Order: Updated order instance
        
        Raises:
            NotFoundError: If order not found
        """
        # Check if order exists
        self.get_by_id(order_id)
        
        query = """
            UPDATE orders o
            SET total_amount = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM order_items
                WHERE order_id = o.id
            )
            WHERE o.id = %s
            RETURNING id
        """
        
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (order_id,))
                    # get_connection context manager commits automatically
                    return self.get_by_id(order_id)
        except Exception as e:
            logger.error(f"Error updating total amount for order {order_id}: {str(e)}")
            raise DatabaseError(f"Failed to update total amount: {str(e)}")
    
    def get_orders_with_items(self, order_id: int) -> Dict[str, Any]:
        """
        Retrieves an order with all its items in a single query.
        
        Args:
            order_id: Order ID
        
        Returns:
            dict: Order data with items
        
        Raises:
            NotFoundError: If order not found
        """
        # First check if order exists
        self.get_by_id(order_id)
        
        query = """
            SELECT 
                o.*,
                json_agg(
                    json_build_object(
                        'id', oi.id,
                        'product_id', oi.product_id,
                        'quantity', oi.quantity,
                        'unit_price', oi.unit_price,
                        'subtotal', oi.subtotal,
                        'product_description', p.description
                    )
                ) AS items
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.id
            LEFT JOIN products p ON p.id = oi.product_id
            WHERE o.id = %s
            GROUP BY o.id
        """
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, (order_id,))
                result = cur.fetchone()
                if not result:
                    raise NotFoundError('Order', order_id)
                return result
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching order with items {order_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch order with items: {str(e)}")
    
    def get_order_report(self) -> List[Dict[str, Any]]:
        """
        Retrieves the order report using the vw_order_report view.
        
        Returns:
            List[Dict]: Report data
        """
        query = "SELECT * FROM vw_order_report"
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error fetching order report: {str(e)}")
            raise DatabaseError(f"Failed to fetch order report: {str(e)}")