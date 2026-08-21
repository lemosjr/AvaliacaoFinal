# frontend/src/connectors/base_connector.py
"""
Base connector with common error handling for all connectors.
"""

import logging
from typing import Callable, Any, Dict, Optional

from backend.utils.exceptions import AppException, ValidationError, AuthenticationError, NotFoundError, BusinessRuleError

logger = logging.getLogger(__name__)


class BaseConnector:
    """
    Classe base para connectors.
    Fornece tratamento uniforme de erros e logging.
    """

    def _handle_error(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Executa uma função e trata exceções de forma consistente.

        Args:
            func: Função a ser executada
            *args, **kwargs: Argumentos da função

        Returns:
            Dict com 'success' e 'data' ou 'error'
        """
        try:
            result = func(*args, **kwargs)

            # Se o resultado já for um dict com 'success', retorna diretamente
            if isinstance(result, dict) and 'success' in result:
                return result

            # Caso contrário, embrulha em um dict de sucesso
            return {'success': True, 'data': result}

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'code': 'VALIDATION_ERROR',
                'details': e.details
            }

        except AuthenticationError as e:
            logger.warning(f"Authentication error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'code': 'AUTHENTICATION_ERROR'
            }

        except NotFoundError as e:
            logger.warning(f"Not found error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'code': 'NOT_FOUND'
            }

        except BusinessRuleError as e:
            logger.warning(f"Business rule error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'code': e.code,
                'details': e.details
            }

        except AppException as e:
            logger.error(f"Application error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'code': e.code,
                'details': e.details
            }

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'An unexpected error occurred. Please try again.',
                'code': 'INTERNAL_ERROR'
            }

    def _handle_sync(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Sinônimo de _handle_error para clareza.
        """
        return self._handle_error(func, *args, **kwargs)