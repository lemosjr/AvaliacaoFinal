# frontend/src/dialogs/create_order_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from frontend.src.connectors.order_connector import OrderConnector
from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.utils.formatters import format_currency
from frontend.src.utils.validators import validate_required
from frontend.src.utils.event_bus import event_bus
from frontend.src.styles.dark_theme import DIALOG_STYLE, BTN_SECONDARY, BTN_SUCCESS, TEXT_PRIMARY, TEXT_MUTED, DANGER, DARK_BORDER
import logging

logger = logging.getLogger(__name__)


class CreateOrderDialog(QDialog):
    order_created = pyqtSignal(dict)

    def __init__(self, order_connector=None, product_connector=None, user_id=None, parent=None):
        super().__init__(parent)
        self.order_connector = order_connector or OrderConnector()
        self.product_connector = product_connector or ProductConnector()
        self.user_id = user_id
        self.products = []
        self.selected_items = []
        self.setup_ui()
        self.setup_connections()
        self.load_products()

    def setup_ui(self):
        self.setWindowTitle("Novo Pedido")
        self.setModal(True)
        self.setFixedSize(700, 600)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 20)

        title = QLabel("📋 Criar Pedido")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {TEXT_PRIMARY};")
        main_layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Nome do cliente")
        self.customer_input.setMinimumHeight(36)
        form_layout.addRow("Cliente:", self.customer_input)
        main_layout.addLayout(form_layout)

        items_label = QLabel("🛒 Itens do Pedido")
        items_label.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; font-size: 14px;")
        main_layout.addWidget(items_label)

        add_item_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(36)
        add_item_layout.addWidget(self.product_combo, stretch=2)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setMinimumHeight(36)
        add_item_layout.addWidget(self.qty_spin, stretch=1)

        self.add_btn = QPushButton("➕ Adicionar")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_item_layout.addWidget(self.add_btn)
        main_layout.addLayout(add_item_layout)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["ID", "Produto", "Qtd", "Preço Unit.", "Subtotal"])
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setMinimumHeight(150)
        main_layout.addWidget(self.items_table)

        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        self.total_label = QLabel("Total: R$ 0,00")
        self.total_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY};")
        totals_layout.addWidget(self.total_label)
        main_layout.addLayout(totals_layout)

        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"color: {DANGER}; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.clear_btn = QPushButton("🗑️ Limpar Itens")
        self.clear_btn.setStyleSheet(BTN_SECONDARY)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.clear_btn)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setStyleSheet(BTN_SECONDARY)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("✅ Criar Pedido")
        self.save_btn.setStyleSheet(BTN_SUCCESS)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

        self.status_label = QLabel("Adicione produtos ao pedido")
        self.status_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        main_layout.addWidget(self.status_label)

    def setup_connections(self):
        self.add_btn.clicked.connect(self.add_item)
        self.clear_btn.clicked.connect(self.clear_items)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.create_order)

    def load_products(self):
        try:
            result = self.product_connector.list_products()
            if result['success']:
                self.products = result['data'].get('products', [])
                self.product_combo.clear()
                for p in self.products:
                    self.product_combo.addItem(f"{p['description']} - {format_currency(p['price'])}", p['id'])
                self.status_label.setText(f"{len(self.products)} produtos disponíveis")
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.status_label.setText("❌ Erro ao carregar produtos")

    def add_item(self):
        idx = self.product_combo.currentIndex()
        if idx < 0:
            return
        product_id = self.product_combo.currentData()
        product = next((p for p in self.products if p['id'] == product_id), None)
        if not product:
            return
        quantity = self.qty_spin.value()
        for item in self.selected_items:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                item['subtotal'] = item['quantity'] * item['unit_price']
                self.update_table()
                self._update_total_display()
                return
        self.selected_items.append({
            'product_id': product_id, 'name': product['description'],
            'quantity': quantity, 'unit_price': product['price'],
            'subtotal': quantity * product['price']
        })
        self.update_table()
        self._update_total_display()

    def remove_item(self, row):
        if 0 <= row < len(self.selected_items):
            self.selected_items.pop(row)
            self.update_table()
            self._update_total_display()

    def clear_items(self):
        if not self.selected_items:
            return
        if QMessageBox.question(self, "Limpar Itens", "Remover todos os itens?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.selected_items.clear()
            self.update_table()
            self._update_total_display()

    def update_table(self):
        self.items_table.setRowCount(len(self.selected_items))
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["ID", "Produto", "Qtd", "Preço Unit.", "Subtotal", ""])
        for row, item in enumerate(self.selected_items):
            self.items_table.setItem(row, 0, QTableWidgetItem(str(item['product_id'])))
            self.items_table.setItem(row, 1, QTableWidgetItem(item['name']))
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_table.setItem(row, 2, qty_item)
            self.items_table.setItem(row, 3, QTableWidgetItem(format_currency(item['unit_price'])))
            self.items_table.setItem(row, 4, QTableWidgetItem(format_currency(item['subtotal'])))
            btn = QPushButton("✖")
            btn.setStyleSheet(f"QPushButton {{ background-color: {DANGER}; color: white; border: none; border-radius: 4px; padding: 4px 8px; }} QPushButton:hover {{ background-color: #c0392b; }}")
            btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.items_table.setCellWidget(row, 5, btn)
        self.items_table.resizeColumnsToContents()

    def _update_total_display(self):
        total = sum(item['subtotal'] for item in self.selected_items)
        self.total_label.setText(f"Total: {format_currency(total)}")

    def create_order(self):
        customer = self.customer_input.text().strip()
        if not customer:
            self.error_label.setText("❌ Cliente é obrigatório")
            self.error_label.show()
            return
        if not self.selected_items:
            self.error_label.setText("❌ Adicione pelo menos um produto")
            self.error_label.show()
            return
        self.error_label.hide()
        items = [{'product_id': i['product_id'], 'quantity': i['quantity']} for i in self.selected_items]
        self._set_loading(True)
        try:
            result = self.order_connector.create_order(customer, items)
            if result['success']:
                order = result['data'].get('order', result['data'])
                self.order_created.emit(order)
                event_bus.emit('order_created', order)
                QTimer.singleShot(500, self.accept)
            else:
                self.error_label.setText(f"❌ {result.get('error', 'Erro ao criar pedido')}")
                self.error_label.show()
        except Exception as e:
            logger.error(f"Error creating order: {e}", exc_info=True)
            self.error_label.setText("❌ Erro inesperado ao criar pedido")
            self.error_label.show()
        finally:
            self._set_loading(False)

    def show_error(self, message):
        self.error_label.setText(f"❌ {message}")
        self.error_label.show()

    def hide_error(self):
        self.error_label.hide()

    def _set_loading(self, loading):
        for w in [self.save_btn, self.cancel_btn, self.add_btn, self.clear_btn, self.customer_input]:
            w.setEnabled(not loading)
        self.save_btn.setText("⏳ Criando..." if loading else "✅ Criar Pedido")
        self.status_label.setText("⏳ Processando..." if loading else "Pronto")
