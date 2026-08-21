# frontend/src/main_window.py
"""
Main Window - Dashboard principal da aplicação.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QFrame,
    QStatusBar, QToolBar, QMenu, QMessageBox,
    QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont

from frontend.src.connectors.auth_connector import AuthConnector
from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.connectors.order_connector import OrderConnector
from frontend.src.widgets.table_widget import TableWidget
from frontend.src.widgets.product_widget import ProductWidget
from frontend.src.widgets.order_widget import OrderWidget
from frontend.src.utils.formatters import format_currency, format_date

from frontend.src.dialogs.add_product_dialog import AddProductDialog
from frontend.src.dialogs.create_order_dialog import CreateOrderDialog
from frontend.src.dialogs.add_item_dialog import AddItemDialog
from frontend.src.dialogs.confirmation_dialog import ConfirmationDialog

import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Janela principal após login bem-sucedido."""

    def __init__(self, user: dict, auth_connector: AuthConnector):
        super().__init__()

        self.user = user
        self.auth_connector = auth_connector

        # Connectors
        self.product_connector = ProductConnector()
        self.order_connector = OrderConnector()

        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()

        # Carrega dados iniciais
        self.load_dashboard_data()

        logger.info(f"Main window opened for user: {user.get('email')}")

    def setup_ui(self):
        """Configura a interface da janela principal."""
        self.setWindowTitle(f"E-Commerce Orders - {self.user.get('name', 'Usuário')}")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ===== TABS =====
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                background-color: #ecf0f1;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        # Tab: Dashboard
        self.tab_dashboard = self._create_dashboard_tab()
        self.tabs.addTab(self.tab_dashboard, "📊 Dashboard")

        # Tab: Produtos
        self.tab_products = self._create_products_tab()
        self.tabs.addTab(self.tab_products, "📦 Produtos")

        # Tab: Pedidos
        self.tab_orders = self._create_orders_tab()
        self.tabs.addTab(self.tab_orders, "📋 Pedidos")

        main_layout.addWidget(self.tabs)

        # ===== STATUS BAR =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema pronto")

    def setup_menu(self):
        """Configura o menu da aplicação."""
        menubar = self.menuBar()

        # Menu Arquivo
        file_menu = menubar.addMenu("📁 Arquivo")

        logout_action = QAction("🚪 Sair", self)
        logout_action.setShortcut("Ctrl+Q")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        # Menu Produtos
        product_menu = menubar.addMenu("📦 Produtos")

        add_product_action = QAction("➕ Cadastrar Produto", self)
        add_product_action.triggered.connect(self.open_add_product)
        product_menu.addAction(add_product_action)

        list_products_action = QAction("📋 Listar Produtos", self)
        list_products_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        product_menu.addAction(list_products_action)

        product_menu.addSeparator()

        refresh_products_action = QAction("🔄 Atualizar", self)
        refresh_products_action.triggered.connect(self.load_products)
        product_menu.addAction(refresh_products_action)

        # Menu Pedidos
        order_menu = menubar.addMenu("📋 Pedidos")

        create_order_action = QAction("➕ Criar Pedido", self)
        create_order_action.triggered.connect(self.open_create_order)
        order_menu.addAction(create_order_action)

        list_orders_action = QAction("📋 Listar Pedidos", self)
        list_orders_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        order_menu.addAction(list_orders_action)

        order_menu.addSeparator()

        refresh_orders_action = QAction("🔄 Atualizar", self)
        refresh_orders_action.triggered.connect(self.load_orders)
        order_menu.addAction(refresh_orders_action)

        # Menu Ajuda
        help_menu = menubar.addMenu("❓ Ajuda")

        about_action = QAction("ℹ️ Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """Configura a toolbar."""
        toolbar = self.addToolBar("Ferramentas")
        toolbar.setMovable(False)

        # Botão: Cadastrar Produto
        add_prod_btn = QPushButton("➕ Novo Produto")
        add_prod_btn.clicked.connect(self.open_add_product)
        toolbar.addWidget(add_prod_btn)

        toolbar.addSeparator()

        # Botão: Criar Pedido
        create_order_btn = QPushButton("➕ Novo Pedido")
        create_order_btn.clicked.connect(self.open_create_order)
        toolbar.addWidget(create_order_btn)

        toolbar.addSeparator()

        # Botão: Atualizar
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.load_dashboard_data)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()

        # Nome do usuário
        user_label = QLabel(f"👤 {self.user.get('name', 'Usuário')}")
        user_label.setStyleSheet("font-weight: bold; padding: 5px;")
        toolbar.addWidget(user_label)

    # ========== DASHBOARD TAB ==========

    def _create_dashboard_tab(self):
        """Cria a tab de dashboard."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # ===== CARDS DE ESTATÍSTICAS =====
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self.card_products = self._create_stat_card("Total Produtos", "0", "📦", "#3498db")
        self.card_orders = self._create_stat_card("Total Pedidos", "0", "📋", "#2ecc71")
        self.card_orders_active = self._create_stat_card("Pedidos Ativos", "0", "🔄", "#f39c12")
        self.card_revenue = self._create_stat_card("Faturamento", "R$ 0,00", "💰", "#9b59b6")

        stats_layout.addWidget(self.card_products)
        stats_layout.addWidget(self.card_orders)
        stats_layout.addWidget(self.card_orders_active)
        stats_layout.addWidget(self.card_revenue)

        layout.addLayout(stats_layout)

        # ===== ÚLTIMOS PEDIDOS =====
        recent_label = QLabel("📋 Últimos Pedidos")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(recent_label)

        # Tabela de pedidos recentes
        self.recent_orders_table = TableWidget(
            headers=["ID", "Cliente", "Status", "Total", "Data"]
        )
        self.recent_orders_table.set_status_filter_visible(False)
        self.recent_orders_table.item_selected.connect(self._on_order_selected)
        layout.addWidget(self.recent_orders_table)

        # ===== ÚLTIMOS PRODUTOS =====
        recent_products_label = QLabel("📦 Últimos Produtos")
        recent_products_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(recent_products_label)

        # Grid de produtos recentes
        self.recent_products_grid = QGridLayout()
        self.recent_products_grid.setSpacing(15)
        layout.addLayout(self.recent_products_grid)

        return widget

    def _create_stat_card(self, title: str, value: str, icon: str, color: str):
        """Cria um card de estatística."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 12px;
                padding: 15px;
                min-height: 80px;
                min-width: 150px;
            }}
        """)
        card_layout = QVBoxLayout(card)

        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        card_layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName(f"stat_{title.replace(' ', '_')}")
        value_label.setStyleSheet(f"""
            font-size: 26px;
            font-weight: bold;
            color: {color};
        """)
        card_layout.addWidget(value_label)

        return card

    # ========== PRODUCTS TAB ==========

    def _create_products_tab(self):
        """Cria a tab de produtos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # ===== TOOLBAR =====
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        add_btn = QPushButton("➕ Cadastrar Produto")
        add_btn.clicked.connect(self.open_add_product)
        toolbar.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.load_products)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # ===== TABELA =====
        self.products_table = TableWidget(
            headers=["ID", "Descrição", "Preço", "Estoque", "Data"]
        )
        self.products_table.item_selected.connect(self._on_product_selected)
        layout.addWidget(self.products_table)

        return widget

    # ========== ORDERS TAB ==========

    def _create_orders_tab(self):
        """Cria a tab de pedidos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # ===== TOOLBAR =====
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        add_btn = QPushButton("➕ Criar Pedido")
        add_btn.clicked.connect(self.open_create_order)
        toolbar.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.load_orders)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # ===== TABELA =====
        self.orders_table = TableWidget(
            headers=["ID", "Cliente", "Status", "Total", "Itens", "Data"]
        )
        self.orders_table.set_status_filter_visible(True)
        self.orders_table.item_selected.connect(self._on_order_selected)
        layout.addWidget(self.orders_table)

        return widget

    # ========== DATA LOADING ==========

    def load_dashboard_data(self):
        """Carrega dados para o dashboard."""
        self.load_stats()
        self.load_recent_orders()
        self.load_recent_products()

    def load_stats(self):
        """Carrega estatísticas."""
        try:
            # Total de produtos
            products_result = self.product_connector.list_products()
            if products_result['success']:
                products = products_result['data']['products']
                total_products = len(products)
                self._update_stat_card("Total Produtos", str(total_products))

            # Total de pedidos
            orders_result = self.order_connector.list_orders()
            if orders_result['success']:
                orders = orders_result['data']['orders']
                total_orders = len(orders)
                self._update_stat_card("Total Pedidos", str(total_orders))

                # Pedidos ativos (não completos/cancelados)
                active_orders = [o for o in orders if o.get('status') not in ['completed', 'cancelled']]
                self._update_stat_card("Pedidos Ativos", str(len(active_orders)))

                # Faturamento (soma dos completos)
                revenue = sum(o.get('total_amount', 0) for o in orders if o.get('status') == 'completed')
                self._update_stat_card("Faturamento", format_currency(revenue))

        except Exception as e:
            logger.error(f"Error loading stats: {str(e)}")
            self.status_bar.showMessage("Erro ao carregar estatísticas", 5000)

    def _update_stat_card(self, title: str, value: str):
        """Atualiza o valor de um card de estatística."""
        for child in self.card_products.parent().children():
            if isinstance(child, QFrame):
                for label in child.findChildren(QLabel):
                    if label.objectName() == f"stat_{title.replace(' ', '_')}":
                        label.setText(value)
                        return

    def load_recent_orders(self, limit: int = 5):
        """Carrega os pedidos recentes para o dashboard."""
        try:
            result = self.order_connector.list_orders()
            if result['success']:
                orders = result['data']['orders'][:limit]
                data = []
                for order in orders:
                    data.append({
                        'id': order.get('id'),
                        'customer': order.get('customer'),
                        'status': order.get('status'),
                        'total': format_currency(order.get('total_amount', 0)),
                        'date': format_date(order.get('created_at', ''))
                    })
                self.recent_orders_table.set_data(data)
        except Exception as e:
            logger.error(f"Error loading recent orders: {str(e)}")

    def load_recent_products(self, limit: int = 4):
        """Carrega os produtos recentes para o dashboard."""
        try:
            result = self.product_connector.list_products()
            if result['success']:
                products = result['data']['products'][:limit]

                # Limpa o grid
                for i in reversed(range(self.recent_products_grid.count())):
                    widget = self.recent_products_grid.itemAt(i).widget()
                    if widget:
                        widget.deleteLater()

                # Adiciona produtos ao grid
                for idx, product in enumerate(products):
                    row = idx // 2
                    col = idx % 2
                    product_widget = ProductWidget(product)
                    product_widget.product_clicked.connect(self._on_product_selected)
                    self.recent_products_grid.addWidget(product_widget, row, col)

                # Preenche o resto com espaços vazios
                remaining = limit - len(products)
                for i in range(remaining):
                    placeholder = QFrame()
                    placeholder.setStyleSheet("min-width: 200px; min-height: 150px;")
                    self.recent_products_grid.addWidget(placeholder, (len(products) + i) // 2, (len(products) + i) % 2)

        except Exception as e:
            logger.error(f"Error loading recent products: {str(e)}")

    def load_products(self):
        """Carrega todos os produtos na tab de produtos."""
        try:
            result = self.product_connector.list_products()
            if result['success']:
                products = result['data']['products']
                data = []
                for product in products:
                    data.append({
                        'id': product.get('id'),
                        'description': product.get('description'),
                        'price': format_currency(product.get('price', 0)),
                        'quantity_available': product.get('quantity_available', 0),
                        'date': format_date(product.get('created_at', ''))
                    })
                self.products_table.set_data(data)
                self.status_bar.showMessage(f"✅ {len(products)} produtos carregados", 3000)
        except Exception as e:
            logger.error(f"Error loading products: {str(e)}")
            self.status_bar.showMessage("❌ Erro ao carregar produtos", 5000)

    def load_orders(self):
        """Carrega todos os pedidos na tab de pedidos."""
        try:
            result = self.order_connector.list_orders()
            if result['success']:
                orders = result['data']['orders']
                data = []
                for order in orders:
                    data.append({
                        'id': order.get('id'),
                        'customer': order.get('customer'),
                        'status': order.get('status'),
                        'total': format_currency(order.get('total_amount', 0)),
                        'items': len(order.get('items', [])),
                        'date': format_date(order.get('created_at', ''))
                    })
                self.orders_table.set_data(data)
                self.status_bar.showMessage(f"✅ {len(orders)} pedidos carregados", 3000)
        except Exception as e:
            logger.error(f"Error loading orders: {str(e)}")
            self.status_bar.showMessage("❌ Erro ao carregar pedidos", 5000)

    # ========== EVENT HANDLERS ==========

    def _on_product_selected(self, product_data: dict):
        """Manipula seleção de produto."""
        logger.info(f"Product selected: {product_data.get('id')}")
        # Mostra detalhes em uma mensagem (pode ser expandido)
        QMessageBox.information(
            self,
            "Detalhes do Produto",
            f"""
            <b>ID:</b> {product_data.get('id')}
            <b>Descrição:</b> {product_data.get('description')}
            <b>Preço:</b> {format_currency(product_data.get('price', 0))}
            <b>Estoque:</b> {product_data.get('quantity_available', 0)}
            """
        )

    def _on_order_selected(self, order_data: dict):
        """Manipula seleção de pedido."""
        logger.info(f"Order selected: {order_data.get('id')}")
        # Mostra detalhes em uma mensagem (pode ser expandido)
        QMessageBox.information(
            self,
            "Detalhes do Pedido",
            f"""
            <b>ID:</b> {order_data.get('id')}
            <b>Cliente:</b> {order_data.get('customer')}
            <b>Status:</b> {order_data.get('status')}
            <b>Total:</b> {format_currency(order_data.get('total_amount', 0))}
            <b>Data:</b> {format_date(order_data.get('created_at', ''))}
            """
        )

    # ========== DIALOGS ==========

    def open_add_product(self):
        """Abre o diálogo para cadastrar produto."""
        dialog = AddProductDialog(self.product_connector, self)
        if dialog.exec():
            self.load_products()
            self.load_dashboard_data()
            self.status_bar.showMessage("✅ Produto cadastrado com sucesso!", 3000)

    def open_create_order(self):
        """Abre o diálogo para criar pedido."""
        dialog = CreateOrderDialog(self.order_connector, self.product_connector, self)
        if dialog.exec():
            self.load_orders()
            self.load_dashboard_data()
            self.status_bar.showMessage("✅ Pedido criado com sucesso!", 3000)

    def open_add_item_to_order(self, order_id: int):
        """Abre o diálogo para adicionar item a um pedido."""
        dialog = AddItemDialog(self.order_connector, self.product_connector, order_id, self)
        if dialog.exec():
            self.load_orders()
            self.load_dashboard_data()

    # ========== ACTIONS ==========

    def logout(self):
        """Realiza logout do usuário."""
        reply = QMessageBox.question(
            self,
            "Confirmar saída",
            "Tem certeza que deseja sair?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.auth_connector.logout()
            self.close()
            logger.info("User logged out")

    def show_about(self):
        """Exibe informações sobre a aplicação."""
        QMessageBox.about(
            self,
            "Sobre",
            """
            <h2>📦 E-Commerce Orders</h2>
            <p><b>Versão:</b> 1.0.0</p>
            <p>Sistema de gerenciamento de pedidos para e-commerce.</p>
            <p><b>Tecnologias:</b></p>
            <ul>
                <li>Python 3.x</li>
                <li>PyQt6 (Interface Desktop)</li>
                <li>PostgreSQL (Banco de Dados)</li>
            </ul>
            <p>Desenvolvido para atividade acadêmica.</p>
            """
        )

    def closeEvent(self, event):
        """Evento de fechamento da janela."""
        logger.info("Main window closed")
        event.accept()