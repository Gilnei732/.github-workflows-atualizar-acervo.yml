#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, csv
from pathlib import Path
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
OUTDIR = Path(__file__).parent.parent / "dados" / "exportacao_fora_escopo"
OUTDIR.mkdir(parents=True, exist_ok=True)

data = json.loads(ACERVO.read_text(encoding="utf-8"))
kw_tema = ["negro", "negra", "racismo", "afro", "quilomb", "etnico", "étnico", "racial", "discrimina", "african", "afro-brasileiro", "afro brasileiro", "capoeira", "candombl", "umbanda", "ancestralidade", "escravid", "escravo", "aboliç", "preconceito", "diversidade", "identidade", "movimento negro", "relações étnico"]

def is_related(title, citacao):
    text = ((title or "") + " " + (citacao or "")).lower()
    return any(k in text for k in kw_tema)

fora = [it for it in data if not (any(k in (it.get("titulo") or "").lower() for k in ["negro", "negra", "racismo"]) or is_related(it.get("titulo"), it.get("citacao_abnt")))]

# CSV with BOM
csv_path = OUTDIR / "fora_escopo_numerado.csv"
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Nº", "ID", "Autor", "Ano", "Tipo", "Instituição", "Título", "Referência ABNT", "Link", "PDF", "Eliminar?"])
    for idx, it in enumerate(fora, 1):
        w.writerow([idx, it.get("id"), it.get("autor"), it.get("ano"), it.get("tipo"), it.get("instituicao"), it.get("titulo"), it.get("citacao_abnt"), it.get("link"), it.get("pdf"), ""])

# HTML .xls
html_path = OUTDIR / "fora_escopo_numerado.xls"
cols = ["Nº", "ID", "Autor", "Ano", "Tipo", "Instituição", "Título", "Referência ABNT", "Link", "PDF", "Eliminar?"]
html = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:excel" xmlns="http://www.w3.org/TR/REC-html40">'
html += '<head><meta charset="UTF-8"><style>td,th{border:1px solid #999;padding:4px;font-family:Calibri;font-size:11pt;} th{background:#2c3e50;color:#fff;font-weight:bold;} tr:nth-child(even){background:#f2f2f2;}</style></head><body>'
html += '<table><thead><tr>' + ''.join('<th>'+c+'</th>' for c in cols) + '</tr></thead><tbody>'
for idx, it in enumerate(fora, 1):
    vals = [idx, it.get("id"), it.get("autor"), it.get("ano"), it.get("tipo"), it.get("instituicao"), it.get("titulo"), it.get("citacao_abnt"), it.get("link"), it.get("pdf"), ""]
    html += '<tr>' + ''.join('<td>' + ("" if v is None else str(v)) + '</td>' for v in vals) + '</tr>'
html += '</tbody></table></body></html>'
html_path.write_text(html, encoding="utf-8")

print("CSV:", csv_path, "(", len(fora), "itens )")
print("XLS (HTML):", html_path, "(", len(fora), "itens )")