# backend/repository/user_repository.py
"""
User repository for database operations related to users.
"""

import logging
from typing import Optional, List

from backend.repository.base_repository import BaseRepository
from backend.model.user_model import User
from backend.utils.exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Repository for User entity with additional user-specific methods.
    """
    
    def __init__(self):
        super().__init__(User, 'users', 'id')
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user by email.
        
        Args:
            email: User email address
        
        Returns:
            Optional[User]: User instance or None if not found
        """
        results = self.get_by_field('email', email)
        return results[0] if results else None
    
    def get_active_users(self) -> List[User]:
        """
        Retrieves all active users.
        
        Returns:
            List[User]: List of active users
        """
        return self.get_by_field('is_active', True)
    
    def update_last_login(self, user_id: int) -> bool:
        """
        Updates the last_login timestamp for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if updated successfully
        
        Raises:
            NotFoundError: If user not found
        """
        # Check if user exists
        self.get_by_id(user_id)
        
        query = """
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE id = %s
        """
        
        try:
            from backend.config.database import db
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (user_id,))
                    return True
        except Exception as e:
            logger.error(f"Error updating last_login for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to update last_login: {str(e)}")
    
    def deactivate_user(self, user_id: int) -> User:
        """
        Deactivates a user (sets is_active = False).
        
        Args:
            user_id: User ID
        
        Returns:
            User: Updated user instance
        
        Raises:
            NotFoundError: If user not found
        """
        return self.update(user_id, {'is_active': False})
    
    def activate_user(self, user_id: int) -> User:
        """
        Activates a user (sets is_active = True).
        
        Args:
            user_id: User ID
        
        Returns:
            User: Updated user instance
        
        Raises:
            NotFoundError: If user not found
        """
        return self.update(user_id, {'is_active': True})
    
    def get_users_with_stats(self) -> List[dict]:
        """
        Retrieves users with statistics (order count, total spent).
        Uses a JOIN query for aggregated data.
        
        Returns:
            List[dict]: List of user statistics
        """
        query = """
            SELECT 
                u.id,
                u.email,
                u.name,
                u.is_active,
                u.created_at,
                u.last_login,
                COUNT(o.id) AS total_orders,
                COALESCE(SUM(o.total_amount), 0) AS total_spent
            FROM users u
            LEFT JOIN orders o ON o.user_id = u.id
            GROUP BY u.id
            ORDER BY u.id
        """
        
        try:
            from backend.config.database import db
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error fetching users with stats: {str(e)}")
            raise DatabaseError(f"Failed to fetch user stats: {str(e)}")