# backend/model/user_model.py
"""
User model representing system users.
Contains authentication and profile information.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class User:
    """
    User entity representing a system user.
    
    Attributes:
        id: Unique identifier
        email: User's email (unique)
        password_hash: Hashed password (bcrypt)
        name: User's full name
        active: Whether the account is active
        created_at: Account creation timestamp
        last_login: Last login timestamp
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        email: str = '',
        password_hash: str = '',
        name: str = '',
        active: bool = True,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.active = active
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts user to dictionary.
        Excludes password_hash for security.
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def to_dict_with_hash(self) -> Dict[str, Any]:
        """
        Converts user to dictionary including password_hash.
        Use with caution - only for internal operations.
        """
        data = self.to_dict()
        data['password_hash'] = self.password_hash
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Creates a User instance from a dictionary.
        """
        return cls(
            id=data.get('id'),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            name=data.get('name', ''),
            active=data.get('active', True),
            created_at=data.get('created_at'),
            last_login=data.get('last_login')
        )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.email})"