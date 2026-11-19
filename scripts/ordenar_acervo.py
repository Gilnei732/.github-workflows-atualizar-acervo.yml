#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))

def sort_key(it):
    cit = (it.get("citacao_abnt") or "").strip()
    autor = (it.get("autor") or "").strip()
    base = cit or autor or (it.get("titulo") or "")
    return base.lower()

data.sort(key=sort_key)
ACERVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Ordenado:", len(data), "itens")