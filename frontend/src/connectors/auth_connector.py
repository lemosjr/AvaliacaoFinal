# frontend/src/connectors/auth_connector.py
"""
Auth Connector - Ponte entre a interface e o AuthController.
"""

from backend.controller.auth_controller import AuthController
from frontend.src.connectors.base_connector import BaseConnector
from frontend.src.utils.session_manager import session
import logging

logger = logging.getLogger(__name__)


class AuthConnector(BaseConnector):
    """Conector para operações de autenticação."""

    def __init__(self):
        self.controller = AuthController()

    def login(self, email: str, password: str, remember: bool = False) -> dict:
        """
        Realiza login do usuário.

        Args:
            email: Email do usuário
            password: Senha
            remember: Se True, mantém sessão

        Returns:
            Dict com 'success' e 'data' (usuário) ou 'error'
        """
        logger.info(f"Attempting login for: {email}")

        result = self._handle_error(
            self.controller.login,
            {'email': email, 'password': password}
        )

        if result['success']:
            user = result['data']['user']
            token = result['data']['token']
            # Salva sessão
            session.set_session(user, token, remember=remember)
            logger.info(f"Login successful for: {email}")

        return result

    def register(self, name: str, email: str, password: str, password_confirm: str) -> dict:
        """
        Registra um novo usuário.

        Args:
            name: Nome completo
            email: Email
            password: Senha
            password_confirm: Confirmação de senha

        Returns:
            Dict com 'success' e 'data' ou 'error'
        """
        logger.info(f"Attempting registration for: {email}")

        result = self._handle_error(
            self.controller.register,
            {
                'name': name,
                'email': email,
                'password': password,
                'password_confirm': password_confirm
            }
        )

        if result['success']:
            logger.info(f"Registration successful for: {email}")

        return result

    def logout(self) -> dict:
        """Realiza logout do usuário."""
        session.clear_session()
        logger.info("User logged out")
        return {'success': True, 'message': 'Logged out successfully'}

    def get_current_user(self) -> dict:
        """Retorna o usuário atual."""
        user = session.get_user()
        if user:
            return {'success': True, 'data': user}
        return {'success': False, 'error': 'No user logged in'}

    def is_authenticated(self) -> bool:
        """Verifica se há usuário autenticado."""
        return session.is_authenticated()

    def refresh_token(self) -> dict:
        """
        Atualiza o token JWT.

        Returns:
            Dict com 'success' e novo token ou 'error'
        """
        token = session.get_token()
        if not token:
            return {'success': False, 'error': 'No token to refresh'}

        result = self._handle_error(
            self.controller.refresh_token,
            token
        )

        if result['success']:
            new_token = result['data']['token']
            # Atualiza token na sessão
            user = session.get_user()
            session.set_session(user, new_token, remember=False)
            logger.info("Token refreshed successfully")

        return result