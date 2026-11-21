#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))

kw_tema = ["negro", "negra", "racismo", "afro", "quilomb", "etnico", "étnico", "racial", "discrimina", "african", "afro-brasileiro", "afro brasileiro", "capoeira", "candombl", "umbanda", "ancestralidade", "escravid", "escravo", "aboliç", "preconceito", "diversidade", "identidade", "movimento negro", "relações étnico"]

def is_related(title, citacao):
    text = ((title or "") + " " + (citacao or "")).lower()
    return any(k in text for k in kw_tema)

fora = []
for it in data:
    t = (it.get("titulo") or "").lower()
    has_kw = any(k in t for k in ["negro", "negra", "racismo"])
    related = is_related(it.get("titulo"), it.get("citacao_abnt"))
    if not has_kw and not related:
        fora.append(it)

out = []
out.append("# Trabalhos fora do escopo temático (" + str(len(fora)) + " de " + str(len(data)) + " registros)\n")
out.append("Itens cujo título não contém 'negro', 'negra', 'racismo' nem termos afins (afro, quilombo, racial, escravidão, identidade, etc.).\n")
out.append("| # | ID | Autor | Ano | Título |")
out.append("|---|-----|-------|-----|--------|")
for idx, it in enumerate(fora, 1):
    ano = it.get("ano") if it.get("ano") else "s/d"
    autor = (it.get("autor") or "(não informado)").replace("|", "/")
    titulo = (it.get("titulo") or "").replace("|", "/")[:80]
    out.append("| " + str(idx) + " | " + it["id"] + " | " + autor + " | " + str(ano) + " | " + titulo + " |")

(Path(__file__).parent.parent / "relatorio_fora_escopo.md").write_text("\n".join(out), encoding="utf-8")
print("Total itens:", len(data))
print("Fora do escopo:", len(fora))
print("Salvo em: relatorio_fora_escopo.md")