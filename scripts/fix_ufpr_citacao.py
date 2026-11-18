#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-busca citacao_abnt para itens UFPR que estão sem."""
import json, re, html, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))

def fetch_citacao(item):
    url = item.get("link", "")
    if not url:
        return item["id"], ""
    try:
        r = requests.get(url, verify=False, timeout=30)
        html_text = r.text
    except Exception:
        return item["id"], ""
    metas = dict(re.findall(r'<meta name="([^"]+)" content="([^"]*)"', html_text))
    author = metas.get("DC.creator", "").strip()
    title = metas.get("DC.title", "").strip()
    year = (metas.get("citation_date") or metas.get("DCTERMS.issued") or "").strip()[:4]
    extent = metas.get("DCTERMS.extent", "").strip()
    # degree desc
    degree_desc = ""
    for d in re.findall(r'DC\.description" content="([^"]*)"', html_text):
        if any(k in d.lower() for k in ["disserta", "tese", "monografia", "trabalho de conclus"]):
            degree_desc = d
            break
    # clean author (remove birth year)
    author = re.sub(r",\s*\d{4}-?\s*$", "", author).strip()
    # build citation
    citacao = ""
    if author:
        citacao += author + ". "
    if title:
        citacao += html.unescape(title) + ". "
    if year:
        citacao += year + ". "
    if extent:
        citacao += extent + ". "
    if degree_desc:
        citacao += degree_desc + "."
    return item["id"], html.unescape(citacao.strip())

# target items: ufpr with empty citacao
targets = [it for it in data if it["id"].startswith("ufpr") and not (it.get("citacao_abnt") or "").strip()]
print("Itens sem citacao: " + str(len(targets)), flush=True)

results = {}
done = 0
with ThreadPoolExecutor(max_workers=20) as ex:
    futures = {ex.submit(fetch_citacao, it): it for it in targets}
    for fut in as_completed(futures):
        rid, cit = fut.result()
        results[rid] = cit
        done += 1
        if done % 25 == 0:
            print("Processados " + str(done) + "/" + str(len(targets)), flush=True)

# apply
changed = 0
for item in data:
    if item["id"] in results and results[item["id"]]:
        item["citacao_abnt"] = results[item["id"]]
        changed += 1

ACERVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Citações atualizadas: " + str(changed), flush=True)
still = sum(1 for i in data if i["id"].startswith("ufpr") and not (i.get("citacao_abnt") or "").strip())
print("Ainda sem citacao: " + str(still), flush=True)