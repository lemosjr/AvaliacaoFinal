# backend/middleware/auth_middleware.py
"""
Authentication middleware for protecting API routes.
Validates JWT tokens and extracts user information.
"""

import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps

from backend.utils.jwt_utils import JWTUtils
from backend.utils.exceptions import AuthenticationError, AuthorizationError
from backend.service.auth_service import AuthService

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """
    Authentication middleware for protecting routes.
    Validates JWT tokens and adds user context.
    """

    def __init__(self):
        self.auth_service = AuthService()

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validates a JWT token and returns user info.

        Args:
            token: JWT token string

        Returns:
            Dict with user_id, email, and additional claims

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = JWTUtils.decode_token(token)
            user_id = payload.get('user_id')
            email = payload.get('email')

            if not user_id or not email:
                raise AuthenticationError("Invalid token payload")

            # Optionally verify user still exists and is active
            user = self.auth_service.get_user_by_id(user_id)
            if not user:
                raise AuthenticationError("User not found")

            if not user.is_active:
                raise AuthenticationError("User is inactive")

            return {
                'user_id': user_id,
                'email': email,
                'is_admin': payload.get('is_admin', False),
                'payload': payload
            }

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise AuthenticationError("Invalid token")

    def require_auth(self, func: Callable) -> Callable:
        """
        Decorator for routes that require authentication.
        Extracts token from request context and validates it.

        Usage:
            @auth_middleware.require_auth
            def protected_route(request, context):
                user_id = context['user_id']
                # ... route logic
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get token from request (adapt to your framework)
            # This is a generic implementation; adapt for Flask/FastAPI/PyQt
            request = kwargs.get('request') or args[0] if args else None
            if not request:
                raise AuthenticationError("No request context provided")

            # Extract token from headers (Flask style)
            token = self._extract_token_from_request(request)
            if not token:
                raise AuthenticationError("Authorization token required")

            try:
                user_data = self.validate_token(token)
                kwargs['auth_context'] = user_data
                return func(*args, **kwargs)
            except AuthenticationError as e:
                logger.warning(f"Authentication failed: {str(e)}")
                raise

        return wrapper

    def _extract_token_from_request(self, request) -> Optional[str]:
        """
        Extracts JWT token from request headers.
        Adapt this method based on your framework.

        For Flask: request.headers.get('Authorization')
        For FastAPI: request.headers.get('Authorization')
        For PyQt: can be adapted differently
        """
        # Flask/FastAPI style
        if hasattr(request, 'headers'):
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                return auth_header[7:]
        return None

    def require_admin(self, func: Callable) -> Callable:
        """
        Decorator for routes that require admin privileges.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_context = kwargs.get('auth_context')
            if not auth_context:
                raise AuthenticationError("Authentication required")

            if not auth_context.get('is_admin', False):
                raise AuthorizationError("Admin privileges required")

            return func(*args, **kwargs)
        return wrapper

    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Public method to get user info from token (without raising exception).
        """
        try:
            return self.validate_token(token)
        except AuthenticationError:
            return None