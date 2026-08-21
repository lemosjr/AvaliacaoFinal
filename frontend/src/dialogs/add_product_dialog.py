# frontend/src/dialogs/add_product_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.utils.validators import validate_required, validate_length, validate_price_frontend, validate_quantity_frontend
from frontend.src.utils.event_bus import event_bus
from frontend.src.styles.dark_theme import DIALOG_STYLE, BTN_SECONDARY, TEXT_PRIMARY, TEXT_MUTED, DANGER
import logging

logger = logging.getLogger(__name__)


class AddProductDialog(QDialog):
    product_saved = pyqtSignal(dict)

    def __init__(self, product_connector: ProductConnector = None, product_data: dict = None, parent=None):
        super().__init__(parent)
        self.product_connector = product_connector or ProductConnector()
        self.product_data = product_data
        self.is_edit = product_data is not None
        self.setup_ui()
        self.setup_connections()
        if self.is_edit:
            self.load_product_data()

    def setup_ui(self):
        self.setWindowTitle("Editar Produto" if self.is_edit else "Novo Produto")
        self.setModal(True)
        self.setFixedSize(500, 380)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 20)

        title = QLabel("📦 " + ("Editar Produto" if self.is_edit else "Cadastrar Produto"))
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {TEXT_PRIMARY};")
        main_layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Ex: Notebook Dell XPS 13")
        self.desc_input.setMinimumHeight(36)
        form_layout.addRow("Descrição:", self.desc_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 999999.99)
        self.price_input.setSingleStep(0.50)
        self.price_input.setPrefix("R$ ")
        self.price_input.setDecimals(2)
        self.price_input.setMinimumHeight(36)
        form_layout.addRow("Preço:", self.price_input)

        self.qty_input = QSpinBox()
        self.qty_input.setRange(0, 99999)
        self.qty_input.setMinimumHeight(36)
        form_layout.addRow("Quantidade:", self.qty_input)

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

        self.save_btn = QPushButton("Salvar" if self.is_edit else "Criar")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

        self.status_label = QLabel()
        self.status_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        main_layout.addWidget(self.status_label)

    def setup_connections(self):
        self.save_btn.clicked.connect(self.handle_save)
        self.cancel_btn.clicked.connect(self.reject)
        self.desc_input.returnPressed.connect(self.handle_save)

    def load_product_data(self):
        self.desc_input.setText(self.product_data.get('description', ''))
        self.price_input.setValue(float(self.product_data.get('price', 0)))
        self.qty_input.setValue(int(self.product_data.get('quantity_available', 0)))

    def handle_save(self):
        errors = []
        desc = self.desc_input.text().strip()
        err = validate_required(desc, "Descrição") or validate_length(desc, 3, 200, "Descrição")
        if err: errors.append(err)
        err = validate_price_frontend(self.price_input.value())
        if err: errors.append(err)
        err = validate_quantity_frontend(self.qty_input.value())
        if err: errors.append(err)

        if errors:
            self.error_label.setText("❌ " + "\n".join(errors))
            self.error_label.show()
            return

        self.error_label.hide()
        data = {'description': desc, 'price': self.price_input.value(), 'quantity_available': self.qty_input.value()}
        self._set_loading(True)

        try:
            if self.is_edit:
                result = self.product_connector.update_product(self.product_data['id'], data)
            else:
                result = self.product_connector.create_product(**data)

            if result['success']:
                product = result['data'].get('product', result['data'])
                self.product_saved.emit(product)
                event_bus.emit('product_updated', product)
                QTimer.singleShot(500, self.accept)
            else:
                self.error_label.setText(f"❌ {result.get('error', 'Erro ao salvar')}")
                self.error_label.show()
        except Exception as e:
            logger.error(f"Error saving product: {e}", exc_info=True)
            self.error_label.setText("❌ Erro inesperado ao salvar produto")
            self.error_label.show()
        finally:
            self._set_loading(False)

    def _set_loading(self, loading):
        self.save_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)
        self.desc_input.setEnabled(not loading)
        self.price_input.setEnabled(not loading)
        self.qty_input.setEnabled(not loading)
        self.save_btn.setText("Salvando..." if loading else ("Salvar" if self.is_edit else "Criar"))
        self.status_label.setText("⏳ Processando..." if loading else "Pronto")
