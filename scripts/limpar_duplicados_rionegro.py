#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))
antes = len(data)

# 1. Remove exact duplicate: keep perg-127750, remove perg-175650
ids_remove = {"perg-175650"}

# 2. Remove all items with "Rio Negro" in title
for it in data:
    if "rio negro" in (it.get("titulo") or "").lower():
        ids_remove.add(it["id"])

print("IDs a remover:", len(ids_remove))
for rid in sorted(ids_remove):
    print("  ", rid)

novos = [it for it in data if it["id"] not in ids_remove]
ACERVO.write_text(json.dumps(novos, ensure_ascii=False, indent=2), encoding="utf-8")
print("Antes:", antes, "Depois:", len(novos), "Removidos:", antes - len(novos))