#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Limpa entidades HTML e ajusta nomes de autor nos itens UFPR do acervo."""
import json, html, re
from pathlib import Path
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))

def clean_author(a):
    # remove trailing birth year like ", 1987-"
    a = re.sub(r",\s*\d{4}-?\s*$", "", a.strip())
    return a.strip()

changed = 0
for item in data:
    if not item.get("id", "").startswith("ufpr"):
        continue
    # decode html entities in text fields
    for f in ["titulo", "citacao_abnt", "resumo", "autor"]:
        if item.get(f):
            item[f] = html.unescape(item[f])
    # clean author
    item["autor"] = clean_author(item.get("autor", ""))
    # remove birth year from citacao_abnt (", YYYY-." pattern)
    if item.get("citacao_abnt"):
        item["citacao_abnt"] = re.sub(r",\s*\d{4}-\.", ".", item["citacao_abnt"])
        item["citacao_abnt"] = re.sub(r",\s*\d{4}-\s*\.", ".", item["citacao_abnt"])
    changed += 1

ACERVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Itens UFPR limpos: " + str(changed))