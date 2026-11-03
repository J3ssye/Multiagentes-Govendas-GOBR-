# -*- coding: utf-8 -*-
"""Entrega 3 - partes compartilhadas da indexação do manual (passos 5.2 a 5.4).

Reaproveita a Entrega 2 SEM alterar nenhum arquivo dela: importa de entrega2/comum.py o BM25, o
Reranker, a busca em duas fases (reordenar_com_reranker) e as funções que carregam os modelos.
Aqui fica só o que depende do corpus: folhas do manual no lugar de regras.

Estratégias de chunking (Passo 3, aprovado em 02/11/2026):
  C (estrutural, principal): um nó por folha da hierarquia (subseção x.y.z, seção x.y ou abertura
    n.0); texto = trilha ("Cap. 6 ... › 6.2 ...") + corpo. Acima de TETO_C tokens divide só em
    fronteira natural: entre blocos; tabela em grupos de linhas com o cabeçalho repetido; parágrafo
    em frases. Código nunca é cortado. Sobreposição 0.
  B (controle): o texto limpo do manual inteiro, em ordem, cortado pelo SentenceSplitter do
    LlamaIndex com CHUNK_B/OVERLAP_B tokens (receita da aula para manuais). A folha principal do
    chunk é a que tem mais caracteres dentro dele (regra fixada no Passo 4, conjuntos_manual.py).

Nenhuma função daqui carrega modelo; os imports pesados ficam dentro das funções.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENTREGA2 = AQUI.parent / "entrega2"
if str(ENTREGA2) not in sys.path:
    # Vai para o FIM do caminho de busca: a pasta da Entrega 3 continua na frente. Como aqui não
    # existe comum.py, "import comum" encontra o da Entrega 2.
    sys.path.append(str(ENTREGA2))

from comum import (  # noqa: E402  (Entrega 2, sem alteração)
    BM25,
    MODELO_EMBEDDING,
    Reranker,
    criar_contador_tokens,
    criar_embedding,
    criar_reranker,
    reordenar_com_reranker,
)

BLOCOS = AQUI / "saida" / "manual_blocos.jsonl"
DIR_INDICES = AQUI / "indices"
CONJUNTOS = {"dev": "consultas_manual_dev.json", "teste": "consultas_manual_teste.json"}
ESTRATEGIAS = ("C", "B")
ESTRATEGIA_PADRAO = "C"   # provisório: o Passo 6 decide pela regra fixada (maior MRR no dev)

# Origem de cada parâmetro (ver README da Entrega 3):
TETO_C = 512       # chunk_size da aula (copy_of_rag_local_llamaindex.py, l. 119-122), usado como TETO: escolha de engenharia
CHUNK_B = 256      # atividade de RAG, Célula 7, l. 165-166: ".docx (manuais): passos curtos -> chunks menores"
OVERLAP_B = 32     # idem
N_CANDIDATOS = 50  # o mesmo da Entrega 2
K_RRF = 60         # o mesmo da Entrega 2 (valor da literatura; não está no material)
COBERTURA_MINIMA = 0.5  # só na análise de sensibilidade; não encontrei no material, escolha de engenharia


# ---------------------------------------------------------------- dados ----
def carregar_blocos(caminho: Path = BLOCOS) -> list[dict]:
    """Blocos do passo 5.1 (extrair_manual.py), na ordem de leitura."""
    with open(caminho, encoding="utf-8") as f:
        return sorted((json.loads(l) for l in f if l.strip()), key=lambda b: b["ordem"])


def carregar_consultas(conjunto: str) -> list[dict]:
    with open(AQUI / CONJUNTOS[conjunto], encoding="utf-8") as f:
        return json.load(f)["consultas"]


def titulo_da_folha(b: dict) -> str:
    if b.get("subsecao"):
        return f"{b['subsecao']} {b['titulo_subsecao']}"
    if b.get("secao"):
        return f"{b['secao']} {b['titulo_secao']}"
    return f"{b['capitulo']} {b['titulo_capitulo']}"


def trilha(b: dict) -> str:
    """Caminho hierárquico da folha do bloco: 'Cap. 6 Regras para ... › 6.2 Filtros de ...'."""
    partes = [f"Cap. {b['capitulo']} {b['titulo_capitulo']}"]
    if b.get("secao"):
        partes.append(f"{b['secao']} {b['titulo_secao']}")
    if b.get("subsecao"):
        partes.append(f"{b['subsecao']} {b['titulo_subsecao']}")
    return " › ".join(partes)


def paginas(blocos: list[dict]) -> dict:
    return {
        "pagina_pdf_ini": min(b["pagina_pdf_ini"] for b in blocos),
        "pagina_pdf_fim": max(b["pagina_pdf_fim"] for b in blocos),
        "pagina_impressa_ini": min(b["pagina_impressa_ini"] for b in blocos),
        "pagina_impressa_fim": max(b["pagina_impressa_fim"] for b in blocos),
    }


def montar_folhas(blocos: list[dict]) -> list[dict]:
    """Blocos de conteúdo agrupados por folha, na ordem do manual. Folha só com título
    (como 4.3 e 7.3, que abrem direto em subseções) não aparece: não tem texto a indexar."""
    por_folha: dict[str, list[dict]] = {}
    for b in blocos:
        if b["tipo"] != "titulo":
            por_folha.setdefault(b["folha"], []).append(b)
    return [{"folha": f, "titulo": titulo_da_folha(bs[0]), "caminho": trilha(bs[0]),
             "capitulo": bs[0]["capitulo"], "secao": bs[0]["secao"], "subsecao": bs[0]["subsecao"],
             "blocos": bs} for f, bs in por_folha.items()]


# ------------------------------------------------------- estratégia C ----
_FIM_DE_FRASE = re.compile(r"(?<=[.!?;:])\s+")


def _pecas(bloco: dict, cabeca: str, teto: int, contar) -> list[str]:
    """Um bloco vira uma ou mais peças. Só se quebra o bloco que, sozinho com a trilha, passa do
    teto: tabela em grupos de linhas, cada grupo com o cabeçalho; parágrafo em frases. Código nunca
    (cortar um exemplo no meio entregaria meio exemplo ao agente)."""
    texto = bloco["texto"]
    if bloco["tipo"] == "codigo" or contar(cabeca + texto) <= teto:
        return [texto]
    if bloco["tipo"] == "tabela":
        topo, juntar = " | ".join(bloco["cabecalho"]) + "\n", "\n"
        unidades = [" | ".join(linha) for linha in bloco["linhas"]]
    else:
        topo, juntar = "", " "
        unidades = [u for u in _FIM_DE_FRASE.split(texto) if u.strip()]
    pecas, atual = [], []
    for u in unidades:
        if atual and contar(cabeca + topo + juntar.join(atual + [u])) > teto:
            pecas.append(topo + juntar.join(atual))
            atual = [u]
        else:
            atual.append(u)
    if atual:
        pecas.append(topo + juntar.join(atual))
    return pecas


def dividir_folha(folha: dict, teto: int, contar) -> list[tuple[str, list[dict]]]:
    """[(texto do nó, blocos usados)]. Uma parte se a folha couber no teto; senão junta peças
    inteiras, em ordem, enquanto couberem. Toda parte começa pela trilha."""
    cabeca = folha["caminho"] + "\n\n"
    pecas = [(p, b) for b in folha["blocos"] for p in _pecas(b, cabeca, teto, contar)]
    partes, atual = [], []
    for p, b in pecas:
        if atual and contar(cabeca + "\n\n".join(x for x, _ in atual + [(p, b)])) > teto:
            partes.append(atual)
            atual = [(p, b)]
        else:
            atual.append((p, b))
    if atual:
        partes.append(atual)
    return [(cabeca + "\n\n".join(x for x, _ in parte), [b for _, b in parte]) for parte in partes]


def nos_C(blocos: list[dict], contar, teto: int = TETO_C):
    """Um TextNode por folha (ou por parte). Só o TEXTO entra no embedding: todo metadado vai em
    excluded_embed_metadata_keys, como na Entrega 2."""
    from llama_index.core.schema import TextNode

    nos, tokens, divididas, acima = [], [], {}, []
    folhas = montar_folhas(blocos)
    for f in folhas:
        partes = dividir_folha(f, teto, contar)
        total = len("\n\n".join(b["texto"] for b in f["blocos"]))
        if len(partes) > 1:
            divididas[f["folha"]] = len(partes)
        for k, (texto, bs) in enumerate(partes, 1):
            n_tok = contar(texto)
            tokens.append(n_tok)
            nid = f"C:{f['folha']}#{k}"
            if n_tok > teto:
                acima.append(nid)        # só acontece com um bloco de código maior que o teto
            meta = {"estrategia": "C", "folha": f["folha"], "folhas": [f["folha"]], "titulo": f["titulo"],
                    "caminho": f["caminho"], "capitulo": f["capitulo"], "secao": f["secao"],
                    "subsecao": f["subsecao"], **paginas(bs),
                    "tem_tabela": any(b["tipo"] == "tabela" for b in bs),
                    "tem_codigo": any(b["tipo"] == "codigo" for b in bs),
                    "parte": k, "n_partes": len(partes), "tokens": n_tok,
                    "cobertura": {f["folha"]: round(min(1.0, (len(texto) - len(f["caminho"]) - 2) / total), 3)}}
            nos.append(TextNode(id_=nid, text=texto, metadata=meta, excluded_embed_metadata_keys=list(meta)))
    rel = {"estrategia": "C", "teto_tokens": teto, "sobreposicao": 0, "folhas": len(folhas), "nos": len(nos),
           "tokens_mediana": statistics.median(tokens), "tokens_max": max(tokens),
           "folhas_divididas": divididas, "nos_acima_do_teto": acima}
    return nos, rel


# ------------------------------------------------------- estratégia B ----
def texto_plano(blocos: list[dict]) -> tuple[str, list[tuple[int, int, dict]]]:
    """O manual limpo como um texto só (títulos inclusive, como num texto corrido) e o trecho
    [início, fim) de cada bloco dentro dele."""
    partes, trechos, pos = [], [], 0
    for b in blocos:
        if partes:
            pos += 2                      # o "\n\n" entre blocos
        trechos.append((pos, pos + len(b["texto"]), b))
        partes.append(b["texto"])
        pos += len(b["texto"])
    return "\n\n".join(partes), trechos


def localizar(pedacos: list[str], texto: str) -> list[tuple[int, int]]:
    """Onde cada pedaço do SentenceSplitter está no texto. Os pedaços são trechos contíguos (sem
    espaço nas pontas); com a sobreposição, cada um começa antes do fim do anterior, então a busca
    recomeça logo depois do início do anterior. Se o espaçamento tiver mudado, casa palavra a palavra."""
    saida, cursor = [], 0
    for p in pedacos:
        ini = texto.find(p, cursor)
        if ini >= 0:
            fim = ini + len(p)
        else:
            m = re.compile(r"\s+".join(map(re.escape, p.split()))).search(texto, cursor)
            if m is None:
                raise ValueError(f"pedaço do SentenceSplitter não encontrado no texto: {p[:80]!r}")
            ini, fim = m.start(), m.end()
        saida.append((ini, fim))
        cursor = ini + 1
    return saida


def folha_principal(ini: int, fim: int, trechos) -> tuple[str, dict[str, int]]:
    """Folha com mais caracteres de conteúdo (títulos não contam) dentro de [ini, fim); empate: a
    que aparece primeiro. Também devolve quantos caracteres de cada folha tocada caem no trecho."""
    conta: dict[str, int] = {}
    for a, z, b in trechos:
        sob = min(z, fim) - max(a, ini)
        if sob > 0 and b["tipo"] != "titulo":
            conta[b["folha"]] = conta.get(b["folha"], 0) + sob
    if not conta:                         # pedaço só com título(s)
        b = next(b for a, z, b in trechos if min(z, fim) - max(a, ini) > 0)
        return b["folha"], {}
    ordem = list(conta)                   # dict guarda a ordem de inserção = ordem do texto
    return max(ordem, key=lambda f: (conta[f], -ordem.index(f))), conta


def nos_B(blocos: list[dict], tokenizador, chunk: int = CHUNK_B, sobreposicao: int = OVERLAP_B):
    """Chunks de tamanho fixo sobre o texto plano. `tokenizador(texto) -> lista de tokens` é o que
    o SentenceSplitter usa para medir chunk_size (a aula não diz qual tokenizer conta)."""
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.schema import TextNode

    texto, trechos = texto_plano(blocos)
    pedacos = SentenceSplitter(chunk_size=chunk, chunk_overlap=sobreposicao,
                               tokenizer=tokenizador).split_text(texto)
    posicoes = localizar(pedacos, texto)
    folhas = montar_folhas(blocos)
    info = {f["folha"]: f for f in folhas}
    total: dict[str, int] = {}
    for a, z, b in trechos:
        if b["tipo"] != "titulo":
            total[b["folha"]] = total.get(b["folha"], 0) + (z - a)
    nos, tokens = [], []
    for i, (p, (a, z)) in enumerate(zip(pedacos, posicoes), 1):
        principal, conta = folha_principal(a, z, trechos)
        tocadas = list(conta) or [principal]
        bs = [b for x, y, b in trechos if min(y, z) - max(x, a) > 0]
        f = info.get(principal) or {"titulo": titulo_da_folha(bs[0]), "caminho": trilha(bs[0]),
                                    "capitulo": bs[0]["capitulo"], "secao": bs[0]["secao"],
                                    "subsecao": bs[0]["subsecao"]}
        n_tok = len(tokenizador(p))
        tokens.append(n_tok)
        meta = {"estrategia": "B", "folha": principal, "folhas": tocadas, "titulo": f["titulo"],
                "caminho": f["caminho"], "capitulo": f["capitulo"], "secao": f["secao"],
                "subsecao": f["subsecao"], **paginas(bs),
                "tem_tabela": any(b["tipo"] == "tabela" for b in bs),
                "tem_codigo": any(b["tipo"] == "codigo" for b in bs),
                "inicio": a, "fim": z, "parte": i, "n_partes": len(pedacos), "tokens": n_tok,
                "cobertura": {fl: round(n / total[fl], 3) for fl, n in conta.items()}}
        nos.append(TextNode(id_=f"B:{i:04d}", text=p, metadata=meta, excluded_embed_metadata_keys=list(meta)))
    coberto = bytearray(len(texto))
    for a, z in posicoes:
        coberto[a:z] = b"\x01" * (z - a)
    descobertos = sum(1 for j, c in enumerate(texto) if not coberto[j] and not c.isspace())
    principais = {n.metadata["folha"] for n in nos}
    rel = {"estrategia": "B", "chunk_tokens": chunk, "sobreposicao_tokens": sobreposicao, "folhas": len(folhas),
           "nos": len(nos), "tokens_mediana": statistics.median(tokens), "tokens_max": max(tokens),
           "folhas_nunca_principais": [f["folha"] for f in folhas if f["folha"] not in principais],
           "caracteres_fora_de_qualquer_chunk": descobertos}
    return nos, rel


def acerta(meta: dict, gabarito, regra: str = "principal") -> bool:
    """Regra oficial (Passo 4): o nó acerta se a sua folha principal está no gabarito.
    Regra 'cobertura' (análise de sensibilidade, só relatada): também acerta o nó que contém pelo
    menos COBERTURA_MINIMA dos caracteres de alguma folha do gabarito. Em B uma folha pequena pode
    caber inteira num chunk sem ser a principal; o agente veria o texto, mas a regra oficial não conta."""
    if meta["folha"] in gabarito:
        return True
    return regra == "cobertura" and any(meta["cobertura"].get(f, 0.0) >= COBERTURA_MINIMA for f in gabarito)


def consultas_inalcancaveis(nos, regra: str = "principal") -> dict[str, list[str]]:
    """Consultas que nenhum nó desta estratégia consegue acertar pela regra dada. Só lê os
    gabaritos; não faz busca."""
    metas = [n.metadata for n in nos]
    return {nome: [c["id"] for c in carregar_consultas(nome)
                   if not any(acerta(m, c["gabarito"], regra) for m in metas)]
            for nome in CONJUNTOS}


# ---------------------------------------------------------------- busca ----
class RerankerComCache(Reranker):
    """Guarda a nota de cada par (consulta, texto). 'vetor + rerank' e 'híbrido + rerank' releem
    quase os mesmos candidatos, e o cross-encoder é a parte cara no CPU: mesma nota, menos pares."""

    def __init__(self, base: Reranker):
        super().__init__(base.prever, base.nome)
        self.cache: dict[tuple[str, str], float] = {}
        self.pares_avaliados = 0

    def pontuar(self, consulta: str, textos: list[str]) -> list[float]:
        faltam = [t for t in dict.fromkeys(textos) if (consulta, t) not in self.cache]
        if faltam:
            for t, s in zip(faltam, super().pontuar(consulta, faltam)):
                self.cache[(consulta, t)] = s
            self.pares_avaliados += len(faltam)
        return [self.cache[(consulta, t)] for t in textos]


def fundir_rrf_nos(rankings: list[list], k_rrf: int = K_RRF):
    """O RRF da Entrega 2 (fundir_rrf), generalizado: a chave é o id do nó, porque no manual não há
    'regra' a agrupar. Nota = soma de 1/(k_rrf + posição) em cada ranking."""
    from llama_index.core.schema import NodeWithScore

    nota: dict[str, float] = {}
    no: dict[str, object] = {}
    for ranking in rankings:
        for pos, n in enumerate(ranking, 1):
            nid = n.node.node_id
            nota[nid] = nota.get(nid, 0.0) + 1.0 / (k_rrf + pos)
            no.setdefault(nid, n.node)
    return [NodeWithScore(node=no[i], score=s) for i, s in sorted(nota.items(), key=lambda x: -x[1])]


_BM25: dict[int, tuple] = {}


def ranking_bm25(index, consulta: str):
    """Todos os nós ordenados pelo BM25 da Entrega 2 (sem alteração), como lá."""
    from llama_index.core.schema import NodeWithScore

    if id(index) not in _BM25:
        nos = list(index.docstore.docs.values())
        _BM25[id(index)] = (BM25([n.text for n in nos]), nos)
    bm25, nos = _BM25[id(index)]
    pares = sorted(zip(nos, bm25.notas(consulta)), key=lambda x: -x[1])
    return [NodeWithScore(node=n, score=s) for n, s in pares]


def buscar(index, consulta: str, k: int | None = 5, reranker: Reranker | None = None,
           n_candidatos: int = N_CANDIDATOS, hibrido: bool = False):
    """Ranking de chunks (sem agrupar: o agente recebe chunks). Mesma sequência da Entrega 2:
    vetorial -> [fusão RRF com BM25] -> [re-ranking dos n_candidatos primeiros]."""
    ranking = index.as_retriever(similarity_top_k=len(index.docstore.docs)).retrieve(consulta)
    if hibrido:
        ranking = fundir_rrf_nos([ranking, ranking_bm25(index, consulta)])
    if reranker is not None:
        ranking = reordenar_com_reranker(ranking, consulta, reranker, n_candidatos)
    return ranking[:k] if k else ranking


def caminho_indice(estrategia: str) -> Path:
    return DIR_INDICES / f"indice_manual_{estrategia}"


def carregar_indice(estrategia: str, embed_model):
    from llama_index.core import StorageContext, load_index_from_storage

    ctx = StorageContext.from_defaults(persist_dir=str(caminho_indice(estrategia)))
    return load_index_from_storage(ctx, embed_model=embed_model)


# ------------------------------------------- modelo (só no notebook) -------
def criar_tokenizador():
    """Tokenizer do bge-m3 como lista de tokens, sem os especiais: mede o chunk_size do B no
    mesmo modelo que embeda (a aula não diz qual tokenizer usar)."""
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODELO_EMBEDDING)
    return lambda texto: tok.encode(texto, add_special_tokens=False)
