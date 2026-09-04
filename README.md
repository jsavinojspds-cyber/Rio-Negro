# 🌊 Rio Negro Dashboard · Manaus

Dashboard interativo para monitoramento hidrométrico do Rio Negro no Porto
de Manaus. **Atualiza sozinho, automaticamente, de segunda a sexta às 8h.**

## 📊 Funcionalidades

- **Atualização automática diária** via GitHub Actions (scraper + cron)
- **Série temporal completa** (Jan/2024 → atual) com filtros por ano
- **Comparação multi-ano** (2024 vs 2025 vs 2026...) na mesma janela do calendário
- **Heatmap diário** com filtro por mês (abre automaticamente no mês atual)
- **KPIs calculados dinamicamente**: cota atual, tendência 7 dias, distância
  ao pico, comparação com anos anteriores — tudo computado em tempo real a
  partir dos dados brutos, nada hardcoded
- **Régua visual do rio** com animação de água
- **PWA instalável** no iPhone/Android (funciona offline)

## 🤖 Automação

```
GitHub Actions (seg-sex, 8h Manaus)
   → scraper.py busca portodemanaus.com.br
   → atualiza src/data.js
   → commit + push automático
   → GitHub Pages republica sozinho
```

Ver **`docs/AUTOMACAO.md`** para o guia completo de configuração.

## 🚀 Deploy

Publicado via GitHub Pages. Ver `docs/DEPLOY.md` para setup manual, ou
`docs/AUTOMACAO.md` para o setup completo com automação.

## 📱 Instalar como App

**iPhone (Safari):** Abrir o link → ⬆️ Compartilhar → "Adicionar à Tela de Início"

**Android (Chrome):** Abrir o link → Menu (⋮) → "Instalar app"

## 🗂️ Estrutura

```
rio-negro-app/
├── src/
│   ├── index.html          # Dashboard completo (HTML+CSS+JS)
│   └── data.js             # Dados brutos (gerado pelo scraper — não editar à mão)
├── data/
│   └── rio-negro-cotas.json # Backup estruturado dos dados
├── scripts/
│   ├── scraper.py          # 🤖 Roda automaticamente, busca dados do site
│   ├── update-data.py      # Fallback manual (emergência)
│   ├── deploy.sh           # Deploy manual (normalmente desnecessário)
│   └── requirements.txt
├── .github/workflows/
│   └── atualizar-dados.yml # Configuração do cron job
├── docs/
│   ├── AUTOMACAO.md        # 👉 Comece por aqui para configurar o robô
│   ├── DEPLOY.md
│   └── DATA-FORMAT.md
├── CLAUDE.md                # Instruções para o Claude Code
└── README.md
```

## 🔄 Como os dados são atualizados

**Automático (padrão):** o robô roda sozinho, você não faz nada.

**Manual (emergência/fallback):**
```bash
python3 scripts/update-data.py --mes 2026-09 --dados "24.09,23.94,23.80"
bash scripts/deploy.sh "Update manual setembro"
```

## 📈 Fonte de dados

- **Porto de Manaus** — https://portodemanaus.com.br/nivel-do-rio-negro/
- Atualização pelo Porto: aproximadamente diária

## 🛠️ Tech Stack

- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript + Chart.js (CDN)
- **Automação**: Python (requests + BeautifulSoup) + GitHub Actions
- **Deploy**: GitHub Pages
- **PWA**: Manifest inline

## 👤 Autor

**Jean Savino** — Manaus/AM

---

Feito com 💙 para monitoramento do Rio Negro
