# frontend/src/__init__.py
"""
Frontend package - Main application windows, widgets, dialogs and utilities.
"""

from frontend.src.main_window import MainWindow
from frontend.src.login_window import LoginWindow
from frontend.src.register_window import RegisterWindow

__all__ = [
    'MainWindow',
    'LoginWindow',
    'RegisterWindow'
]