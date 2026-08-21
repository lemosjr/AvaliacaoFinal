# Relatório de Testes — Etapa 4

---

## Teste 01 — Cenário que provocava a falha (texto invisível)

**Objetivo:** Confirmar que o texto digitado nos campos de login é visível após a correção.

**Procedimento:**
1. Iniciar a aplicação
2. Clicar no campo Email e digitar `admin@ecommerce.com`
3. Clicar no campo Senha e digitar `admin123`

**Resultado esperado:** Texto visível em ambos os campos.

**Resultado obtido:** ✅ Texto exibido corretamente com cor `#ecf0f1` sobre fundo `#34495e` (dark theme).

**Correção aplicada:**
```python
# login_window.py — após correção
QLineEdit {
    background-color: #34495e;
    color: #ecf0f1;  /* cor explícita adicionada */
    border: 2px solid #4a6278;
}
```

---

## Teste 02 — Operação normal (login e navegação completa)

**Objetivo:** Confirmar que o fluxo principal da aplicação funciona corretamente.

**Procedimento:**
1. Iniciar a aplicação
2. Fazer login com `admin@ecommerce.com` / `admin123`
3. Navegar pelas abas Dashboard, Produtos e Pedidos
4. Cadastrar um novo produto
5. Criar um pedido com o produto cadastrado

**Resultado esperado:** Todas as operações concluídas sem erros.

**Resultado obtido:** ✅ Login realizado, dashboard carregado com estatísticas, produto cadastrado e listado, pedido criado com total calculado corretamente.

---

## Teste 03 — Regra de negócio (navegação entre login e registro)

**Objetivo:** Confirmar que clicar em "Fazer login" na tela de registro retorna à tela de login sem encerrar a aplicação.

**Procedimento:**
1. Iniciar a aplicação
2. Clicar em "Criar conta" na tela de login
3. Na tela de registro, clicar em "Fazer login"

**Resultado esperado:** Tela de login reaparecer normalmente.

**Resultado obtido:** ✅ Tela de login reexibida corretamente. Aplicação não encerrou.

**Correção aplicada:**
```python
# login_window.py — após correção
def _open_register(self):
    from frontend.src.register_window import RegisterWindow
    self.register_window = RegisterWindow(self.auth_connector)
    self.register_window.registration_success.connect(self._on_register_back)
    self.register_window.show()
    self.hide()

def _on_register_back(self):
    self.show()  # reexibe o login ao receber o sinal
```

---

## Teste 04 — Regressão (cadastro de conta e login com novo usuário)

**Objetivo:** Confirmar que o fluxo de registro de novo usuário não foi afetado pelas correções.

**Procedimento:**
1. Iniciar a aplicação
2. Clicar em "Criar conta"
3. Preencher nome, email, senha e confirmar senha
4. Aceitar os termos e clicar em "Criar Conta"
5. Após mensagem de sucesso, fazer login com as novas credenciais

**Resultado esperado:** Conta criada e login realizado com sucesso.

**Resultado obtido:** ✅ Conta criada, tela de login reexibida automaticamente, login realizado com as novas credenciais e dashboard carregado normalmente.
