#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exporta os itens extraídos do Pergamum para arquivos XLSX por tipo."""
import json
from pathlib import Path
from collections import defaultdict

import pandas as pd

SRC = Path(__file__).parent.parent / "dados" / "pergamum_extraido.json"
OUTDIR = Path(__file__).parent.parent / "dados" / "exportacao_pergamum"
OUTDIR.mkdir(parents=True, exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))

COLS = ["id", "titulo", "autor", "ano", "tipo", "instituicao", "citacao_abnt", "link", "pdf", "possui_pdf"]
# build dataframe
rows = []
for i in data:
    rows.append({
        "id": i.get("id"),
        "titulo": i.get("titulo"),
        "autor": i.get("autor"),
        "ano": i.get("ano"),
        "tipo": i.get("tipo"),
        "instituicao": i.get("instituicao"),
        "citacao_abnt": i.get("citacao_abnt"),
        "link": i.get("link"),
        "pdf": i.get("pdf"),
        "possui_pdf": "Sim" if i.get("pdf") else "Não",
    })
df = pd.DataFrame(rows, columns=COLS)

# Combined file with one sheet per type
tipos = ["dissertacao", "tese", "artigo", "monografia", "tcc", "outro"]
labels = {
    "dissertacao": "Dissertacoes",
    "tese": "Teses",
    "artigo": "Artigos",
    "monografia": "Monografias",
    "tcc": "TCCs",
    "outro": "Outros",
}

combined_path = OUTDIR / "pergamum_todos_por_tipo.xlsx"
with pd.ExcelWriter(combined_path, engine="openpyxl") as writer:
    for t in tipos:
        sub = df[df["tipo"] == t]
        if len(sub) == 0:
            continue
        sub.to_excel(writer, sheet_name=labels[t], index=False)

# Separate file per type
for t in tipos:
    sub = df[df["tipo"] == t]
    if len(sub) == 0:
        continue
    path = OUTDIR / ("pergamum_" + t + ".xlsx")
    sub.to_excel(path, index=False, engine="openpyxl")
    print("Criado: " + str(path) + " (" + str(len(sub)) + " itens)")

# Also a single combined sheet (all items)
all_path = OUTDIR / "pergamum_todos.xlsx"
df.to_excel(all_path, index=False, engine="openpyxl")
print("Criado: " + str(all_path) + " (" + str(len(df)) + " itens)")
print("Criado: " + str(combined_path))
print("Pasta: " + str(OUTDIR))
