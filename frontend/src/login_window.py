# frontend/src/login_window.py
"""
Login Window - Tela de autenticação do usuário.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

from frontend.src.connectors.auth_connector import AuthConnector
from frontend.src.utils.session_manager import session
import logging

logger = logging.getLogger(__name__)


class LoginWindow(QMainWindow):
    """
    Janela de login da aplicação.
    """

    # Sinal emitido quando o login é bem-sucedido
    login_success = pyqtSignal(dict)

    def __init__(self, auth_connector: AuthConnector = None):
        super().__init__()

        self.auth_connector = auth_connector or AuthConnector()

        # Verifica se já há sessão ativa
        if self.auth_connector.is_authenticated():
            # Emite sinal para abrir janela principal imediatamente
            QTimer.singleShot(100, lambda: self.login_success.emit(
                session.get_user()
            ))
            # Fecha a janela de login
            self.close()
            return

        self.setup_ui()
        self.setup_connections()
        self.apply_styles()

        logger.info("Login window initialized")

    def setup_ui(self):
        """Configura a interface da janela."""
        self.setWindowTitle("E-Commerce Orders - Login")
        self.setFixedSize(420, 520)
        self.setMinimumSize(380, 480)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 30)

        # ===== LOGO/TÍTULO =====
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        # Ícone/Logo (emoji como placeholder)
        logo_label = QLabel("📦")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px;")
        title_layout.addWidget(logo_label)

        # Título
        title_label = QLabel("E-Commerce Orders")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Sistema de Gerenciamento de Pedidos")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        title_layout.addWidget(subtitle_label)

        main_layout.addLayout(title_layout)

        # Espaçamento
        main_layout.addSpacing(10)

        # ===== CAMPOS DE LOGIN =====
        # Email
        email_label = QLabel("Email")
        email_label.setStyleSheet("font-weight: bold; color: #34495e;")
        main_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu@email.com")
        self.email_input.setStyleSheet(self._input_style())
        self.email_input.setMinimumHeight(40)
        main_layout.addWidget(self.email_input)

        # Senha
        password_label = QLabel("Senha")
        password_label.setStyleSheet("font-weight: bold; color: #34495e;")
        main_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.setMinimumHeight(40)
        main_layout.addWidget(self.password_input)

        # Opções (lembrar + esqueci senha)
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 5, 0, 5)

        self.remember_check = QCheckBox("Lembrar-me")
        self.remember_check.setStyleSheet("color: #7f8c8d;")
        options_layout.addWidget(self.remember_check)

        options_layout.addStretch()

        # Link "Esqueci a senha" (placeholder - não implementado)
        forgot_label = QLabel("<a href='#' style='color: #3498db; text-decoration: none;'>Esqueceu a senha?</a>")
        forgot_label.setOpenExternalLinks(False)
        forgot_label.linkActivated.connect(self._show_forgot_password)
        options_layout.addWidget(forgot_label)

        main_layout.addLayout(options_layout)

        # ===== BOTÃO LOGIN =====
        self.login_button = QPushButton("Entrar")
        self.login_button.setStyleSheet(self._button_style())
        self.login_button.setMinimumHeight(45)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.login_button)

        # ===== LINK PARA REGISTRO =====
        register_layout = QHBoxLayout()
        register_layout.addStretch()

        register_text = QLabel("Não tem uma conta?")
        register_text.setStyleSheet("color: #7f8c8d;")
        register_layout.addWidget(register_text)

        self.register_link = QLabel("<a href='#' style='color: #3498db; text-decoration: none; font-weight: bold;'>Criar conta</a>")
        self.register_link.setOpenExternalLinks(False)
        self.register_link.linkActivated.connect(self._open_register)
        register_layout.addWidget(self.register_link)

        register_layout.addStretch()
        main_layout.addLayout(register_layout)

        # Espaçamento inferior
        main_layout.addStretch()

        # ===== STATUS BAR =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Digite suas credenciais para acessar o sistema")

        # ===== CARREGANDO INDICATOR =====
        # Usado para desabilitar botão durante requisição
        self._is_loading = False

    def setup_connections(self):
        """Conecta os sinais e slots."""
        self.login_button.clicked.connect(self.handle_login)

        # Enter key para login
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def apply_styles(self):
        """Aplica estilos adicionais."""
        # Estilo geral da janela
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QWidget {
                background-color: transparent;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)

    def _input_style(self) -> str:
        """Estilo para campos de entrada."""
        return """
            QLineEdit {
                border: 2px solid #dcdde1;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f0f8ff;
            }
            QLineEdit:hover {
                border-color: #b2bec3;
            }
        """

    def _button_style(self) -> str:
        """Estilo para botões."""
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
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

    def handle_login(self):
        """Processa a tentativa de login."""
        if self._is_loading:
            return

        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        # Validação básica
        if not email or not password:
            QMessageBox.warning(
                self,
                "Campos obrigatórios",
                "Por favor, preencha todos os campos para continuar.",
                QMessageBox.StandardButton.Ok
            )
            return

        # Desabilita botão durante o processo
        self._set_loading(True)

        # Simula um pequeno delay para feedback visual
        QTimer.singleShot(300, lambda: self._perform_login(email, password))

    def _perform_login(self, email: str, password: str):
        """Executa a requisição de login."""
        try:
            remember = self.remember_check.isChecked()

            # Chama o connector
            result = self.auth_connector.login(email, password, remember=remember)

            if result['success']:
                user = result['data'].get('user', result['data'])
                self.status_bar.showMessage(f"Bem-vindo(a), {user['name']}!", 3000)

                # Emite sinal para abrir a janela principal
                self.login_success.emit(user)

                # Fecha a janela de login
                self.close()

            else:
                error_msg = result.get('error', 'Erro ao realizar login')
                QMessageBox.critical(
                    self,
                    "Erro de autenticação",
                    f"❌ {error_msg}\n\nVerifique seu email e senha e tente novamente.",
                    QMessageBox.StandardButton.Ok
                )
                self.status_bar.showMessage("Login falhou. Verifique suas credenciais.", 5000)

        except Exception as e:
            logger.error(f"Unexpected error in login: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Erro inesperado",
                "Ocorreu um erro inesperado. Tente novamente mais tarde.",
                QMessageBox.StandardButton.Ok
            )
        finally:
            self._set_loading(False)

    def _set_loading(self, loading: bool):
        """Atualiza estado de carregamento."""
        self._is_loading = loading
        self.login_button.setEnabled(not loading)
        self.login_button.setText("⏳ Entrando..." if loading else "Entrar")
        self.email_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)

        if loading:
            self.status_bar.showMessage("Autenticando...")
        else:
            self.status_bar.showMessage("Pronto")

    def _open_register(self):
        """Abre a janela de registro."""
        from frontend.src.register_window import RegisterWindow
        self.register_window = RegisterWindow(self.auth_connector)
        self.register_window.show()
        self.hide()

    def _show_forgot_password(self):
        """Exibe mensagem de funcionalidade futura."""
        QMessageBox.information(
            self,
            "Recuperação de senha",
            "🔐 A funcionalidade de recuperação de senha será implementada em breve.\n\n"
            "Por enquanto, entre em contato com o administrador do sistema.",
            QMessageBox.StandardButton.Ok
        )

    def closeEvent(self, event):
        """Evento de fechamento da janela."""
        logger.info("Login window closed")
        event.accept()