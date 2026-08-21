# backend/utils/jwt_utils.py
"""
JWT (JSON Web Token) utilities for authentication.
Handles token generation, validation, and decoding.
"""

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import datetime
from typing import Dict, Any, Optional

from backend.config.settings import Settings
from backend.utils.exceptions import AuthenticationError


class JWTUtils:
    """
    Utility class for JWT operations.
    Uses HS256 algorithm with configured secret key.
    """
    
    @staticmethod
    def generate_token(user_id: int, email: str, additional_claims: Optional[Dict] = None) -> str:
        """
        Generates a JWT token for a user.
        
        Args:
            user_id: User ID
            email: User email
            additional_claims: Optional extra payload data
        
        Returns:
            str: JWT token string
        
        Example:
            token = JWTUtils.generate_token(123, "user@email.com", {"role": "admin"})
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Settings.JWT_EXPIRATION_HOURS)
        }
        
        # Add additional claims if provided
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, Settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodes and validates a JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            dict: Decoded payload
        
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def get_user_id_from_token(token: str) -> int:
        """
        Extracts user ID from a validated token.
        
        Args:
            token: JWT token string
        
        Returns:
            int: User ID
        
        Raises:
            AuthenticationError: If token is invalid
        """
        payload = JWTUtils.decode_token(token)
        user_id = payload.get('user_id')
        
        if not user_id:
            raise AuthenticationError("Token does not contain user_id")
        
        return user_id
    
    @staticmethod
    def get_email_from_token(token: str) -> str:
        """
        Extracts email from a validated token.
        
        Args:
            token: JWT token string
        
        Returns:
            str: User email
        
        Raises:
            AuthenticationError: If token is invalid
        """
        payload = JWTUtils.decode_token(token)
        email = payload.get('email')
        
        if not email:
            raise AuthenticationError("Token does not contain email")
        
        return email
    
    @staticmethod
    def refresh_token(token: str) -> str:
        """
        Refreshes an existing token (generates a new one).
        
        Args:
            token: Current JWT token (must be valid)
        
        Returns:
            str: New JWT token
        
        Raises:
            AuthenticationError: If token is invalid
        """
        payload = JWTUtils.decode_token(token)
        user_id = payload.get('user_id')
        email = payload.get('email')
        
        if not user_id or not email:
            raise AuthenticationError("Invalid token payload")
        
        # Remove expiration so we can generate a new one
        payload.pop('exp', None)
        payload.pop('iat', None)
        
        return JWTUtils.generate_token(user_id, email, payload)
    
    @staticmethod
    def is_token_valid(token: str) -> bool:
        """
        Checks if a token is valid without raising exceptions.
        
        Args:
            token: JWT token string
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            JWTUtils.decode_token(token)
            return True
        except AuthenticationError:
            return False