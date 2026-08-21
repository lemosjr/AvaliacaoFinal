# frontend/src/dialogs/message_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from frontend.src.styles.dark_theme import DIALOG_STYLE, TEXT_PRIMARY


class MessageDialog(QDialog):
    def __init__(self, title="Mensagem", message="", message_type="info", button_text="OK", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 180)
        self.setStyleSheet(DIALOG_STYLE)

        icons = {'info': ('ℹ️', '#3498db'), 'success': ('✅', '#2ecc71'),
                 'warning': ('⚠️', '#f39c12'), 'error': ('❌', '#e74c3c')}
        icon, color = icons.get(message_type, ('📌', '#95a5a6'))

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 25, 30, 20)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px; background: transparent;")
        top_layout.addWidget(icon_label)
        msg_label = QLabel(message)
        msg_label.setStyleSheet(f"font-size: 14px; color: {color}; background: transparent;")
        msg_label.setWordWrap(True)
        top_layout.addWidget(msg_label)
        main_layout.addLayout(top_layout)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_btn = QPushButton(button_text)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    @staticmethod
    def show_info(title, message, parent=None):
        return MessageDialog(title, message, 'info', parent=parent).exec()

    @staticmethod
    def show_success(title, message, parent=None):
        return MessageDialog(title, message, 'success', parent=parent).exec()

    @staticmethod
    def show_warning(title, message, parent=None):
        return MessageDialog(title, message, 'warning', parent=parent).exec()

    @staticmethod
    def show_error(title, message, parent=None):
        return MessageDialog(title, message, 'error', parent=parent).exec()
