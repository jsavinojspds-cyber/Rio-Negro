# 📊 Formato de Dados

## Fonte

**https://portodemanaus.com.br/nivel-do-rio-negro/**

Com a automação ativa, o `scripts/scraper.py` lê essa página sozinho,
seg-sex às 8h. Este documento é útil para entender o formato ou para
atualizações manuais de emergência.

## `src/data.js` (o que o app realmente usa)

```javascript
// 🌊 Dados do Rio Negro — Porto de Manaus
// ⚠️ ARQUIVO GERADO AUTOMATICAMENTE pelo scraper (scripts/scraper.py)
// Não editar manualmente — suas mudanças serão sobrescritas no próximo update
//
// Última atualização: 2026-09-03 19:32

const dados = {
    "2024-01": [18.79,18.91,19.04,...],
    "2024-02": [21.20,21.28,...],
    ...
    "2026-09": [24.09,23.94,23.80]
};
```

- Chave: `"YYYY-MM"`
- Valor: array de cotas em metros, um número por dia do mês (posição 0 = dia 1)
- Ordem: sempre cronológica

## `data/rio-negro-cotas.json` (backup/referência)

Mesma informação em formato JSON com metadados:

```json
{
    "metadata": {
        "fonte": "Porto de Manaus",
        "ultima_atualizacao": "2026-09-03 19:32",
        "meses_totais": 33
    },
    "dados": { "2024-01": [...], ... }
}
```

## Formato do site (o que o scraper precisa entender)

```
Setembro 2026
2026
2º Semestre

Dia   Cota (m)   Encheu/Vazou (cm)
1     24.09      -10.00
2     23.94      -15.00
3     23.80      -14.00
```

O site mostra os últimos ~5-6 meses nessa estrutura, mais recente primeiro.

## Atualização manual (fallback)

Se a automação falhar temporariamente:

```bash
python3 scripts/update-data.py --mes 2026-09 --dados "24.09,23.94,23.80"
bash scripts/deploy.sh "Update manual setembro"
```

## Validações automáticas

Tanto o `scraper.py` quanto o `update-data.py` detectam:

1. **Variações suspeitas**: >30cm entre dias consecutivos
2. **Valores fora da faixa**: cotas < 10m ou > 32m
3. **Transições inconsistentes** entre o fim de um mês e o início do outro

Erros comuns do site (observados historicamente):
- Dígito faltando (`20.12` em vez de `28.12`)
- Vírgula em vez de ponto (`27,52` em vez de `27.52`)
- Dias duplicados ou pulados na numeração

O scraper **avisa mas não bloqueia** essas anomalias (não há como pedir
confirmação humana num cron job) — os alertas aparecem na aba **Actions**
do GitHub como `::warning::`. Vale revisar de vez em quando.

## Validar tudo de uma vez

```bash
python3 scripts/update-data.py --validar
```
