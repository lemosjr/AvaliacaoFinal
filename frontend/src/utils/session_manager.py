# frontend/src/utils/session_manager.py
"""
Session Manager - Singleton para gerenciar estado do usuário.
Persiste a sessão em memória e opcionalmente em disco.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Gerenciador de sessão singleton.
    Mantém o usuário atual e token, com persistência opcional.
    """

    _instance: Optional['SessionManager'] = None

    def __new__(cls) -> 'SessionManager':
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._user: Optional[Dict[str, Any]] = None
        self._token: Optional[str] = None
        self._session_file = Path.home() / '.ecommerce_session.json'
        self._load_session()
        logger.debug("SessionManager initialized")

    def set_session(self, user: Dict[str, Any], token: str, remember: bool = False) -> None:
        """
        Define a sessão atual.

        Args:
            user: Dados do usuário
            token: JWT token
            remember: Se True, persiste no disco
        """
        self._user = user
        self._token = token
        if remember:
            self._save_session()
        logger.info(f"Session set for user: {user.get('email')}")

    def get_user(self) -> Optional[Dict[str, Any]]:
        """Retorna o usuário atual."""
        return self._user

    def get_token(self) -> Optional[str]:
        """Retorna o token atual."""
        return self._token

    def is_authenticated(self) -> bool:
        """Verifica se o usuário está autenticado."""
        return self._user is not None and self._token is not None

    def clear_session(self) -> None:
        """Limpa a sessão atual."""
        self._user = None
        self._token = None
        self._delete_session_file()
        logger.info("Session cleared")

    def _save_session(self) -> None:
        """Salva a sessão no disco."""
        try:
            data = {
                'user': self._user,
                'token': self._token
            }
            with open(self._session_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Session saved to disk")
        except Exception as e:
            logger.warning(f"Could not save session: {str(e)}")

    def _load_session(self) -> None:
        """Carrega a sessão do disco."""
        try:
            if self._session_file.exists():
                with open(self._session_file, 'r') as f:
                    data = json.load(f)
                self._user = data.get('user')
                self._token = data.get('token')
                logger.debug("Session loaded from disk")
        except Exception as e:
            logger.warning(f"Could not load session: {str(e)}")

    def _delete_session_file(self) -> None:
        """Remove o arquivo de sessão."""
        try:
            if self._session_file.exists():
                self._session_file.unlink()
                logger.debug("Session file deleted")
        except Exception as e:
            logger.warning(f"Could not delete session file: {str(e)}")


# Singleton instance
session = SessionManager()