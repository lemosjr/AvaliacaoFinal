# frontend/src/widgets/status_badge.py
"""
Status Badge - Exibe status com cores e ícones.
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette


class StatusBadge(QLabel):
    """
    Widget para exibir status com cores e ícones.
    """

    STATUS_COLORS = {
        'created': ('#f39c12', '🆕'),      # Amarelo
        'processing': ('#3498db', '🔄'),   # Azul
        'completed': ('#2ecc71', '✅'),    # Verde
        'cancelled': ('#e74c3c', '❌'),    # Vermelho
    }

    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.set_status(status)

    def set_status(self, status: str):
        """Define o status e atualiza a aparência."""
        status_lower = status.lower()
        color, icon = self.STATUS_COLORS.get(status_lower, ('#95a5a6', '❓'))

        # Define texto com ícone
        self.setText(f"{icon} {status.capitalize()}")

        # Define estilo
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)