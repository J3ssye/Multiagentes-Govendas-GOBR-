# -*- coding: utf-8 -*-
"""Entrega 3, passo 5.3 - indexa o manual com o bge-m3 local, nas estratégias C e/ou B.

Grava em entrega3/indices/indice_manual_<C|B>/ e o relatório em indices/relatorio_manual_<C|B>.json.
Os índices das regras (entrega2/indices) não são tocados.

Uso (PowerShell, na pasta trabalho\\entrega3):
    python indexar_manual.py                    # C e B
    python indexar_manual.py --estrategia C
"""
from __future__ import annotations

import argparse
import json
import shutil
import time

from comum_manual import (CHUNK_B, DIR_INDICES, ESTRATEGIAS, OVERLAP_B, TETO_C, caminho_indice, carregar_blocos,
                          consultas_inalcancaveis, criar_contador_tokens, criar_embedding, criar_tokenizador,
                          montar_folhas, nos_B, nos_C)
from indexar import _com_tentativas  # Entrega 2, sem alteração: repete operações de pasta presas pelo OneDrive


def gravar(estrategia: str, nos, rel: dict, emb) -> None:
    from llama_index.core import VectorStoreIndex

    t0 = time.time()
    index = VectorStoreIndex(nos, embed_model=emb, show_progress=True)  # nós prontos: nenhum splitter automático
    rel["segundos_embedding"] = round(time.time() - t0, 1)
    destino = caminho_indice(estrategia)
    tmp = destino.with_name(destino.name + ".tmp")  # grava ao lado e só então troca: falha no meio não estraga o bom
    _com_tentativas(lambda: shutil.rmtree(tmp) if tmp.exists() else None)
    index.storage_context.persist(persist_dir=str(tmp))
    _com_tentativas(lambda: shutil.rmtree(destino) if destino.exists() else None)
    _com_tentativas(lambda: tmp.rename(destino))
    with open(DIR_INDICES / f"relatorio_manual_{estrategia}.json", "w", encoding="utf-8") as f:
        json.dump(rel, f, ensure_ascii=False, indent=2)
    print(f"[{estrategia}] índice salvo em {destino} ({rel['segundos_embedding']} s de embedding)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estrategia", choices=[*ESTRATEGIAS, "ambas"], default="ambas")
    ap.add_argument("--teto", type=int, default=TETO_C, help="teto de tokens do nó na estratégia C")
    ap.add_argument("--chunk", type=int, default=CHUNK_B, help="chunk_size da estratégia B")
    ap.add_argument("--overlap", type=int, default=OVERLAP_B, help="chunk_overlap da estratégia B")
    args = ap.parse_args()
    estrategias = ESTRATEGIAS if args.estrategia == "ambas" else (args.estrategia,)

    blocos = carregar_blocos()
    print(f"{len(blocos)} blocos do manual | {len(montar_folhas(blocos))} folhas com conteúdo")
    DIR_INDICES.mkdir(exist_ok=True)
    emb, dispositivo = criar_embedding()
    contar = criar_contador_tokens()
    print(f"Embedding: {emb.model_name} em {dispositivo} | max_length = {emb.max_length} tokens")

    for e in estrategias:
        if e == "C":
            nos, rel = nos_C(blocos, contar, args.teto)
            print(f"\n[C] {rel['folhas']} folhas -> {rel['nos']} nós | tokens: mediana {rel['tokens_mediana']:.0f}, "
                  f"máx {rel['tokens_max']} (teto {args.teto}) | folhas divididas: {rel['folhas_divididas'] or 'nenhuma'}")
            if rel["nos_acima_do_teto"]:
                print(f"[C] acima do teto (bloco de código inteiro, que não se corta): {rel['nos_acima_do_teto']}")
        else:
            nos, rel = nos_B(blocos, criar_tokenizador(), args.chunk, args.overlap)
            print(f"\n[B] {rel['nos']} chunks (chunk {args.chunk}, sobreposição {args.overlap} tokens) | tokens: "
                  f"mediana {rel['tokens_mediana']:.0f}, máx {rel['tokens_max']} | caracteres fora de qualquer chunk: "
                  f"{rel['caracteres_fora_de_qualquer_chunk']}")
            print(f"[B] {len(rel['folhas_nunca_principais'])} folhas nunca são a principal de um chunk: "
                  f"{rel['folhas_nunca_principais']}")
        acima_do_modelo = [n.node_id for n in nos if contar(n.text) > emb.max_length]
        if acima_do_modelo:
            print(f"[{e}] ATENÇÃO: nós acima do limite do modelo (o fim seria truncado): {acima_do_modelo}")
        for regra in ("principal", "cobertura"):
            inal = consultas_inalcancaveis(nos, regra)
            rel[f"inalcancaveis_{regra}"] = inal
            print(f"[{e}] consultas que nenhum nó pode acertar (regra {regra}): "
                  f"dev {inal['dev'] or 'nenhuma'} | teste {inal['teste'] or 'nenhuma'}")
        gravar(e, nos, rel, emb)


if __name__ == "__main__":
    main()
