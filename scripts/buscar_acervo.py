#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para SUGERIR entradas ao acervo (dados/acervo.json) do Observatório NEAB/UEL.
NÃO publica automaticamente: gera um arquivo de rascunho para revisão humana.

Requisitos: pip install requests
Uso: python buscar_acervo.py
Saída: scripts/acervo_candidatos.json
"""
import json
import time
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Instale as dependências: pip install requests")

# Consultas sugeridas (pode ampliar conforme necessidade)
QUERIES = [
    '"população negra" Paraná',
    '"estudos afro-brasileiros" Paraná',
    '"temática negra" Paraná NEAB',
    '"relações étnico-raciais" Paraná',
    '"quilombos" Paraná',
    '"discriminação racial" Paraná',
    '"racismo" Paraná educação',
]

OUTPUT = Path(__file__).parent / "acervo_candidatos.json"


def buscar_openalex(query, per_page=8):
    """Busca na API OpenAlex (https://docs.openalex.org)."""
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": per_page,
        "sort": "publication_year:desc",
    }
    headers = {
        "User-Agent": "ObservatorioNEAB-UEL/1.0 (acervo-helper; mailto:neab_repositorio@uel.br)",
    }
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])


def normalizar_autores(authorships):
    nomes = []
    for a in authorships or []:
        author = a.get("author") or {}
        nome = author.get("display_name")
        if nome:
            nomes.append(nome)
    return "; ".join(nomes) if nomes else ""


def mapear_tipo(tipo_openalex):
    t = (tipo_openalex or "").lower()
    if "thesis" in t or "dissertation" in t:
        return "dissertacao"
    if "article" in t:
        return "artigo"
    if "book-chapter" in t or "book" in t:
        return "outro"
    return "outro"


def main():
    vistos = set()
    candidatos = []
    for q in QUERIES:
        print(f"Buscando: {q}")
        try:
            works = buscar_openalex(q, per_page=6)
        except Exception as e:
            print(f"  Erro: {e}")
            continue
        for w in works:
            wid = w.get("id") or w.get("doi") or w.get("title")
            if not wid or wid in vistos:
                continue
            vistos.add(wid)
            titulo = w.get("display_name") or w.get("title") or ""
            ano = w.get("publication_year")
            doi = w.get("doi") or ""
            link = doi or w.get("id") or ""
            oa = w.get("open_access") or {}
            pdf = oa.get("oa_url") or ""
            instituicao = ""
            for a in w.get("authorships") or []:
                insts = a.get("institutions") or []
                if insts:
                    instituicao = insts[0].get("display_name") or ""
                    break
            candidato = {
                "id": f"auto-{len(candidatos)+1:04d}",
                "titulo": titulo,
                "autor": normalizar_autores(w.get("authorships")),
                "ano": ano,
                "tipo": mapear_tipo(w.get("type")),
                "instituicao": instituicao,
                "nucleo": "",
                "regiao": "Paraná (verificar)",
                "tema": q,
                "resumo": "",
                "link": link,
                "pdf": pdf,
                "citacao_abnt": "",
                "destaque": False,
                "_observacao": "GERADO AUTOMATICAMENTE: revisar dados, confirmar vínculo com Paraná/NEAB, definir tipo correto, preencher citacao_abnt e links/PDF."
            }
            candidatos.append(candidato)
        time.sleep(1)

    OUTPUT.write_text(json.dumps(candidatos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRascunho salvo em: {OUTPUT}")
    print("Revise e copie entradas válidas para observatorio-neab-uel/dados/acervo.json.")


if __name__ == "__main__":
    main()
