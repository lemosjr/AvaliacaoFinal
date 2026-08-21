# frontend/src/utils/__init__.py
"""
Utility modules for the frontend application.
Provides session management, event bus, formatters, constants, and validators.
"""

from frontend.src.utils.session_manager import SessionManager, session
from frontend.src.utils.event_bus import EventBus, event_bus
from frontend.src.utils.formatters import (
    format_currency,
    format_date,
    format_datetime,
    format_status,
    format_quantity,
    format_phone,
    format_cpf_cnpj,
    truncate_text,
    capitalize_words
)
from frontend.src.utils.constants import (
    APP_NAME,
    APP_VERSION,
    ORDER_STATUSES,
    STATUS_COLORS,
    STATUS_ICONS,
    PRODUCT_CATEGORIES,
    UI_SETTINGS
)
from frontend.src.utils.validators import (
    validate_email_frontend,
    validate_password_frontend,
    validate_required,
    validate_length,
    validate_positive_number
)

__all__ = [
    'SessionManager',
    'session',
    'EventBus',
    'event_bus',
    'format_currency',
    'format_date',
    'format_datetime',
    'format_status',
    'format_quantity',
    'format_phone',
    'format_cpf_cnpj',
    'truncate_text',
    'capitalize_words',
    'APP_NAME',
    'APP_VERSION',
    'ORDER_STATUSES',
    'STATUS_COLORS',
    'STATUS_ICONS',
    'PRODUCT_CATEGORIES',
    'UI_SETTINGS',
    'validate_email_frontend',
    'validate_password_frontend',
    'validate_required',
    'validate_length',
    'validate_positive_number'
]