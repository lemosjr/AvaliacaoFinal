# backend/service/state_service.py
"""
State management service for orders.
Handles state transitions and validations.
"""

from typing import Dict, List, Optional
from backend.model.order_model import Order
from backend.utils.exceptions import BusinessRuleError, StateError


class StateService:
    """
    Manages order states and transitions.
    States: created, processing, completed, cancelled
    """

    # Allowed transitions
    TRANSITIONS = {
        'created': ['processing', 'cancelled'],
        'processing': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': []
    }

    # Human-readable state names
    STATE_LABELS = {
        'created': 'Created',
        'processing': 'Processing',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }

    # Operations allowed in each state
    ALLOWED_OPERATIONS = {
        'created': ['add_item', 'remove_item', 'update_item', 'change_status', 'calculate_total'],
        'processing': ['add_item', 'remove_item', 'update_item', 'change_status', 'calculate_total'],
        'completed': ['view', 'calculate_total'],  # read-only
        'cancelled': ['view']  # read-only
    }

    @classmethod
    def can_transition(cls, current_status: str, new_status: str) -> bool:
        """
        Checks if a status transition is allowed.
        """
        if current_status not in cls.TRANSITIONS:
            return False
        return new_status in cls.TRANSITIONS[current_status]

    @classmethod
    def get_allowed_operations(cls, status: str) -> List[str]:
        """
        Returns list of operations allowed for a given status.
        """
        return cls.ALLOWED_OPERATIONS.get(status, [])

    @classmethod
    def validate_transition(cls, current_status: str, new_status: str) -> None:
        """
        Validates transition, raises StateError if invalid.
        """
        if not cls.can_transition(current_status, new_status):
            raise StateError(
                f"Cannot transition from '{cls.STATE_LABELS[current_status]}' to '{cls.STATE_LABELS[new_status]}'",
                current_state=current_status,
                operation=f"change_status_to_{new_status}"
            )

    @classmethod
    def validate_operation(cls, status: str, operation: str) -> None:
        """
        Validates if an operation is allowed in the current state.
        """
        allowed = cls.get_allowed_operations(status)
        if operation not in allowed:
            raise StateError(
                f"Operation '{operation}' not allowed in '{cls.STATE_LABELS[status]}' state",
                current_state=status,
                operation=operation
            )

    @classmethod
    def get_next_statuses(cls, current_status: str) -> List[str]:
        """
        Returns list of possible next statuses.
        """
        return cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def get_status_label(cls, status: str) -> str:
        """
        Returns human-readable label for a status.
        """
        return cls.STATE_LABELS.get(status, status)

    @classmethod
    def is_final_status(cls, status: str) -> bool:
        """
        Checks if status is final (completed or cancelled).
        """
        return status in ['completed', 'cancelled']

    @classmethod
    def is_active_status(cls, status: str) -> bool:
        """
        Checks if status is active (created or processing).
        """
        return status in ['created', 'processing']