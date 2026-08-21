# frontend/src/dialogs/confirmation_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from frontend.src.styles.dark_theme import DIALOG_STYLE, BTN_SECONDARY, BTN_DANGER, TEXT_PRIMARY


class ConfirmationDialog(QDialog):
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, title="Confirmar", message="Tem certeza?",
                 confirm_text="Confirmar", cancel_text="Cancelar",
                 icon="⚠️", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 180)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 25, 30, 20)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px; background: transparent;")
        top_layout.addWidget(icon_label)
        msg_label = QLabel(message)
        msg_label.setStyleSheet(f"font-size: 14px; color: {TEXT_PRIMARY}; background: transparent;")
        msg_label.setWordWrap(True)
        top_layout.addWidget(msg_label)
        main_layout.addLayout(top_layout)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton(cancel_text)
        self.cancel_btn.setStyleSheet(BTN_SECONDARY)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton(confirm_text)
        self.confirm_btn.setStyleSheet(BTN_DANGER)
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.setDefault(True)
        button_layout.addWidget(self.confirm_btn)

        main_layout.addLayout(button_layout)

        self.confirm_btn.clicked.connect(lambda: (self.confirmed.emit(), self.accept()))
        self.cancel_btn.clicked.connect(lambda: (self.cancelled.emit(), self.reject()))
