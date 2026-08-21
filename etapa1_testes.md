# test.md — Registro de Erros e Correções

## 1. Texto invisível nos campos de entrada (Login e Registro)

**Problema:** O `style.qss` global define `color: #ecf0f1` (branco) para todos os `QWidget`. Os inputs de login e registro sobrescreviam o fundo com `background-color: white`, mas não definiam `color`, tornando o texto digitado invisível.

**Correção:** Adicionado `color: #2c3e50` explicitamente nos estilos inline dos `QLineEdit` de `login_window.py` e `register_window.py`. Posteriormente, toda a aplicação foi migrada para dark theme completo via `dark_theme.py`, eliminando o conflito.

---

## 2. App fechava ao clicar "Fazer login" na tela de registro

**Problema:** `_open_register` em `login_window.py` chamava `self.hide()` mas não conectava o sinal `registration_success` da janela de registro. Ao fechar o registro, a janela de login permanecia oculta e o Qt encerrava o processo por não haver janelas visíveis.

**Correção:** Conectado `register_window.registration_success` ao método `_on_register_back`, que chama `self.show()` para reexibir o login.

---

## 3. Erro ao criar conta — `User with identifier '2' not found`

**Problema:** Em `base_repository.py`, o método `create` chamava `self.get_by_id(new_id)` **dentro** do bloco `with db.get_connection()`. O `get_by_id` abria uma nova conexão antes do commit da transação original ser efetivado, portanto o registro ainda não era visível no banco.

**Correção:** Movido o `get_by_id(new_id)` para **fora** do bloco `with`, garantindo que o commit ocorra antes da busca. O mesmo ajuste foi aplicado ao método `update`.

---

## 4. `AttributeError: 'QToolBar' object has no attribute 'addStretch'`

**Problema:** `QToolBar` no PyQt6 não possui o método `addStretch()`.

**Correção:** Substituído por um `QWidget` com `QSizePolicy.Policy.Expanding` adicionado via `toolbar.addWidget(spacer)`.

---

## 5. `AttributeError: 'MainWindow' object has no attribute 'get'`

**Problema:** Em `main_window.py`, `open_add_product` chamava `AddProductDialog(self.product_connector, self)`. A assinatura do dialog é `(product_connector, product_data, parent)`, então `self` (MainWindow) era interpretado como `product_data`, e o dialog tentava chamar `.get()` nele.

**Correção:** Corrigida a chamada para `AddProductDialog(self.product_connector, None, self)`.

---

## 6. Dashboard com tema claro — ilegível no dark theme

**Problema:** Estilos inline em `main_window.py`, `product_widget.py`, `order_widget.py` e `table_widget.py` usavam cores claras (`white`, `#f8f9fa`, `#ecf0f1` como fundo) que sobrescreviam o QSS global escuro.

**Correção:** Criado `dark_theme.py` com constantes de cor e estilos compartilhados. Todos os arquivos do frontend foram reescritos para usar exclusivamente as cores do dark theme (`#1e2a38`, `#2c3e50`, `#34495e`, `#ecf0f1`).

---

## 7. Cards de produto exibindo valores incorretos (Decimal do psycopg2)

**Problema:** O psycopg2 retorna colunas `NUMERIC`/`DECIMAL` do PostgreSQL como objetos `Decimal` do Python. Os modelos `Product`, `Order` e `OrderItem` armazenavam esses valores sem conversão, causando exibição incorreta (ex: `Decimal('49.90')` em vez de `49.90`).

**Correção:** Adicionadas conversões explícitas nos `__init__` dos três modelos:
- `Product`: `price → float`, `quantity_available → int`
- `Order`: `total_amount → float`
- `OrderItem`: `quantity → int`, `unit_price → float`, `subtotal → float`

---

## 8. Colunas Descrição, Preço, Estoque e Data em branco na aba Produtos

**Problema:** `TableWidget._populate_table` derivava a chave do dict transformando o header com `.lower().replace(' ', '_')`. Os headers `"Descrição"`, `"Preço"`, `"Estoque"` viravam `"descrição"`, `"preço"`, `"estoque"`, mas o dict passado por `load_products` usava as chaves `"description"`, `"price"`, `"quantity_available"`. Apenas `"id"` coincidia.

**Correção:** `TableWidget` passou a aceitar dois parâmetros separados: `headers` (chaves do dict) e `display_headers` (labels visíveis na tabela). As chamadas em `main_window.py` foram atualizadas para passar as chaves corretas.

---

## 9. Status na aba de Pedidos com badge colorido destoante

**Problema:** A coluna de status usava o widget `StatusBadge` (label arredondado colorido) dentro de células da tabela, criando inconsistência visual com as demais colunas de texto simples.

**Correção:** Removido o `StatusBadge` do `_populate_table`. O status agora é exibido como texto simples igual às outras colunas.
