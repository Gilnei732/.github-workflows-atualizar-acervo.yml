#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrai URLs diretas de PDF para os itens online do pergamum_extraido.json."""
import json, re, time
from pathlib import Path

OUT = Path(__file__).parent.parent / "dados" / "pergamum_extraido.json"
data = json.loads(OUT.read_text(encoding="utf-8"))

def get_pdf(handle_url):
    try:
        import requests
        r = requests.get(handle_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30, allow_redirects=True)
        m = re.search(r'citation_pdf_url"\s+content="([^"]+)"', r.text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""

online = [i for i in data if i.get("_possui_doc_online")]
print("Itens online: " + str(len(online)), flush=True)
done = 0
for i in online:
    if i.get("pdf", "").endswith("/download"):
        continue
    pdf = get_pdf(i["link"])
    if pdf:
        i["pdf"] = pdf
    done += 1
    if done % 10 == 0:
        print("Processados " + str(done) + "/" + str(len(online)), flush=True)
    time.sleep(0.2)

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
com_pdf = sum(1 for i in data if i.get("pdf", "").endswith("/download") or "bitstreams" in i.get("pdf",""))
print("Concluido. Com PDF direto: " + str(com_pdf), flush=True)
print("Salvo em: " + str(OUT), flush=True)
