#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
import pandas as pd

ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
UFPR = Path(__file__).parent.parent / "dados" / "ufpr_extraido.json"
PERG = Path(__file__).parent.parent / "dados" / "pergamum_extraido.json"

def norm(s):
    if s is None or (isinstance(s, float) and s != s):
        return ""
    return re.sub(r"\s+", " ", str(s).strip().lower())

df = pd.read_excel(r"C:\Users\Usuario\Desktop\fora_escopo_numerado.xlsx")
sim = df[df["Eliminar?"].astype(str).str.strip().str.lower() == "sim"]
print("Marcados 'sim':", len(sim))

# Build set of (autor_norm, titulo_norm) to remove
to_remove_keys = set()
for _, row in sim.iterrows():
    to_remove_keys.add((norm(row.get("Autor")), norm(row.get("Título"))))

# Also build set of titles alone for matching (in case author differs slightly)
to_remove_titles = set(norm(row.get("Título")) for _, row in sim.iterrows())

# Update acervo.json
data = json.loads(ACERVO.read_text(encoding="utf-8"))
antes = len(data)
removed_ids = []
kept = []
for it in data:
    key = (norm(it.get("autor")), norm(it.get("titulo")))
    if key in to_remove_keys or norm(it.get("titulo")) in to_remove_titles:
        removed_ids.append(it["id"])
        continue
    kept.append(it)
ACERVO.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
print("Acervo: antes", antes, "depois", len(kept), "removidos", antes - len(kept))

# Update ufpr_extraido.json
if UFPR.exists():
    ufpr = json.loads(UFPR.read_text(encoding="utf-8"))
    before = len(ufpr)
    ufpr = [it for it in ufpr if norm(it.get("titulo")) not in to_remove_titles]
    UFPR.write_text(json.dumps(ufpr, ensure_ascii=False, indent=2), encoding="utf-8")
    print("UFPR extraido: antes", before, "depois", len(ufpr), "removidos", before - len(ufpr))

# Update pergamum_extraido.json
if PERG.exists():
    perg = json.loads(PERG.read_text(encoding="utf-8"))
    before = len(perg)
    perg = [it for it in perg if norm(it.get("titulo")) not in to_remove_titles]
    PERG.write_text(json.dumps(perg, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Pergamum extraido: antes", before, "depois", len(perg), "removidos", before - len(perg))

# Save removed ids
(Path(__file__).parent / "removidos_fora_escopo.txt").write_text("\n".join(sorted(removed_ids)), encoding="utf-8")
print("IDs removidos salvos em scripts/removidos_fora_escopo.txt")