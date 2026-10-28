# -*- coding: utf-8 -*-
"""Busca nas explicações indexadas: devolve as regras mais parecidas com um pedido.

Uso:
    python buscar.py "ativos 14 dias, risco de inatividade 7 dias, não agendar inadimplentes"
    python buscar.py "..." --variante com_pontos -k 3 --mostrar-gobr
"""
from __future__ import annotations

import argparse

from comum import VARIANTES, buscar_regras, carregar_indice, criar_embedding, criar_reranker


def imprimir(resultados, mostrar_gobr: bool):
    for pos, n in enumerate(resultados, 1):
        m = n.node.metadata
        resumo = n.node.text.split("\n")[1] if "\n" in n.node.text else ""
        print(f"\n#{pos}  score={n.score:.4f}  {m['titulo']}  [{m['regra_id']}]")
        print(f"    {m['n_blocos']} blocos | origem: {m['origem']} | duplicatas absorvidas: {len(m['duplicatas'])}")
        print(f"    {resumo[:260]}")
        if mostrar_gobr:
            print("    --- GOBR ---")
            print("    " + m["gobr"].replace("\n", "\n    "))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("consulta")
    ap.add_argument("--variante", choices=VARIANTES, default="sem_pontos")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--mostrar-gobr", action="store_true")
    ap.add_argument("--rerank", action="store_true", help="re-ranking com cross-encoder após a busca vetorial")
    ap.add_argument("--candidatos", type=int, default=50)
    ap.add_argument("--hibrido", action="store_true", help="funde a busca vetorial com BM25 (RRF)")
    args = ap.parse_args()

    emb, _ = criar_embedding()
    index = carregar_indice(args.variante, emb)
    reranker = criar_reranker()[0] if args.rerank else None
    imprimir(buscar_regras(index, args.consulta, args.k, reranker, args.candidatos, args.hibrido), args.mostrar_gobr)


if __name__ == "__main__":
    main()
