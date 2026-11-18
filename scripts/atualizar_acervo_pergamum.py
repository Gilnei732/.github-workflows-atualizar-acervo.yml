#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza dados/acervo.json com os itens de pergamum_todos_por_tipo.xlsx."""
import json
from pathlib import Path

import pandas as pd

SRC_XLSX = Path(__file__).parent.parent / "dados" / "exportacao_pergamum" / "pergamum_todos_por_tipo.xlsx"
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"

# Ler todas as abas
xl = pd.ExcelFile(SRC_XLSX)
frames = []
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    frames.append(df)
combined = pd.concat(frames, ignore_index=True)
print("Itens lidos do XLSX: " + str(len(combined)))

# Carregar acervo existente
existing = json.loads(ACERVO.read_text(encoding="utf-8")) if ACERVO.exists() else []
existing_ids = {r.get("id") for r in existing}
print("Itens existentes no acervo: " + str(len(existing)))

# Mapeamento de tipo (garantir classe correta)
tipo_map = {
    "dissertacao": "dissertacao",
    "tese": "tese",
    "artigo": "artigo",
    "monografia": "monografia",
    "tcc": "tcc",
    "outro": "outro",
}

novos = []
for _, row in combined.iterrows():
    rid = str(row.get("id", "")).strip()
    if not rid or rid == "nan":
        continue
    if rid in existing_ids:
        continue
    tipo_raw = str(row.get("tipo", "")).strip().lower()
    tipo = tipo_map.get(tipo_raw, "outro")
    ano = row.get("ano")
    try:
        ano = int(ano) if pd.notna(ano) else None
    except (ValueError, TypeError):
        ano = None
    pdf = row.get("pdf")
    pdf = str(pdf).strip() if pd.notna(pdf) and str(pdf).strip() and str(pdf).strip().lower() != "nan" else ""
    link = row.get("link")
    link = str(link).strip() if pd.notna(link) and str(link).strip() and str(link).strip().lower() != "nan" else ""
    citacao = row.get("citacao_abnt")
    citacao = str(citacao).strip() if pd.notna(citacao) else ""
    autor = row.get("autor")
    autor = str(autor).strip() if pd.notna(autor) else ""
    titulo = row.get("titulo")
    titulo = str(titulo).strip() if pd.notna(titulo) else ""
    instituicao = row.get("instituicao")
    instituicao = str(instituicao).strip() if pd.notna(instituicao) else "Biblioteca UEL (acervo)"

    item = {
        "id": rid,
        "titulo": titulo,
        "autor": autor,
        "ano": ano,
        "tipo": tipo,
        "instituicao": instituicao,
        "nucleo": "",
        "regiao": "",
        "tema": "tematica negra (catalogo Pergamum/UEL)",
        "resumo": "",
        "link": link,
        "pdf": pdf,
        "citacao_abnt": citacao,
        "destaque": False,
    }
    novos.append(item)
    existing_ids.add(rid)

merged = existing + novos
ACERVO.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
print("Novos itens adicionados: " + str(len(novos)))
print("Total no acervo agora: " + str(len(merged)))

from collections import Counter
print("Por tipo: " + str(dict(Counter(i["tipo"] for i in merged))))
print("Com PDF: " + str(sum(1 for i in merged if i.get("pdf"))))
print("Sem PDF: " + str(sum(1 for i in merged if not i.get("pdf"))))
