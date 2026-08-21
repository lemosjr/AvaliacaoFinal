# frontend/src/widgets/table_widget.py
"""
Generic Table Widget - Tabela reutilizável com ações.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView,
    QLabel, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from frontend.src.widgets.status_badge import StatusBadge


class TableWidget(QWidget):
    """
    Tabela genérica com suporte a filtros e ações.
    """

    # Sinal emitido quando um item é selecionado
    item_selected = pyqtSignal(dict)
    # Sinal emitido quando uma ação é acionada
    action_triggered = pyqtSignal(str, dict)

    def __init__(self, headers: list, parent=None):
        super().__init__(parent)

        self.headers = headers
        self.data = []
        self.actions = {}

        self.setup_ui()

    def setup_ui(self):
        """Configura a interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ===== TOOLBAR =====
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Barra de pesquisa
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Pesquisar...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.search_input)

        toolbar.addStretch()

        # Filtro de status (opcional)
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos os status")
        self.status_filter.addItems(['created', 'processing', 'completed', 'cancelled'])
        self.status_filter.setVisible(False)
        self.status_filter.currentTextChanged.connect(self.filter_table)
        toolbar.addWidget(self.status_filter)

        layout.addLayout(toolbar)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)

        # Estilo
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 6px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.table)

        # ===== FOOTER =====
        footer = QHBoxLayout()
        self.row_count_label = QLabel("0 registros")
        self.row_count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        footer.addWidget(self.row_count_label)
        footer.addStretch()
        layout.addLayout(footer)

    def set_data(self, data: list, id_field: str = 'id'):
        """
        Define os dados da tabela.

        Args:
            data: Lista de dicionários com os dados
            id_field: Nome do campo que identifica unicamente cada item
        """
        self.data = data
        self.id_field = id_field
        self._populate_table(data)

    def _populate_table(self, data: list):
        """Popula a tabela com os dados."""
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(self.headers))

        for row, item in enumerate(data):
            for col, header in enumerate(self.headers):
                key = header.lower().replace(' ', '_')
                value = item.get(key, '')

                # Tratamento especial para status
                if key == 'status' and value:
                    # Cria um StatusBadge embutido
                    badge = StatusBadge(value)
                    self.table.setCellWidget(row, col, badge)
                else:
                    # Texto normal
                    table_item = QTableWidgetItem(str(value))
                    table_item.setData(Qt.ItemDataRole.UserRole, item.get(self.id_field))
                    self.table.setItem(row, col, table_item)

        self.row_count_label.setText(f"{len(data)} registros")

    def filter_table(self):
        """Filtra a tabela com base na pesquisa e no filtro de status."""
        search_text = self.search_input.text().lower().strip()
        status_filter = self.status_filter.currentText().lower()

        filtered_data = []
        for item in self.data:
            # Filtro por texto (busca em todos os campos)
            if search_text:
                match = False
                for value in item.values():
                    if search_text in str(value).lower():
                        match = True
                        break
                if not match:
                    continue

            # Filtro por status
            if status_filter != 'todos os status':
                item_status = item.get('status', '').lower()
                if item_status != status_filter:
                    continue

            filtered_data.append(item)

        self._populate_table(filtered_data)

    def set_status_filter_visible(self, visible: bool):
        """Mostra ou oculta o filtro de status."""
        self.status_filter.setVisible(visible)

    def _on_item_double_clicked(self, item):
        """Emite sinal quando um item é duplo clicado."""
        row = item.row()
        item_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if item_id:
            # Encontra o item nos dados
            for data_item in self.data:
                if data_item.get(self.id_field) == item_id:
                    self.item_selected.emit(data_item)
                    break

    def get_selected_item(self) -> dict:
        """Retorna o item selecionado atualmente."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            for data_item in self.data:
                if data_item.get(self.id_field) == item_id:
                    return data_item
        return None