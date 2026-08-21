# frontend/src/widgets/search_bar.py
"""
Search Bar Widget - Componente de busca reutilizável.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon

class SearchBar(QWidget):
    """
    Barra de pesquisa com campo de texto e botão.
    Emite um sinal quando a pesquisa é acionada.
    """

    # Sinal emitido quando a pesquisa é solicitada
    search_requested = pyqtSignal(str)

    # Sinal emitido quando o texto do campo é alterado
    text_changed = pyqtSignal(str)

    # Sinal emitido quando a pesquisa é limpa
    cleared = pyqtSignal()

    def __init__(self, placeholder: str = "Pesquisar...", parent=None):
        super().__init__(parent)

        self.setup_ui(placeholder)
        self.setup_connections()

    def setup_ui(self, placeholder: str):
        """Configura a interface do widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Campo de entrada
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.setMinimumHeight(32)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                padding: 6px 12px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.search_input, 1)

        # Botão de busca
        self.search_button = QPushButton("🔍")
        self.search_button.setFixedSize(34, 34)
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.setToolTip("Pesquisar")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        layout.addWidget(self.search_button)

        # Botão de limpar (opcional)
        self.clear_button = QPushButton("✕")
        self.clear_button.setFixedSize(34, 34)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setToolTip("Limpar")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        layout.addWidget(self.clear_button)

        # Esconde o botão limpar inicialmente
        self.clear_button.hide()

    def setup_connections(self):
        """Conecta os sinais."""
        # Botão de busca
        self.search_button.clicked.connect(self.emit_search)

        # Enter no campo de entrada
        self.search_input.returnPressed.connect(self.emit_search)

        # Texto alterado
        self.search_input.textChanged.connect(self.on_text_changed)

        # Botão limpar
        self.clear_button.clicked.connect(self.clear_search)

    def emit_search(self):
        """Emite o sinal de pesquisa com o texto atual."""
        text = self.search_input.text().strip()
        self.search_requested.emit(text)

    def on_text_changed(self, text: str):
        """Manipula mudança de texto no campo."""
        # Mostra/esconde botão limpar
        if text.strip():
            self.clear_button.show()
        else:
            self.clear_button.hide()

        # Emite sinal de texto alterado
        self.text_changed.emit(text)

    def clear_search(self):
        """Limpa o campo de pesquisa."""
        self.search_input.clear()
        self.clear_button.hide()
        self.cleared.emit()
        # Emite sinal de pesquisa vazia
        self.search_requested.emit("")

    def set_text(self, text: str):
        """Define o texto do campo de pesquisa."""
        self.search_input.setText(text)

    def text(self) -> str:
        """Retorna o texto atual."""
        return self.search_input.text().strip()

    def set_placeholder(self, text: str):
        """Define o texto placeholder."""
        self.search_input.setPlaceholderText(text)

    def clear(self):
        """Limpa o campo."""
        self.clear_search()