# frontend/src/utils/constants.py
"""
Constants - Valores constantes usados em toda a aplicação.
"""

# ==================== APPLICATION ====================
APP_NAME = "E-Commerce Orders"
APP_VERSION = "1.0.0"

# ==================== ORDER STATUSES ====================
ORDER_STATUSES = {
    'created': 'Criado',
    'processing': 'Em Processamento',
    'completed': 'Finalizado',
    'cancelled': 'Cancelado'
}

# Cores para cada status (HTML/Hex)
STATUS_COLORS = {
    'created': '#3498db',      # Azul
    'processing': '#f39c12',   # Laranja
    'completed': '#2ecc71',    # Verde
    'cancelled': '#e74c3c'     # Vermelho
}

# Ícones para cada status
STATUS_ICONS = {
    'created': '🆕',
    'processing': '🔄',
    'completed': '✅',
    'cancelled': '❌'
}

# ==================== PRODUCT CATEGORIES ====================
PRODUCT_CATEGORIES = [
    'Eletrônicos',
    'Informática',
    'Acessórios',
    'Periféricos',
    'Áudio e Vídeo',
    'Casa e Jardim',
    'Escritório',
    'Games',
    'Smart Home',
    'Outros'
]

# ==================== UI SETTINGS ====================
UI_SETTINGS = {
    'window_min_width': 800,
    'window_min_height': 600,
    'table_font_size': 12,
    'button_height': 40,
    'input_height': 36,
    'padding': 12,
    'border_radius': 8,
    'animation_duration': 300,  # ms
}

# ==================== MESSAGES ====================
MESSAGES = {
    'login_success': 'Login realizado com sucesso!',
    'login_failed': 'Email ou senha inválidos. Tente novamente.',
    'registration_success': 'Usuário registrado com sucesso!',
    'registration_failed': 'Falha no registro. Verifique os dados.',
    'product_created': 'Produto criado com sucesso!',
    'product_updated': 'Produto atualizado com sucesso!',
    'product_deleted': 'Produto excluído com sucesso!',
    'order_created': 'Pedido criado com sucesso!',
    'order_updated': 'Pedido atualizado com sucesso!',
    'item_added': 'Item adicionado ao pedido!',
    'confirm_delete': 'Tem certeza que deseja excluir este item?',
    'confirm_cancel': 'Tem certeza que deseja cancelar esta operação?',
    'no_data': 'Nenhum dado encontrado.',
    'loading': 'Carregando...',
    'processing': 'Processando...',
    'error_generic': 'Ocorreu um erro inesperado. Tente novamente.',
    'error_network': 'Erro de conexão. Verifique sua internet.',
}

# ==================== VALIDATION ====================
VALIDATION = {
    'name_min_length': 2,
    'name_max_length': 100,
    'password_min_length': 8,
    'description_min_length': 3,
    'description_max_length': 200,
    'price_min': 0.01,
    'quantity_min': 0,
}