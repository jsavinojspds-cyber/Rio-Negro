# 🚀 Deploy

**Nota:** se você configurou a automação (ver `docs/AUTOMACAO.md`), o deploy
já acontece sozinho a cada execução do GitHub Actions. Este guia é para o
setup inicial e para deploys manuais eventuais.

## Setup inicial (uma vez só)

### 1. Criar repositório no GitHub
Crie um repo público chamado `rio-negro` na conta `jsavinojspds-cyber`.

### 2. Subir o projeto
```bash
git clone https://github.com/jsavinojspds-cyber/rio-negro.git
cd rio-negro
cp -r /caminho/para/rio-negro-app/* .
git add .
git commit -m "Initial commit - Rio Negro Dashboard"
git push origin main
```

### 3. Ativar GitHub Pages
Settings → Pages → Source: branch `main`, pasta `/ (root)` → Save

**Link final:** `https://jsavinojspds-cyber.github.io/rio-negro`

### 4. Ativar a automação
Ver `docs/AUTOMACAO.md` para o passo a passo completo (permissões do
Actions, teste manual do workflow, etc).

## Deploy manual (raramente necessário)

```bash
bash scripts/deploy.sh "Mensagem do commit"
```

Ou manualmente:
```bash
cp src/index.html index.html
cp src/data.js data.js
git add .
git commit -m "Update manual"
git push origin main
```

## Force cache refresh no iPhone

Se o app instalado não mostrar dados novos:

**Safari:** Configurações → Safari → Limpar Histórico e Dados

**PWA instalado:** Delete o app da tela inicial → abra o link no Safari →
reinstale via Compartilhar → Adicionar à Tela de Início
