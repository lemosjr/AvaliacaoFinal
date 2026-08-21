# backend/utils/validators.py
"""
Common validation functions used across the application.
Provides reusable validation logic for input data.
"""

import re
from typing import Any, Optional, Union


def validate_non_empty_string(value: Any, field_name: str = "Field") -> str:
    """
    Validates that a value is a non-empty string.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for error message)
    
    Returns:
        str: The validated string
    
    Raises:
        ValueError: If value is empty or not a string
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    
    return value


def validate_email(email: str) -> str:
    """
    Validates an email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        str: The validated email (lowercased)
    
    Raises:
        ValueError: If email format is invalid
    """
    email = validate_non_empty_string(email, "Email")
    
    # Simple but robust email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: {email}")
    
    return email.lower()


def validate_password_strength(password: str, min_length: int = 8) -> str:
    """
    Validates password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum length required
    
    Returns:
        str: The validated password
    
    Raises:
        ValueError: If password is too weak
    """
    password = validate_non_empty_string(password, "Password")
    
    if len(password) < min_length:
        raise ValueError(f"Password must be at least {min_length} characters")
    
    # Optional: Add more strength checks if needed
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one number")
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    return password


def validate_positive_number(value: Union[int, float], field_name: str = "Value") -> Union[int, float]:
    """
    Validates that a number is positive (> 0).
    
    Args:
        value: Number to validate
        field_name: Name of the field (for error message)
    
    Returns:
        Union[int, float]: The validated number
    
    Raises:
        ValueError: If value is not positive
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero")
    
    return value


def validate_non_negative_number(value: Union[int, float], field_name: str = "Value") -> Union[int, float]:
    """
    Validates that a number is non-negative (>= 0).
    
    Args:
        value: Number to validate
        field_name: Name of the field (for error message)
    
    Returns:
        Union[int, float]: The validated number
    
    Raises:
        ValueError: If value is negative
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")
    
    return value


def validate_price(price: Union[int, float]) -> float:
    """
    Validates a price value (must be > 0 and have at most 2 decimals).
    
    Args:
        price: Price value to validate
    
    Returns:
        float: The validated price (rounded to 2 decimals)
    
    Raises:
        ValueError: If price is invalid
    """
    price = float(validate_positive_number(price, "Price"))
    
    # Check for more than 2 decimal places
    if round(price, 2) != price:
        raise ValueError("Price must have at most 2 decimal places")
    
    return round(price, 2)


def validate_quantity(quantity: int) -> int:
    """
    Validates a quantity value (must be > 0 and integer).
    
    Args:
        quantity: Quantity to validate
    
    Returns:
        int: The validated quantity
    
    Raises:
        ValueError: If quantity is invalid
    """
    if not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer")
    
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")
    
    return quantity


def validate_enum_value(value: str, valid_values: list, field_name: str = "Field") -> str:
    """
    Validates that a value is in a predefined list of valid values.
    
    Args:
        value: Value to validate
        valid_values: List of allowed values
        field_name: Name of the field (for error message)
    
    Returns:
        str: The validated value (lowercased)
    
    Raises:
        ValueError: If value is not in the allowed list
    """
    value = validate_non_empty_string(value, field_name)
    value_lower = value.lower()
    
    if value_lower not in [v.lower() for v in valid_values]:
        raise ValueError(
            f"{field_name} must be one of: {', '.join(valid_values)}. Got: {value}"
        )
    
    return value_lower


def validate_length(value: str, min_length: int, max_length: int, field_name: str = "Field") -> str:
    """
    Validates that a string length is within bounds.
    
    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length
        field_name: Name of the field (for error message)
    
    Returns:
        str: The validated string (trimmed)
    
    Raises:
        ValueError: If length is out of bounds
    """
    value = validate_non_empty_string(value, field_name)
    
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters")
    
    if len(value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters")
    
    return value