# 🤖 Automação — Atualização Diária Automática

Este guia explica como funciona a automação e como configurá-la do zero.

## 🏗️ Como funciona

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions (roda de graça na infraestrutura do      │
│  GitHub, você não precisa deixar computador ligado)      │
│                                                            │
│  ⏰ Cron: seg-sex, 8h Manaus (12:00 UTC)                  │
│      │                                                     │
│      ▼                                                     │
│  🐍 scripts/scraper.py                                    │
│      1. Acessa portodemanaus.com.br/nivel-do-rio-negro/  │
│      2. Extrai as tabelas de cota diária (últimos meses)  │
│      3. Compara com src/data.js (dados já salvos)         │
│      4. Detecta anomalias (variação >30cm/dia = alerta)   │
│      5. Atualiza src/data.js com os dados novos           │
│      │                                                     │
│      ▼                                                     │
│  📦 Commit + push automático                               │
│      (só commita SE algo realmente mudou)                 │
│      │                                                     │
│      ▼                                                     │
│  🌐 GitHub Pages detecta o push e republica sozinho        │
│      │                                                     │
│      ▼                                                     │
│  📱 Seu app (e de quem você compartilhou o link)          │
│      mostra os dados atualizados automaticamente          │
└─────────────────────────────────────────────────────────┘
```

**Você não precisa fazer nada no dia a dia.** O robô roda sozinho, de segunda a sexta, às 8h.

## 🎯 Por que o dashboard calcula tudo sozinho agora

Antes, toda vez que chegavam dados novos, era preciso editar manualmente:
cota atual, variação 24h, tendência 7 dias, comparação com anos anteriores,
texto do insight, data no rodapé... cerca de 10 lugares diferentes no HTML.

Agora isso foi refatorado: **o JavaScript do dashboard calcula tudo sozinho**
a partir do array de dados brutos (`dados`). O scraper só precisa atualizar
esse array — nenhum KPI precisa ser tocado manualmente. Isso é o que torna
a automação real: sem esse motor de cálculo dinâmico, o robô teria que ser
muito mais complexo (teria que "entender" o HTML e editar 10+ textos
diferentes). Ver `CLAUDE.md` seção "Motor de Cálculo Dinâmico" para detalhes técnicos.

## 📋 Setup — passo a passo completo

### 1. Subir o projeto para o GitHub (se ainda não fez)

```bash
cd rio-negro-app
git init
git branch -M main
git remote add origin https://github.com/jsavinojspds-cyber/rio-negro.git
git add .
git commit -m "Setup inicial com automação"
git push -u origin main
```

### 2. Ativar GitHub Pages

1. `github.com/jsavinojspds-cyber/rio-negro/settings/pages`
2. Source: Branch `main`, pasta `/ (root)`
3. Save

### 3. Ativar permissões de escrita para o Actions

Isso é necessário para o robô conseguir fazer commit/push sozinho:

1. `github.com/jsavinojspds-cyber/rio-negro/settings/actions`
2. Role até **"Workflow permissions"**
3. Marque **"Read and write permissions"**
4. Save

### 4. Testar manualmente (sem esperar o cron)

1. `github.com/jsavinojspds-cyber/rio-negro/actions`
2. Clique no workflow **"Atualizar dados do Rio Negro"**
3. Clique em **"Run workflow"** → **"Run workflow"** (botão verde)
4. Aguarde ~30 segundos, atualize a página
5. Clique na execução para ver os logs — deve mostrar
   `✅ X mês(es) encontrado(s) na página`

Se der certo, o app já vai estar atualizado com os dados mais recentes do site.

### 5. Pronto! A partir de agora roda sozinho

Todo dia útil, às 8h de Manaus, o robô roda automaticamente. Você pode
acompanhar as execuções em `Actions` a qualquer momento.

## 🔍 Como verificar se está funcionando

- **Aba Actions do GitHub**: mostra o histórico de todas as execuções (✅ ou ❌)
- **Histórico de commits**: cada atualização aparece como um commit
  `🌊 Atualização automática: 2026-09-04 08:00 UTC`
- **O próprio app**: a data no rodapé/header reflete o último dia com dado

## ⚠️ Se o scraper parar de funcionar

O site do Porto de Manaus pode eventualmente mudar de estrutura (novo design,
nova plataforma). Se isso acontecer, o workflow vai falhar visivelmente
(❌ vermelho na aba Actions, e você pode configurar notificação por e-mail
nas configurações da sua conta GitHub).

Quando isso acontecer, é só pedir para o Claude Code:

> "O scraper do Rio Negro parou de funcionar, o site mudou. Aqui está o
> HTML atual da página: [colar]. Ajuste o parser em scripts/scraper.py"

Enquanto isso, use o `scripts/update-data.py` manualmente como fallback
(mesmo processo de sempre, colando os dados do site).

## 🕐 Sobre o horário

- Cron do GitHub Actions usa **UTC**, sempre
- Manaus é **UTC-4** o ano todo (Brasil não usa mais horário de verão desde 2019)
- Por isso `0 12 * * 1-5` = 12:00 UTC = **8h em Manaus**, seg-sex

Se quiser mudar o horário, edite `.github/workflows/atualizar-dados.yml`:
```yaml
- cron: '0 12 * * 1-5'  # minuto hora dia-do-mês mês dia-da-semana (UTC)
```

Exemplos:
- `0 11 * * 1-5` → 7h Manaus
- `0 20 * * 1-5` → 16h Manaus
- `0 12 * * *` → todo dia (incluindo fins de semana)

## 🌐 Sobre uso responsável do scraper

O `scraper.py` foi construído para ser um bom cidadão da internet:
- Faz **1 única requisição** por execução
- Roda no máximo **1x por dia útil** (não fica martelando o site)
- Se identifica com um **User-Agent descritivo** (não finge ser navegador)
- Lê apenas a **página pública** que qualquer visitante acessa no navegador
- Falha de forma **visível** em vez de silenciosamente corromper dados

Isso é equivalente ao que você vinha fazendo manualmente (abrir o site e
copiar a tabela), só que automatizado e em um horário fixo — não gera mais
carga no site do que um usuário normal geraria.
