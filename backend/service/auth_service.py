# backend/service/auth_service.py
"""
Authentication service handles user registration, login, and token management.
"""

from typing import Optional, Tuple
from backend.repository.user_repository import UserRepository
from backend.utils.hash_utils import HashUtils
from backend.utils.jwt_utils import JWTUtils
from backend.utils.exceptions import AuthenticationError, ValidationError
from backend.service.validation_service import ValidationService
from backend.model.user_model import User
from backend.utils.logger import logger


class AuthService:
    """
    Service for authentication and user management.
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.validator = ValidationService()

    def register(self, email: str, password: str, name: str) -> User:
        """
        Registers a new user.
        """
        # Validate input
        validated = self.validator.validate_user_registration(email, password, name)
        
        # Check if email already exists
        existing = self.user_repo.get_by_email(validated['email'])
        if existing:
            raise ValidationError("Email already registered")
        
        # Hash password
        password_hash = HashUtils.hash_password(validated['password'])
        
        # Create user
        user = User(
            email=validated['email'],
            password_hash=password_hash,
            name=validated['name']
        )
        
        created = self.user_repo.create(user)
        logger.info(f"User registered: {created.email}")
        return created

    def authenticate(self, email: str, password: str) -> Tuple[User, str]:
        """
        Authenticates a user and returns (user, token).
        """
        if not email or not password:
            raise AuthenticationError("Email and password are required")
        
        # Find user
        user = self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        if not user.is_active:
            raise AuthenticationError("Account is inactive")
        
        # Verify password
        if not HashUtils.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        
        # Generate JWT
        token = JWTUtils.generate_token(user.id, user.email)
        
        # Update last login
        self.user_repo.update_last_login(user.id)
        
        logger.info(f"User authenticated: {user.email}")
        return user, token

    def validate_token(self, token: str) -> dict:
        """
        Validates a JWT token and returns the payload.
        """
        return JWTUtils.decode_token(token)

    def get_user_from_token(self, token: str) -> User:
        """
        Gets user from token.
        """
        payload = self.validate_token(token)
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationError("Invalid token: missing user_id")
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("Account is inactive")
        
        return user

    def refresh_token(self, token: str) -> str:
        """
        Refreshes an existing token.
        """
        payload = JWTUtils.decode_token(token)
        user_id = payload.get('user_id')
        email = payload.get('email')
        
        if not user_id or not email:
            raise AuthenticationError("Invalid token payload")
        
        # Generate new token
        return JWTUtils.generate_token(user_id, email)