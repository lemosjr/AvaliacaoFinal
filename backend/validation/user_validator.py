# backend/validation/user_validator.py
"""
Validator for User entity.
Handles validation of user registration, login, and profile updates.
"""

from typing import Optional, Dict, Any
from backend.utils.validators import (
    validate_email,
    validate_password_strength,
    validate_non_empty_string,
    validate_length
)
from backend.utils.exceptions import ValidationError


class UserValidator:
    """Validation methods for User operations."""

    @staticmethod
    def validate_register(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates user registration data.

        Required fields:
            - name: non-empty string, max 100 chars
            - email: valid email format
            - password: strong password (min 8 chars, with number, uppercase, lowercase)
            - password_confirm: must match password

        Args:
            data: Dictionary with registration data

        Returns:
            Dict with validated and sanitized data

        Raises:
            ValidationError: If any field is invalid
        """
        errors = []

        # Extract fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')

        # Validate name
        try:
            name = validate_non_empty_string(name, 'Name')
            name = validate_length(name, 2, 100, 'Name')
        except ValueError as e:
            errors.append(str(e))

        # Validate email
        try:
            email = validate_email(email)
        except ValueError as e:
            errors.append(str(e))

        # Validate password
        try:
            password = validate_password_strength(password)
        except ValueError as e:
            errors.append(str(e))

        # Validate password confirmation
        if password and password_confirm:
            if password != password_confirm:
                errors.append("Password and confirmation do not match")
        else:
            if not password_confirm:
                errors.append("Password confirmation is required")

        if errors:
            raise ValidationError("Validation failed for registration", details=errors)

        return {
            'name': name,
            'email': email,
            'password': password
        }

    @staticmethod
    def validate_login(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates login credentials.

        Args:
            data: Dictionary with email and password

        Returns:
            Dict with validated email and password

        Raises:
            ValidationError: If fields are missing or invalid
        """
        email = data.get('email', '').strip()
        password = data.get('password', '')

        errors = []

        try:
            email = validate_email(email)
        except ValueError as e:
            errors.append(str(e))

        if not password:
            errors.append("Password is required")

        if errors:
            raise ValidationError("Invalid login credentials", details=errors)

        return {
            'email': email,
            'password': password
        }

    @staticmethod
    def validate_update(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates user profile update.

        Only validates fields that are present.
        """
        validated = {}
        errors = []

        # Validate name if provided
        if 'name' in data:
            try:
                name = validate_non_empty_string(data['name'], 'Name')
                name = validate_length(name, 2, 100, 'Name')
                validated['name'] = name
            except ValueError as e:
                errors.append(str(e))

        # Validate email if provided
        if 'email' in data:
            try:
                validated['email'] = validate_email(data['email'])
            except ValueError as e:
                errors.append(str(e))

        # Validate password if provided
        if 'password' in data and data['password']:
            try:
                validated['password'] = validate_password_strength(data['password'])
            except ValueError as e:
                errors.append(str(e))

        if errors:
            raise ValidationError("Validation failed for update", details=errors)

        return validated

    @staticmethod
    def validate_email_exists(email: str) -> str:
        """
        Validates that an email is not empty and is in correct format.
        """
        return validate_email(email)