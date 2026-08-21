# frontend/src/dialogs/message_dialog.py
"""
Generic message dialog for displaying success, error, info, or warning messages.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal


class MessageDialog(QDialog):
    """
    Simple dialog to display a message with an icon and button.
    """

    def __init__(self, title: str = "Mensagem",
                 message: str = "",
                 message_type: str = "info",  # info, success, warning, error
                 button_text: str = "OK",
                 parent=None):
        super().__init__(parent)

        self.title = title
        self.message = message
        self.message_type = message_type
        self.button_text = button_text

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setModal(True)
        self.setFixedSize(400, 180)
        self.setMinimumSize(350, 150)

        # Icon mapping
        icons = {
            'info': ('ℹ️', '#3498db'),
            'success': ('✅', '#2ecc71'),
            'warning': ('⚠️', '#f39c12'),
            'error': ('❌', '#e74c3c')
        }
        icon, color = icons.get(self.message_type, ('📌', '#7f8c8d'))

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 25, 30, 20)

        # Icon and message
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 36px;")
        top_layout.addWidget(icon_label)

        msg_label = QLabel(self.message)
        msg_label.setStyleSheet(f"font-size: 14px; color: {color};")
        msg_label.setWordWrap(True)
        top_layout.addWidget(msg_label)

        main_layout.addLayout(top_layout)

        main_layout.addStretch()

        # Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_btn = QPushButton(self.button_text)
        self.ok_btn.setStyleSheet(self._button_style())
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

    def setup_connections(self):
        self.ok_btn.clicked.connect(self.accept)

    def _button_style(self) -> str:
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """

    @staticmethod
    def show_info(title: str, message: str, parent=None):
        """Show an info dialog."""
        dialog = MessageDialog(title, message, 'info', parent=parent)
        return dialog.exec()

    @staticmethod
    def show_success(title: str, message: str, parent=None):
        """Show a success dialog."""
        dialog = MessageDialog(title, message, 'success', parent=parent)
        return dialog.exec()

    @staticmethod
    def show_warning(title: str, message: str, parent=None):
        """Show a warning dialog."""
        dialog = MessageDialog(title, message, 'warning', parent=parent)
        return dialog.exec()

    @staticmethod
    def show_error(title: str, message: str, parent=None):
        """Show an error dialog."""
        dialog = MessageDialog(title, message, 'error', parent=parent)
        return dialog.exec()