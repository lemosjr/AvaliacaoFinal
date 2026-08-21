# frontend/src/widgets/order_widget.py
"""
Order Widget - Exibe informações de um pedido em formato de card.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from frontend.src.widgets.status_badge import StatusBadge
from frontend.src.utils.formatters import format_currency, format_date


class OrderWidget(QFrame):
    """
    Widget em formato de card para exibir um pedido.
    """

    # Sinal emitido quando o pedido é clicado
    order_clicked = pyqtSignal(dict)

    def __init__(self, order_data: dict, parent=None):
        super().__init__(parent)

        self.order_data = order_data
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Configura a interface do card."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # ===== CABEÇALHO: ID + STATUS =====
        header_layout = QHBoxLayout()

        id_label = QLabel(f"Pedido #{self.order_data.get('id', 'N/A')}")
        id_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(id_label)

        header_layout.addStretch()

        # Status badge
        status = self.order_data.get('status', 'created')
        badge = StatusBadge(status)
        header_layout.addWidget(badge)

        layout.addLayout(header_layout)

        # ===== CLIENTE =====
        customer = self.order_data.get('customer', 'Cliente')
        customer_label = QLabel(f"👤 {customer}")
        customer_label.setStyleSheet("font-size: 14px; color: #34495e;")
        layout.addWidget(customer_label)

        # ===== TOTAL =====
        total = self.order_data.get('total_amount', 0)
        total_label = QLabel(format_currency(total))
        total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        layout.addWidget(total_label)

        # ===== DATA =====
        created_at = self.order_data.get('created_at', '')
        date_label = QLabel(f"📅 {format_date(created_at)}")
        date_label.setStyleSheet("font-size: 11px; color: #95a5a6;")
        layout.addWidget(date_label)

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

        # Define tamanho
        self.setFixedSize(260, 220)

    def apply_styles(self):
        """Aplica estilos ao widget."""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #3498db;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)

    def _on_click(self):
        """Emite sinal quando o card é clicado."""
        self.order_clicked.emit(self.order_data)