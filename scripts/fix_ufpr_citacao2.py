#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, time
from html import unescape as html_unescape
from pathlib import Path
import requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"
data = json.loads(ACERVO.read_text(encoding="utf-8"))

def fetch_citacao(url):
    for attempt in range(3):
        try:
            r = requests.get(url, verify=False, timeout=30)
            if r.status_code != 200:
                time.sleep(1)
                continue
            r.encoding = "utf-8"
            html_text = r.text
            metas = dict(re.findall(r'<meta name="([^"]+)" content="([^"]*)"', html_text))
            author = re.sub(r",\s*\d{4}-?\s*$", "", metas.get("DC.creator", "").strip()).strip()
            title = html_unescape(metas.get("DC.title", "").strip())
            year = (metas.get("citation_date") or metas.get("DCTERMS.issued") or "").strip()[:4]
            extent = metas.get("DCTERMS.extent", "").strip()
            degree_desc = ""
            for d in re.findall(r'DC\.description" content="([^"]*)"', html_text):
                if any(k in d.lower() for k in ["disserta", "tese", "monografia", "trabalho de conclus"]):
                    degree_desc = html_unescape(d)
                    break
            citacao = ""
            if author: citacao += author + ". "
            if title: citacao += title + ". "
            if year: citacao += year + ". "
            if extent: citacao += extent + ". "
            if degree_desc: citacao += degree_desc + "."
            return citacao.strip()
        except Exception:
            time.sleep(1)
    return ""

targets = [it for it in data if it["id"].startswith("ufpr") and not (it.get("citacao_abnt") or "").strip()]
print("Pendentes: " + str(len(targets)), flush=True)

changed = 0
for i, item in enumerate(targets):
    cit = fetch_citacao(item.get("link", ""))
    if cit:
        item["citacao_abnt"] = cit
        changed += 1
    if (i+1) % 25 == 0:
        ACERVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Processados " + str(i+1) + "/" + str(len(targets)) + " | atualizados: " + str(changed), flush=True)
    time.sleep(0.2)

ACERVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Concluido. Atualizados: " + str(changed) + "/" + str(len(targets)), flush=True)
still = sum(1 for i in data if i["id"].startswith("ufpr") and not (i.get("citacao_abnt") or "").strip())
print("Ainda sem citacao: " + str(still), flush=True)