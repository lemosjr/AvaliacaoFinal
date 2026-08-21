# frontend/src/dialogs/add_item_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.connectors.order_connector import OrderConnector
from frontend.src.utils.formatters import format_currency
from frontend.src.utils.validators import validate_quantity_frontend
from frontend.src.utils.event_bus import event_bus
from frontend.src.styles.dark_theme import DIALOG_STYLE, BTN_SECONDARY, TEXT_PRIMARY, TEXT_MUTED, DANGER
import logging

logger = logging.getLogger(__name__)


class AddItemDialog(QDialog):
    item_added = pyqtSignal(dict)

    def __init__(self, order_id, order_connector=None, product_connector=None, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.order_connector = order_connector or OrderConnector()
        self.product_connector = product_connector or ProductConnector()
        self.products = []
        self.setup_ui()
        self.setup_connections()
        self.load_products()

    def setup_ui(self):
        self.setWindowTitle("Adicionar Produto ao Pedido")
        self.setModal(True)
        self.setFixedSize(450, 300)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 20)

        title = QLabel(f"📦 Adicionar Produto ao Pedido #{self.order_id}")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY};")
        main_layout.addWidget(title)

        self.info_label = QLabel("Selecione um produto")
        self.info_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        main_layout.addWidget(self.info_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(36)
        form_layout.addRow("Produto:", self.product_combo)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setMinimumHeight(36)
        form_layout.addRow("Quantidade:", self.qty_spin)

        main_layout.addLayout(form_layout)

        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"color: {DANGER}; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setStyleSheet(BTN_SECONDARY)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.add_btn = QPushButton("Adicionar")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setDefault(True)
        button_layout.addWidget(self.add_btn)

        main_layout.addLayout(button_layout)

        self.status_label = QLabel("Selecione um produto e quantidade")
        self.status_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        main_layout.addWidget(self.status_label)

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
                self.update_product_info()
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.status_label.setText("❌ Erro ao carregar produtos")

    def update_product_info(self):
        product_id = self.product_combo.currentData()
        product = next((p for p in self.products if p['id'] == product_id), None)
        if product:
            self.info_label.setText(
                f"📦 {product['description']} | Preço: {format_currency(product['price'])} | Estoque: {product['quantity_available']}"
            )

    def handle_add(self):
        if self.product_combo.currentIndex() < 0:
            self.error_label.setText("❌ Selecione um produto")
            self.error_label.show()
            return

        product_id = self.product_combo.currentData()
        quantity = self.qty_spin.value()

        err = validate_quantity_frontend(quantity)
        if err:
            self.error_label.setText(f"❌ {err}")
            self.error_label.show()
            return

        product = next((p for p in self.products if p['id'] == product_id), None)
        if product and quantity > product['quantity_available']:
            self.error_label.setText(f"❌ Estoque insuficiente. Disponível: {product['quantity_available']}")
            self.error_label.show()
            return

        self.error_label.hide()
        self._set_loading(True)
        try:
            result = self.order_connector.add_item_to_order(self.order_id, product_id, quantity)
            if result['success']:
                order = result['data'].get('order', result['data'])
                self.item_added.emit({'order': order, 'product_id': product_id})
                event_bus.emit('order_updated', order)
                QTimer.singleShot(300, self.accept)
            else:
                self.error_label.setText(f"❌ {result.get('error', 'Erro ao adicionar item')}")
                self.error_label.show()
        except Exception as e:
            logger.error(f"Error adding item: {e}", exc_info=True)
            self.error_label.setText("❌ Erro inesperado")
            self.error_label.show()
        finally:
            self._set_loading(False)

    def _set_loading(self, loading):
        for w in [self.add_btn, self.cancel_btn, self.product_combo, self.qty_spin]:
            w.setEnabled(not loading)
        self.add_btn.setText("⏳ Adicionando..." if loading else "Adicionar")
        self.status_label.setText("⏳ Processando..." if loading else "Pronto")
