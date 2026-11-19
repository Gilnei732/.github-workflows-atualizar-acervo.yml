#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))
data.sort(key=lambda it: ((it.get("autor") or "").lower(), (it.get("titulo") or "").lower()))
ACERVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Ordenado:", len(data), "itens")