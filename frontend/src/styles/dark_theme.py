"""Dark theme constants and shared stylesheet for all dialogs/widgets."""

DARK_BG      = "#1e2a38"
DARK_CARD    = "#2c3e50"
DARK_INPUT   = "#34495e"
DARK_BORDER  = "#4a6278"
TEXT_PRIMARY = "#ecf0f1"
TEXT_MUTED   = "#95a5a6"
ACCENT       = "#3498db"
ACCENT_HOVER = "#2980b9"
SUCCESS      = "#2ecc71"
DANGER       = "#e74c3c"

DIALOG_STYLE = f"""
    QDialog, QWidget {{
        background-color: {DARK_CARD};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", Arial, sans-serif;
    }}
    QLabel {{
        color: {TEXT_PRIMARY};
        background: transparent;
    }}
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {DARK_INPUT};
        border: 2px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        color: {TEXT_PRIMARY};
        font-size: 14px;
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 2px solid {ACCENT};
    }}
    QLineEdit::placeholder {{ color: {TEXT_MUTED}; }}
    QComboBox::drop-down {{ border: none; }}
    QComboBox QAbstractItemView {{
        background-color: {DARK_INPUT};
        color: {TEXT_PRIMARY};
        selection-background-color: {ACCENT};
    }}
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        background-color: {DARK_BORDER};
        border: none;
        width: 16px;
    }}
    QPushButton {{
        background-color: {ACCENT};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:pressed {{ background-color: #1c6ea4; }}
    QPushButton:disabled {{ background-color: {DARK_BORDER}; color: {TEXT_MUTED}; }}
    QTableWidget {{
        background-color: {DARK_INPUT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        gridline-color: {DARK_BORDER};
        color: {TEXT_PRIMARY};
    }}
    QTableWidget::item {{ padding: 6px; color: {TEXT_PRIMARY}; }}
    QTableWidget::item:selected {{ background-color: {ACCENT}; color: white; }}
    QHeaderView::section {{
        background-color: {DARK_CARD};
        color: {TEXT_PRIMARY};
        padding: 8px;
        border: none;
        font-weight: bold;
    }}
    QScrollBar:vertical {{
        background: {DARK_CARD};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {DARK_BORDER};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
"""

BTN_SECONDARY = f"""
    QPushButton {{
        background-color: {DARK_INPUT};
        color: {TEXT_PRIMARY};
        border: 2px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {DARK_BORDER}; }}
"""

BTN_SUCCESS = f"""
    QPushButton {{
        background-color: {SUCCESS};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: #27ae60; }}
    QPushButton:pressed {{ background-color: #1e8449; }}
    QPushButton:disabled {{ background-color: {DARK_BORDER}; color: {TEXT_MUTED}; }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background-color: {DANGER};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: #c0392b; }}
"""
