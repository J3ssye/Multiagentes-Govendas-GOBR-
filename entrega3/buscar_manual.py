# -*- coding: utf-8 -*-
"""Entrega 3 - consulta o índice do manual pela linha de comando.

Uso (PowerShell, na pasta trabalho\\entrega3):
    python buscar_manual.py "como tiro da agenda os clientes inativos?" --hibrido --rerank
    python buscar_manual.py "filtro de dias úteis" --estrategia B -k 3 --texto
"""
from __future__ import annotations

import argparse

from comum_manual import (ESTRATEGIA_PADRAO, ESTRATEGIAS, N_CANDIDATOS, buscar, carregar_indice, criar_embedding,
                          criar_reranker)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("consulta")
    ap.add_argument("--estrategia", choices=ESTRATEGIAS, default=ESTRATEGIA_PADRAO)
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--hibrido", action="store_true", help="funde o ranking vetorial com o BM25 (RRF)")
    ap.add_argument("--rerank", action="store_true", help="relê os primeiros candidatos com o cross-encoder")
    ap.add_argument("--candidatos", type=int, default=N_CANDIDATOS)
    ap.add_argument("--texto", action="store_true", help="mostra o texto inteiro de cada chunk")
    a = ap.parse_args()

    emb, _ = criar_embedding()
    index = carregar_indice(a.estrategia, emb)
    reranker = criar_reranker()[0] if a.rerank else None
    ranking = buscar(index, a.consulta, k=a.k, reranker=reranker, n_candidatos=a.candidatos, hibrido=a.hibrido)
    for i, n in enumerate(ranking, 1):
        m = n.node.metadata
        ini, fim = m["pagina_impressa_ini"], m["pagina_impressa_fim"]
        pag = f"{ini}" if ini == fim else f"{ini}-{fim}"
        print(f"\n{i}. [{n.score:.4f}] {n.node.node_id} | folha {m['folha']} | p. {pag} | {m['caminho']}")
        corpo = n.node.text
        print(corpo if a.texto else corpo[:400] + (" ..." if len(corpo) > 400 else ""))


if __name__ == "__main__":
    main()
