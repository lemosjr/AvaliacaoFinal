# Documentação — E-Commerce Orders

## Objetivo

Aplicação desktop para gerenciamento de pedidos de e-commerce. Permite cadastrar produtos, criar pedidos, adicionar itens, calcular totais e acompanhar o ciclo de vida dos pedidos por meio de estados controlados.

---

## Funcionalidades

- Autenticação de usuário (login e registro)
- Cadastro e consulta de produtos
- Criação de pedidos com seleção de produtos e quantidades
- Cálculo automático do total do pedido
- Consulta de pedidos com filtro por status
- Alteração de situação do pedido respeitando transições válidas
- Validação de estoque antes de adicionar itens
- Dashboard com estatísticas gerais

---

## Estrutura do Projeto

```
AvaliacaoFinal/
├── main.py                        # Ponto de entrada
├── .env                           # Configurações de ambiente
├── requirements.txt
├── backend/
│   ├── config/                    # Conexão com banco e settings
│   ├── controller/                # Recebe chamadas do frontend, delega ao service
│   ├── migrations/                # Criação de tabelas e dados iniciais
│   ├── model/                     # Entidades: Product, Order, OrderItem, User
│   ├── repository/                # Acesso ao banco (CRUD genérico + específico)
│   ├── service/                   # Regras de negócio
│   ├── utils/                     # JWT, hash, logger, exceções
│   └── validation/                # Validadores de entrada
└── frontend/
    └── src/
        ├── connectors/            # Ponte entre UI e controllers
        ├── dialogs/               # Janelas modais (produto, pedido, item)
        ├── styles/                # QSS global e dark_theme.py
        ├── utils/                 # Formatadores, validadores, session
        ├── widgets/               # Componentes reutilizáveis (tabela, cards)
        ├── login_window.py
        ├── register_window.py
        └── main_window.py
```

---

## Armazenamento

PostgreSQL via psycopg2 com pool de conexões. As migrations rodam automaticamente na primeira execução e populam o banco com dados de exemplo (produtos, pedidos e usuário admin).

---

## Principais Regras Implementadas

- Preço do produto deve ser maior que zero
- Quantidade disponível não pode ser negativa
- Pedido exige cliente informado
- Não é possível adicionar quantidade superior ao estoque
- Pedido finalizado ou cancelado não aceita novos itens
- Transições de status seguem o fluxo: `created → processing → completed` ou `cancelled`
- Total do pedido é recalculado a cada item adicionado

---

## Decisões Técnicas

| Decisão | Justificativa |
|---|---|
| PyQt6 + PostgreSQL sem servidor HTTP | Requisito da atividade; comunicação direta via connectors |
| BaseRepository genérico com TypeVar | Evita duplicação de CRUD entre Product, Order e User |
| dark_theme.py centralizado | Elimina conflito entre estilos inline e QSS global |
| Conversão de tipos no `__init__` dos modelos | psycopg2 retorna `Decimal` para colunas NUMERIC; conversão garante compatibilidade com a UI |
| Separação `headers` / `display_headers` no TableWidget | Desacopla chaves do dict dos labels visíveis, evitando mapeamento frágil por string |
