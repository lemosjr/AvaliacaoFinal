# frontend/src/utils/validators.py
"""
Validators - Funções de validação para uso no frontend.
São validações rápidas para feedback imediato ao usuário.
"""

import re
from typing import Optional, Any


def validate_required(value: Any, field_name: str = "Campo") -> Optional[str]:
    """
    Valida se um campo não está vazio.

    Args:
        value: Valor a ser validado
        field_name: Nome do campo (para mensagem de erro)

    Returns:
        str: Mensagem de erro ou None se válido
    """
    if value is None or value == '' or (isinstance(value, str) and not value.strip()):
        return f"{field_name} é obrigatório"
    return None


def validate_length(value: str, min_len: int, max_len: int, field_name: str = "Campo") -> Optional[str]:
    """
    Valida o comprimento de uma string.

    Args:
        value: String a ser validada
        min_len: Comprimento mínimo
        max_len: Comprimento máximo
        field_name: Nome do campo (para mensagem de erro)

    Returns:
        str: Mensagem de erro ou None se válido
    """
    if not value:
        return f"{field_name} é obrigatório"
    if len(value) < min_len:
        return f"{field_name} deve ter pelo menos {min_len} caracteres"
    if len(value) > max_len:
        return f"{field_name} deve ter no máximo {max_len} caracteres"
    return None


def validate_email_frontend(email: str) -> Optional[str]:
    """
    Valida formato de email.

    Args:
        email: Email a ser validado

    Returns:
        str: Mensagem de erro ou None se válido
    """
    if not email:
        return "Email é obrigatório"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return "Formato de email inválido"
    return None


def validate_password_frontend(password: str, min_length: int = 8) -> Optional[str]:
    """
    Valida força da senha.

    Args:
        password: Senha a ser validada
        min_length: Comprimento mínimo

    Returns:
        str: Mensagem de erro ou None se válido
    """
    if not password:
        return "Senha é obrigatória"
    if len(password) < min_length:
        return f"Senha deve ter pelo menos {min_length} caracteres"
    if not re.search(r'\d', password):
        return "Senha deve conter pelo menos um número"
    if not re.search(r'[A-Z]', password):
        return "Senha deve conter pelo menos uma letra maiúscula"
    if not re.search(r'[a-z]', password):
        return "Senha deve conter pelo menos uma letra minúscula"
    return None


def validate_positive_number(value: Any, field_name: str = "Valor") -> Optional[str]:
    """
    Valida se um valor é um número positivo.

    Args:
        value: Valor a ser validado
        field_name: Nome do campo (para mensagem de erro)

    Returns:
        str: Mensagem de erro ou None se válido
    """
    if value is None:
        return f"{field_name} é obrigatório"
    try:
        num = float(value)
        if num < 0:
            return f"{field_name} deve ser positivo"
        return None
    except (TypeError, ValueError):
        return f"{field_name} deve ser um número válido"


def validate_price_frontend(value: Any) -> Optional[str]:
    """
    Valida se um valor é um preço válido (> 0).

    Args:
        value: Valor a ser validado

    Returns:
        str: Mensagem de erro ou None se válido
    """
    if value is None:
        return "Preço é obrigatório"
    try:
        price = float(value)
        if price <= 0:
            return "Preço deve ser maior que zero"
        if price > 999999.99:
            return "Preço muito alto"
        return None
    except (TypeError, ValueError):
        return "Preço deve ser um número válido"


def validate_quantity_frontend(value: Any) -> Optional[str]:
    """
    Valida se um valor é uma quantidade válida.

    Args:
        value: Valor a ser validado

    Returns:
        str: Mensagem de erro ou None se válido
    """
    if value is None:
        return "Quantidade é obrigatória"
    try:
        qty = int(value)
        if qty < 0:
            return "Quantidade não pode ser negativa"
        if qty > 99999:
            return "Quantidade muito alta"
        return None
    except (TypeError, ValueError):
        return "Quantidade deve ser um número inteiro"