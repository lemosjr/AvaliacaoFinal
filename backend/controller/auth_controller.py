# backend/controller/auth_controller.py
"""
Authentication Controller.
Handles user registration, login, token refresh, and logout.
"""

import logging
from typing import Dict, Any

from backend.service.auth_service import AuthService
from backend.validation.user_validator import UserValidator
from backend.utils.exceptions import ValidationError, AuthenticationError, AppException
from backend.utils.jwt_utils import JWTUtils

logger = logging.getLogger(__name__)


class AuthController:
    """Controller for authentication-related operations."""

    def __init__(self):
        self.auth_service = AuthService()

    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            data: Dict with name, email, password, password_confirm

        Returns:
            Dict with user info and token

        Raises:
            ValidationError: If input data is invalid
            AppException: If registration fails
        """
        try:
            # 1. Validate input
            validated = UserValidator.validate_register(data)

            # 2. Call service
            user, token = self.auth_service.register_user(
                name=validated['name'],
                email=validated['email'],
                password=validated['password']
            )

            logger.info(f"User registered: {user.email} (ID: {user.id})")

            return {
                'success': True,
                'user': user.to_dict(),
                'token': token
            }

        except (ValidationError, AppException) as e:
            logger.warning(f"Registration failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            raise AppException("Registration failed due to internal error")

    def login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate a user and return token.

        Args:
            data: Dict with email and password

        Returns:
            Dict with user info and token

        Raises:
            ValidationError: If input data is invalid
            AuthenticationError: If credentials are incorrect
        """
        try:
            # 1. Validate input
            validated = UserValidator.validate_login(data)

            # 2. Call service
            user, token = self.auth_service.authenticate_user(
                email=validated['email'],
                password=validated['password']
            )

            logger.info(f"User logged in: {user.email} (ID: {user.id})")

            return {
                'success': True,
                'user': user.to_dict(),
                'token': token
            }

        except (ValidationError, AuthenticationError) as e:
            logger.warning(f"Login failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            raise AppException("Login failed due to internal error")

    def refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Refresh an existing token.

        Args:
            token: Current JWT token

        Returns:
            Dict with new token

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            new_token = JWTUtils.refresh_token(token)
            return {'success': True, 'token': new_token}
        except AuthenticationError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {str(e)}")
            raise AppException("Token refresh failed")

    def logout(self, token: str) -> Dict[str, Any]:
        """
        Logout user (invalidate token).

        In a stateless JWT system, logout is client-side.
        This method exists for completeness.
        """
        # JWT is stateless; we just return success
        logger.info("User logged out (client-side)")
        return {'success': True, 'message': 'Logged out successfully'}

    def get_current_user(self, token: str) -> Dict[str, Any]:
        """
        Get current user from token.

        Args:
            token: JWT token

        Returns:
            Dict with user info

        Raises:
            AuthenticationError: If token invalid
        """
        try:
            payload = JWTUtils.decode_token(token)
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationError("Invalid token: missing user_id")

            user = self.auth_service.get_user_by_id(user_id)
            if not user:
                raise AuthenticationError("User not found")

            return {'success': True, 'user': user.to_dict()}

        except AuthenticationError as e:
            logger.warning(f"Get current user failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user: {str(e)}")
            raise AppException("Failed to get current user")