#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrai URLs diretas de PDF para os itens da UFPR (concorrente)."""
import json, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUT = Path(__file__).parent.parent / "dados" / "ufpr_extraido.json"
data = json.loads(OUT.read_text(encoding="utf-8"))

def get_pdf(handle_url):
    try:
        r = requests.get(handle_url, verify=False, timeout=30)
        m = re.search(r'citation_pdf_url"\s+content="([^"]+)"', r.text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""

# only pending
pending_idx = [i for i, it in enumerate(data) if not it.get("pdf")]
print("Pendentes: " + str(len(pending_idx)), flush=True)

def worker(i):
    pdf = get_pdf(data[i]["link"])
    return i, pdf

done = 0
with ThreadPoolExecutor(max_workers=30) as ex:
    futures = {ex.submit(worker, i): i for i in pending_idx}
    for fut in as_completed(futures):
        i, pdf = fut.result()
        if pdf:
            data[i]["pdf"] = pdf
        done += 1
        if done % 100 == 0:
            OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            com = sum(1 for x in data if x.get("pdf"))
            print("Processados " + str(done) + "/" + str(len(pending_idx)) + " | com PDF: " + str(com), flush=True)

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
com = sum(1 for x in data if x.get("pdf"))
print("Concluido. Com PDF: " + str(com) + "/" + str(len(data)), flush=True)