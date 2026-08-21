# frontend/src/dialogs/create_order_dialog.py
"""
Dialog for creating new orders with product selection.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSpinBox, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from frontend.src.connectors.order_connector import OrderConnector
from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.utils.formatters import format_currency, format_status
from frontend.src.utils.validators import validate_required
from frontend.src.utils.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)


class CreateOrderDialog(QDialog):
    """
    Dialog for creating a new order with items.
    Emits 'order_created' signal when order is successfully created.
    """

    order_created = pyqtSignal(dict)

    def __init__(self, order_connector: OrderConnector = None,
                 product_connector: ProductConnector = None,
                 user_id: int = None, parent=None):
        super().__init__(parent)

        self.order_connector = order_connector or OrderConnector()
        self.product_connector = product_connector or ProductConnector()
        self.user_id = user_id
        self.products = []
        self.selected_items = []  # List of dicts with product_id, name, quantity, unit_price

        self.setup_ui()
        self.setup_connections()
        self.load_products()

        logger.info("CreateOrderDialog initialized")

    def setup_ui(self):
        """Configures the dialog interface."""
        self.setWindowTitle("Novo Pedido")
        self.setModal(True)
        self.setFixedSize(700, 600)
        self.setMinimumSize(600, 500)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 20)

        # Title
        title = QLabel("📋 Criar Pedido")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)

        # Customer field
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Nome do cliente")
        self.customer_input.setMinimumHeight(36)
        self.customer_input.setStyleSheet(self._input_style())
        form_layout.addRow("Cliente:", self.customer_input)

        main_layout.addLayout(form_layout)

        # Items section
        items_label = QLabel("🛒 Itens do Pedido")
        items_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        main_layout.addWidget(items_label)

        # Add item row
        add_item_layout = QHBoxLayout()

        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(36)
        self.product_combo.setStyleSheet(self._input_style())
        add_item_layout.addWidget(self.product_combo, stretch=2)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setMinimumHeight(36)
        self.qty_spin.setStyleSheet(self._input_style())
        add_item_layout.addWidget(self.qty_spin, stretch=1)

        self.add_btn = QPushButton("➕ Adicionar")
        self.add_btn.setStyleSheet(self._button_style())
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_item_layout.addWidget(self.add_btn)

        main_layout.addLayout(add_item_layout)

        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["ID", "Produto", "Qtd", "Preço Unit.", "Subtotal"])
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setMinimumHeight(150)
        self.items_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #dcdde1;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)
        main_layout.addWidget(self.items_table)

        # Totals
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()

        self.total_label = QLabel("Total: R$ 0,00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        totals_layout.addWidget(self.total_label)

        main_layout.addLayout(totals_layout)

        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.clear_btn = QPushButton("🗑️ Limpar Itens")
        self.clear_btn.setStyleSheet(self._button_style(secondary=True))
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.clear_btn)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setStyleSheet(self._button_style(secondary=True))
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("✅ Criar Pedido")
        self.save_btn.setStyleSheet(self._button_style())
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

        # Status
        self.status_label = QLabel("Adicione produtos ao pedido")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        main_layout.addWidget(self.status_label)

        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QFormLayout QLabel {
                font-weight: bold;
                color: #34495e;
            }
        """)

    def setup_connections(self):
        """Connects signals and slots."""
        self.add_btn.clicked.connect(self.add_item)
        self.clear_btn.clicked.connect(self.clear_items)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.create_order)

        # Enter key triggers add
        self.qty_spin.valueChanged.connect(self._update_total_display)

    def load_products(self):
        """Loads products from the backend."""
        try:
            result = self.product_connector.list_products()
            if result['success']:
                self.products = result['data']
                self.product_combo.clear()
                for p in self.products:
                    self.product_combo.addItem(
                        f"{p['description']} - {format_currency(p['price'])}",
                        p['id']
                    )
                self.status_label.setText(f"{len(self.products)} produtos disponíveis")
            else:
                self.status_label.setText("❌ Erro ao carregar produtos")
        except Exception as e:
            logger.error(f"Error loading products: {str(e)}")
            self.status_label.setText("❌ Erro ao carregar produtos")

    def add_item(self):
        """Adds a product to the order items list."""
        idx = self.product_combo.currentIndex()
        if idx < 0:
            return

        product_id = self.product_combo.currentData()
        product = next((p for p in self.products if p['id'] == product_id), None)
        if not product:
            return

        quantity = self.qty_spin.value()

        # Check if already in items
        for item in self.selected_items:
            if item['product_id'] == product_id:
                # Update quantity
                item['quantity'] += quantity
                item['subtotal'] = item['quantity'] * item['unit_price']
                self.update_table()
                self._update_total_display()
                self.status_label.setText(f"✅ Atualizado: {product['description']} (+{quantity})")
                return

        # Add new item
        self.selected_items.append({
            'product_id': product_id,
            'name': product['description'],
            'quantity': quantity,
            'unit_price': product['price'],
            'subtotal': quantity * product['price']
        })

        self.update_table()
        self._update_total_display()
        self.status_label.setText(f"✅ Adicionado: {product['description']} (x{quantity})")

    def remove_item(self, row):
        """Removes an item from the order."""
        if row < 0 or row >= len(self.selected_items):
            return

        removed = self.selected_items.pop(row)
        self.update_table()
        self._update_total_display()
        self.status_label.setText(f"🗑️ Removido: {removed['name']}")

    def clear_items(self):
        """Clears all items."""
        if not self.selected_items:
            return

        reply = QMessageBox.question(
            self,
            "Limpar Itens",
            "Tem certeza que deseja remover todos os itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.selected_items.clear()
            self.update_table()
            self._update_total_display()
            self.status_label.setText("🗑️ Todos os itens removidos")

    def update_table(self):
        """Updates the items table."""
        self.items_table.setRowCount(len(self.selected_items))

        for row, item in enumerate(self.selected_items):
            # ID
            self.items_table.setItem(row, 0, QTableWidgetItem(str(item['product_id'])))

            # Name
            self.items_table.setItem(row, 1, QTableWidgetItem(item['name']))

            # Quantity
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_table.setItem(row, 2, qty_item)

            # Unit Price
            self.items_table.setItem(row, 3, QTableWidgetItem(format_currency(item['unit_price'])))

            # Subtotal
            self.items_table.setItem(row, 4, QTableWidgetItem(format_currency(item['subtotal'])))

        # Remove button column (action)
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(
            ["ID", "Produto", "Qtd", "Preço Unit.", "Subtotal", ""]
        )

        for row in range(len(self.selected_items)):
            btn = QPushButton("✖")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.items_table.setCellWidget(row, 5, btn)

        self.items_table.resizeColumnsToContents()

    def _update_total_display(self):
        """Updates the total amount display."""
        total = sum(item['subtotal'] for item in self.selected_items)
        self.total_label.setText(f"Total: {format_currency(total)}")

    def create_order(self):
        """Creates the order."""
        # Validate customer
        customer = self.customer_input.text().strip()
        error = validate_required(customer, "Cliente")
        if error:
            self.show_error(error)
            return

        if not self.selected_items:
            self.show_error("Adicione pelo menos um produto ao pedido")
            return

        self.hide_error()

        # Prepare items for backend
        items = [
            {
                'product_id': item['product_id'],
                'quantity': item['quantity']
            }
            for item in self.selected_items
        ]

        data = {
            'customer': customer,
            'items': items,
            'user_id': self.user_id
        }

        # Disable buttons
        self._set_loading(True)

        try:
            result = self.order_connector.create_order(data)

            if result['success']:
                order = result['data']
                self.status_label.setText("✅ Pedido criado com sucesso!")

                # Emit signal and global event
                self.order_created.emit(order)
                event_bus.emit('order_created', order)

                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, self.accept)
            else:
                error_msg = result.get('error', 'Erro ao criar pedido')
                self.show_error(error_msg)

        except Exception as e:
            logger.error(f"Error creating order: {str(e)}", exc_info=True)
            self.show_error("Erro inesperado ao criar pedido")

        finally:
            self._set_loading(False)

    def show_error(self, message):
        self.error_label.setText(f"❌ {message}")
        self.error_label.show()

    def hide_error(self):
        self.error_label.hide()

    def _set_loading(self, loading: bool):
        self.save_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)
        self.add_btn.setEnabled(not loading)
        self.clear_btn.setEnabled(not loading)
        self.customer_input.setEnabled(not loading)

        if loading:
            self.save_btn.setText("⏳ Criando...")
            self.status_label.setText("⏳ Processando...")
        else:
            self.save_btn.setText("✅ Criar Pedido")
            self.status_label.setText("Pronto")

    def _input_style(self) -> str:
        return """
            QLineEdit, QComboBox, QSpinBox {
                border: 2px solid #dcdde1;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #3498db;
                background-color: #f0f8ff;
            }
        """

    def _button_style(self, secondary: bool = False) -> str:
        if secondary:
            return """
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
            """
        return """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """