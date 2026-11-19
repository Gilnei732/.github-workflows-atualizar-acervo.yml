#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re
from collections import defaultdict, Counter
from pathlib import Path

d = json.load(open(Path(__file__).parent.parent / "dados" / "acervo.json", encoding="utf-8"))
lines = []
lines.append("# Relatório de análise do acervo (" + str(len(d)) + " registros)\n")

# 1. Duplicados
lines.append("## 1. Elementos repetidos (duplicados ou edições múltiplas)\n")
# exact dupes by author+title
groups = defaultdict(list)
for i, it in enumerate(d):
    key = ((it.get("autor") or "").strip().lower(), (it.get("titulo") or "").strip().lower())
    groups[key].append(i)
exact = {k: v for k, v in groups.items() if len(v) > 1}
lines.append("### Duplicata exata (mesmo título e autor)\n")
if exact:
    lines.append("| # | ID | Autor | Ano | Título |")
    lines.append("|---|-----|-------|-----|--------|")
    n = 1
    for k, v in exact.items():
        for i in v:
            it = d[i]
            ano = it.get("ano") if it.get("ano") else "s/d"
            lines.append("| " + str(n) + " | " + it["id"] + " | " + (it.get("autor") or "") + " | " + str(ano) + " | " + (it.get("titulo") or "")[:70] + " |")
            n += 1
else:
    lines.append("Nenhuma duplicata exata encontrada.\n")

# near-dupes by first 50 chars of title
short = defaultdict(list)
for i, it in enumerate(d):
    t = (it.get("titulo") or "")[:50].lower().strip()
    short[t].append(i)
near = {k: v for k, v in short.items() if len(v) > 1 and k not in [ ( (d[i].get("autor") or "").strip().lower(), (d[i].get("titulo") or "").strip().lower()) for i in [] ]}
# exclude exact dupes
near = {}
for k, v in short.items():
    if len(v) > 1:
        # check if not exact duplicate
        authors = set((d[i].get("autor") or "").strip().lower() for i in v)
        if len(authors) > 1 or len(v) > 2:
            near[k] = v
        elif len(v) == 2:
            # could be exact dupe; check titles fully
            t0 = (d[v[0]].get("titulo") or "").strip().lower()
            t1 = (d[v[1]].get("titulo") or "").strip().lower()
            if t0 != t1:
                near[k] = v

lines.append("\n### Mesma obra em edições/anos diferentes\n")
lines.append("| # | ID | Autor | Ano | Título |")
lines.append("|---|-----|-------|-----|--------|")
n = 1
for k, v in near.items():
    for i in v:
        it = d[i]
        ano = it.get("ano") if it.get("ano") else "s/d"
        lines.append("| " + str(n) + " | " + it["id"] + " | " + (it.get("autor") or "") + " | " + str(ano) + " | " + (it.get("titulo") or "")[:70] + " |")
        n += 1

# 2. Rio Negro
lines.append("\n## 2. Itens com \"Rio Negro\" no título (" + str(sum(1 for it in d if "rio negro" in (it.get("titulo") or "").lower())) + " registros)\n")
lines.append("| # | ID | Autor | Ano | Título |")
lines.append("|---|-----|-------|-----|--------|")
rn = [(i, it) for i, it in enumerate(d) if "rio negro" in (it.get("titulo") or "").lower()]
for idx, (i, it) in enumerate(rn, 1):
    ano = it.get("ano") if it.get("ano") else "s/d"
    autor = it.get("autor") or "(não informado)"
    lines.append("| " + str(idx) + " | " + it["id"] + " | " + autor + " | " + str(ano) + " | " + (it.get("titulo") or "")[:70] + " |")

lines.append("\n> **Nota:** Vários desses itens referem-se a \"Rio Negro\" como nome de lugar (rio/região amazônica) e não necessariamente à temática negra. Recomenda-se revisão para manter apenas os pertinentes ao acervo.")

(Path(__file__).parent.parent / "relatorio_duplicados_rionegro.md").write_text("\n".join(lines), encoding="utf-8")
print("Relatório salvo.")