# backend/utils/exceptions.py
"""
Custom exceptions for the application.
Provides meaningful error types for different scenarios.
"""

from typing import Optional, Any


class AppException(Exception):
    """
    Base exception for all application-specific errors.
    All custom exceptions should inherit from this.
    """
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.code = code or 'APP_ERROR'
        self.details = details
        super().__init__(message)
    
    def to_dict(self) -> dict:
        """Converts exception to dictionary for JSON responses."""
        return {
            'error': self.code,
            'message': self.message,
            'details': self.details
        }


class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code='VALIDATION_ERROR', details=details)


class AuthenticationError(AppException):
    """Raised when authentication fails (invalid credentials, expired token)."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, code='AUTHENTICATION_ERROR', details=details)


class AuthorizationError(AppException):
    """Raised when user lacks permission for an operation."""
    
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message, code='AUTHORIZATION_ERROR', details=details)


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, code='NOT_FOUND', details={'resource': resource, 'identifier': identifier})


class BusinessRuleError(AppException):
    """Raised when a business rule is violated."""
    
    def __init__(self, message: str, rule: Optional[str] = None, details: Optional[Any] = None):
        code = f'BUSINESS_RULE_{rule.upper()}' if rule else 'BUSINESS_RULE'
        super().__init__(message, code=code, details=details)


class DatabaseError(AppException):
    """Raised for database-related errors."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code='DATABASE_ERROR', details=details)


class StateError(BusinessRuleError):
    """Raised when an operation is incompatible with the current state."""
    
    def __init__(self, message: str, current_state: str, operation: str):
        details = {
            'current_state': current_state,
            'attempted_operation': operation
        }
        super().__init__(
            message,
            rule='INVALID_STATE',
            details=details
        )