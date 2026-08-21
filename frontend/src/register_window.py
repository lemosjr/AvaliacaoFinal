# frontend/src/register_window.py
"""
Register Window - Tela de cadastro de novos usuários.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QMessageBox, QStatusBar, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from frontend.src.connectors.auth_connector import AuthConnector
import logging

logger = logging.getLogger(__name__)


class RegisterWindow(QMainWindow):
    """
    Janela de registro de novos usuários.
    """

    # Sinal emitido quando o registro é bem-sucedido (volta para login)
    registration_success = pyqtSignal()

    def __init__(self, auth_connector: AuthConnector = None):
        super().__init__()

        self.auth_connector = auth_connector or AuthConnector()
        self._is_loading = False

        self.setup_ui()
        self.setup_connections()
        self.apply_styles()

        logger.info("Register window initialized")

    def setup_ui(self):
        """Configura a interface da janela."""
        self.setWindowTitle("E-Commerce Orders - Criar Conta")
        self.setFixedSize(440, 580)
        self.setMinimumSize(400, 520)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(40, 30, 40, 25)

        # ===== TÍTULO =====
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        # Ícone
        logo_label = QLabel("📝")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 40px;")
        title_layout.addWidget(logo_label)

        # Título
        title_label = QLabel("Criar Nova Conta")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Preencha os dados abaixo para se cadastrar")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        title_layout.addWidget(subtitle_label)

        main_layout.addLayout(title_layout)
        main_layout.addSpacing(5)

        # ===== CAMPOS DO FORMULÁRIO =====
        # Nome
        name_label = QLabel("Nome completo")
        name_label.setStyleSheet("font-weight: bold; color: #34495e;")
        main_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Seu nome completo")
        self.name_input.setStyleSheet(self._input_style())
        self.name_input.setMinimumHeight(40)
        main_layout.addWidget(self.name_input)

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
        self.password_input.setPlaceholderText("Mínimo 8 caracteres, com número e maiúscula")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.setMinimumHeight(40)
        main_layout.addWidget(self.password_input)

        # Confirmar senha
        confirm_label = QLabel("Confirmar senha")
        confirm_label.setStyleSheet("font-weight: bold; color: #34495e;")
        main_layout.addWidget(confirm_label)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Digite a senha novamente")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setStyleSheet(self._input_style())
        self.confirm_input.setMinimumHeight(40)
        main_layout.addWidget(self.confirm_input)

        # Espaço para requisitos de senha (opcional)
        self.password_hint = QLabel("🔒 A senha deve ter: 8+ caracteres, 1 número, 1 letra maiúscula")
        self.password_hint.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        main_layout.addWidget(self.password_hint)

        # ===== TERMOS E CONDIÇÕES =====
        terms_layout = QHBoxLayout()
        terms_layout.setContentsMargins(0, 5, 0, 5)

        self.terms_check = QCheckBox("Li e aceito os ")
        self.terms_check.setStyleSheet("color: #7f8c8d;")
        terms_layout.addWidget(self.terms_check)

        terms_link = QLabel("<a href='#' style='color: #3498db; text-decoration: none;'>Termos de Uso</a>")
        terms_link.setOpenExternalLinks(False)
        terms_link.linkActivated.connect(self._show_terms)
        terms_layout.addWidget(terms_link)

        terms_layout.addStretch()
        main_layout.addLayout(terms_layout)

        # ===== BOTÃO REGISTRAR =====
        self.register_button = QPushButton("Criar Conta")
        self.register_button.setStyleSheet(self._button_style())
        self.register_button.setMinimumHeight(45)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.register_button)

        # ===== LINK PARA LOGIN =====
        login_layout = QHBoxLayout()
        login_layout.addStretch()

        login_text = QLabel("Já tem uma conta?")
        login_text.setStyleSheet("color: #7f8c8d;")
        login_layout.addWidget(login_text)

        self.login_link = QLabel("<a href='#' style='color: #3498db; text-decoration: none; font-weight: bold;'>Fazer login</a>")
        self.login_link.setOpenExternalLinks(False)
        self.login_link.linkActivated.connect(self._open_login)
        login_layout.addWidget(self.login_link)

        login_layout.addStretch()
        main_layout.addLayout(login_layout)

        # Espaçamento inferior
        main_layout.addStretch()

        # ===== STATUS BAR =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Preencha os dados e clique em Criar Conta")

    def setup_connections(self):
        """Conecta sinais e slots."""
        self.register_button.clicked.connect(self.handle_register)

        # Enter key para registrar
        self.name_input.returnPressed.connect(self.handle_register)
        self.email_input.returnPressed.connect(self.handle_register)
        self.password_input.returnPressed.connect(self.handle_register)
        self.confirm_input.returnPressed.connect(self.handle_register)

    def apply_styles(self):
        """Aplica estilos visuais."""
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
        """Estilo dos campos de entrada."""
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
        """Estilo do botão principal."""
        return """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
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

    def handle_register(self):
        """Processa o registro do usuário."""
        if self._is_loading:
            return

        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        # ===== VALIDAÇÃO BÁSICA =====
        errors = []

        if not name:
            errors.append("Nome completo é obrigatório")
        elif len(name) < 3:
            errors.append("Nome deve ter pelo menos 3 caracteres")

        if not email:
            errors.append("Email é obrigatório")
        elif '@' not in email or '.' not in email:
            errors.append("Email inválido")

        if not password:
            errors.append("Senha é obrigatória")
        elif len(password) < 8:
            errors.append("Senha deve ter pelo menos 8 caracteres")

        if not confirm:
            errors.append("Confirmação de senha é obrigatória")
        elif password != confirm:
            errors.append("Senhas não coincidem")

        if not self.terms_check.isChecked():
            errors.append("Você deve aceitar os Termos de Uso")

        if errors:
            error_msg = "\n".join(f"• {e}" for e in errors)
            QMessageBox.warning(
                self,
                "Validação",
                f"Por favor, corrija os seguintes erros:\n\n{error_msg}",
                QMessageBox.StandardButton.Ok
            )
            self.status_bar.showMessage("Corrija os erros antes de continuar", 4000)
            return

        # ===== ENVIA REGISTRO =====
        self._set_loading(True)

        QTimer.singleShot(300, lambda: self._perform_register(name, email, password, confirm))

    def _perform_register(self, name: str, email: str, password: str, confirm: str):
        """Executa a requisição de registro."""
        try:
            result = self.auth_connector.register(name, email, password, confirm)

            if result['success']:
                self.status_bar.showMessage("✅ Conta criada com sucesso!", 3000)

                QMessageBox.information(
                    self,
                    "Registro concluído",
                    "🎉 Sua conta foi criada com sucesso!\n\n"
                    "Agora você pode fazer login com seu email e senha.",
                    QMessageBox.StandardButton.Ok
                )

                # Emite sinal para voltar ao login
                self.registration_success.emit()
                self.close()

            else:
                error_msg = result.get('error', 'Erro ao criar conta')
                QMessageBox.critical(
                    self,
                    "Erro no registro",
                    f"❌ {error_msg}\n\nPor favor, tente novamente.",
                    QMessageBox.StandardButton.Ok
                )
                self.status_bar.showMessage("Registro falhou. Verifique os dados.", 4000)

        except Exception as e:
            logger.error(f"Unexpected error in register: {str(e)}", exc_info=True)
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
        self.register_button.setEnabled(not loading)
        self.register_button.setText("⏳ Criando..." if loading else "Criar Conta")
        self.name_input.setEnabled(not loading)
        self.email_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)
        self.confirm_input.setEnabled(not loading)
        self.terms_check.setEnabled(not loading)

        if loading:
            self.status_bar.showMessage("Criando sua conta...")
        else:
            self.status_bar.showMessage("Pronto")

    def _open_login(self):
        """Volta para a tela de login."""
        self.registration_success.emit()
        self.close()

    def _show_terms(self):
        """Exibe os termos de uso (placeholder)."""
        QMessageBox.information(
            self,
            "Termos de Uso",
            "📋 Termos de Uso\n\n"
            "1. Ao criar uma conta, você concorda em fornecer informações verdadeiras.\n"
            "2. Você é responsável pela segurança de sua senha.\n"
            "3. O sistema é para uso acadêmico/demonstração.\n"
            "4. Os dados serão armazenados com segurança.\n\n"
            "Ao continuar, você concorda com estes termos.",
            QMessageBox.StandardButton.Ok
        )

    def closeEvent(self, event):
        """Evento de fechamento."""
        logger.info("Register window closed")
        event.accept()