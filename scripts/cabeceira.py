#!/usr/bin/env python3
"""Busca no SACE/SGB o nível diário de estações a montante de Manaus
(Tabatinga e Manacapuru, rio Solimões) e grava src/cabeceira.js.

Fonte: https://sace.sgb.gov.br (relatório de cada estação, dados de telemetria).
Falha ruidosamente (exit 1) se não conseguir ler: nunca grava dado incerto.
"""
import json, re, sys, datetime
from collections import OrderedDict
import requests

BASE = "https://sace.sgb.gov.br/relatorio.php"
ESTACOES = OrderedDict([
    ("tabatinga",  {"nome": "Tabatinga",  "rio": "Solimões", "pm": 15, "s": 36, "sr": ""}),
    ("manacapuru", {"nome": "Manacapuru", "rio": "Solimões", "pm": 12, "s": 26, "sr": 99}),
])
DIAS = 150


def parse(html):
    m = re.search(r"const labels\s*=\s*\[([^\]]*)\]", html)
    v = re.search(r"const valoresCota\s*=\s*\[([^\]]*)\]", html)
    if not m or not v:
        raise ValueError("labels/valoresCota não encontrados (site mudou?)")
    labels = re.findall(r"'([^']+)'", m.group(1))
    vals = [x.strip() for x in v.group(1).split(",") if x.strip()]
    if len(labels) != len(vals):
        raise ValueError("labels e valores com tamanhos diferentes")
    por_dia = {}
    for l, x in zip(labels, vals):
        try:
            c = float(x)
        except ValueError:
            continue
        if c == 0:  # preenchimento sem leitura
            continue
        por_dia.setdefault(l[:10], []).append(c / 100.0)
    dias = sorted(por_dia)[-DIAS:]
    serie = [[d, round(sum(por_dia[d]) / len(por_dia[d]), 2)] for d in dias]
    return serie


def main():
    out = OrderedDict()
    for chave, e in ESTACOES.items():
        r = requests.get(BASE, params={"apenas_grafico": "sim", "bacia": "amazonas",
                                       "pm": e["pm"], "s": e["s"], "sr": e["sr"]},
                         headers={"User-Agent": "Mozilla/5.0 RioNegroDashboard"}, timeout=60)
        r.raise_for_status()
        serie = parse(r.text)
        if len(serie) < 20:
            raise ValueError("%s: poucos dias lidos (%d)" % (e["nome"], len(serie)))
        niveis = [x[1] for x in serie]
        if min(niveis) < -2 or max(niveis) > 40:
            raise ValueError("%s: valores fora do intervalo plausível" % e["nome"])
        ultimo = datetime.date.fromisoformat(serie[-1][0])
        if (datetime.date.today() - ultimo).days > 5:
            print("::warning::%s: último dado é de %s" % (e["nome"], ultimo))
        out[chave] = {"nome": e["nome"], "rio": e["rio"], "dias": serie}
        print("%s: %d dias, último %s = %.2f m" % (e["nome"], len(serie), serie[-1][0], serie[-1][1]))
    corpo = ("// Dados do SACE/SGB (sace.sgb.gov.br): gerado automaticamente por scripts/cabeceira.py\n"
             "// Não editar manualmente. Atualizado em %s UTC\n"
             "const cabeceira = %s;\n") % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                                          json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    open("src/cabeceira.js", "w", encoding="utf-8").write(corpo)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa
        print("::error::cabeceira.py falhou: %s" % exc)
        sys.exit(1)
