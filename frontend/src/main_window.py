# frontend/src/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QFrame,
    QStatusBar, QToolBar, QMessageBox,
    QScrollArea, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from frontend.src.connectors.auth_connector import AuthConnector
from frontend.src.connectors.product_connector import ProductConnector
from frontend.src.connectors.order_connector import OrderConnector
from frontend.src.widgets.table_widget import TableWidget
from frontend.src.widgets.product_widget import ProductWidget
from frontend.src.utils.formatters import format_currency, format_date
from frontend.src.dialogs.add_product_dialog import AddProductDialog
from frontend.src.dialogs.create_order_dialog import CreateOrderDialog
from frontend.src.dialogs.add_item_dialog import AddItemDialog
from frontend.src.styles.dark_theme import (
    DARK_BG, DARK_CARD, DARK_INPUT, DARK_BORDER,
    TEXT_PRIMARY, TEXT_MUTED, ACCENT, ACCENT_HOVER, SUCCESS
)

import logging
logger = logging.getLogger(__name__)


MAIN_STYLE = f"""
    QMainWindow {{ background-color: {DARK_BG}; }}
    QWidget {{ background-color: transparent; color: {TEXT_PRIMARY}; font-family: "Segoe UI", Arial, sans-serif; }}
    QMenuBar {{ background-color: {DARK_CARD}; color: {TEXT_PRIMARY}; }}
    QMenuBar::item:selected {{ background-color: {ACCENT}; }}
    QMenu {{ background-color: {DARK_CARD}; color: {TEXT_PRIMARY}; border: 1px solid {DARK_BORDER}; }}
    QMenu::item:selected {{ background-color: {ACCENT}; }}
    QToolBar {{ background-color: {DARK_CARD}; border-bottom: 1px solid {DARK_BORDER}; spacing: 6px; padding: 4px; }}
    QPushButton {{
        background-color: {ACCENT};
        color: white; border: none; border-radius: 6px;
        padding: 8px 16px; font-size: 13px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:pressed {{ background-color: #1c6ea4; }}
    QPushButton:disabled {{ background-color: {DARK_BORDER}; color: {TEXT_MUTED}; }}
    QTabWidget::pane {{
        border: 1px solid {DARK_BORDER}; border-radius: 8px; background-color: {DARK_CARD};
    }}
    QTabBar::tab {{
        padding: 10px 20px; margin-right: 5px;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
        background-color: {DARK_INPUT}; color: {TEXT_PRIMARY}; font-weight: bold;
    }}
    QTabBar::tab:selected {{ background-color: {ACCENT}; color: white; }}
    QStatusBar {{ background-color: {DARK_CARD}; color: {TEXT_MUTED}; }}
    QScrollArea {{ border: none; background-color: transparent; }}
    QScrollBar:vertical {{
        background: {DARK_CARD}; width: 8px; border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {DARK_BORDER}; border-radius: 4px; min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QScrollBar:horizontal {{
        background: {DARK_CARD}; height: 8px; border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {DARK_BORDER}; border-radius: 4px; min-width: 20px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
"""


class MainWindow(QMainWindow):
    def __init__(self, user: dict, auth_connector: AuthConnector):
        super().__init__()
        self.user = user
        self.auth_connector = auth_connector
        self.product_connector = ProductConnector()
        self.order_connector = OrderConnector()

        self.setStyleSheet(MAIN_STYLE)
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.load_dashboard_data()
        logger.info(f"Main window opened for user: {user.get('email')}")

    def setup_ui(self):
        self.setWindowTitle(f"E-Commerce Orders - {self.user.get('name', 'Usuário')}")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {DARK_BG};")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.tabs = QTabWidget()
        self.tab_dashboard = self._create_dashboard_tab()
        self.tabs.addTab(self.tab_dashboard, "📊 Dashboard")
        self.tab_products = self._create_products_tab()
        self.tabs.addTab(self.tab_products, "📦 Produtos")
        self.tab_orders = self._create_orders_tab()
        self.tabs.addTab(self.tab_orders, "📋 Pedidos")
        main_layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema pronto")

    def setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("📁 Arquivo")
        logout_action = QAction("🚪 Sair", self)
        logout_action.setShortcut("Ctrl+Q")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

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

        help_menu = menubar.addMenu("❓ Ajuda")
        about_action = QAction("ℹ️ Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        toolbar = self.addToolBar("Ferramentas")
        toolbar.setMovable(False)

        add_prod_btn = QPushButton("➕ Novo Produto")
        add_prod_btn.clicked.connect(self.open_add_product)
        toolbar.addWidget(add_prod_btn)
        toolbar.addSeparator()

        create_order_btn = QPushButton("➕ Novo Pedido")
        create_order_btn.clicked.connect(self.open_create_order)
        toolbar.addWidget(create_order_btn)
        toolbar.addSeparator()

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.load_dashboard_data)
        toolbar.addWidget(refresh_btn)

        from PyQt6.QtWidgets import QSizePolicy
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        user_label = QLabel(f"👤 {self.user.get('name', 'Usuário')}")
        user_label.setStyleSheet(f"font-weight: bold; padding: 5px; color: {TEXT_PRIMARY};")
        toolbar.addWidget(user_label)

    # ========== DASHBOARD TAB ==========

    def _create_dashboard_tab(self):
        # Outer widget with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content = QWidget()
        content.setStyleSheet(f"background-color: {DARK_BG};")
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)

        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        self.card_products     = self._create_stat_card("Total Produtos",  "0",       "📦", ACCENT)
        self.card_orders       = self._create_stat_card("Total Pedidos",   "0",       "📋", SUCCESS)
        self.card_orders_active= self._create_stat_card("Pedidos Ativos",  "0",       "🔄", "#f39c12")
        self.card_revenue      = self._create_stat_card("Faturamento",     "R$ 0,00", "💰", "#9b59b6")
        for card in [self.card_products, self.card_orders, self.card_orders_active, self.card_revenue]:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)

        # Recent orders
        recent_label = QLabel("📋 Últimos Pedidos")
        recent_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {TEXT_PRIMARY};")
        layout.addWidget(recent_label)

        self.recent_orders_table = TableWidget(headers=["id", "customer", "status", "total", "date"],
                                               display_headers=["ID", "Cliente", "Status", "Total", "Data"])
        self.recent_orders_table.set_status_filter_visible(False)
        self.recent_orders_table.item_selected.connect(self._on_order_selected)
        self.recent_orders_table.setMinimumHeight(200)
        layout.addWidget(self.recent_orders_table)

        # Recent products
        recent_products_label = QLabel("📦 Últimos Produtos")
        recent_products_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {TEXT_PRIMARY};")
        layout.addWidget(recent_products_label)

        self.recent_products_grid = QGridLayout()
        self.recent_products_grid.setSpacing(15)
        layout.addLayout(self.recent_products_grid)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _create_stat_card(self, title, value, icon, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 12px;
                padding: 15px;
                min-height: 90px;
                min-width: 160px;
            }}
        """)
        card_layout = QVBoxLayout(card)

        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED}; background: transparent;")
        card_layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName(f"stat_{title.replace(' ', '_')}")
        value_label.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {color}; background: transparent;")
        card_layout.addWidget(value_label)
        return card

    # ========== PRODUCTS TAB ==========

    def _create_products_tab(self):
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {DARK_CARD};")
        layout = QVBoxLayout(widget)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Cadastrar Produto")
        add_btn.clicked.connect(self.open_add_product)
        toolbar.addWidget(add_btn)
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.load_products)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.products_table = TableWidget(headers=["id", "description", "price", "quantity_available", "date"],
                                           display_headers=["ID", "Descrição", "Preço", "Estoque", "Data"])
        self.products_table.item_selected.connect(self._on_product_selected)
        layout.addWidget(self.products_table)
        return widget

    # ========== ORDERS TAB ==========

    def _create_orders_tab(self):
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {DARK_CARD};")
        layout = QVBoxLayout(widget)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Criar Pedido")
        add_btn.clicked.connect(self.open_create_order)
        toolbar.addWidget(add_btn)
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.load_orders)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.orders_table = TableWidget(headers=["id", "customer", "status", "total", "items", "date"],
                                         display_headers=["ID", "Cliente", "Status", "Total", "Itens", "Data"])
        self.orders_table.set_status_filter_visible(True)
        self.orders_table.item_selected.connect(self._on_order_selected)
        layout.addWidget(self.orders_table)
        return widget

    # ========== DATA LOADING ==========

    def load_dashboard_data(self):
        self.load_stats()
        self.load_recent_orders()
        self.load_recent_products()

    def load_stats(self):
        try:
            products_result = self.product_connector.list_products()
            if products_result['success']:
                products = products_result['data'].get('products', [])
                self._update_stat_card("Total Produtos", str(len(products)))

            orders_result = self.order_connector.list_orders()
            if orders_result['success']:
                orders = orders_result['data'].get('orders', [])
                self._update_stat_card("Total Pedidos", str(len(orders)))
                active = [o for o in orders if o.get('status') not in ['completed', 'cancelled']]
                self._update_stat_card("Pedidos Ativos", str(len(active)))
                revenue = sum(o.get('total_amount', 0) for o in orders if o.get('status') == 'completed')
                self._update_stat_card("Faturamento", format_currency(revenue))
        except Exception as e:
            logger.error(f"Error loading stats: {e}")

    def _update_stat_card(self, title, value):
        for card in [self.card_products, self.card_orders, self.card_orders_active, self.card_revenue]:
            for label in card.findChildren(QLabel):
                if label.objectName() == f"stat_{title.replace(' ', '_')}":
                    label.setText(value)
                    return

    def load_recent_orders(self, limit=5):
        try:
            result = self.order_connector.list_orders()
            if result['success']:
                orders = result['data'].get('orders', [])[:limit]
                data = [{'id': o.get('id'), 'customer': o.get('customer'), 'status': o.get('status'),
                         'total': format_currency(o.get('total_amount', 0)),
                         'date': format_date(o.get('created_at', ''))} for o in orders]
                self.recent_orders_table.set_data(data)
        except Exception as e:
            logger.error(f"Error loading recent orders: {e}")

    def load_recent_products(self, limit=4):
        try:
            result = self.product_connector.list_products()
            if result['success']:
                products = result['data'].get('products', [])[:limit]
                for i in reversed(range(self.recent_products_grid.count())):
                    w = self.recent_products_grid.itemAt(i).widget()
                    if w:
                        w.deleteLater()
                for idx, product in enumerate(products):
                    pw = ProductWidget(product)
                    pw.product_clicked.connect(self._on_product_selected)
                    self.recent_products_grid.addWidget(pw, idx // 2, idx % 2)
        except Exception as e:
            logger.error(f"Error loading recent products: {e}")

    def load_products(self):
        try:
            result = self.product_connector.list_products()
            if result['success']:
                products = result['data'].get('products', [])
                data = [{'id': p.get('id'), 'description': p.get('description'),
                         'price': format_currency(p.get('price', 0)),
                         'quantity_available': p.get('quantity_available', 0),
                         'date': format_date(p.get('created_at', ''))} for p in products]
                self.products_table.set_data(data)
                self.status_bar.showMessage(f"✅ {len(products)} produtos carregados", 3000)
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.status_bar.showMessage("❌ Erro ao carregar produtos", 5000)

    def load_orders(self):
        try:
            result = self.order_connector.list_orders()
            if result['success']:
                orders = result['data'].get('orders', [])
                data = [{'id': o.get('id'), 'customer': o.get('customer'), 'status': o.get('status'),
                         'total': format_currency(o.get('total_amount', 0)),
                         'items': len(o.get('items', [])),
                         'date': format_date(o.get('created_at', ''))} for o in orders]
                self.orders_table.set_data(data)
                self.status_bar.showMessage(f"✅ {len(orders)} pedidos carregados", 3000)
        except Exception as e:
            logger.error(f"Error loading orders: {e}")
            self.status_bar.showMessage("❌ Erro ao carregar pedidos", 5000)

    # ========== EVENT HANDLERS ==========

    def _on_product_selected(self, product_data: dict):
        QMessageBox.information(self, "Detalhes do Produto",
            f"<b>ID:</b> {product_data.get('id')}<br>"
            f"<b>Descrição:</b> {product_data.get('description')}<br>"
            f"<b>Preço:</b> {format_currency(product_data.get('price', 0))}<br>"
            f"<b>Estoque:</b> {product_data.get('quantity_available', 0)}")

    def _on_order_selected(self, order_data: dict):
        QMessageBox.information(self, "Detalhes do Pedido",
            f"<b>ID:</b> {order_data.get('id')}<br>"
            f"<b>Cliente:</b> {order_data.get('customer')}<br>"
            f"<b>Status:</b> {order_data.get('status')}<br>"
            f"<b>Total:</b> {format_currency(order_data.get('total_amount', 0))}<br>"
            f"<b>Data:</b> {format_date(order_data.get('created_at', ''))}")

    # ========== DIALOGS ==========

    def open_add_product(self):
        dialog = AddProductDialog(self.product_connector, None, self)
        if dialog.exec():
            self.load_products()
            self.load_dashboard_data()
            self.status_bar.showMessage("✅ Produto cadastrado com sucesso!", 3000)

    def open_create_order(self):
        dialog = CreateOrderDialog(self.order_connector, self.product_connector, self)
        if dialog.exec():
            self.load_orders()
            self.load_dashboard_data()
            self.status_bar.showMessage("✅ Pedido criado com sucesso!", 3000)

    def open_add_item_to_order(self, order_id):
        dialog = AddItemDialog(order_id, self.order_connector, self.product_connector, self)
        if dialog.exec():
            self.load_orders()
            self.load_dashboard_data()

    # ========== ACTIONS ==========

    def logout(self):
        if QMessageBox.question(self, "Confirmar saída", "Tem certeza que deseja sair?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.auth_connector.logout()
            self.close()

    def show_about(self):
        QMessageBox.about(self, "Sobre",
            "<h2>📦 E-Commerce Orders</h2>"
            "<p><b>Versão:</b> 1.0.0</p>"
            "<p>Sistema de gerenciamento de pedidos para e-commerce.</p>"
            "<p><b>Tecnologias:</b> Python 3.x · PyQt6 · PostgreSQL</p>")

    def closeEvent(self, event):
        logger.info("Main window closed")
        event.accept()
