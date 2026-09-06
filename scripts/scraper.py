#!/usr/bin/env python3
"""
Scraper do Rio Negro — Porto de Manaus

Busca a página pública https://portodemanaus.com.br/nivel-do-rio-negro/,
extrai as tabelas de cota diária (uma por mês, a página mostra os últimos
5-6 meses) e atualiza src/data.js com os valores mais recentes.

Uso:
    python3 scripts/scraper.py                 # roda normalmente, grava mudanças
    python3 scripts/scraper.py --dry-run        # só mostra o que mudaria, não grava
    python3 scripts/scraper.py --verbose         # mostra detalhes de parsing

Rodado automaticamente via GitHub Actions (.github/workflows/atualizar-dados.yml)
de segunda a sexta às 8h (horário de Manaus).

⚠️ Sobre uso responsável:
Este script faz UMA requisição por execução, roda no máximo 1x/dia em dias
úteis, e se identifica com um User-Agent descritivo. Ele lê apenas a página
pública de consulta de nível do rio — a mesma que qualquer visitante vê no
navegador. Se o site mudar de estrutura e o scraper parar de funcionar,
ele vai falhar de forma visível (erro no GitHub Actions) em vez de silenciosamente
gravar dados errados.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Dependências faltando. Rode: pip install -r scripts/requirements.txt")
    sys.exit(1)


URL = "https://portodemanaus.com.br/nivel-do-rio-negro/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RioNegroDashboardBot/1.0; "
        "+https://github.com/jsavinojspds-cyber/rio-negro; uso pessoal, 1 req/dia)"
    )
}

MESES_PT = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
}

PROJECT_ROOT = Path(__file__).parent.parent
DATA_JS_PATH = PROJECT_ROOT / "src" / "data.js"
DATA_JSON_PATH = PROJECT_ROOT / "data" / "rio-negro-cotas.json"

MANAUS_TZ = timezone(timedelta(hours=-4))


def log(msg, verbose_only=False, verbose=False):
    if not verbose_only or verbose:
        print(msg)


def fetch_page():
    """Busca o HTML da página do Porto de Manaus."""
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_tabelas(html, verbose=False):
    """
    Retorna lista de dicts: [{"ano": 2026, "mes": 9, "cotas": [24.09, 23.94, ...]}]
    Uma entrada por tabela mensal encontrada na página (a página mostra
    tipicamente os últimos 5-6 meses, do mais recente para o mais antigo).
    """
    soup = BeautifulSoup(html, "html.parser")
    tabelas = soup.find_all("table")
    log(f"🔍 {len(tabelas)} tabela(s) encontrada(s) na página", verbose_only=True, verbose=verbose)

    resultados = []
    padrao_mes_ano = re.compile(
        r"(Janeiro|Fevereiro|Março|Marco|Abril|Maio|Junho|Julho|Agosto|"
        r"Setembro|Outubro|Novembro|Dezembro)\s+(\d{4})",
        re.IGNORECASE,
    )

    for tbl in tabelas:
        # Procura o texto "Mês AAAA" mais próximo ANTES desta tabela no documento
        texto_anterior = tbl.find_previous(string=padrao_mes_ano)
        if not texto_anterior:
            continue

        m = padrao_mes_ano.search(str(texto_anterior))
        if not m:
            continue

        mes_nome = m.group(1).lower()
        ano = int(m.group(2))
        mes_num = MESES_PT.get(mes_nome)
        if not mes_num:
            continue

        linhas = []
        trs = tbl.find_all("tr")
        for tr in trs[1:]:  # pula cabeçalho (Dia / Cota / Encheu-Vazou)
            celulas = tr.find_all(["td", "th"])
            textos = [c.get_text(strip=True) for c in celulas]
            if len(textos) < 2:
                continue
            try:
                dia = int(re.sub(r"[^\d]", "", textos[0]))
                cota_str = textos[1].replace(",", ".")
                cota = float(re.sub(r"[^\d.\-]", "", cota_str))
                linhas.append((dia, cota))
            except (ValueError, IndexError):
                continue

        if not linhas:
            continue

        linhas.sort(key=lambda x: x[0])
        cotas = [c for _, c in linhas]

        resultados.append({"ano": ano, "mes": mes_num, "cotas": cotas})
        log(f"  📅 {mes_nome.capitalize()}/{ano}: {len(cotas)} dias "
            f"(último: dia {linhas[-1][0]} = {linhas[-1][1]}m)", verbose_only=True, verbose=verbose)

    return resultados


def validar_cotas(cotas, contexto=""):
    """Detecta anomalias óbvias (mesma lógica do update-data.py)."""
    alertas = []
    for i in range(1, len(cotas)):
        diff = abs(cotas[i] - cotas[i - 1]) * 100
        if diff > 30:
            alertas.append(
                f"{contexto}: variação suspeita de {diff:.0f}cm no dia {i+1} "
                f"({cotas[i-1]}m → {cotas[i]}m)"
            )
    for i, v in enumerate(cotas):
        if v < 10 or v > 32:
            alertas.append(f"{contexto}: valor fora da faixa no dia {i+1}: {v}m")
    return alertas


def load_dados_atuais():
    """Lê o objeto `dados` já existente em src/data.js."""
    if not DATA_JS_PATH.exists():
        return {}
    content = DATA_JS_PATH.read_text(encoding="utf-8")
    match = re.search(r"const dados = (\{.*?\});", content, re.DOTALL)
    if not match:
        raise ValueError("Não foi possível localizar 'const dados = {...}' em data.js")
    return json.loads(match.group(1))


def save_data_js(dados, timestamp_str):
    """Grava o objeto `dados` atualizado em src/data.js."""
    chaves = sorted(dados.keys())
    linhas = [
        "// 🌊 Dados do Rio Negro — Porto de Manaus",
        "// ⚠️ ARQUIVO GERADO AUTOMATICAMENTE pelo scraper (scripts/scraper.py)",
        "// Não editar manualmente — suas mudanças serão sobrescritas no próximo update",
        "//",
        f"// Última atualização: {timestamp_str}",
        "",
        f'const ultimaVerificacao = "{timestamp_str}";', "", "const dados = {",
    ]
    for i, k in enumerate(chaves):
        valores_str = ",".join(str(v) for v in dados[k])
        virgula = "," if i < len(chaves) - 1 else ""
        linhas.append(f'    "{k}": [{valores_str}]{virgula}')
    linhas.append("};")
    linhas.append("")
    linhas.append("if (typeof module !== 'undefined' && module.exports) {")
    linhas.append("    module.exports = dados;")
    linhas.append("}")
    DATA_JS_PATH.write_text("\n".join(linhas), encoding="utf-8")


def save_json_backup(dados, timestamp_str):
    """Mantém também um JSON de referência/backup."""
    DATA_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "fonte": "Porto de Manaus",
            "url_original": URL,
            "unidade": "metros",
            "ultima_atualizacao": timestamp_str,
            "meses_totais": len(dados),
        },
        "dados": dados,
    }
    DATA_JSON_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description="Atualiza dados do Rio Negro a partir do site do Porto de Manaus")
    parser.add_argument("--dry-run", action="store_true", help="Não grava nada, só mostra o que mudaria")
    parser.add_argument("--verbose", action="store_true", help="Mostra detalhes do parsing")
    args = parser.parse_args()

    print(f"🌊 Rio Negro Scraper — {datetime.now(MANAUS_TZ).strftime('%Y-%m-%d %H:%M')} (Manaus)")
    print(f"📡 Buscando: {URL}")

    try:
        html = fetch_page()
    except requests.RequestException as e:
        print(f"❌ Falha ao acessar o site: {e}")
        print("::error::Scraper não conseguiu acessar portodemanaus.com.br")
        sys.exit(1)

    resultados = parse_tabelas(html, verbose=args.verbose)
    
    # Correções conhecidas de erros de digitação no site oficial
    # (o site mostra o dígito errado e provavelmente nunca vai corrigir)
    CORRECOES_CONHECIDAS = {
        ("2026-06", 6): 28.12,  # site mostra 20.12, valor real é 28.12
    }
    for item in resultados:
        key = f"{item['ano']}-{item['mes']:02d}"
        for i, cota in enumerate(item["cotas"]):
            dia = i + 1
            if (key, dia) in CORRECOES_CONHECIDAS:
                valor_correto = CORRECOES_CONHECIDAS[(key, dia)]
                if cota != valor_correto:
                    print(f"🔧 Corrigindo erro conhecido: {key} dia {dia}: {cota}m → {valor_correto}m")
                    item["cotas"][i] = valor_correto

    if not resultados:
        print("❌ Nenhuma tabela de dados foi encontrada na página.")
        print("   O site pode ter mudado de estrutura — o parser precisa ser ajustado.")
        print("::error::Scraper não encontrou nenhuma tabela reconhecível")
        sys.exit(1)

    print(f"✅ {len(resultados)} mês(es) encontrado(s) na página")

    dados_atuais = load_dados_atuais()
    dados_novos = dict(dados_atuais)  # cópia
    mudancas = []
    alertas_totais = []

    for item in resultados:
        key = f"{item['ano']}-{item['mes']:02d}"
        cotas_novas = item["cotas"]
        cotas_antigas = dados_atuais.get(key)

        alertas = validar_cotas(cotas_novas, contexto=key)
        if alertas:
            alertas_totais.extend(alertas)

        if cotas_antigas != cotas_novas:
            dados_novos[key] = cotas_novas
            if cotas_antigas is None:
                mudancas.append(f"➕ {key}: novo mês, {len(cotas_novas)} dias")
            else:
                dias_antes = len(cotas_antigas)
                dias_depois = len(cotas_novas)
                mudancas.append(
                    f"🔄 {key}: {dias_antes} → {dias_depois} dias "
                    f"(último valor: {cotas_novas[-1]}m)"
                )

    if alertas_totais:
        print("\n⚠️  ALERTAS DE VALIDAÇÃO:")
        for a in alertas_totais:
            print(f"   {a}")
            print(f"::warning::{a}")

    if False:  # sempre grava, mesmo sem mudanca (registra hora da verificacao)
        print("\n✅ Nenhuma mudança — dados já estão atualizados.")
        # Ainda assim retorna 0 (sucesso), o workflow não vai commitar nada
        sys.exit(0)

    print(f"\n📝 {len(mudancas)} mudança(s) detectada(s):")
    for m in mudancas:
        print(f"   {m}")

    if args.dry_run:
        print("\n🧪 Modo --dry-run: nada foi gravado.")
        sys.exit(0)

    timestamp_str = datetime.now(MANAUS_TZ).strftime("%Y-%m-%d %H:%M")
    save_data_js(dados_novos, timestamp_str)
    save_json_backup(dados_novos, timestamp_str)

    print(f"\n✅ src/data.js atualizado ({len(dados_novos)} meses no total)")
    print(f"✅ data/rio-negro-cotas.json atualizado (backup)")


if __name__ == "__main__":
    main()
