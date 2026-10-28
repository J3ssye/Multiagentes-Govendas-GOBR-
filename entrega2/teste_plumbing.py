# -*- coding: utf-8 -*-
"""Teste do encanamento da Entrega 2, SEM o bge-m3.

Usa um embedding de teste (hash de palavras) que não entende significado: serve
só para provar que o código monta os textos, divide regras grandes sem perder
segmento, grava/recarrega o índice e agrupa partes por regra. Os números que ele
produz NÃO medem a qualidade da busca — isso é o avaliar.py com o bge-m3.

Precisa apenas de: pip install llama-index-core
Uso: python teste_plumbing.py
"""
from __future__ import annotations

import hashlib
import math
import re
import shutil
import tempfile
from pathlib import Path

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.schema import MetadataMode

import avaliar
from comum import (
    MARCA_PONTOS,
    BM25,
    Reranker,
    agrupar_por_regra,
    buscar_regras,
    carregar_regras,
    construir_nodes,
    dividir_texto,
    fundir_rrf,
    texto_para_embedding,
)

DIM = 512


class EmbeddingDeTeste(BaseEmbedding):
    """Saco de palavras com hash (determinístico). Sem semântica nenhuma."""

    def _vec(self, texto: str) -> list[float]:
        v = [0.0] * DIM
        for w in re.findall(r"\w+", texto.lower()):
            h = int(hashlib.md5(w.encode()).hexdigest(), 16)
            v[h % DIM] += 1.0
        norma = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norma for x in v]

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._vec(query)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._vec(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._vec(text)


def contar_palavras(texto: str) -> int:
    return len(texto.split())


def ok(msg: str):
    print(f"  ok  {msg}")


def main():
    print("1) consolidação das regras")
    regras = carregar_regras()
    assert len(regras) == 199 and len({r["id"] for r in regras}) == 199
    ok(f"{len(regras)} regras únicas; origem: { {r['origem'] for r in regras} }")

    print("2) texto que vira vetor")
    com = [r for r in regras if MARCA_PONTOS in r["texto_indexavel"]]
    for r in regras:
        assert MARCA_PONTOS not in texto_para_embedding(r, "sem_pontos")
        assert texto_para_embedding(r, "com_pontos") == r["texto_indexavel"]
    assert all(texto_para_embedding(r, "sem_pontos") in r["texto_indexavel"] for r in com)
    ok(f"sem_pontos remove a linha final de {len(com)} regras; as outras {199 - len(com)} ficam iguais")

    print("3) divisão de regra grande (limite artificial de 800 palavras)")
    r032 = next(r for r in regras if r["id"].endswith("regra_032.gobr"))
    texto = texto_para_embedding(r032, "sem_pontos")
    partes = dividir_texto(texto, 800, contar_palavras)
    assert len(partes) > 1
    cab = "\n".join(texto.split("\n")[:2])
    segs_orig = texto.split("\n")[2:]
    segs_partes = []
    for p in partes:
        assert p.startswith(cab), "toda parte deve repetir título + resumo"
        assert contar_palavras(p) <= 800
        segs_partes += p.split("\n")[2:]
    assert segs_partes == segs_orig, "nenhum segmento pode sumir, repetir ou mudar de ordem"
    assert dividir_texto("a\nb\n- c", 800, contar_palavras) == ["a\nb\n- c"]
    ok(f"regra_032 ({len(segs_orig)} segmentos) -> {len(partes)} partes; segmentos idênticos e na ordem")

    print("4) metadado fora do embedding")
    nodes, rel = construir_nodes(regras, "sem_pontos", contar_palavras, 800)
    assert rel["regras"] == 199 and rel["nodes"] > 199 and rel["nodes_acima_do_limite"] == 0
    for n in nodes:
        assert n.get_content(metadata_mode=MetadataMode.EMBED) == n.text
        assert "gobr" in n.metadata and n.metadata["gobr"]
    ok(f"{rel['nodes']} nós; texto embedado == texto puro (gobr e demais metadados ficam de fora)")

    print("5) índice: gravar, recarregar, buscar")
    emb = EmbeddingDeTeste()
    index = VectorStoreIndex(nodes, embed_model=emb)
    tmp = Path(tempfile.mkdtemp())
    try:
        index.storage_context.persist(persist_dir=str(tmp / "ix"))
        recarregado = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=str(tmp / "ix")), embed_model=emb
        )
    finally:
        pass
    consulta = "clientes ativos 14 dias risco de inatividade 7 dias inativos prospects"
    a = buscar_regras(index, consulta, k=5)
    b = buscar_regras(recarregado, consulta, k=5)
    assert [x.node.node_id for x in a] == [x.node.node_id for x in b]
    ok("ranking idêntico antes e depois de gravar/recarregar")

    todos = buscar_regras(recarregado, consulta, k=None)
    ids = [x.node.metadata["regra_id"] for x in todos]
    assert len(ids) == len(set(ids)) == 199, "partes da mesma regra devem virar UMA entrada"
    por_id = {r["id"]: r for r in regras}
    assert all(x.node.metadata["gobr"] == por_id[x.node.metadata["regra_id"]]["gobr"] for x in todos)
    ok("199 regras sem repetição (partes agrupadas) e o gobr volta inteiro como metadado")
    shutil.rmtree(tmp, ignore_errors=True)

    # a parte que casa com a consulta decide a posição da regra dividida
    n032 = [n for n in nodes if n.metadata["regra_id"] == r032["id"]]
    assert len(n032) == len(partes)

    print("6) métricas")
    assert avaliar.posicao_da_primeira_relevante(["a", "b", "c"], ["c", "z"]) == 3
    assert avaliar.posicao_da_primeira_relevante(["a"], ["z"]) is None
    m = avaliar.metricas([1, 3, None, 12])
    assert m["hit@1"] == 0.25 and m["hit@3"] == 0.5 and m["hit@10"] == 0.5
    assert abs(m["MRR"] - (1 + 1 / 3 + 0 + 1 / 12) / 4) < 1e-9
    ok("hit@k e MRR conferem com o cálculo à mão")

    print("7) re-ranking (reranker de teste: nota = -tamanho do texto; NÃO mede relevância)")
    vistos = []

    def prever_teste(pares):
        vistos.extend(pares)
        return [-len(texto) for _, texto in pares]

    rr = Reranker(prever_teste)
    base = buscar_regras(recarregado, consulta, k=None)                       # só vetor
    com_rr = buscar_regras(recarregado, consulta, k=None, reranker=rr, n_candidatos=10)
    ids_base = [x.node.metadata["regra_id"] for x in base]
    ids_rr = [x.node.metadata["regra_id"] for x in com_rr]
    assert len(ids_rr) == len(set(ids_rr)) == 199, "re-ranking não pode perder nem duplicar regra"
    assert set(ids_rr[:10]) == set(ids_base[:10]), "só os 10 candidatos são reordenados entre si"
    assert ids_rr[10:] == ids_base[10:], "o resto mantém a ordem vetorial"
    tam = {x.node.metadata["regra_id"]: len(x.node.text) for x in base}
    assert [tam[i] for i in ids_rr[:10]] == sorted(tam[i] for i in ids_rr[:10]), "candidatos ordenados pela nota do reranker"
    assert len(vistos) == 10 and all(q == consulta for q, _ in vistos)
    textos_node = {x.node.text for x in base}
    assert all(t in textos_node for _, t in vistos), "o reranker recebe o texto do nó, sem metadado"
    assert not any("parametros" in t.lower() and "gobr" in t.lower() for _, t in vistos)
    assert buscar_regras(recarregado, consulta, k=3, reranker=rr, n_candidatos=500)[0].node.metadata["regra_id"] in ids_base
    ok("10 candidatos reordenados, resto intacto, 199 regras sem repetição, texto sem metadado")

    print("7b) busca híbrida (BM25 + RRF)")
    bm = BM25(["ativos a cada 14 dias", "inativos a cada 28 dias", "prospects 7 dias"])
    nt = bm.notas("28 dias")
    assert nt[1] > nt[0] and nt[1] > nt[2], "o número exato 28 deve favorecer o 2º documento"
    assert BM25(["Inativos"]).notas("inatívos")[0] > 0, "acento e maiúscula não podem atrapalhar"
    hib = buscar_regras(recarregado, consulta, k=None, hibrido=True)
    ids_h = [x.node.metadata["regra_id"] for x in hib]
    assert len(ids_h) == len(set(ids_h)) == 199, "híbrido não pode perder nem duplicar regra"
    assert all(x.node.metadata["gobr"] for x in hib)
    # RRF à mão: A é 1º nos dois; B 2º/3º; C 3º/2º
    from llama_index.core.schema import NodeWithScore, TextNode

    def _N(rid):
        return NodeWithScore(node=TextNode(text=rid, metadata={"regra_id": rid}), score=0.0)
    r1 = [_N("A"), _N("B"), _N("C")]
    r2 = [_N("A"), _N("C"), _N("B")]
    f = fundir_rrf([r1, r2])
    assert [x.node.metadata["regra_id"] for x in f][0] == "A"
    assert abs(f[0].score - 2 / 61) < 1e-12
    com_h_rr = buscar_regras(recarregado, consulta, k=None, reranker=rr, n_candidatos=10, hibrido=True)
    assert len({x.node.metadata["regra_id"] for x in com_h_rr}) == 199
    ok("BM25 casa número e ignora acento; RRF confere à mão; híbrido (com e sem rerank) mantém 199 regras")

    print("8) fluxo de avaliação ponta a ponta (embedding de teste, NÃO é resultado real)")
    ids_corpus = set(por_id)
    dev = avaliar.carregar_consultas(avaliar.AQUI / avaliar.CONJUNTOS["dev"])
    teste = avaliar.carregar_consultas(avaliar.AQUI / avaliar.CONJUNTOS["teste"])
    for c in dev + teste:
        assert set(c["relevantes"]) <= ids_corpus, f"gabarito inexistente em {c['id']}"
    gold_dev = {r for c in dev for r in c["relevantes"]}
    gold_teste = {r for c in teste for r in c["relevantes"]}
    assert not gold_dev & gold_teste, "teste e desenvolvimento não podem compartilhar regra"
    assert len(teste) == 20 and len(gold_teste) == 20
    consultas = dev
    linhas = avaliar.avaliar_indice(recarregado, consultas)
    linhas_rr = avaliar.avaliar_indice(recarregado, consultas, reranker=rr, n_candidatos=50)
    assert len(linhas) == len(linhas_rr) == len(consultas)
    assert len(avaliar.avaliar_indice(recarregado, teste, hibrido=True)) == 20
    assert "híbrido" in avaliar.resumo_configs([("híbrido", linhas)])
    assert "Teto do re-ranking" in avaliar.comparar(linhas, linhas_rr, 50)
    print(avaliar.formatar("TESTE-hash-de-palavras", linhas))
    print("TUDO OK")


if __name__ == "__main__":
    main()
