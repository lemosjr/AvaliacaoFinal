# Relatório de Incidente

---

## Etapa 2 — Falhas Controladas Introduzidas

Foram introduzidas duas falhas controladas na interface, ambas relacionadas à camada de apresentação.

### Falha 1 — Texto invisível nos campos de entrada

**Componente alterado:** `frontend/src/styles/style.qss`, `login_window.py`, `register_window.py`

**Alteração realizada:** O QSS global define `color: #ecf0f1` para todos os `QWidget`. Os inputs de login e registro foram estilizados com `background-color: white` sem definir `color`, criando o conflito.

**Trecho de código com a falha:**
```css
/* style.qss */
QWidget {
    color: #ecf0f1; /* branco herdado por todos os widgets */
}
```
```python
# login_window.py — input sem color definido
QLineEdit {
    background-color: white;
    font-size: 14px;
    /* color não definido → herda branco do QSS → texto invisível */
}
```

**Comportamento provocado:** Usuário digita email e senha mas não vê o texto, impossibilitando o login.

---

### Falha 2 — Aplicação fecha ao voltar para o login a partir do registro

**Componente alterado:** `frontend/src/login_window.py`, método `_open_register`

**Alteração realizada:** O método ocultava a janela de login com `self.hide()` mas não conectava o sinal `registration_success` da janela de registro para reexibi-la.

**Trecho de código com a falha:**
```python
def _open_register(self):
    from frontend.src.register_window import RegisterWindow
    self.register_window = RegisterWindow(self.auth_connector)
    self.register_window.show()
    self.hide()  # login oculto, sinal não conectado
```

**Comportamento provocado:** Ao clicar em "Fazer login" na tela de registro, a janela de registro fechava, a janela de login permanecia oculta e o Qt encerrava o processo por não haver janelas visíveis.

---

## Etapa 3 — Diagnóstico e Evidência do Incidente

---

### Incidente 1 — Texto invisível nos campos de login e registro

**Título:** Texto digitado invisível nos campos de entrada

**Descrição:** Ao abrir a tela de login ou registro, os campos de email e senha apresentavam fundo branco mas o texto digitado não era visível, pois herdava a cor branca do tema global.

**Passos para reprodução:**
1. Iniciar a aplicação com `python main.py`
2. Na tela de login, clicar no campo Email e digitar qualquer texto
3. Observar que o texto não aparece

**Resultado esperado:** Texto digitado visível no campo.

**Resultado obtido:** Campo aparentemente vazio mesmo com texto digitado.

**Causa técnica:** Herança de `color: #ecf0f1` do seletor `QWidget` no `style.qss` global. O estilo inline do input definia `background-color: white` mas omitia `color`, fazendo o texto branco se fundir com o fundo branco.

**Componente afetado:** `frontend/src/styles/style.qss`, `login_window.py`, `register_window.py`

**Impacto:** Usuário incapaz de realizar login ou criar conta, bloqueando completamente o acesso ao sistema.

---

### Incidente 2 — Aplicação encerra inesperadamente ao navegar entre login e registro

**Título:** Encerramento inesperado da aplicação ao clicar "Fazer login" na tela de registro

**Descrição:** Ao acessar a tela de registro a partir do login e clicar em "Fazer login" para voltar, a aplicação encerrava sem mensagem de erro.

**Passos para reprodução:**
1. Iniciar a aplicação
2. Na tela de login, clicar em "Criar conta"
3. Na tela de registro, clicar em "Fazer login"
4. Observar o encerramento da aplicação

**Resultado esperado:** Tela de login reaparecer normalmente.

**Resultado obtido:** Aplicação encerrada silenciosamente.

**Causa técnica:** `_open_register` chamava `self.hide()` na janela de login sem conectar o sinal `registration_success` ao método que a reexibiria. Com a janela de registro fechada e a de login oculta, o Qt interpretou que não havia mais janelas ativas e encerrou o event loop.

**Componente afetado:** `frontend/src/login_window.py`, método `_open_register`

**Impacto:** Usuário sem conta não consegue navegar entre as telas de autenticação, sendo forçado a reiniciar a aplicação.
