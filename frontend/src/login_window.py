# frontend/src/login_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from frontend.src.connectors.auth_connector import AuthConnector
from frontend.src.utils.session_manager import session
import logging

logger = logging.getLogger(__name__)

DARK_BG       = "#1e2a38"
DARK_CARD     = "#2c3e50"
DARK_INPUT    = "#34495e"
DARK_BORDER   = "#4a6278"
TEXT_PRIMARY  = "#ecf0f1"
TEXT_MUTED    = "#95a5a6"
ACCENT        = "#3498db"
ACCENT_HOVER  = "#2980b9"


class LoginWindow(QMainWindow):
    login_success = pyqtSignal(dict)

    def __init__(self, auth_connector: AuthConnector = None):
        super().__init__()
        self.auth_connector = auth_connector or AuthConnector()

        if self.auth_connector.is_authenticated():
            QTimer.singleShot(100, lambda: self.login_success.emit(session.get_user()))
            self.close()
            return

        self.setup_ui()
        self.setup_connections()
        self._apply_dark_theme()
        self._is_loading = False
        logger.info("Login window initialized")

    def setup_ui(self):
        self.setWindowTitle("E-Commerce Orders - Login")
        self.setFixedSize(420, 520)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 30)

        logo_label = QLabel("📦")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px; background: transparent;")
        main_layout.addWidget(logo_label)

        title_label = QLabel("E-Commerce Orders")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {TEXT_PRIMARY}; background: transparent;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Sistema de Gerenciamento de Pedidos")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED}; background: transparent;")
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(10)

        email_label = QLabel("Email")
        email_label.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; background: transparent;")
        main_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu@email.com")
        self.email_input.setMinimumHeight(40)
        main_layout.addWidget(self.email_input)

        password_label = QLabel("Senha")
        password_label.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; background: transparent;")
        main_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        main_layout.addWidget(self.password_input)

        options_layout = QHBoxLayout()
        self.remember_check = QCheckBox("Lembrar-me")
        options_layout.addWidget(self.remember_check)
        options_layout.addStretch()

        forgot_label = QLabel(f"<a href='#' style='color: {ACCENT}; text-decoration: none;'>Esqueceu a senha?</a>")
        forgot_label.setOpenExternalLinks(False)
        forgot_label.linkActivated.connect(self._show_forgot_password)
        options_layout.addWidget(forgot_label)
        main_layout.addLayout(options_layout)

        self.login_button = QPushButton("Entrar")
        self.login_button.setMinimumHeight(45)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.login_button)

        reg_layout = QHBoxLayout()
        reg_layout.addStretch()
        reg_text = QLabel("Não tem uma conta?")
        reg_text.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        reg_layout.addWidget(reg_text)
        self.register_link = QLabel(f"<a href='#' style='color: {ACCENT}; text-decoration: none; font-weight: bold;'>Criar conta</a>")
        self.register_link.setOpenExternalLinks(False)
        self.register_link.linkActivated.connect(self._open_register)
        reg_layout.addWidget(self.register_link)
        reg_layout.addStretch()
        main_layout.addLayout(reg_layout)

        main_layout.addStretch()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Digite suas credenciais para acessar o sistema")

    def _apply_dark_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {DARK_BG}; }}
            QWidget {{ background-color: transparent; color: {TEXT_PRIMARY}; font-family: "Segoe UI", Arial, sans-serif; }}
            QLineEdit {{
                background-color: {DARK_INPUT};
                border: 2px solid {DARK_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                color: {TEXT_PRIMARY};
                font-size: 14px;
            }}
            QLineEdit:focus {{ border: 2px solid {ACCENT}; }}
            QLineEdit::placeholder {{ color: {TEXT_MUTED}; }}
            QPushButton {{
                background-color: {ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
            QPushButton:pressed {{ background-color: #1c6ea4; }}
            QPushButton:disabled {{ background-color: {DARK_BORDER}; color: {TEXT_MUTED}; }}
            QCheckBox {{ color: {TEXT_MUTED}; }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                background-color: {DARK_INPUT};
                border: 2px solid {DARK_BORDER};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {ACCENT};
                border: 2px solid {ACCENT};
            }}
            QStatusBar {{ background-color: {DARK_CARD}; color: {TEXT_MUTED}; }}
        """)

    def setup_connections(self):
        self.login_button.clicked.connect(self.handle_login)
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        if self._is_loading:
            return
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Campos obrigatórios", "Por favor, preencha todos os campos.")
            return
        self._set_loading(True)
        QTimer.singleShot(300, lambda: self._perform_login(email, password))

    def _perform_login(self, email, password):
        try:
            result = self.auth_connector.login(email, password, remember=self.remember_check.isChecked())
            if result['success']:
                user = result['data'].get('user', result['data'])
                self.login_success.emit(user)
                self.close()
            else:
                QMessageBox.critical(self, "Erro de autenticação", f"❌ {result.get('error', 'Erro ao realizar login')}")
                self.status_bar.showMessage("Login falhou.", 5000)
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro inesperado", "Ocorreu um erro inesperado.")
        finally:
            self._set_loading(False)

    def _set_loading(self, loading):
        self._is_loading = loading
        self.login_button.setEnabled(not loading)
        self.login_button.setText("⏳ Entrando..." if loading else "Entrar")
        self.email_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)
        self.status_bar.showMessage("Autenticando..." if loading else "Pronto")

    def _open_register(self):
        from frontend.src.register_window import RegisterWindow
        self.register_window = RegisterWindow(self.auth_connector)
        self.register_window.registration_success.connect(self._on_register_back)
        self.register_window.show()
        self.hide()

    def _on_register_back(self):
        self.show()

    def _show_forgot_password(self):
        QMessageBox.information(self, "Recuperação de senha",
            "🔐 Funcionalidade será implementada em breve.\n\nEntre em contato com o administrador.")

    def closeEvent(self, event):
        logger.info("Login window closed")
        event.accept()
