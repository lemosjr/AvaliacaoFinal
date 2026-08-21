# backend/utils/__init__.py
"""
Utility modules for the application.
Provides logging, exceptions, hashing, JWT, and validation helpers.
"""

from backend.utils.logger import setup_logging, logger
from backend.utils.exceptions import (
    AppException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    BusinessRuleError,
    DatabaseError,
    StateError
)
from backend.utils.hash_utils import HashUtils
from backend.utils.jwt_utils import JWTUtils
from backend.utils.validators import (
    validate_email,
    validate_password_strength,
    validate_positive_number,
    validate_non_empty_string,
    validate_quantity,
    validate_price
)

__all__ = [
    'setup_logging',
    'logger',
    'AppException',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'NotFoundError',
    'BusinessRuleError',
    'HashUtils',
    'JWTUtils',
    'validate_email',
    'validate_password_strength',
    'validate_positive_number',
    'validate_non_empty_string',
    'validate_quantity',
    'validate_price'
]