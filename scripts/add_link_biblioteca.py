#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adiciona campo link_biblioteca ao acervo.json para itens do Pergamum."""
import json
from pathlib import Path

ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))

for item in data:
    if "link_biblioteca" in item:
        continue
    if item.get("id", "").startswith("perg-"):
        cod = item["id"].replace("perg-", "")
        item["link_biblioteca"] = "https://uel.pergamum.com.br/acervo/" + cod
    else:
        item["link_biblioteca"] = ""

ACERVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Atualizado: " + str(len(data)) + " itens")
print("Com link_biblioteca: " + str(sum(1 for i in data if i.get("link_biblioteca"))))
