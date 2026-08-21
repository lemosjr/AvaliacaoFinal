# AvaliacaoFinal — E-Commerce Orders

Aplicação desktop de gerenciamento de pedidos e produtos, desenvolvida com **PyQt6** (interface gráfica) e **PostgreSQL** (banco de dados). A comunicação entre frontend e backend é feita diretamente via classes connector, sem servidor HTTP.

---

## Pré-requisitos

- Python 3.10+
- PostgreSQL instalado e rodando localmente
- Git (opcional)

---

## Configuração do Banco de Dados

1. Abra o **pgAdmin** ou o **psql** e crie o banco de dados:

```sql
CREATE DATABASE ecommerce;
```

2. Confirme que o usuário e senha do PostgreSQL batem com o arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=postgres
```

> Edite o `.env` se o seu usuário ou senha forem diferentes.

---

## Instalação das Dependências

Na raiz do projeto (`c:\AvaliacaoFinal`), execute:

```bash
pip install -r requirements.txt
```

---

## Como Rodar

Na raiz do projeto, execute:

```bash
python main.py
```

Na primeira execução, as migrations rodam automaticamente e o banco é populado com dados de exemplo (produtos, pedidos e o usuário admin).

---

## Como Logar

Use as credenciais do usuário administrador criado pelo seeder:

| Campo | Valor |
|-------|-------|
| **E-mail** | `admin@ecommerce.com` |
| **Senha** | `admin123` |

> Caso o login falhe com essas credenciais, veja a seção **Troubleshooting** abaixo.

---

## Estrutura do Projeto

```
AvaliacaoFinal/
├── main.py                  # Ponto de entrada da aplicação
├── .env                     # Variáveis de ambiente (DB, JWT, etc.)
├── requirements.txt         # Dependências Python
├── backend/
│   ├── config/              # Configurações de banco e settings
│   ├── controller/          # Lógica de controle (auth, orders, products)
│   ├── migrations/          # Migrations e seeders
│   ├── model/               # Modelos de dados
│   ├── repository/          # Acesso ao banco de dados
│   ├── service/             # Regras de negócio
│   └── utils/               # Utilitários (JWT, hash, logger)
└── frontend/
    └── src/
        ├── connectors/      # Ponte entre frontend e backend
        ├── dialogs/         # Janelas de criação/edição
        ├── widgets/         # Componentes reutilizáveis
        ├── login_window.py  # Tela de login
        └── main_window.py   # Tela principal
```

---

## Troubleshooting

**Login falha com `admin@ecommerce.com` / `admin123`**

O hash de senha do seeder pode ser incompatível com a versão do bcrypt instalada. Para corrigir, gere um novo hash e atualize o banco:

```python
# execute no terminal Python (python -c "...")
import bcrypt
print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())
```

Copie o hash gerado e execute no psql:

```sql
UPDATE users SET password_hash = '<hash_gerado>' WHERE email = 'admin@ecommerce.com';
```

**Erro de conexão com o banco**

- Confirme que o PostgreSQL está rodando
- Confirme que o banco `ecommerce` existe
- Verifique as credenciais no `.env`

**Módulo não encontrado**

Certifique-se de rodar `python main.py` a partir da raiz `c:\AvaliacaoFinal` e não de dentro de subpastas.
