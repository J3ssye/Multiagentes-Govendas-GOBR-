# -*- coding: utf-8 -*-
"""Funções compartilhadas da Entrega 2 (indexação das explicações).

Nada aqui baixa modelo: os imports pesados (torch, transformers, HuggingFace)
ficam dentro das funções criar_*, para o teste de encanamento rodar sem eles.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SAIDA_ENTREGA1 = AQUI.parent / "entrega1" / "saida"
DIR_INDICES = AQUI / "indices"

MODELO_EMBEDDING = "BAAI/bge-m3"
MODELO_RERANKER = "BAAI/bge-reranker-v2-m3"  # o mesmo da atividade de RAG
# O SentenceTransformerRerank do LlamaIndex fixa 512 tokens; regras maiores seriam
# cortadas. Usamos o CrossEncoder direto, com limite maior (maior regra: ~3.900 tokens).
RERANKER_MAX_LENGTH = 2048
VARIANTES = ("sem_pontos", "com_pontos")
MARCA_PONTOS = "Pontos de atenção:"


# ---------------------------------------------------------------- dados ----
def _ler_jsonl(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def carregar_regras(saida: Path = SAIDA_ENTREGA1) -> list[dict]:
    """Uma regra por id, na ordem do arquivo determinístico (as 199 únicas).

    Usa o registro do LLM quando existe E passou na verificação da Entrega 1;
    senão, cai no determinístico. (No estado final da Entrega 1 são 199/199 LLM,
    mas o código não assume isso.)
    """
    det = {r["id"]: r for r in _ler_jsonl(saida / "explicacoes_deterministicas.jsonl")}
    llm = {r["id"]: r for r in _ler_jsonl(saida / "explicacoes.jsonl")}

    estranhos = set(llm) - set(det)
    if estranhos:
        raise ValueError(f"ids em explicacoes.jsonl que não existem no determinístico: {sorted(estranhos)[:5]}")

    regras = []
    for id_, base in det.items():
        r = llm.get(id_)
        regras.append(r if (r is not None and r["verificacao"]["ok"]) else base)
    return regras


def texto_para_embedding(regra: dict, variante: str) -> str:
    """Texto que vira vetor.

    sem_pontos: tira a linha final 'Pontos de atenção: ...' (ela descreve defeitos
                da regra, e o pedido do usuário descreve a regra de negócio).
    com_pontos: usa o texto_indexavel inteiro, como saiu da Entrega 1.
    """
    if variante not in VARIANTES:
        raise ValueError(f"variante inválida: {variante}")
    texto = regra["texto_indexavel"]
    if variante == "com_pontos":
        return texto
    return "\n".join(l for l in texto.split("\n") if not l.startswith(MARCA_PONTOS))


# --------------------------------------------------------------- chunks ----
def dividir_texto(texto: str, limite_tokens: int, contar) -> list[str]:
    """Devolve [texto] se couber no limite; senão divide POR SEGMENTO.

    Cada parte repete as duas primeiras linhas (título + resumo), para que
    qualquer parte sozinha ainda diga de que regra se trata. Nunca corta no
    meio de um segmento (uma linha '- nome: critério -> ação').
    """
    if contar(texto) <= limite_tokens:
        return [texto]

    linhas = texto.split("\n")
    cabecalho = "\n".join(linhas[:2])
    partes: list[str] = []
    atual: list[str] = []
    for seg in linhas[2:]:
        candidato = "\n".join([cabecalho, *atual, seg])
        if atual and contar(candidato) > limite_tokens:
            partes.append("\n".join([cabecalho, *atual]))
            atual = [seg]
        else:
            atual.append(seg)
    if atual:
        partes.append("\n".join([cabecalho, *atual]))
    return partes


def construir_nodes(regras: list[dict], variante: str, contar, limite_tokens: int):
    """Um TextNode por regra (ou por parte, se a regra estourar o limite).

    Só o TEXTO entra no embedding: todas as chaves de metadado são marcadas em
    excluded_embed_metadata_keys. O LlamaIndex, por padrão, concatena o metadado
    ao texto antes de embedar — sem isso o código GOBR inteiro viraria vetor.
    """
    from llama_index.core.schema import TextNode

    nodes = []
    tokens_por_no = []
    divididas = []
    for r in regras:
        partes = dividir_texto(texto_para_embedding(r, variante), limite_tokens, contar)
        if len(partes) > 1:
            divididas.append({"id": r["id"], "partes": len(partes)})
        for k, parte in enumerate(partes, 1):
            n_tok = contar(parte)
            tokens_por_no.append(n_tok)
            meta = {
                "regra_id": r["id"],
                "arquivo": r["arquivo"],
                "titulo": r["explicacao"]["titulo"],
                "parte": k,
                "n_partes": len(partes),
                "tokens": n_tok,
                "n_blocos": r["n_blocos"],
                "origem": r["origem"],
                "modelo": r["modelo"],
                "duplicatas": r["duplicatas"],
                "pontos_de_atencao": r["explicacao"]["pontos_de_atencao"],
                "achados_automaticos": r["achados_automaticos"],
                "gobr": r["gobr"],
            }
            nodes.append(
                TextNode(
                    id_=f"{r['id']}#{k}",
                    text=parte,
                    metadata=meta,
                    excluded_embed_metadata_keys=list(meta),
                )
            )

    relatorio = {
        "variante": variante,
        "limite_tokens": limite_tokens,
        "regras": len(regras),
        "nodes": len(nodes),
        "tokens_mediana": statistics.median(tokens_por_no),
        "tokens_max": max(tokens_por_no),
        "regras_divididas": divididas,
        "nodes_acima_do_limite": sum(1 for t in tokens_por_no if t > limite_tokens),
    }
    return nodes, relatorio


# ---------------------------------------------------------------- busca ----
def agrupar_por_regra(nos_com_score, k: int | None = None):
    """Várias partes da mesma regra viram UMA entrada (a de maior score).

    O agente recebe sempre a regra inteira (o gobr completo está no metadado),
    então a divisão em partes é só um detalhe do índice.
    """
    melhor: dict[str, object] = {}
    for n in nos_com_score:
        rid = n.node.metadata["regra_id"]
        if rid not in melhor or n.score > melhor[rid].score:
            melhor[rid] = n
    ordenados = sorted(melhor.values(), key=lambda n: -n.score)
    return ordenados[:k] if k else ordenados


class Reranker:
    """Cross-encoder: lê a consulta e a regra JUNTAS e devolve uma nota de relevância.

    Recebe qualquer função `prever(pares) -> notas` (pares = lista de
    (consulta, texto)). Em produção é o CrossEncoder do bge-reranker; nos testes,
    uma função falsa. As notas só servem para ordenar.
    """

    def __init__(self, prever, nome: str = MODELO_RERANKER):
        self.prever = prever
        self.nome = nome

    def pontuar(self, consulta: str, textos: list[str]) -> list[float]:
        return [float(s) for s in self.prever([(consulta, t) for t in textos])]


def reordenar_com_reranker(ranking_vetorial, consulta: str, reranker: Reranker, n_candidatos: int = 50):
    """Segunda fase da busca em duas fases (Atividade de RAG, Células 8 e 10).

    Fase 1 (já feita): o ranking vetorial. Fase 2: os `n_candidatos` primeiros
    são relidos pelo cross-encoder e reordenados pela nota dele. O restante vem
    depois, na ordem vetorial original (o reranker não consegue trazer para cima
    quem ficou fora dos candidatos).

    Atenção: na lista devolvida, o score dos `n_candidatos` primeiros é a nota
    do reranker; o do restante continua sendo a similaridade vetorial.
    """
    from llama_index.core.schema import NodeWithScore

    candidatos = ranking_vetorial[:n_candidatos]
    resto = ranking_vetorial[n_candidatos:]
    if not candidatos:
        return list(ranking_vetorial)
    notas = reranker.pontuar(consulta, [n.node.text for n in candidatos])
    novos = [NodeWithScore(node=n.node, score=s) for n, s in zip(candidatos, notas)]
    novos.sort(key=lambda n: -n.score)
    return novos + list(resto)


# ------------------------------------------------- busca híbrida (opcional) ----
def _tokens(texto: str) -> list[str]:
    """Minúsculas, sem acento; números ficam como tokens ('14', '60')."""
    import re
    import unicodedata

    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    return re.findall(r"\w+", sem_acento)


class BM25:
    """BM25 clássico (k1=1.5, b=0.75: valores usuais da literatura; NÃO estão no material da disciplina).

    Casa palavras e números exatos: complementa o embedding, que tende a dar pouco peso
    a '14 dias' x '28 dias'.
    """

    def __init__(self, documentos: list[str], k1: float = 1.5, b: float = 0.75):
        import math
        from collections import Counter

        self.k1, self.b = k1, b
        self.tf = [Counter(_tokens(d)) for d in documentos]
        self.tam = [sum(t.values()) for t in self.tf]
        self.media = (sum(self.tam) / len(self.tam)) if self.tam else 0.0
        df = Counter(w for t in self.tf for w in t)
        n = len(documentos)
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}

    def notas(self, consulta: str) -> list[float]:
        q = _tokens(consulta)
        saida = []
        for tf, tam in zip(self.tf, self.tam):
            nota = 0.0
            for w in q:
                f = tf.get(w, 0)
                if f:
                    nota += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * tam / (self.media or 1.0)))
            saida.append(nota)
        return saida


_CACHE_BM25: dict[int, tuple] = {}


def _bm25_do_indice(index):
    chave = id(index)
    if chave not in _CACHE_BM25:
        nos = list(index.docstore.docs.values())
        _CACHE_BM25[chave] = (BM25([n.text for n in nos]), nos)
    return _CACHE_BM25[chave]


def fundir_rrf(rankings: list[list], k_rrf: int = 60):
    """Reciprocal Rank Fusion: nota = soma de 1/(k_rrf + posição) em cada ranking.

    Usa só posições (não precisa comparar notas de escalas diferentes). k_rrf=60 é o valor
    da literatura; NÃO está no material da disciplina. Cada ranking é uma lista de
    NodeWithScore já sem regra repetida.
    """
    from llama_index.core.schema import NodeWithScore

    nota: dict[str, float] = {}
    no: dict[str, object] = {}
    for ranking in rankings:
        for pos, n in enumerate(ranking, 1):
            rid = n.node.metadata["regra_id"]
            nota[rid] = nota.get(rid, 0.0) + 1.0 / (k_rrf + pos)
            no.setdefault(rid, n.node)
    return [NodeWithScore(node=no[r], score=s) for r, s in sorted(nota.items(), key=lambda x: -x[1])]


def ranking_bm25(index, consulta: str):
    from llama_index.core.schema import NodeWithScore

    bm25, nos = _bm25_do_indice(index)
    notas = bm25.notas(consulta)
    return agrupar_por_regra([NodeWithScore(node=n, score=s) for n, s in zip(nos, notas)])


def buscar_regras(index, consulta: str, k: int | None = 5, reranker: Reranker | None = None,
                  n_candidatos: int = 50, hibrido: bool = False):
    """Ranking de regras (sem repetição) para uma consulta em linguagem natural.

    Sem `reranker`: só a busca vetorial. Com `reranker`: busca vetorial e depois
    re-ranking dos `n_candidatos` primeiros. Com `hibrido`, a 1ª fase funde o ranking
    vetorial com o BM25 (RRF) antes do re-ranking.
    """
    n_nos = len(index.docstore.docs)
    retriever = index.as_retriever(similarity_top_k=n_nos)
    ranking = agrupar_por_regra(retriever.retrieve(consulta))
    if hibrido:
        ranking = fundir_rrf([ranking, ranking_bm25(index, consulta)])
    if reranker is not None:
        ranking = reordenar_com_reranker(ranking, consulta, reranker, n_candidatos)
    return ranking[:k] if k else ranking


def caminho_indice(variante: str) -> Path:
    return DIR_INDICES / f"indice_{variante}"


def carregar_indice(variante: str, embed_model):
    from llama_index.core import StorageContext, load_index_from_storage

    ctx = StorageContext.from_defaults(persist_dir=str(caminho_indice(variante)))
    return load_index_from_storage(ctx, embed_model=embed_model)


# ------------------------------------------- modelo (só no notebook) -------
def criar_embedding():
    """bge-m3 local, o mesmo da atividade de RAG da disciplina."""
    import torch
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    emb = HuggingFaceEmbedding(
        model_name=MODELO_EMBEDDING,
        device=dispositivo,
        embed_batch_size=4,  # documentos longos: lote pequeno poupa memória
    )
    return emb, dispositivo


def criar_reranker():
    """bge-reranker-v2-m3 local (cross-encoder), lido com max_length maior que o padrão."""
    import torch
    from sentence_transformers import CrossEncoder

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    modelo = CrossEncoder(MODELO_RERANKER, max_length=RERANKER_MAX_LENGTH, device=dispositivo)
    return Reranker(lambda pares: modelo.predict(pares, batch_size=4, show_progress_bar=False)), dispositivo


def criar_contador_tokens():
    """Conta tokens com o tokenizer do próprio bge-m3 (inclui tokens especiais)."""
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODELO_EMBEDDING)
    return lambda texto: len(tok.encode(texto, add_special_tokens=True))
