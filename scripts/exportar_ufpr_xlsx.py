#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exporta os itens da UFPR (com PDF) para XLSX, incluindo citacao ABNT."""
import json
from pathlib import Path

import pandas as pd

SRC = Path(__file__).parent.parent / "dados" / "ufpr_extraido.json"
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
OUTDIR = Path(__file__).parent.parent / "dados" / "exportacao_ufpr"
OUTDIR.mkdir(parents=True, exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))
acervo = {i["id"]: i for i in json.loads(ACERVO.read_text(encoding="utf-8"))}

# only items with pdf
data = [i for i in data if i.get("pdf")]

COLS = ["id", "titulo", "autor", "ano", "tipo", "instituicao", "resumo", "link", "pdf", "possui_pdf", "citacao_abnt", "data_original"]
rows = []
for i in data:
    ai = acervo.get(i["id"], {})
    rows.append({
        "id": i.get("id"),
        "titulo": i.get("titulo"),
        "autor": i.get("autor"),
        "ano": i.get("ano"),
        "tipo": ai.get("tipo", i.get("tipo")),
        "instituicao": i.get("instituicao"),
        "resumo": i.get("resumo"),
        "link": i.get("link"),
        "pdf": i.get("pdf"),
        "possui_pdf": "Sim",
        "citacao_abnt": ai.get("citacao_abnt", ""),
        "data_original": i.get("_data_original"),
    })
df = pd.DataFrame(rows, columns=COLS)

path = OUTDIR / "ufpr_com_pdf.xlsx"
df.to_excel(path, index=False, engine="openpyxl")
print("Criado: " + str(path) + " (" + str(len(df)) + " itens)")
print("Pasta: " + str(OUTDIR))