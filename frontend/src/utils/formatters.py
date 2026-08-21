# frontend/src/utils/formatters.py
"""
Formatters - Funções para formatar dados para exibição na interface.
"""

from datetime import datetime
from typing import Union, Optional
import re


def format_currency(value: Union[int, float]) -> str:
    """
    Formata um valor como moeda (R$).

    Args:
        value: Valor numérico

    Returns:
        str: Valor formatado (ex: R$ 1.234,56)
    """
    if value is None:
        return 'R$ 0,00'
    try:
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (TypeError, ValueError):
        return 'R$ 0,00'


def format_date(date_str: Optional[str]) -> str:
    """
    Formata uma string de data para exibição (dd/mm/aaaa).

    Args:
        date_str: String de data (ISO format)

    Returns:
        str: Data formatada
    """
    if not date_str:
        return ''
    try:
        # Tenta diferentes formatos
        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%d/%m/%Y')
            except ValueError:
                continue
        return date_str
    except (ValueError, TypeError):
        return date_str


def format_datetime(date_str: Optional[str]) -> str:
    """
    Formata uma string de data/hora para exibição (dd/mm/aaaa HH:MM).

    Args:
        date_str: String de data/hora (ISO format)

    Returns:
        str: Data/hora formatada
    """
    if not date_str:
        return ''
    try:
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%d/%m/%Y %H:%M')
            except ValueError:
                continue
        return date_str
    except (ValueError, TypeError):
        return date_str


def format_status(status: str) -> str:
    """
    Formata um status para exibição com ícone.

    Args:
        status: String do status (ex: 'created', 'processing')

    Returns:
        str: Status formatado com ícone
    """
    status_map = {
        'created': '🆕 Criado',
        'processing': '🔄 Processando',
        'completed': '✅ Finalizado',
        'cancelled': '❌ Cancelado'
    }
    return status_map.get(status.lower(), status.capitalize())


def format_quantity(quantity: int, show_unit: bool = True) -> str:
    """
    Formata uma quantidade para exibição.

    Args:
        quantity: Quantidade
        show_unit: Se True, adiciona "unidade(s)"

    Returns:
        str: Quantidade formatada
    """
    if quantity is None:
        return '0'
    try:
        qty = int(quantity)
        if show_unit:
            return f"{qty} unidade{'s' if qty != 1 else ''}"
        return str(qty)
    except (TypeError, ValueError):
        return str(quantity)


def format_phone(phone: Optional[str]) -> str:
    """
    Formata um número de telefone.

    Args:
        phone: Número de telefone (ex: '11999999999')

    Returns:
        str: Telefone formatado (ex: '(11) 99999-9999')
    """
    if not phone:
        return ''
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    return phone


def format_cpf_cnpj(value: Optional[str]) -> str:
    """
    Formata CPF ou CNPJ.

    Args:
        value: CPF ou CNPJ (apenas números)

    Returns:
        str: CPF/CNPJ formatado
    """
    if not value:
        return ''
    value = re.sub(r'\D', '', value)
    if len(value) == 11:
        return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"
    elif len(value) == 14:
        return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"
    return value


def truncate_text(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    Trunca um texto para um tamanho máximo.

    Args:
        text: Texto a ser truncado
        max_length: Tamanho máximo
        suffix: Sufixo para indicar truncamento

    Returns:
        str: Texto truncado
    """
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def capitalize_words(text: str) -> str:
    """
    Capitaliza cada palavra de um texto.

    Args:
        text: Texto a ser capitalizado

    Returns:
        str: Texto com palavras capitalizadas
    """
    if not text:
        return ''
    return ' '.join(word.capitalize() for word in text.split())