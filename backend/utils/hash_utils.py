# backend/utils/hash_utils.py
"""
Password hashing utilities using bcrypt.
Provides secure password hashing and verification.
"""

import bcrypt
from typing import Optional


class HashUtils:
    """
    Utility class for password hashing and verification.
    Uses bcrypt with automatic salt generation and storage.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            str: Hashed password (includes salt)
        
        Example:
            hashed = HashUtils.hash_password("my_secret_password")
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Return as string (decoded from bytes)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifies a password against a hashed version.
        
        Args:
            password: Plain text password to check
            hashed: Hashed password stored in database
        
        Returns:
            bool: True if password matches, False otherwise
        
        Example:
            is_valid = HashUtils.verify_password("my_secret_password", stored_hash)
        """
        if not password or not hashed:
            return False
        
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except (ValueError, TypeError):
            # Invalid hash format
            return False
    
    @staticmethod
    def needs_rehash(hashed: str) -> bool:
        """
        Checks if a password hash needs to be rehashed
        (e.g., if bcrypt rounds have increased).
        
        Args:
            hashed: Hashed password
        
        Returns:
            bool: True if hash should be rehashed
        
        Example:
            if HashUtils.needs_rehash(user.password_hash):
                user.password_hash = HashUtils.hash_password(new_password)
        """
        try:
            return bcrypt.checkpw(hashed, hashed)
        except (ValueError, TypeError):
            # Invalid hash, needs rehash
            return True