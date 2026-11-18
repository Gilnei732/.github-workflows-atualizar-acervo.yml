#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza dados/acervo.json com os itens da UFPR que possuem PDF."""
import json, re, time
from html import unescape as html_unescape
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SRC = Path(__file__).parent.parent / "dados" / "ufpr_extraido.json"
ACERVO = Path(__file__).parent.parent / "dados" / "acervo.json"

data = json.loads(SRC.read_text(encoding="utf-8"))
items_with_pdf = [it for it in data if it.get("pdf")]
print("Itens com PDF: " + str(len(items_with_pdf)), flush=True)

def fetch_meta(item):
    url = item["link"]
    try:
        r = requests.get(url, verify=False, timeout=30)
        r.encoding = "utf-8"
        html_text = r.text
    except Exception:
        return item, None
    metas = dict(re.findall(r'<meta name="([^"]+)" content="([^"]*)"', html_text))
    pdf = metas.get("citation_pdf_url") or item.get("pdf") or ""
    dc_type = (metas.get("DC.type") or "").strip().lower()
    degree_desc = ""
    for d in re.findall(r'DC\.description" content="([^"]*)"', html_text):
        if any(k in d.lower() for k in ["disserta", "tese", "monografia", "trabalho de conclus"]):
            degree_desc = html_unescape(d)
            break
    tipo = "outro"
    if "disserta" in dc_type or "disserta" in degree_desc.lower():
        tipo = "dissertacao"
    elif "tese" in dc_type or "tese" in degree_desc.lower():
        tipo = "tese"
    elif "monografia" in degree_desc.lower():
        tipo = "monografia"
    elif "trabalho de conclus" in degree_desc.lower() or "tcc" in degree_desc.lower():
        tipo = "tcc"
    elif "artigo" in dc_type:
        tipo = "artigo"
    author = html_unescape(metas.get("DC.creator", "").strip())
    author = re.sub(r",\s*\d{4}-?\s*$", "", author).strip()
    title = html_unescape(metas.get("DC.title", "").strip())
    year = (metas.get("citation_date") or metas.get("DCTERMS.issued") or "").strip()[:4]
    extent = html_unescape(metas.get("DCTERMS.extent", "").strip())
    resumo = html_unescape(metas.get("DCTERMS.abstract", "").strip())
    resumo = re.sub(r"^Resumo:\s*", "", resumo)
    instituicao = "Universidade Federal do Paran\u00e1"
    for c in re.findall(r'DC\.contributor" content="([^"]*)"', html_text):
        if "Universidade" in c:
            instituicao = html_unescape(c.split(".")[0].strip() if "." in c else c.strip())
            break
    citacao = ""
    if author: citacao += author + ". "
    if title: citacao += title + ". "
    if year: citacao += year + ". "
    if extent: citacao += extent + ". "
    if degree_desc: citacao += degree_desc + "."
    citacao = citacao.strip()
    return item, {
        "author": author, "title": title, "year": year, "tipo": tipo,
        "degree_desc": degree_desc, "extent": extent, "pdf": pdf,
        "citacao": citacao, "resumo": resumo, "instituicao": instituicao,
    }

results = {}
done = 0
with ThreadPoolExecutor(max_workers=20) as ex:
    futures = {ex.submit(fetch_meta, it): it for it in items_with_pdf}
    for fut in as_completed(futures):
        item, meta = fut.result()
        results[item["id"]] = (item, meta)
        done += 1
        if done % 25 == 0:
            print("Processados " + str(done) + "/" + str(len(items_with_pdf)), flush=True)

existing = json.loads(ACERVO.read_text(encoding="utf-8")) if ACERVO.exists() else []
existing_ids = {r.get("id") for r in existing}
novos = []
for item in items_with_pdf:
    _, meta = results[item["id"]]
    if meta is None:
        continue
    rid = item["id"]
    if rid in existing_ids:
        continue
    ano = None
    try:
        ano = int(meta["year"]) if meta["year"].isdigit() else None
    except Exception:
        ano = item.get("ano")
    acervo_item = {
        "id": rid,
        "titulo": meta["title"] or item.get("titulo", ""),
        "autor": meta["author"] or item.get("autor", ""),
        "ano": ano if ano else item.get("ano"),
        "tipo": meta["tipo"],
        "instituicao": meta["instituicao"],
        "nucleo": "",
        "regiao": "Curitiba/PR",
        "tema": "tematica negra (repositorio UFPR)",
        "resumo": meta["resumo"],
        "link": item.get("link", ""),
        "pdf": meta["pdf"],
        "citacao_abnt": meta["citacao"],
        "destaque": False,
        "link_biblioteca": item.get("link", ""),
    }
    novos.append(acervo_item)
    existing_ids.add(rid)

merged = existing + novos
ACERVO.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
print("Novos adicionados: " + str(len(novos)), flush=True)
print("Total no acervo: " + str(len(merged)), flush=True)
from collections import Counter
print("Por tipo: " + str(dict(Counter(i["tipo"] for i in merged))), flush=True)
print("Com PDF: " + str(sum(1 for i in merged if i.get("pdf"))), flush=True)