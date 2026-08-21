# frontend/src/styles/__init__.py
"""
Styles - Arquivos de estilo (QSS) para a aplicação.
"""

from pathlib import Path

STYLE_PATH = Path(__file__).parent / 'style.qss'

def load_stylesheet() -> str:
    """
    Carrega o arquivo de estilo QSS.

    Returns:
        str: Conteúdo do arquivo de estilo ou string vazia se não encontrado.
    """
    if STYLE_PATH.exists():
        with open(STYLE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

__all__ = ['STYLE_PATH', 'load_stylesheet']