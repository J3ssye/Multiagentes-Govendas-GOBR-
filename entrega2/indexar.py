# -*- coding: utf-8 -*-
"""Entrega 2 — Indexação das explicações.

Lê as explicações geradas na Entrega 1, transforma cada regra em um nó
(texto + metadados), calcula os embeddings com o bge-m3 local e grava o índice
em disco.

Uso (PowerShell, dentro de trabalho/entrega2):
    python indexar.py                         # variante sem_pontos (a recomendada)
    python indexar.py --variante com_pontos   # variante para comparar na avaliação
    python indexar.py --variante ambas
"""
from __future__ import annotations

import argparse
import json
import shutil
import time

from comum import (
    DIR_INDICES,
    VARIANTES,
    caminho_indice,
    carregar_regras,
    construir_nodes,
    criar_contador_tokens,
    criar_embedding,
)


def _com_tentativas(operacao, tentativas: int = 5, espera: float = 2.0):
    """Repete operações de pasta: o OneDrive às vezes segura os arquivos enquanto sincroniza."""
    for i in range(tentativas):
        try:
            return operacao()
        except PermissionError:
            if i == tentativas - 1:
                raise
            time.sleep(espera)


def indexar_variante(regras, variante, emb, contar, limite):
    from llama_index.core import VectorStoreIndex

    nodes, rel = construir_nodes(regras, variante, contar, limite)
    print(f"\n[{variante}] {rel['regras']} regras -> {rel['nodes']} nós | "
          f"tokens: mediana {rel['tokens_mediana']:.0f}, máx {rel['tokens_max']} "
          f"(limite {limite})")
    if rel["regras_divididas"]:
        print(f"[{variante}] regras divididas por segmento: {rel['regras_divididas']}")
    else:
        print(f"[{variante}] nenhuma regra precisou ser dividida.")
    if rel["nodes_acima_do_limite"]:
        print(f"[{variante}] ATENÇÃO: {rel['nodes_acima_do_limite']} nó(s) ainda acima do limite "
              "(o modelo vai truncar o final desse texto).")

    t0 = time.time()
    # Passamos os nós prontos: nenhum splitter automático mexe neles.
    index = VectorStoreIndex(nodes, embed_model=emb, show_progress=True)
    rel["segundos_embedding"] = round(time.time() - t0, 1)

    # Grava numa pasta temporária e só então troca: uma falha no meio não
    # deixa um índice pela metade no lugar do bom.
    destino = caminho_indice(variante)
    tmp = destino.with_name(destino.name + ".tmp")
    _com_tentativas(lambda: shutil.rmtree(tmp) if tmp.exists() else None)
    index.storage_context.persist(persist_dir=str(tmp))
    _com_tentativas(lambda: shutil.rmtree(destino) if destino.exists() else None)
    _com_tentativas(lambda: tmp.rename(destino))

    with open(DIR_INDICES / f"relatorio_{variante}.json", "w", encoding="utf-8") as f:
        json.dump(rel, f, ensure_ascii=False, indent=2)
    print(f"[{variante}] índice salvo em {destino} ({rel['segundos_embedding']} s de embedding)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variante", choices=[*VARIANTES, "ambas"], default="sem_pontos")
    args = ap.parse_args()
    variantes = VARIANTES if args.variante == "ambas" else (args.variante,)

    regras = carregar_regras()
    origens = {}
    for r in regras:
        origens[r["origem"]] = origens.get(r["origem"], 0) + 1
    print(f"{len(regras)} regras únicas carregadas da Entrega 1 | origem: {origens}")

    DIR_INDICES.mkdir(exist_ok=True)
    emb, dispositivo = criar_embedding()
    contar = criar_contador_tokens()
    limite = emb.max_length  # lido do próprio modelo, não fixado no código
    print(f"Embedding: {emb.model_name} em {dispositivo} | max_length = {limite} tokens")

    for v in variantes:
        indexar_variante(regras, v, emb, contar, limite)


if __name__ == "__main__":
    main()
