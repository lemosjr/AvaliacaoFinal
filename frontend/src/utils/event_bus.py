# frontend/src/utils/event_bus.py
"""
Event Bus - Sistema de comunicação entre componentes desacoplados.
Permite que diferentes partes da aplicação troquem mensagens sem conhecer
diretamente umas às outras.
"""

from typing import Dict, List, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Event bus singleton para comunicação entre componentes.
    """

    _instance: Optional['EventBus'] = None

    def __new__(cls) -> 'EventBus':
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._listeners: Dict[str, List[Callable]] = {}
        self._once_listeners: Dict[str, List[Callable]] = {}
        logger.debug("EventBus initialized")

    def subscribe(self, event: str, callback: Callable) -> None:
        """
        Registra um listener para um evento.

        Args:
            event: Nome do evento (ex: 'product_updated')
            callback: Função a ser chamada quando o evento for emitido
        """
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
        logger.debug(f"Subscribed to event: {event}")

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """
        Remove um listener de um evento.

        Args:
            event: Nome do evento
            callback: Função a ser removida
        """
        if event in self._listeners:
            try:
                self._listeners[event].remove(callback)
                logger.debug(f"Unsubscribed from event: {event}")
            except ValueError:
                pass

    def once(self, event: str, callback: Callable) -> None:
        """
        Registra um listener que será executado apenas uma vez.

        Args:
            event: Nome do evento
            callback: Função a ser chamada uma única vez
        """
        if event not in self._once_listeners:
            self._once_listeners[event] = []
        self._once_listeners[event].append(callback)
        logger.debug(f"Registered once listener for: {event}")

    def emit(self, event: str, data: Any = None) -> None:
        """
        Emite um evento com dados.

        Args:
            event: Nome do evento
            data: Dados a serem passados para os listeners
        """
        # Chama listeners normais
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event listener for {event}: {str(e)}")

        # Chama listeners "once" e os remove
        if event in self._once_listeners:
            for callback in self._once_listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in once listener for {event}: {str(e)}")
            del self._once_listeners[event]

        logger.debug(f"Event emitted: {event}")

    def clear(self) -> None:
        """Remove todos os listeners."""
        self._listeners.clear()
        self._once_listeners.clear()
        logger.debug("EventBus cleared")

    def has_listeners(self, event: str) -> bool:
        """Verifica se há listeners para um evento."""
        return (event in self._listeners and len(self._listeners[event]) > 0) or \
               (event in self._once_listeners and len(self._once_listeners[event]) > 0)


# Singleton instance
event_bus = EventBus()