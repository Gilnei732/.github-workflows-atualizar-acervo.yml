#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
import pandas as pd

ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
OUTDIR = Path(__file__).parent.parent / "dados" / "exportacao_fora_escopo"
OUTDIR.mkdir(parents=True, exist_ok=True)

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

rows = []
for idx, it in enumerate(fora, 1):
    rows.append({
        "Nº": idx,
        "ID": it.get("id"),
        "Autor": it.get("autor"),
        "Ano": it.get("ano"),
        "Tipo": it.get("tipo"),
        "Instituição": it.get("instituicao"),
        "Título": it.get("titulo"),
        "Referência ABNT": it.get("citacao_abnt"),
        "Link": it.get("link"),
        "PDF": it.get("pdf"),
        "Eliminar?": "",
    })

df = pd.DataFrame(rows)
path = OUTDIR / "fora_escopo_numerado.xlsx"
df.to_excel(path, index=False, engine="openpyxl")
print("Criado:", path, "(", len(df), "itens )")
print("Pasta:", OUTDIR)