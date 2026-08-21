# frontend/src/dialogs/add_item_dialog.py
"""
Dialog for adding items to an existing order.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.connectors.order_connector import OrderConnector
from frontend.src.utils.formatters import format_currency
from frontend.src.utils.validators import validate_quantity_frontend
from frontend.src.utils.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)


class AddItemDialog(QDialog):
    """
    Dialog for adding items to an existing order.
    Emits 'item_added' signal when an item is successfully added.
    """

    item_added = pyqtSignal(dict)

    def __init__(self, order_id: int, order_connector: OrderConnector = None,
                 product_connector: ProductConnector = None, parent=None):
        super().__init__(parent)

        self.order_id = order_id
        self.order_connector = order_connector or OrderConnector()
        self.product_connector = product_connector or ProductConnector()
        self.products = []

        self.setup_ui()
        self.setup_connections()
        self.load_products()

        logger.info(f"AddItemDialog initialized for order {order_id}")

    def setup_ui(self):
        self.setWindowTitle("Adicionar Produto ao Pedido")
        self.setModal(True)
        self.setFixedSize(450, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 20)

        # Title
        title = QLabel(f"📦 Adicionar Produto ao Pedido #{self.order_id}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(36)
        self.product_combo.setStyleSheet(self._input_style())
        form_layout.addRow("Produto:", self.product_combo)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setMinimumHeight(36)
        self.qty_spin.setStyleSheet(self._input_style())
        form_layout.addRow("Quantidade:", self.qty_spin)

        # Product info display
        self.info_label = QLabel("Selecione um produto")
        self.info_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        main_layout.addWidget(self.info_label)

        main_layout.addLayout(form_layout)

        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setStyleSheet(self._button_style(secondary=True))
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.add_btn = QPushButton("Adicionar")
        self.add_btn.setStyleSheet(self._button_style())
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setDefault(True)
        button_layout.addWidget(self.add_btn)

        main_layout.addLayout(button_layout)

        # Status
        self.status_label = QLabel("Selecione um produto e quantidade")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        main_layout.addWidget(self.status_label)

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
        self.add_btn.clicked.connect(self.handle_add)
        self.cancel_btn.clicked.connect(self.reject)
        self.product_combo.currentIndexChanged.connect(self.update_product_info)

    def load_products(self):
        try:
            result = self.product_connector.list_products()
            if result['success']:
                self.products = result['data'].get('products', [])
                self.product_combo.clear()
                for p in self.products:
                    self.product_combo.addItem(
                        f"{p['description']} - {format_currency(p['price'])} (estoque: {p['quantity_available']})",
                        p['id']
                    )
                self.status_label.setText(f"{len(self.products)} produtos disponíveis")
                self.update_product_info()
            else:
                self.status_label.setText("❌ Erro ao carregar produtos")
        except Exception as e:
            logger.error(f"Error loading products: {str(e)}")
            self.status_label.setText("❌ Erro ao carregar produtos")

    def update_product_info(self):
        idx = self.product_combo.currentIndex()
        if idx < 0:
            return

        product_id = self.product_combo.currentData()
        product = next((p for p in self.products if p['id'] == product_id), None)
        if product:
            self.info_label.setText(
                f"📦 {product['description']} | "
                f"Preço: {format_currency(product['price'])} | "
                f"Estoque: {product['quantity_available']} unidades"
            )

    def handle_add(self):
        idx = self.product_combo.currentIndex()
        if idx < 0:
            self.show_error("Selecione um produto")
            return

        product_id = self.product_combo.currentData()
        quantity = self.qty_spin.value()

        # Validate quantity
        error = validate_quantity_frontend(quantity)
        if error:
            self.show_error(error)
            return

        # Check stock
        product = next((p for p in self.products if p['id'] == product_id), None)
        if product and quantity > product['quantity_available']:
            self.show_error(
                f"Estoque insuficiente. Disponível: {product['quantity_available']}"
            )
            return

        self.hide_error()
        self._set_loading(True)

        try:
            result = self.order_connector.add_item_to_order(
                self.order_id,
                product_id,
                quantity
            )

            if result['success']:
                order = result['data'].get('order', result['data'])
                self.status_label.setText("✅ Item adicionado com sucesso!")

                # Emit signal and global event
                self.item_added.emit({'order': order, 'product_id': product_id})
                event_bus.emit('order_updated', order)

                from PyQt6.QtCore import QTimer
                QTimer.singleShot(300, self.accept)
            else:
                error_msg = result.get('error', 'Erro ao adicionar item')
                self.show_error(error_msg)

        except Exception as e:
            logger.error(f"Error adding item: {str(e)}", exc_info=True)
            self.show_error("Erro inesperado ao adicionar item")

        finally:
            self._set_loading(False)

    def show_error(self, message):
        self.error_label.setText(f"❌ {message}")
        self.error_label.show()

    def hide_error(self):
        self.error_label.hide()

    def _set_loading(self, loading: bool):
        self.add_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)
        self.product_combo.setEnabled(not loading)
        self.qty_spin.setEnabled(not loading)

        if loading:
            self.add_btn.setText("⏳ Adicionando...")
            self.status_label.setText("⏳ Processando...")
        else:
            self.add_btn.setText("Adicionar")
            self.status_label.setText("Pronto")

    def _input_style(self) -> str:
        return """
            QComboBox, QSpinBox {
                border: 2px solid #dcdde1;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox:focus, QSpinBox:focus {
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
                    padding: 8px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
            """
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """