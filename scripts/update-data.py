#!/usr/bin/env python3
"""
Atualização manual de dados do Rio Negro (uso de backup/emergência).

Com a automação via GitHub Actions (scripts/scraper.py rodando de seg-sex
às 8h), este script normalmente NÃO é necessário. Use-o apenas se:
- Quiser adicionar um dia específico rapidamente sem esperar o próximo scrape
- O scraper automático falhar (mudança no site) e você precisar de um fallback manual
- Quiser corrigir/preencher um mês retroativo que o scraper não capturou

Uso:
    python3 scripts/update-data.py --mes 2026-09 --dados "24.09,23.94,23.80"
    python3 scripts/update-data.py --validar   # valida todos os dados existentes
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_JS_PATH = PROJECT_ROOT / "src" / "data.js"
DATA_JSON_PATH = PROJECT_ROOT / "data" / "rio-negro-cotas.json"


def load_dados():
    content = DATA_JS_PATH.read_text(encoding="utf-8")
    match = re.search(r"const dados = (\{.*?\});", content, re.DOTALL)
    if not match:
        raise ValueError("Não foi possível localizar 'const dados = {...}' em src/data.js")
    return json.loads(match.group(1))


def save_dados(dados, timestamp_str):
    chaves = sorted(dados.keys())
    linhas = [
        "// 🌊 Dados do Rio Negro — Porto de Manaus",
        "// ⚠️ ARQUIVO GERADO AUTOMATICAMENTE pelo scraper (scripts/scraper.py)",
        "// Não editar manualmente — suas mudanças serão sobrescritas no próximo update",
        "//",
        f"// Última atualização: {timestamp_str} (manual via update-data.py)",
        "",
        "const dados = {",
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

    # Backup JSON também
    DATA_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "fonte": "Porto de Manaus",
            "url_original": "https://portodemanaus.com.br/nivel-do-rio-negro/",
            "unidade": "metros",
            "ultima_atualizacao": timestamp_str,
            "meses_totais": len(dados),
        },
        "dados": dados,
    }
    DATA_JSON_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_valores(s):
    valores = []
    for v in s.split(","):
        v = v.strip().replace(",", ".")
        try:
            valores.append(float(v))
        except ValueError:
            print(f"⚠️ Valor inválido ignorado: {v}")
    return valores


def validar(valores, anterior=None):
    alertas = []
    for i in range(1, len(valores)):
        diff = abs(valores[i] - valores[i - 1]) * 100
        if diff > 30:
            alertas.append(f"Dia {i+1}: variação suspeita de {diff:.0f}cm ({valores[i-1]}m → {valores[i]}m)")
    if anterior:
        diff = abs(valores[0] - anterior[-1]) * 100
        if diff > 30:
            alertas.append(f"Transição do mês anterior suspeita: {anterior[-1]}m → {valores[0]}m ({diff:.0f}cm)")
    for i, v in enumerate(valores):
        if v < 10 or v > 32:
            alertas.append(f"Dia {i+1}: valor fora da faixa esperada: {v}m")
    return alertas


def main():
    parser = argparse.ArgumentParser(description="Atualização manual de dados do Rio Negro")
    parser.add_argument("--mes", help="Mês no formato YYYY-MM")
    parser.add_argument("--dados", help='Dados como CSV: "24.09,23.94,23.80"')
    parser.add_argument("--validar", action="store_true", help="Valida todos os dados existentes")
    args = parser.parse_args()

    dados = load_dados()

    if args.validar and not args.mes:
        print("🔍 Validando todos os dados...\n")
        chaves = sorted(dados.keys())
        algum_alerta = False
        for i, mes in enumerate(chaves):
            anterior = dados.get(chaves[i - 1]) if i > 0 else None
            alertas = validar(dados[mes], anterior)
            if alertas:
                algum_alerta = True
                print(f"📅 {mes}:")
                for a in alertas:
                    print(f"   ⚠️ {a}")
        if not algum_alerta:
            print("✅ Nenhuma anomalia encontrada.")
        return

    if not args.mes or not args.dados:
        parser.error("--mes e --dados são obrigatórios (ou use --validar sozinho)")

    if not re.match(r"^\d{4}-\d{2}$", args.mes):
        parser.error("--mes deve estar no formato YYYY-MM")

    valores = parse_valores(args.dados)
    if not valores:
        print("❌ Nenhum valor válido")
        sys.exit(1)

    ano, mes_num = args.mes.split("-")
    mes_int = int(mes_num)
    mes_anterior_key = f"{ano}-{mes_int-1:02d}" if mes_int > 1 else f"{int(ano)-1}-12"
    anterior = dados.get(mes_anterior_key)

    alertas = validar(valores, anterior)
    if alertas:
        print("⚠️ ALERTAS:")
        for a in alertas:
            print(f"   {a}")
        resp = input("\n❓ Continuar mesmo assim? (s/N): ")
        if resp.lower() != "s":
            print("❌ Abortado")
            sys.exit(1)

    dados[args.mes] = valores
    from datetime import datetime, timezone, timedelta
    timestamp_str = datetime.now(timezone(timedelta(hours=-4))).strftime("%Y-%m-%d %H:%M")
    save_dados(dados, timestamp_str)

    print(f"\n✅ {args.mes} atualizado: {len(valores)} dias, último valor {valores[-1]}m")
    print("📝 Lembre-se de: cp src/data.js data.js && cp src/index.html index.html && git add . && git commit && git push")


if __name__ == "__main__":
    main()
