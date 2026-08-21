# Falha Controlada — Estado do Pedido

## Contexto

O sistema implementa um ciclo de vida de pedidos com quatro estados: `created`, `processing`, `completed` e `cancelled`. Pedidos nos estados finais (`completed` e `cancelled`) não devem aceitar modificações. Essa regra é aplicada pelo `StateService.validate_operation` antes de qualquer operação de escrita.

---

## Etapa 2 — Falha Introduzida

### Componente alterado

`backend/service/order_service.py` — método `add_item_to_order`

### Descrição

A linha que valida se a operação `add_item` é permitida no estado atual do pedido foi removida. Sem essa verificação, o sistema aceita a adição de itens em pedidos `completed` ou `cancelled`, corrompendo o estado do pedido silenciosamente.

### Código antes da falha (versão funcional)

```python
def add_item_to_order(self, order_id: int, product_id: int, quantity: int) -> Order:
    order = self.get_order(order_id)

    # Valida se a operação é permitida no estado atual
    StateService.validate_operation(order.status, 'add_item')

    item_data = self.validator.validate_order_item(product_id, quantity, self.product_service.product_repo)
    ...
```

### Código com a falha introduzida

```python
def add_item_to_order(self, order_id: int, product_id: int, quantity: int) -> Order:
    order = self.get_order(order_id)

    # FALHA: validação de estado removida
    # StateService.validate_operation(order.status, 'add_item')

    item_data = self.validator.validate_order_item(product_id, quantity, self.product_service.product_repo)
    ...
```

### Cenário escolhido

Adicionar um produto a um pedido que já foi finalizado (`completed`).

### Comportamento provocado

- O sistema aceita a operação sem erro
- O estoque do produto é decrementado indevidamente
- O total do pedido é recalculado e alterado após a finalização
- O pedido fica em estado inconsistente: `completed` com itens adicionados após o fechamento
- Nenhuma mensagem de erro é exibida ao usuário

---

## Etapa 3 — Diagnóstico e Evidência do Incidente

### Título do incidente

Adição de item permitida em pedido finalizado — violação de regra de estado

### Descrição

Após remover a validação de estado em `add_item_to_order`, o sistema passou a aceitar a inclusão de produtos em pedidos com status `completed` ou `cancelled`. A operação é executada integralmente: o estoque é reservado, o item é persistido no banco e o total é recalculado, deixando o pedido em estado inconsistente.

### Passos para reprodução

1. Iniciar a aplicação e fazer login
2. Criar um pedido com pelo menos um produto
3. Alterar o status do pedido para `completed`
4. Tentar adicionar um novo produto ao mesmo pedido
5. Observar que a operação é aceita sem erro

### Resultado esperado

O sistema deve rejeitar a operação com a mensagem:
```
Operation 'add_item' not allowed in 'Completed' state
```

### Resultado obtido

A operação é executada com sucesso. O item é adicionado, o estoque é decrementado e o total do pedido é alterado. O pedido permanece com status `completed` mas com dados modificados após o fechamento.

### Causa técnica

A chamada `StateService.validate_operation(order.status, 'add_item')` foi removida do método `add_item_to_order` em `order_service.py`. Essa linha era a única barreira que impedia operações de escrita em pedidos nos estados finais `completed` e `cancelled`.

### Componente afetado

`backend/service/order_service.py` — método `add_item_to_order`

### Impacto

- Integridade dos dados comprometida: pedidos finalizados podem ter seu conteúdo e total alterados
- Estoque decrementado indevidamente para pedidos já encerrados
- Relatórios financeiros incorretos, pois o total de pedidos `completed` pode ser alterado após o fechamento
- Ausência de rastreabilidade: a operação não gera erro nem log de violação

---

## Etapa 4 — Correção

### Correção aplicada

Restaurada a chamada `StateService.validate_operation` no início do método, antes de qualquer acesso ao banco:

```python
def add_item_to_order(self, order_id: int, product_id: int, quantity: int) -> Order:
    order = self.get_order(order_id)

    # Validação restaurada: impede operação em estados finais
    StateService.validate_operation(order.status, 'add_item')

    item_data = self.validator.validate_order_item(product_id, quantity, self.product_service.product_repo)
    ...
```

O `StateService.validate_operation` lança `StateError` quando a operação não é permitida no estado atual. O `OrderController` captura `StateError` e o `BaseConnector` o converte em resposta de erro estruturada exibida ao usuário.

### Por que a correção é suficiente

A validação ocorre antes de qualquer acesso ao banco, garantindo que nenhuma alteração parcial seja executada. O estoque não é tocado, nenhum item é criado e o total não é recalculado. A consistência do pedido é preservada integralmente.
