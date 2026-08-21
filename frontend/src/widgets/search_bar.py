# frontend/src/widgets/search_bar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from frontend.src.styles.dark_theme import DARK_INPUT, DARK_BORDER, TEXT_PRIMARY, TEXT_MUTED, ACCENT, ACCENT_HOVER, DANGER


class SearchBar(QWidget):
    search_requested = pyqtSignal(str)
    text_changed = pyqtSignal(str)
    cleared = pyqtSignal()

    def __init__(self, placeholder="Pesquisar...", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.setMinimumHeight(32)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {DARK_BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                background-color: {DARK_INPUT};
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 2px solid {ACCENT}; }}
            QLineEdit::placeholder {{ color: {TEXT_MUTED}; }}
        """)
        layout.addWidget(self.search_input, 1)

        self.search_button = QPushButton("🔍")
        self.search_button.setFixedSize(34, 34)
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.setStyleSheet(f"""
            QPushButton {{ background-color: {ACCENT}; border: none; border-radius: 6px; color: white; font-size: 14px; }}
            QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
        """)
        layout.addWidget(self.search_button)

        self.clear_button = QPushButton("✕")
        self.clear_button.setFixedSize(34, 34)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setStyleSheet(f"""
            QPushButton {{ background-color: {DANGER}; border: none; border-radius: 6px; color: white; font-size: 14px; }}
            QPushButton:hover {{ background-color: #c0392b; }}
        """)
        layout.addWidget(self.clear_button)
        self.clear_button.hide()

        self.search_button.clicked.connect(self.emit_search)
        self.search_input.returnPressed.connect(self.emit_search)
        self.search_input.textChanged.connect(self.on_text_changed)
        self.clear_button.clicked.connect(self.clear_search)

    def emit_search(self):
        self.search_requested.emit(self.search_input.text().strip())

    def on_text_changed(self, text):
        self.clear_button.setVisible(bool(text.strip()))
        self.text_changed.emit(text)

    def clear_search(self):
        self.search_input.clear()
        self.clear_button.hide()
        self.cleared.emit()
        self.search_requested.emit("")

    def set_text(self, text):
        self.search_input.setText(text)

    def text(self):
        return self.search_input.text().strip()

    def set_placeholder(self, text):
        self.search_input.setPlaceholderText(text)

    def clear(self):
        self.clear_search()
