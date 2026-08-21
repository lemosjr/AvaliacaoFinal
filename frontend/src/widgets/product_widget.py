# frontend/src/widgets/product_widget.py
"""
Product Widget - Exibe informações de um produto em formato de card.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from frontend.src.utils.formatters import format_currency


class ProductWidget(QFrame):
    """
    Widget em formato de card para exibir um produto.
    """

    # Sinal emitido quando o produto é clicado
    product_clicked = pyqtSignal(dict)

    def __init__(self, product_data: dict, parent=None):
        super().__init__(parent)

        self.product_data = product_data
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Configura a interface do card."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # ===== NOME DO PRODUTO =====
        name_label = QLabel(self.product_data.get('description', 'Produto'))
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ecf0f1;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # ===== PREÇO =====
        price = self.product_data.get('price', 0)
        price_label = QLabel(format_currency(price))
        price_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60;")
        layout.addWidget(price_label)

        # ===== ESTOQUE =====
        stock = self.product_data.get('quantity_available', 0)
        stock_color = "#2ecc71" if stock > 10 else "#f39c12" if stock > 0 else "#e74c3c"
        stock_label = QLabel(f"📦 Estoque: {stock} unidades")
        stock_label.setStyleSheet(f"font-size: 12px; color: {stock_color};")
        layout.addWidget(stock_label)

        # ===== ID =====
        id_label = QLabel(f"ID: #{self.product_data.get('id', 'N/A')}")
        id_label.setStyleSheet("font-size: 11px; color: #95a5a6;")
        layout.addWidget(id_label)

        # ===== BOTÃO DE AÇÃO =====
        self.action_button = QPushButton("Ver detalhes")
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.action_button.clicked.connect(self._on_click)
        layout.addWidget(self.action_button)

        # Define tamanho fixo
        self.setFixedSize(220, 200)

    def apply_styles(self):
        """Aplica estilos ao widget."""
        self.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 1px solid #4a6278;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #3498db;
            }
        """)

    def _on_click(self):
        """Emite sinal quando o card é clicado."""
        self.product_clicked.emit(self.product_data)