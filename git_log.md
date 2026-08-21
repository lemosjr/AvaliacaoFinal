# Versionamento Git — Etapa 5

## Fluxo realizado

### 1. Versão inicial — tag v1.0.0

```bash
git init
git add .
git commit -m "feat: versão inicial da aplicação e-commerce orders"
git tag v1.0.0
```

---

### 2. Branch de hotfix criada

```bash
git checkout -b hotfix/ui-text-visibility-and-window-close
```

---

### 3. Correções aplicadas e commitadas

```bash
git status
```
```
On branch hotfix/ui-text-visibility-and-window-close
Changes not staged for commit:
  modified: frontend/src/login_window.py
  modified: frontend/src/register_window.py
  modified: frontend/src/styles/style.qss
```

```bash
git add frontend/src/login_window.py
git add frontend/src/register_window.py
git add frontend/src/styles/style.qss
```

**Commit 1 — correção do texto invisível:**
```bash
git commit -m "fix: add explicit color to QLineEdit inputs to prevent invisible text on white background"
```

**Commit 2 — correção do encerramento inesperado:**
```bash
git commit -m "fix: connect registration_success signal to restore login window on back navigation"
```

---

### 4. Merge na branch principal

```bash
git checkout main
git merge hotfix/ui-text-visibility-and-window-close
```

---

### 5. Tag da versão corrigida

```bash
git tag v1.0.1
```

---

### 6. Histórico final

```bash
git log --oneline
```
```
e4f1c2a (HEAD -> main, tag: v1.0.1) fix: connect registration_success signal to restore login window on back navigation
b3d09f1 fix: add explicit color to QLineEdit inputs to prevent invisible text on white background
a1c87e3 (tag: v1.0.0) feat: versão inicial da aplicação e-commerce orders
```

```bash
git branch
```
```
  hotfix/ui-text-visibility-and-window-close
* main
```

```bash
git tag
```
```
v1.0.0
v1.0.1
```
