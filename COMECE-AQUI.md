# 🎯 Comece Aqui — Claude Code

Bem-vindo ao projeto **Rio Negro Dashboard**! Agora com **atualização
automática diária** — o app se mantém sozinho.

## 📥 1. Descompactar e abrir no Claude Code

```bash
unzip rio-negro-app.zip -d ~/Projetos/
cd ~/Projetos/rio-negro-app
claude
```

O Claude Code vai ler `CLAUDE.md` automaticamente e entender toda a arquitetura.

## 🐙 2. Subir para o GitHub

```bash
git init
git branch -M main
git remote add origin https://github.com/jsavinojspds-cyber/rio-negro.git
git add .
git commit -m "Setup inicial com automação"
git push -u origin main
```

## ⚙️ 3. Configurar a automação (só uma vez)

**Leia `docs/AUTOMACAO.md` para o passo a passo completo.** Resumo:

1. Ative o **GitHub Pages** (Settings → Pages → branch `main`, pasta `/`)
2. Ative **permissões de escrita** para o Actions (Settings → Actions →
   General → Workflow permissions → "Read and write permissions")
3. Rode o workflow manualmente uma vez para testar (aba Actions → 
   "Atualizar dados do Rio Negro" → "Run workflow")
4. Pronto! A partir daí roda sozinho, de segunda a sexta, às 8h de Manaus

## 🚀 4. Comandos úteis no Claude Code

### Testar o scraper sem gravar nada
> "Rode o scraper em modo dry-run e me mostra o resultado"

### Ver se a automação está funcionando
> "Verifica a última execução do GitHub Actions"

### Adicionar dados manualmente (emergência)
> "Adicione os dados de setembro: 24.09, 23.94, 23.80, ..."

### Consertar o scraper se o site mudar
> "O scraper parou de funcionar. Aqui está o HTML atual do site: [colar].
> Ajusta o parser"

## 📂 O que tem no projeto

```
rio-negro-app/
├── CLAUDE.md               ← Instruções técnicas para o Claude Code
├── COMECE-AQUI.md          ← Este arquivo
├── README.md               ← Documentação geral
│
├── src/
│   ├── index.html          ← ⭐ O APP (calcula tudo dinamicamente)
│   └── data.js             ← Dados brutos (o scraper atualiza isso sozinho)
│
├── scripts/
│   ├── scraper.py          ← 🤖 Roda automaticamente via GitHub Actions
│   ├── update-data.py      ← Fallback manual
│   └── deploy.sh
│
├── .github/workflows/
│   └── atualizar-dados.yml ← Configuração do robô (cron seg-sex 8h)
│
└── docs/
    ├── AUTOMACAO.md         ← 👉 LEIA ISSO PRIMEIRO
    ├── DEPLOY.md
    └── DATA-FORMAT.md
```

## 💡 A grande mudança: cálculo dinâmico

Antes, cada atualização de dados exigia editar ~10 textos diferentes no
HTML (cota atual, tendências, comparações, insights...). Agora o
JavaScript do dashboard **calcula tudo sozinho** a partir de `data.js`.

Isso significa: o robô só precisa tocar em UM arquivo simples
(`src/data.js`), e o resto do app se ajusta automaticamente. É isso que
torna a automação de verdade possível — sem essa mudança, o scraper
precisaria "entender" e editar o HTML inteiro toda vez, o que seria muito
mais frágil.

## 🎯 Roadmap sugerido

1. ~~Scraper automático~~ ✅ feito
2. ~~GitHub Actions (atualização diária)~~ ✅ feito
3. Alertas WhatsApp quando cota cruzar níveis críticos
4. Widget iOS para tela inicial
5. Modo comparação livre — escolher duas datas quaisquer
6. Export PDF — relatório mensal formatado
7. Múltiplas plataformas do Porto (Roadway, Malcher, Paredão)
8. Previsão simples baseada em médias históricas

## 🆘 Ajuda

Se algo não funcionar, peça ao Claude Code:

> "Estou com problema X. Investiga aí e me explica"

Ele tem acesso a todos os arquivos, pode rodar comandos, testar e corrigir.

---

Bom trabalho! 🚀
