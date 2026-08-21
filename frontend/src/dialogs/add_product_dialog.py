# frontend/src/dialogs/add_product_dialog.py
"""
Dialog for creating and editing products.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.utils.formatters import format_currency
from frontend.src.utils.validators import (
    validate_required,
    validate_length,
    validate_price_frontend,
    validate_quantity_frontend
)
from frontend.src.utils.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)


class AddProductDialog(QDialog):
    """
    Dialog for adding or editing a product.
    Emits 'product_saved' signal when a product is successfully saved.
    """

    product_saved = pyqtSignal(dict)  # Emitted when product is saved

    def __init__(self, product_connector: ProductConnector = None, product_data: dict = None, parent=None):
        """
        Initialize the dialog.

        Args:
            product_connector: Connector for product operations
            product_data: If provided, edit mode (product data to edit)
            parent: Parent widget
        """
        super().__init__(parent)

        self.product_connector = product_connector or ProductConnector()
        self.product_data = product_data
        self.is_edit = product_data is not None

        self.setup_ui()
        self.setup_connections()

        if self.is_edit:
            self.load_product_data()

        logger.info(f"AddProductDialog initialized (mode: {'edit' if self.is_edit else 'create'})")

    def setup_ui(self):
        """Configures the dialog interface."""
        self.setWindowTitle("Editar Produto" if self.is_edit else "Novo Produto")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setMinimumSize(450, 350)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 20)

        # Title
        title = QLabel("📦 " + ("Editar Produto" if self.is_edit else "Cadastrar Produto"))
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Description
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Ex: Notebook Dell XPS 13")
        self.desc_input.setMinimumHeight(36)
        self.desc_input.setStyleSheet(self._input_style())
        form_layout.addRow("Descrição:", self.desc_input)

        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 999999.99)
        self.price_input.setSingleStep(0.50)
        self.price_input.setPrefix("R$ ")
        self.price_input.setDecimals(2)
        self.price_input.setMinimumHeight(36)
        self.price_input.setStyleSheet(self._input_style())
        form_layout.addRow("Preço:", self.price_input)

        # Quantity
        self.qty_input = QSpinBox()
        self.qty_input.setRange(0, 99999)
        self.qty_input.setMinimumHeight(36)
        self.qty_input.setStyleSheet(self._input_style())
        form_layout.addRow("Quantidade:", self.qty_input)

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

        self.save_btn = QPushButton("Salvar" if self.is_edit else "Criar")
        self.save_btn.setStyleSheet(self._button_style())
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

        # Status bar
        self.status_label = QLabel()
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
        self.save_btn.clicked.connect(self.handle_save)
        self.cancel_btn.clicked.connect(self.reject)

        # Enter key triggers save
        self.desc_input.returnPressed.connect(self.handle_save)
        self.price_input.returnPressed.connect(self.handle_save)
        self.qty_input.returnPressed.connect(self.handle_save)

    def load_product_data(self):
        """Loads existing product data for editing."""
        if not self.product_data:
            return

        self.desc_input.setText(self.product_data.get('description', ''))
        self.price_input.setValue(float(self.product_data.get('price', 0)))
        self.qty_input.setValue(int(self.product_data.get('quantity_available', 0)))
        self.status_label.setText("Editando produto existente")

    def handle_save(self):
        """Validates and saves the product."""
        # Validate
        errors = self.validate_inputs()
        if errors:
            self.show_error("\n".join(errors))
            return

        # Clear error
        self.hide_error()

        # Prepare data
        data = {
            'description': self.desc_input.text().strip(),
            'price': self.price_input.value(),
            'quantity_available': self.qty_input.value()
        }

        # Disable buttons during save
        self._set_loading(True)

        try:
            if self.is_edit:
                result = self.product_connector.update_product(
                    self.product_data['id'],
                    data
                )
            else:
                result = self.product_connector.create_product(data)

            if result['success']:
                product = result['data']
                self.status_label.setText("✅ Produto salvo com sucesso!")
                self.product_saved.emit(product)

                # Emit global event
                event_bus.emit('product_updated', product)

                # Close after short delay
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, self.accept)
            else:
                error_msg = result.get('error', 'Erro ao salvar produto')
                self.show_error(error_msg)

        except Exception as e:
            logger.error(f"Error saving product: {str(e)}", exc_info=True)
            self.show_error("Erro inesperado ao salvar produto")

        finally:
            self._set_loading(False)

    def validate_inputs(self):
        """Validates all form inputs."""
        errors = []

        # Description
        desc = self.desc_input.text().strip()
        error = validate_required(desc, "Descrição")
        if error:
            errors.append(error)
        else:
            error = validate_length(desc, 3, 200, "Descrição")
            if error:
                errors.append(error)

        # Price
        error = validate_price_frontend(self.price_input.value())
        if error:
            errors.append(error)

        # Quantity
        error = validate_quantity_frontend(self.qty_input.value())
        if error:
            errors.append(error)

        return errors

    def show_error(self, message):
        """Displays an error message."""
        self.error_label.setText(f"❌ {message}")
        self.error_label.show()

    def hide_error(self):
        """Hides the error message."""
        self.error_label.hide()

    def _set_loading(self, loading: bool):
        """Enables/disables buttons during loading."""
        self.save_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)
        self.desc_input.setEnabled(not loading)
        self.price_input.setEnabled(not loading)
        self.qty_input.setEnabled(not loading)

        if loading:
            self.save_btn.setText("Salvando...")
            self.status_label.setText("⏳ Processando...")
        else:
            self.save_btn.setText("Salvar" if self.is_edit else "Criar")
            if not self.error_label.isVisible():
                self.status_label.setText("Pronto")

    def _input_style(self) -> str:
        """Style for input fields."""
        return """
            QLineEdit, QSpinBox, QDoubleSpinBox {
                border: 2px solid #dcdde1;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #3498db;
                background-color: #f0f8ff;
            }
        """

    def _button_style(self, secondary: bool = False) -> str:
        """Style for buttons."""
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
                QPushButton:pressed {
                    background-color: #bdc3c7;
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