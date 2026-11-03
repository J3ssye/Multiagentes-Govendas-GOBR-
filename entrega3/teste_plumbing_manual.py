# -*- coding: utf-8 -*-
"""Entrega 3, passo 5.5 - testes de encanamento, SEM modelo: tokenizer falso (uma palavra = um token)
e embedding falso (hash de palavras; não mede qualidade). Rodam sobre os blocos reais do manual
(saída do passo 5.1) e sobre os dois conjuntos de consultas.

    python teste_plumbing_manual.py
"""
from __future__ import annotations

import re
import sys
import traceback
import zlib

from llama_index.core.embeddings import BaseEmbedding

from comum_manual import (CHUNK_B, OVERLAP_B, Reranker, RerankerComCache, acerta, buscar, carregar_blocos,
                          carregar_consultas, consultas_inalcancaveis, dividir_folha, folha_principal,
                          fundir_rrf_nos, localizar, montar_folhas, nos_B, nos_C, texto_plano)
from avaliar import metricas  # Entrega 2

BLOCOS = carregar_blocos()
FOLHAS = montar_folhas(BLOCOS)
INFINITO = 10 ** 9
TESTES = []


def contar(texto: str) -> int:        # "token" falso: palavra
    return len(texto.split())


def tokenizar(texto: str) -> list[str]:
    return texto.split()


def teste(f):
    TESTES.append(f)
    return f


class EmbeddingHash(BaseEmbedding):
    """Contagem de palavras em dim posições (crc32), normalizada. Só para o encanamento."""
    dim: int = 256

    def _vetor(self, texto: str) -> list[float]:
        v = [0.0] * self.dim
        for w in re.findall(r"\w+", texto.lower()):
            v[zlib.crc32(w.encode("utf-8")) % self.dim] += 1.0
        n = sum(x * x for x in v) ** 0.5 or 1.0
        return [x / n for x in v]

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._vetor(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._vetor(text)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._vetor(query)


@teste
def uma_folha_um_no_quando_cabe():
    nos, rel = nos_C(BLOCOS, contar, INFINITO)
    assert len(nos) == len(FOLHAS) == rel["folhas"] and not rel["folhas_divididas"]
    assert len({n.node_id for n in nos}) == len(nos)
    for n, f in zip(nos, FOLHAS):
        assert n.metadata["folha"] == f["folha"] and n.text.startswith(f["caminho"] + "\n\n")
        assert n.metadata["cobertura"] == {f["folha"]: 1.0}
        assert set(n.excluded_embed_metadata_keys) == set(n.metadata)  # nenhum metadado entra no vetor


@teste
def folha_so_com_titulo_nao_vira_no():
    vazias = {b["folha"] for b in BLOCOS if b["tipo"] == "titulo"} - {f["folha"] for f in FOLHAS}
    assert vazias, "esperava folhas só com título (ex.: 4.3, 7.3)"
    nos, _ = nos_C(BLOCOS, contar, INFINITO)
    assert not vazias & {n.metadata["folha"] for n in nos}


@teste
def teto_respeitado_sem_perder_texto():
    teto = 60
    for f in FOLHAS:
        partes = dividir_folha(f, teto, contar)
        textos = [t for t, _ in partes]
        for t, bs in partes:
            assert t.startswith(f["caminho"] + "\n\n")
            if contar(t) > teto:  # só estoura uma peça indivisível: bloco de código, frase ou linha de tabela
                corpo = t[len(f["caminho"]) + 2:]
                assert any(corpo == b["texto"] for b in bs if b["tipo"] == "codigo") or "\n\n" not in corpo, \
                    (f["folha"], contar(t))
        for b in f["blocos"]:
            if b["tipo"] == "codigo":
                assert any(b["texto"] in t for t in textos), (f["folha"], "código cortado")
            elif b["tipo"] == "tabela":
                cab = " | ".join(b["cabecalho"])
                for linha in (" | ".join(l) for l in b["linhas"]):
                    donos = [t for t in textos if linha in t]
                    assert donos and all(cab in t for t in donos), (f["folha"], linha[:40])
            else:
                for frase in re.split(r"(?<=[.!?;:])\s+", b["texto"]):
                    assert any(frase.strip() in t for t in textos), (f["folha"], frase[:40])


@teste
def b_cobre_o_texto_em_ordem_com_sobreposicao():
    nos, rel = nos_B(BLOCOS, tokenizar, CHUNK_B, OVERLAP_B)
    texto, _ = texto_plano(BLOCOS)
    inicios = [n.metadata["inicio"] for n in nos]
    assert inicios == sorted(inicios) and len(set(inicios)) == len(inicios)
    assert rel["caracteres_fora_de_qualquer_chunk"] == 0
    assert any(b.metadata["inicio"] < a.metadata["fim"] for a, b in zip(nos, nos[1:])), "sem sobreposição"
    for n in nos:
        assert texto[n.metadata["inicio"]:n.metadata["fim"]].split() == n.text.split()
        assert all(0 < v <= 1 for v in n.metadata["cobertura"].values())


@teste
def folha_principal_por_caracteres():
    b = lambda f, tipo="paragrafo": {"folha": f, "tipo": tipo}
    trechos = [(0, 10, b("1.1", "titulo")), (12, 112, b("1.1")), (114, 144, b("1.2"))]
    assert folha_principal(0, 144, trechos) == ("1.1", {"1.1": 100, "1.2": 30})
    assert folha_principal(100, 144, trechos) == ("1.2", {"1.1": 12, "1.2": 30})
    assert folha_principal(0, 10, trechos) == ("1.1", {})                                # só título
    assert folha_principal(0, 42, [(0, 20, b("2.1")), (22, 42, b("2.2"))])[0] == "2.1"   # empate: a primeira


@teste
def localizar_tolera_espacos_diferentes():
    texto = "Alfa beta.\n\nGama  delta epsilon.\n\nZeta."
    assert localizar(["Alfa beta.", "Gama delta epsilon."], texto) == [(0, 10), (12, 32)]


@teste
def regras_de_acerto():
    meta = {"folha": "6.8", "cobertura": {"6.8": 0.7, "6.9": 1.0, "6.10": 0.2}}
    assert acerta(meta, ["6.8"]) and not acerta(meta, ["6.9"])            # oficial: só a folha principal
    assert acerta(meta, ["6.9"], "cobertura") and not acerta(meta, ["6.10"], "cobertura")


@teste
def gabaritos_existem_e_c_alcanca_todos():
    nos, _ = nos_C(BLOCOS, contar, INFINITO)
    folhas = {n.metadata["folha"] for n in nos}
    for conjunto in ("dev", "teste"):
        for c in carregar_consultas(conjunto):
            assert set(c["gabarito"]) <= folhas, (c["id"], c["gabarito"])
    assert consultas_inalcancaveis(nos) == {"dev": [], "teste": []}


@teste
def busca_vetorial_hibrida_e_rerank_com_cache():
    from llama_index.core import VectorStoreIndex

    nos, _ = nos_C(BLOCOS, contar, INFINITO)
    index = VectorStoreIndex(nos, embed_model=EmbeddingHash())
    q = "clientes inadimplentes com títulos vencidos em aberto"
    for hibrido in (False, True):
        r = buscar(index, q, k=None, hibrido=hibrido)
        assert len(r) == len(nos) == len({n.node.node_id for n in r})
    lotes = []

    def prever(pares):
        lotes.append(len(pares))
        return [len(set(a.lower().split()) & set(t.lower().split())) for a, t in pares]

    rr = RerankerComCache(Reranker(prever, "falso"))
    r1 = buscar(index, q, k=None, reranker=rr, n_candidatos=10)
    notas = [n.score for n in r1[:10]]
    assert notas == sorted(notas, reverse=True)
    buscar(index, q, k=None, reranker=rr, n_candidatos=10, hibrido=True)
    unicos = rr.pares_avaliados
    assert unicos == len(rr.cache) == sum(lotes) <= 20   # cada par (consulta, chunk) lido uma vez só
    buscar(index, q, k=None, reranker=rr, n_candidatos=10)
    assert rr.pares_avaliados == unicos                   # repetir a consulta não chama o modelo de novo


@teste
def rrf_pela_identidade_do_no():
    from llama_index.core.schema import NodeWithScore, TextNode

    a, b, c = (TextNode(id_=x, text=x) for x in "abc")
    r = fundir_rrf_nos([[NodeWithScore(node=a, score=1.0), NodeWithScore(node=b, score=0.5)],
                        [NodeWithScore(node=b, score=9.0), NodeWithScore(node=c, score=1.0)]])
    assert [n.node.node_id for n in r] == ["b", "a", "c"]


@teste
def posicao_do_primeiro_acerto():
    from llama_index.core.schema import NodeWithScore, TextNode

    from avaliar_manual import posicao

    nos = [NodeWithScore(node=TextNode(id_=str(i), text="x", metadata={"folha": f, "cobertura": cob}), score=1.0)
           for i, (f, cob) in enumerate([("6.8", {"6.8": 0.8, "6.9": 1.0}), ("6.9", {"6.9": 1.0})])]
    assert posicao(nos, ["6.9"], "principal") == 2 and posicao(nos, ["6.9"], "cobertura") == 1
    assert posicao(nos, ["7.0"], "principal") is None


@teste
def regra_de_escolha_com_desempates():
    from avaliar_manual import escolher_padrao

    L = lambda ps: [{"posicao": p} for p in ps]
    res = {"C": [("vetor", L([1, 2])), ("híbrido + rerank", L([2, 1]))], "B": [("vetor", L([1, 2]))]}
    assert escolher_padrao(res)[:2] == ("C", "vetor")       # empate em MRR e hit@1: mais simples, depois C
    res["B"].append(("híbrido", L([1, 1])))
    assert escolher_padrao(res)[:2] == ("B", "híbrido")     # maior MRR vence


@teste
def metricas_da_entrega2():
    m = metricas([1, 2, None, 4])
    assert abs(m["MRR"] - (1 + 0.5 + 0.25) / 4) < 1e-9 and m["hit@1"] == 0.25 and m["hit@3"] == 0.5


def main():
    falhas = 0
    for t in TESTES:
        try:
            t()
            print(f"ok    {t.__name__}")
        except Exception:
            falhas += 1
            print(f"FALHOU {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes passaram")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
