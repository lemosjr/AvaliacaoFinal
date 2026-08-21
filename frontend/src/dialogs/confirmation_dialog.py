# frontend/src/dialogs/confirmation_dialog.py
"""
Generic confirmation dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class ConfirmationDialog(QDialog):
    """
    Generic confirmation dialog with custom message and buttons.
    Emits 'confirmed' or 'cancelled' signals.
    """

    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, title: str = "Confirmar",
                 message: str = "Tem certeza?",
                 confirm_text: str = "Confirmar",
                 cancel_text: str = "Cancelar",
                 icon: str = "⚠️",
                 parent=None):
        super().__init__(parent)

        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.icon = icon

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setModal(True)
        self.setFixedSize(400, 180)
        self.setMinimumSize(350, 150)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 25, 30, 20)

        # Icon and message
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 32px;")
        top_layout.addWidget(icon_label)

        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        msg_label.setWordWrap(True)
        top_layout.addWidget(msg_label)

        main_layout.addLayout(top_layout)

        main_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton(self.cancel_text)
        self.cancel_btn.setStyleSheet(self._button_style(secondary=True))
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton(self.confirm_text)
        self.confirm_btn.setStyleSheet(self._button_style())
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.setDefault(True)
        button_layout.addWidget(self.confirm_btn)

        main_layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

    def setup_connections(self):
        self.confirm_btn.clicked.connect(self._on_confirm)
        self.cancel_btn.clicked.connect(self._on_cancel)

    def _on_confirm(self):
        self.confirmed.emit()
        self.accept()

    def _on_cancel(self):
        self.cancelled.emit()
        self.reject()

    def _button_style(self, secondary: bool = False) -> str:
        if secondary:
            return """
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
            """
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """