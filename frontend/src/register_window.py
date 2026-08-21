# frontend/src/register_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from frontend.src.connectors.auth_connector import AuthConnector
import logging

logger = logging.getLogger(__name__)

DARK_BG      = "#1e2a38"
DARK_CARD    = "#2c3e50"
DARK_INPUT   = "#34495e"
DARK_BORDER  = "#4a6278"
TEXT_PRIMARY = "#ecf0f1"
TEXT_MUTED   = "#95a5a6"
ACCENT       = "#3498db"


class RegisterWindow(QMainWindow):
    registration_success = pyqtSignal()

    def __init__(self, auth_connector: AuthConnector = None):
        super().__init__()
        self.auth_connector = auth_connector or AuthConnector()
        self._is_loading = False
        self.setup_ui()
        self.setup_connections()
        self._apply_dark_theme()
        logger.info("Register window initialized")

    def setup_ui(self):
        self.setWindowTitle("E-Commerce Orders - Criar Conta")
        self.setFixedSize(440, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(40, 30, 40, 25)

        logo_label = QLabel("📝")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 40px; background: transparent;")
        main_layout.addWidget(logo_label)

        title_label = QLabel("Criar Nova Conta")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {TEXT_PRIMARY}; background: transparent;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Preencha os dados abaixo para se cadastrar")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED}; background: transparent;")
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(5)

        for field_label in ["Nome completo", "Email", "Senha", "Confirmar senha"]:
            lbl = QLabel(field_label)
            lbl.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; background: transparent;")
            main_layout.addWidget(lbl)

            if field_label == "Nome completo":
                self.name_input = QLineEdit()
                self.name_input.setPlaceholderText("Seu nome completo")
                self.name_input.setMinimumHeight(40)
                main_layout.addWidget(self.name_input)
            elif field_label == "Email":
                self.email_input = QLineEdit()
                self.email_input.setPlaceholderText("seu@email.com")
                self.email_input.setMinimumHeight(40)
                main_layout.addWidget(self.email_input)
            elif field_label == "Senha":
                self.password_input = QLineEdit()
                self.password_input.setPlaceholderText("Mínimo 8 caracteres, com número e maiúscula")
                self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
                self.password_input.setMinimumHeight(40)
                main_layout.addWidget(self.password_input)
            elif field_label == "Confirmar senha":
                self.confirm_input = QLineEdit()
                self.confirm_input.setPlaceholderText("Digite a senha novamente")
                self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
                self.confirm_input.setMinimumHeight(40)
                main_layout.addWidget(self.confirm_input)

        hint = QLabel("🔒 A senha deve ter: 8+ caracteres, 1 número, 1 letra maiúscula")
        hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
        main_layout.addWidget(hint)

        terms_layout = QHBoxLayout()
        self.terms_check = QCheckBox("Li e aceito os ")
        terms_layout.addWidget(self.terms_check)
        terms_link = QLabel(f"<a href='#' style='color: {ACCENT}; text-decoration: none;'>Termos de Uso</a>")
        terms_link.setOpenExternalLinks(False)
        terms_link.linkActivated.connect(self._show_terms)
        terms_layout.addWidget(terms_link)
        terms_layout.addStretch()
        main_layout.addLayout(terms_layout)

        self.register_button = QPushButton("Criar Conta")
        self.register_button.setMinimumHeight(45)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.register_button)

        login_layout = QHBoxLayout()
        login_layout.addStretch()
        login_text = QLabel("Já tem uma conta?")
        login_text.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        login_layout.addWidget(login_text)
        self.login_link = QLabel(f"<a href='#' style='color: {ACCENT}; text-decoration: none; font-weight: bold;'>Fazer login</a>")
        self.login_link.setOpenExternalLinks(False)
        self.login_link.linkActivated.connect(self._open_login)
        login_layout.addWidget(self.login_link)
        login_layout.addStretch()
        main_layout.addLayout(login_layout)

        main_layout.addStretch()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Preencha os dados e clique em Criar Conta")

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
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #27ae60; }}
            QPushButton:pressed {{ background-color: #1e8449; }}
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
        self.register_button.clicked.connect(self.handle_register)
        self.name_input.returnPressed.connect(self.handle_register)
        self.email_input.returnPressed.connect(self.handle_register)
        self.password_input.returnPressed.connect(self.handle_register)
        self.confirm_input.returnPressed.connect(self.handle_register)

    def handle_register(self):
        if self._is_loading:
            return
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        errors = []
        if not name or len(name) < 3:
            errors.append("Nome deve ter pelo menos 3 caracteres")
        if not email or '@' not in email or '.' not in email:
            errors.append("Email inválido")
        if not password or len(password) < 8:
            errors.append("Senha deve ter pelo menos 8 caracteres")
        if password != confirm:
            errors.append("Senhas não coincidem")
        if not self.terms_check.isChecked():
            errors.append("Você deve aceitar os Termos de Uso")

        if errors:
            QMessageBox.warning(self, "Validação",
                "Por favor, corrija os seguintes erros:\n\n" + "\n".join(f"• {e}" for e in errors))
            return

        self._set_loading(True)
        QTimer.singleShot(300, lambda: self._perform_register(name, email, password, confirm))

    def _perform_register(self, name, email, password, confirm):
        try:
            result = self.auth_connector.register(name, email, password, confirm)
            if result['success']:
                QMessageBox.information(self, "Registro concluído",
                    "🎉 Sua conta foi criada com sucesso!\n\nAgora você pode fazer login.")
                self.registration_success.emit()
                self.close()
            else:
                QMessageBox.critical(self, "Erro no registro", f"❌ {result.get('error', 'Erro ao criar conta')}")
                self.status_bar.showMessage("Registro falhou.", 4000)
        except Exception as e:
            logger.error(f"Register error: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro inesperado", "Ocorreu um erro inesperado.")
        finally:
            self._set_loading(False)

    def _set_loading(self, loading):
        self._is_loading = loading
        self.register_button.setEnabled(not loading)
        self.register_button.setText("⏳ Criando..." if loading else "Criar Conta")
        for w in [self.name_input, self.email_input, self.password_input, self.confirm_input, self.terms_check]:
            w.setEnabled(not loading)
        self.status_bar.showMessage("Criando sua conta..." if loading else "Pronto")

    def _open_login(self):
        self.registration_success.emit()
        self.close()

    def _show_terms(self):
        QMessageBox.information(self, "Termos de Uso",
            "📋 Termos de Uso\n\n1. Forneça informações verdadeiras.\n"
            "2. Você é responsável pela segurança de sua senha.\n"
            "3. Sistema para uso acadêmico/demonstração.")

    def closeEvent(self, event):
        logger.info("Register window closed")
        event.accept()
