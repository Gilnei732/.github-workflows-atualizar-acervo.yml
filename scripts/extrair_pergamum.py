#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai materiais do catálogo Pergamum da UEL (busca "Negro;") e gera
dados/pergamum_extraido.json no formato compatível com o acervo do site.

Uso: python scripts/extrair_pergamum.py
Saída: dados/pergamum_extraido.json
"""
import json
import re
import time
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Instale as dependências: pip install requests")

BASE = "https://uel.pergamum.com.br"
API_SEARCH = BASE + "/api/v2/consulta/pesquisa_geral/eBfiQvE4p"
PER_PAGE = 50
OUT = Path(__file__).parent.parent / "dados" / "pergamum_extraido.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ObservatorioNEAB-UEL/1.0)",
    "Accept": "application/json",
}


def buscar_pagina(page):
    params = {
        "termo_pesquisa": "Negro; ",
        "coluna_um": "LIVRE",
        "page": page,
        "perPage": PER_PAGE,
        "orderBy": "obra",
        "direction": "C",
    }
    r = requests.get(API_SEARCH, params=params, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()


def extrair_handle_url(referencia):
    m = re.search(r"Dispon[íi]vel em:\s*(https?://\S+)", referencia or "")
    if m:
        return m.group(1).rstrip(".")
    return ""


def mapear_tipo(desc_tipo, referencia):
    ref = (referencia or "").lower()
    if "disserta" in ref:
        return "dissertacao"
    if "tese" in ref:
        return "tese"
    if "monografia" in ref:
        return "monografia"
    if "tcc" in ref:
        return "tcc"
    if "artigo" in ref:
        return "artigo"
    dt = (desc_tipo or "").lower()
    if "tese" in dt:
        return "tese"
    return "outro"


def extrair_instituicao(referencia):
    ref = referencia or ""
    for inst in [
        "Universidade Estadual de Londrina",
        "Universidade Federal do Paraná",
        "Universidade Tecnológica Federal do Paraná",
        "Universidade Estadual de Maringá",
        "Universidade Estadual do Oeste do Paraná",
        "Universidade Estadual do Centro-Oeste",
        "Universidade Estadual do Norte do Paraná",
    ]:
        if inst in ref:
            return inst
    return "Biblioteca UEL (acervo)"


def main():
    todos = []
    page = 1
    total = None
    while True:
        print("Buscando pagina " + str(page) + "...", flush=True)
        data = buscar_pagina(page)
        total = data.get("totalRegistros", total)
        registros = data.get("registros", [])
        if not registros:
            break
        for reg in registros:
            ref = reg.get("referencia_sem_tag") or reg.get("referencia") or ""
            handle = extrair_handle_url(ref)
            cod = reg.get("cod_acervo")
            possui_online = (reg.get("possui_doc_online") or "").upper() == "S"
            item = {
                "id": "perg-" + str(cod),
                "titulo": reg.get("obra") or reg.get("descricao") or "",
                "autor": reg.get("autor") or "",
                "ano": int(reg["ano_publicacao"]) if (reg.get("ano_publicacao") or "").isdigit() else None,
                "tipo": mapear_tipo(reg.get("desc_tipo_obra"), ref),
                "instituicao": extrair_instituicao(ref),
                "nucleo": "",
                "regiao": "",
                "tema": "tematica negra (catalogo Pergamum/UEL)",
                "resumo": "",
                "link": handle or ("https://uel.pergamum.com.br/acervo/" + str(cod)),
                "pdf": handle if possui_online else "",
                "citacao_abnt": ref,
                "destaque": False,
                "_cod_acervo": cod,
                "_possui_doc_online": possui_online,
            }
            todos.append(item)
        if page * PER_PAGE >= (total or 0):
            break
        page += 1
        time.sleep(0.3)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Total extraido: " + str(len(todos)) + " (de " + str(total) + ")", flush=True)
    print("Salvo em: " + str(OUT), flush=True)

    from collections import Counter
    c = Counter(i["tipo"] for i in todos)
    print("Por tipo: " + str(dict(c)), flush=True)
    online = sum(1 for i in todos if i["_possui_doc_online"])
    print("Com documento online: " + str(online), flush=True)


if __name__ == "__main__":
    main()
