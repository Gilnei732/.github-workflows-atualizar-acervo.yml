#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrai resultados da busca 'negro' no repositorio digital da UFPR."""
import json
from html import unescape as html_unescape
import re
import sys
import time
from pathlib import Path

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://acervodigital.ufpr.br"
SEARCH = BASE + "/xmlui/discover"
RPP = 100
OUT = Path(__file__).parent.parent / "dados" / "ufpr_extraido.json"
INSTITUICAO = "Universidade Federal do Paran\u00e1"

HEADERS = {"User-Agent": "Mozilla/5.0 (ObservatorioNEAB-UEL/1.0)"}


def fetch_page(page):
    params = {"rpp": RPP, "etal": 0, "query": "negro", "group_by": "none", "page": page}
    r = requests.get(SEARCH, params=params, headers=HEADERS, timeout=60, verify=False)
    r.encoding = "utf-8"
    r.raise_for_status()
    return r.text


def parse_items(html_text):
    items = []
    blocks = re.findall(r'<div class="row ds-artifact-item ">(.*?)</div>\s*</div>\s*</div>', html_text, re.S)
    if not blocks:
        blocks = re.findall(r'<div class="col-sm-9 artifact-description">(.*?)</div>\s*</div>', html_text, re.S)
    for b in blocks:
        m = re.search(r'href="(/xmlui/handle/1884/\d+)"', b)
        handle_rel = m.group(1) if m else ""
        handle = BASE + handle_rel if handle_rel else ""
        tm = re.search(r'<h4>(.*?)</h4>', b, re.S)
        title = ""
        if tm:
            t = re.sub(r'<span class="Z3988".*?</span>', '', tm.group(1), flags=re.S)
            title = re.sub(r'<[^>]+>', '', t).strip()
        am = re.search(r'<span class="author h4"><small>(.*?)</small></span>', b, re.S)
        author = re.sub(r'<[^>]+>', '', am.group(1)).strip() if am else ""
        dm = re.search(r'<span class="date">(.*?)</span>', b, re.S)
        date = re.sub(r'<[^>]+>', '', dm.group(1)).strip() if dm else ""
        abm = re.search(r'<div class="abstract">(.*?)</div>', b, re.S)
        abstract = re.sub(r'<[^>]+>', '', abm.group(1)).strip() if abm else ""
        if title or handle:
            items.append({
                "titulo": html_unescape(title),
                "autor": html_unescape(author),
                "data": date,
                "instituicao": INSTITUICAO,
                "resumo": html_unescape(abstract),
                "link": handle,
                "handle": handle,
            })
    return items


def load_existing():
    if OUT.exists():
        try:
            return json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 999

    existing = load_existing()
    seen = {(it.get("handle") or it.get("titulo")) for it in existing}
    all_items = list(existing)

    page = start
    total = None
    while page <= end:
        print("Buscando pagina " + str(page) + "...", flush=True)
        try:
            html_text = fetch_page(page)
        except Exception as e:
            print("  ERRO pagina " + str(page) + ": " + str(e), flush=True)
            page += 1
            continue
        tm = re.search(r'Itens para a visualiza\u00e7\u00e3o no momento \d+-\d+ of (\d+)', html_text)
        if tm:
            total = int(tm.group(1))
        items = parse_items(html_text)
        print("  itens na pagina: " + str(len(items)), flush=True)
        if not items:
            break
        new_count = 0
        for it in items:
            key = it["handle"] or it["titulo"]
            if key in seen:
                continue
            seen.add(key)
            all_items.append(it)
            new_count += 1
        print("  novos: " + str(new_count) + " (acumulado: " + str(len(all_items)) + ")", flush=True)

        out = []
        for idx, it in enumerate(all_items, 1):
            ano = None
            m = re.search(r'(\d{4})', it.get("data") or "")
            if m:
                ano = int(m.group(1))
            out.append({
                "id": "ufpr-" + str(idx).zfill(5),
                "titulo": it["titulo"],
                "autor": it["autor"],
                "ano": ano,
                "tipo": "outro",
                "instituicao": it["instituicao"],
                "nucleo": "",
                "regiao": "Curitiba/PR",
                "tema": "tematica negra (repositorio UFPR)",
                "resumo": it["resumo"],
                "link": it["link"],
                "pdf": "",
                "citacao_abnt": "",
                "destaque": False,
                "_data_original": it.get("data"),
            })
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

        if total and len(all_items) >= total:
            break
        page += 1
        time.sleep(0.3)

    print("Total acumulado: " + str(len(all_items)) + " (de " + str(total) + ")", flush=True)
    print("Salvo em: " + str(OUT), flush=True)


if __name__ == "__main__":
    main()
