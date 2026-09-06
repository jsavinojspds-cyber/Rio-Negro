# Instruções para Claude Code

Este arquivo orienta o Claude Code sobre como trabalhar neste projeto.

## 🎯 Contexto do Projeto

Dashboard PWA para monitorar o nível do Rio Negro em Manaus, feito para o
o dono do projeto (profissional de vendas baseado em Manaus/AM). O app:
- Acompanha cotas diárias **automaticamente** (scraper via GitHub Actions)
- Compara anos (2024, 2025, 2026...)
- É usado para planejar atividades no rio (jet ski, passeios)
- É compartilhado com amigos via link do GitHub Pages

## 📐 Arquitetura (IMPORTANTE — leia antes de mexer)

```
src/
├── index.html    ← Todo o dashboard: HTML + CSS + JS (Chart.js via CDN)
│                    Carrega data.js via <script src="data.js">
│                    NÃO contém dados hardcoded — tudo é calculado dinamicamente
└── data.js       ← APENAS o array de dados: const dados = {"2024-01": [...], ...}
                     Gerado/sobrescrito automaticamente pelo scraper
                     Comentário no topo avisa "não editar manualmente"

scripts/
├── scraper.py       ← Roda via GitHub Actions, busca dados do site, atualiza data.js
├── update-data.py   ← Fallback manual (mesma lógica, mas você cola os dados)
└── requirements.txt ← requests, beautifulsoup4, lxml

.github/workflows/
└── atualizar-dados.yml  ← Cron job: seg-sex 8h Manaus (12:00 UTC)
```

### Por que essa separação?

O dashboard tem duas responsabilidades bem separadas:
1. **`data.js`** = os fatos brutos (cota de cada dia)
2. **`index.html`** = como calcular e exibir tudo a partir desses fatos

Isso significa que **o scraper só precisa tocar em `data.js`**. Nenhum KPI,
insight, comparação ou texto precisa ser editado manualmente — o
"Motor de Cálculo Dinâmico" dentro do `<script>` do `index.html` computa
tudo sozinho toda vez que a página carrega.

## 🧮 Motor de Cálculo Dinâmico (dentro de index.html)

Procure por `// ============= MOTOR DE CÁLCULO DINÂMICO =============`.

O que ele faz, na ordem:

1. `buildFlatSeries()` — achata o objeto `dados` em uma lista cronológica
   de `{ano, mes, dia, cota}`, um item por dia
2. `ultimo` = último item da lista = "hoje" (a data mais recente com dado)
3. `penultimo` = usado para variação 24h
4. `seteDiasAtras` = usado para tendência 7 dias (e para decidir a fase:
   Enchente / Vazante / Estável, com limiar de ±15cm em 7 dias)
5. `picoHist` / `minHist` = maior/menor cota de toda a série histórica
6. `picoAno` = maior cota do ano corrente (`ultimo.ano`)
7. `buscarMesmoDia(ano, mes, dia)` = compara com o mesmo dia em anos
   anteriores (usado nos "vs Set/2025", "vs Set/2024" etc). Se o dia exato
   ainda não existir naquele mês/ano (ex: comparando dia 31 com um mês que
   só tem dados até dia 20), cai para o último dia disponível daquele mês
8. `renderKPIs()` — preenche todos os elementos do DOM (por `id`) com os
   valores calculados: KPIs do topo, régua visual, header, footer, insight

**Regra de ouro**: se você adicionar um novo KPI ou insight, ele DEVE ser
calculado dentro de `renderKPIs()` a partir de `dados`/`flatSeries` — nunca
hardcoded. Isso é o que mantém a automação funcionando sem manutenção.

### "Hoje" não é `new Date()`

Note que `HOJE` (usado pelo heatmap e pelos filtros) é definido como o
**último dia presente em `dados`**, não a data real do dispositivo:

```javascript
const _ultimaChave = Object.keys(dados).sort().pop();
const _ultimoArr = dados[_ultimaChave];
const HOJE = { ano: ..., mes: ..., dia: _ultimoArr.length };
```

Isso é intencional — reflete até onde o scraper conseguiu atualizar, que é
mais confiável do que assumir que o site já tem o dado do dia corrente.

## 🕷️ O Scraper (`scripts/scraper.py`)

- Busca `https://portodemanaus.com.br/nivel-do-rio-negro/`
- Usa BeautifulSoup para achar `<table>` e o texto "Mês AAAA" mais próximo
  antes de cada uma (o site lista os últimos ~5-6 meses, mais recente primeiro)
- Para cada tabela: extrai (dia, cota), ordena por dia
- Compara com o que já existe em `src/data.js`; só sobrescreve se mudou
- Valida anomalias (variação >30cm entre dias consecutivos, valores fora
  de 10-32m) e **avisa mas não bloqueia** (não dá pra pedir confirmação
  humana num cron job) — usa `::warning::` do GitHub Actions para aparecer
  como alerta visível na aba Actions
- Grava `src/data.js` E `data/rio-negro-cotas.json` (backup)

**Se o site mudar de estrutura**: o scraper vai simplesmente não encontrar
tabelas reconhecíveis e vai falhar com `::error::` (visível na aba Actions).
Ele NUNCA deve gravar dados incertos silenciosamente — prefira falhar
ruidosamente a corromper o histórico.

### Ajustando o parser se o site mudar

Se pedirem para consertar o scraper porque o site mudou:
1. Peça o HTML atual da página (ou peça para buscar via `web_fetch` se
   disponível na sessão)
2. Ajuste `parse_tabelas()` em `scraper.py` — provavelmente só a regex de
   `padrao_mes_ano` ou a forma de achar `<table>` vai precisar mudar
3. Teste com `python3 scripts/scraper.py --dry-run --verbose` antes de
   deixar rodar de verdade
4. Nunca remova a validação de anomalias

## ⏰ A Automação (GitHub Actions)

`.github/workflows/atualizar-dados.yml`:
- Cron `0 12 * * *` = todos os dias, 12:00 UTC = **8h em Manaus** (sem DST no Brasil)
- Roda o scraper, copia `src/index.html` e `src/data.js` para a raiz
  (GitHub Pages serve a partir de `/`), commita só se algo mudou
- Precisa de "Read and write permissions" habilitado em
  Settings → Actions → General → Workflow permissions

Ver `docs/AUTOMACAO.md` para o guia completo de setup.

## 🎨 Design System

```css
--bg-dark: #0a1929        /* Fundo principal */
--bg-card: #132f4c        /* Cards */
--accent: #00d4ff         /* Ciano vibrante */
--success: #4caf50        /* Enchente */
--danger: #f44336         /* Vazante */
--warning: #ff9800        /* Estável */
```

- Fonte: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto`
- Tema exclusivamente dark (não implementar light theme sem pedir)
- Valores de nível do rio sempre em metros: inclua o sufixo `m` (ex: `23.65 m`) em qualquer elemento novo que exiba uma cota

## 🔄 Fluxo de trabalho comum

### "Adicione um KPI novo, tipo X"
1. Adicionar o cálculo dentro de `renderKPIs()` em `index.html`, derivado
   de `flatSeries`/`dados` — nunca um valor fixo
2. Adicionar o elemento HTML com `id` correspondente
3. Testar localmente (`python3 -m http.server` dentro de `src/`)

### "O scraper não está pegando os dados certos"
1. Rodar `python3 scripts/scraper.py --dry-run --verbose` e ver o output
2. Se `resultados` vier vazio → o parser não está achando as tabelas,
   provavelmente o HTML mudou
3. Pedir o HTML atual da página para ajustar `parse_tabelas()`

### "Quero mudar o horário da automação"
Editar o `cron:` em `.github/workflows/atualizar-dados.yml` (sempre em UTC)

### "Adicione uma nova aba/gráfico"
Seguir o padrão dos gráficos existentes (`chartSerie`, `chartComparacao`,
`chartMensal`, `chartVelocidade`) — todos usam Chart.js e leem de `dados`
via `flatSeries` ou diretamente

## 🚨 Alertas Importantes

### Nunca hardcode dados ou KPIs no HTML
Se você se pegar escrevendo `document.getElementById('x').textContent = '28.51m'`
com um valor fixo, pare — isso deveria vir de um cálculo em cima de `dados`.

### Nunca inventar dados
Se um mês não tem dados oficiais do site, deixar de fora do objeto `dados`.
Nunca preencher com estimativas ou interpolação sem avisar explicitamente.

### O scraper deve falhar ruidosamente, nunca silenciosamente
Prefira `sys.exit(1)` com mensagem clara a gravar um `data.js` incerto.

## 🎯 Roadmap / Features Possíveis

- [ ] Alertas WhatsApp/Telegram quando cota cruzar limites (ex: <15m ou >28m)
- [ ] Previsão simples baseada em médias históricas do mesmo período
- [ ] Export PDF/PNG do relatório mensal
- [ ] Widget iOS (via Shortcuts + JSON endpoint)
- [ ] Notificação push via PWA
- [ ] Modo comparação livre (escolher 2 datas quaisquer)
- [ ] Múltiplos rios/estações (o site tem outras plataformas: Roadway,
      Plataforma Malcher, Paredão — mencionadas na home page)

## ⚠️ NÃO fazer sem pedir

- Não mudar o tema para light
- Não adicionar tracking/analytics
- Não adicionar dependências pesadas (React, Vue, build step, etc)
- Não voltar a hardcodar dados/KPIs no HTML (quebra a automação)
- Não remover a validação de anomalias do scraper
- Não aumentar a frequência do scraper além de 1x/dia sem necessidade real
