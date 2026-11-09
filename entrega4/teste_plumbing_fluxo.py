# -*- coding: utf-8 -*-
"""Entrega 4 - testes de encanamento, SEM modelo e SEM rede: embedding falso (hash de palavras), reranker falso
(sobreposição de palavras), relógio falso, cliente falso do Gemini. Não medem qualidade de busca.
Rodam sobre os módulos reais das Entregas 2 e 3 (importados) e sobre a regra pré-registrada.

    python teste_plumbing_fluxo.py

Um teste "pulado" não passou nem falhou: não rodou porque falta um insumo (diz qual). Não escreve nada em
entrega1, entrega2, entrega3 nem nesta pasta: tudo que grava vai para pastas temporárias.
"""
from __future__ import annotations

import builtins
import contextlib
import io
import json
import math
import os
import re
import sys
import tempfile
import traceback
import zlib
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import NodeWithScore, TextNode

import avaliar_fluxo as af
import comum_fluxo as cf
import fluxo

TESTES = []
DIM = 64


class Pulado(Exception):
    pass


def teste(f):
    TESTES.append(f)
    return f


# ------------------------------------------------------------------ falsos ----
class Relogio:
    """Relógio falso: só anda quando alguém manda (o embedding falso e o reranker falso cobram tempo)."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def avanca(self, s):
        self.t += s


ESTADO = {"relogio": None, "custo_consulta": 0.0}
# O BM25 das Entregas 2 e 3 fica em cache por índice (a da Entrega 3 usa id(index) como chave). Os índices falsos
# ficam vivos até o fim, para um id reaproveitado depois de liberado nunca devolver o BM25 de outro índice.
_VIVOS: list = []


def _palavras(texto: str) -> list[str]:
    return re.findall(r"\w+", texto.lower())


class EmbeddingFalso(BaseEmbedding):
    dim: int = DIM

    def _vetor(self, texto: str) -> list[float]:
        v = [0.0] * self.dim
        for p in _palavras(texto):
            v[zlib.crc32(p.encode()) % self.dim] += 1.0
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]

    def _get_query_embedding(self, query: str) -> list[float]:
        if ESTADO["relogio"] is not None:
            ESTADO["relogio"].avanca(ESTADO["custo_consulta"])
        return self._vetor(query)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._vetor(text)


def reranker_falso(relogio=None, custo_par: float = 0.0, pares_vistos: list | None = None):
    def prever(pares):
        if pares_vistos is not None:
            pares_vistos.append(len(pares))
        if relogio is not None:
            relogio.avanca(custo_par * len(pares))
        return [float(len(set(_palavras(q)) & set(_palavras(t)))) for q, t in pares]

    return cf.c2.Reranker(prever, "falso")


TEMAS = ["frequencia de contato", "carteira inativa", "desconto progressivo", "limite de credito", "rota de visitas",
         "agenda de supervisores", "pedido minimo", "bloqueio de cliente", "meta mensal", "campanha de reativacao",
         "cobranca de inadimplentes", "prazo de entrega"]


def nos_regras(gobr_extra: str = "") -> list[TextNode]:
    nos = []
    for i, tema in enumerate(TEMAS):
        rid = f"exemplos/Regra{i:02d}.gobr"
        meta = {"regra_id": rid, "titulo": f"Regra de {tema}", "arquivo": rid,
                "gobr": f"version 1.0\nregra {i} {{ tema: \"{tema}\" }}\n" + (gobr_extra if i == 0 else "")}
        no = TextNode(id_=f"no_{i}", text=f"Regra de {tema}. Explica quando aplicar a regra {i}.", metadata=meta)
        no.excluded_embed_metadata_keys = list(meta)
        no.excluded_llm_metadata_keys = list(meta)
        nos.append(no)
    return nos


def nos_manual() -> list[TextNode]:
    nos = []
    for i, tema in enumerate(TEMAS):
        folha = f"{2 + i // 4}.{1 + i % 4}"
        caminho = f"Cap. {2 + i // 4} Estrutura › {folha} {tema}"
        meta = {"caminho": caminho, "folha": folha, "pagina_impressa_ini": 10 + i, "pagina_impressa_fim": 10 + i + i % 2,
                "cobertura": {folha: 1.0}, "titulo": tema}
        no = TextNode(id_=f"man_{i}", text=f"{caminho}\nO manual descreve {tema}.", metadata=meta)
        no.excluded_embed_metadata_keys = list(meta)
        no.excluded_llm_metadata_keys = list(meta)
        nos.append(no)
    return nos


def consultas_regras(n: int) -> list[dict]:
    return [{"id": f"q{k + 1}", "tipo": "texto", "consulta": f"como configurar {TEMAS[(3 * k) % 12]}",
             "relevantes": [f"exemplos/Regra{(3 * k) % 12:02d}.gobr"]} for k in range(n)]


def consultas_manual(n: int) -> list[dict]:
    return [{"id": f"m{k + 1}", "tipo": "opcoes", "consulta": f"quais as opcoes de {TEMAS[(5 * k) % 12]}",
             "gabarito": [f"{2 + ((5 * k) % 12) // 4}.{1 + ((5 * k) % 12) % 4}"]} for k in range(n)]


def recursos_falsos(relogio=None, custo_par: float = 0.0, pares_vistos=None, contagem=None, gobr_extra: str = ""):
    """Recursos com tudo falso. `contagem` (dict) conta quantas vezes cada coisa foi carregada."""
    contagem = contagem if contagem is not None else {}
    emb = EmbeddingFalso()
    idx_r = VectorStoreIndex(nos_regras(gobr_extra), embed_model=emb, show_progress=False)
    idx_m = VectorStoreIndex(nos_manual(), embed_model=emb, show_progress=False)
    _VIVOS.extend([idx_r, idx_m])

    def conta(chave, valor):
        contagem[chave] = contagem.get(chave, 0) + 1
        return valor

    return cf.Recursos(
        fabrica_embedding=lambda: conta("embedding", (emb, "falso")),
        fabrica_reranker=lambda ml: conta(f"reranker_{ml}", (reranker_falso(relogio, custo_par, pares_vistos), f"falso-{ml}")),
        carregar_regras=lambda e: conta("indice_regras", idx_r),
        carregar_manual=lambda e: conta("indice_manual", idx_m),
        fabrica_contador=lambda: conta("tokenizer", lambda t: len(t.split())),
        relogio=relogio or __import__("time").perf_counter)


def silencio(f, *a, **k):
    """Roda f com stdout e stderr capturados. Devolve (resultado, stdout, stderr).
    Se f terminar com SystemExit (argparse faz isso em erro de uso), o resultado é o código de saída."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            r = f(*a, **k)
        except SystemExit as e:
            r = e.code
    return r, out.getvalue(), err.getvalue()


def nada(_msg=""):
    pass


# ------------------------------------------------------- a regra e o código ----
@teste
def constantes_do_codigo_batem_com_o_bloco_da_regra():
    regra = cf.ler_constantes_regra()
    codigo = {"K": cf.K, "TETO_S": cf.TETO_S, "REPETICOES": cf.REPETICOES, "FASE1": cf.FASE1,
              "N_CANDIDATOS": cf.N_CANDIDATOS, "MAX_LENGTH_REGRAS": cf.MAX_LENGTH_REGRAS,
              "MAX_LENGTH_MANUAL": cf.MAX_LENGTH_MANUAL, "CONSULTA_AQUECIMENTO": cf.CONSULTA_AQUECIMENTO}
    assert set(regra) == set(codigo), (sorted(regra), sorted(codigo))
    for nome, valor in codigo.items():
        esperado = [str(x) for x in valor] if isinstance(valor, tuple) else [str(valor)]
        assert regra[nome] == esperado, (nome, regra[nome], esperado)


@teste
def regra_tem_o_sha256_registrado():
    ok, obtido = cf.conferir_regra()
    assert ok, f"sha256 {obtido}"
    # fins de linha CRLF (autocrlf do git no Windows) não mudam o hash
    assert cf.sha256_arquivo(cf.ARQ_REGRA, lf=True) == cf.HASH_REGRA


@teste
def grade_tem_18_e_10_configuracoes_como_a_regra_diz():
    texto = cf.ARQ_REGRA.read_text(encoding="utf-8")
    dito = [int(x) for x in re.findall(r"= (\d+) configurações", texto)]
    assert dito == [18, 10], dito
    assert (len(cf.grade("regras")), len(cf.grade("manual"))) == (18, 10)
    nomes = [c.nome for c in cf.todas_as_configs()]
    assert len(nomes) == len(set(nomes)) == 28
    assert all(c.n != 3 for c in cf.todas_as_configs())            # N = 3 não entra (regra, seção 4)
    assert {c.max_length for c in cf.grade("manual") if c.n} == {2048}
    assert {c.max_length for c in cf.grade("regras") if c.n} == {512, 2048}
    for nome in nomes:                                             # nome de arquivo válido no Windows
        assert not set('<>:"/\\|?*') & set(nome), nome


@teste
def plano_de_execucao_cobre_a_grade_uma_vez_e_agrupa_por_max_length():
    plano = cf.plano_execucao()
    assert [ml for ml, _ in plano] == [0, 512, 2048]
    todas = [c for _, cfgs in plano for c in cfgs]
    assert sorted(c.nome for c in todas) == sorted(c.nome for c in cf.todas_as_configs()) and len(todas) == 28
    for ml, cfgs in plano:
        assert all(c.max_length == ml for c in cfgs)
    assert [len(c) for _, c in plano] == [4, 8, 16]


@teste
def simplicidade_ordena_como_a_regra_manda():
    # Regra, seção 6, item 4, nesta ordem de prioridade: sem reranker antes de com reranker; vetor antes de híbrido;
    # menor N; max_length 512 antes de 2048. Logo "vetor com N = 10" vem ANTES de "híbrido com N = 5".
    C = cf.Config
    ordem = [C("regras", "vetor"), C("regras", "hibrido"), C("regras", "vetor", 5, 512), C("regras", "vetor", 5, 2048),
             C("regras", "vetor", 10, 512), C("regras", "hibrido", 5, 512), C("regras", "hibrido", 5, 2048)]
    assert sorted(reversed(ordem), key=lambda c: c.simplicidade) == ordem
    # sem reranker antes de com reranker, mesmo híbrido sem rerank contra vetor com rerank
    assert C("regras", "hibrido").simplicidade < C("regras", "vetor", 5, 512).simplicidade


@teste
def config_valida_os_campos_e_faz_ida_e_volta():
    C = cf.Config
    for ruim in (lambda: C("outro", "vetor"), lambda: C("regras", "denso"), lambda: C("regras", "vetor", 5, 0),
                 lambda: C("regras", "vetor", 0, 512)):
        try:
            ruim()
        except ValueError:
            continue
        raise AssertionError("aceitou configuração inválida")
    for c in cf.todas_as_configs():
        assert C.from_dict(c.to_dict()) == c
    d = cf.grade("regras")[2].to_dict()
    d["nome"] = "outro_nome"
    try:
        C.from_dict(d)
    except ValueError:
        return
    raise AssertionError("aceitou nome incoerente")


@teste
def reuso_so_por_import_dos_arquivos_reais_das_entregas_2_e_3():
    assert Path(cf.c2.__file__).resolve().parent == cf.ENTREGA2.resolve()
    assert Path(cf.av2.__file__).resolve().parent == cf.ENTREGA2.resolve()
    assert Path(cf.c3.__file__).resolve().parent == cf.ENTREGA3.resolve()
    assert (cf.c3.ESTRATEGIA_PADRAO, cf.c3.RERANK_PADRAO, cf.c3.HIBRIDO_PADRAO) == ("C", True, False)  # intactas
    assert getattr(cf.c2, "RERANKER_MAX_LENGTH", None) == 2048    # o "2048" da regra é o da Entrega 2


@teste
def arquivos_prometidos_para_o_passo_5_existem():
    texto = cf.ARQ_REGRA.read_text(encoding="utf-8")
    prometidos = re.findall(r"^\| `([^`]+)` \|[^|]*\| passo 5 \|$", texto, re.M)
    assert set(prometidos) == {"comum_fluxo.py", "fluxo.py", "avaliar_fluxo.py", "teste_plumbing_fluxo.py",
                               "requirements.txt"}, prometidos
    faltam = [p for p in prometidos if not (cf.AQUI / p).exists()]
    assert not faltam, faltam


@teste
def insumos_da_regra_sao_13_e_a_conferencia_acha_diferenca():
    itens = cf.insumos_da_regra()
    assert len(itens) == 13 and all(len(h) == 64 for _, h in itens), len(itens)
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        regra = raiz / "regra.md"
        (raiz / "a.txt").write_text("conteudo", encoding="utf-8")
        import hashlib
        h = hashlib.sha256(b"conteudo").hexdigest()
        regra.write_text(f"| Arquivo | sha256 |\n|---|---|\n| `a.txt` (rótulo) | `{h}` |\n| `b.txt` | `{'0' * 64}` |\n",
                         encoding="utf-8")
        r = cf.conferir_insumos(raiz, regra)
        assert [(i["arquivo"], i["ok"]) for i in r] == [("a.txt", True), ("b.txt", False)]
        assert r[1]["obtido"] is None                                # arquivo ausente
        (raiz / "a.txt").write_text("mudou", encoding="utf-8")
        assert not cf.conferir_insumos(raiz, regra)[0]["ok"]


# ------------------------------------------------------------ acerto e métricas ----
@teste
def metricas_exatas_batem_com_as_da_entrega_2():
    casos = [[1, 2, None, 5, 3, None, 1, 12, 4, 2, 1, 7, None, 3],
             [None] * 15, [1] * 15, [3, 3, 4, 2, 10, 11, None, 1, 1, 5, 6, 2, 3, 9, 1, 20, None, 4, 4, 2]]
    for pos in casos:
        e, f = cf.metricas_exatas(pos), cf.av2.metricas(pos)
        assert abs(float(e["hit@3"]) - f["hit@3"]) < 1e-12 and abs(float(e["MRR"]) - f["MRR"]) < 1e-12, pos
    assert cf.metricas_exatas([1, None, 3])["hit@3"] == Fraction(2, 3)
    assert cf.metricas_exatas([2, 2])["MRR"] == Fraction(1, 2)
    assert cf.metricas_exatas([])["hit@3"] == 0


@teste
def acerto_do_manual_usa_a_regra_oficial_da_entrega_3_e_o_das_regras_a_da_entrega_2():
    def no(folha, cob=None):
        return NodeWithScore(node=TextNode(text="x", metadata={"folha": folha, "cobertura": cob or {folha: 1.0}}), score=1.0)

    ranking = [no("2.1"), no("3.4"), no("5.1", {"5.1": 0.2, "6.2": 0.9})]
    assert cf.posicao_manual(ranking, {"gabarito": ["3.4"]}) == 2
    assert cf.posicao_manual(ranking, {"gabarito": ["9.9"]}) is None
    assert cf.posicao_manual(ranking, {"gabarito": ["6.2"]}) is None       # cobertura 90% não conta: regra oficial
    assert cf.posicao_manual(ranking, {"gabarito": ["2.1", "3.4"]}) == 1

    def regra(rid):
        return NodeWithScore(node=TextNode(text="x", metadata={"regra_id": rid}), score=1.0)

    assert cf.posicao_regras([regra("a"), regra("b")], {"relevantes": ["b", "z"]}) == 2
    assert cf.posicao_regras([regra("a")], {"relevantes": ["z"]}) is None


# -------------------------------------------------------------------- busca ----
@teste
def busca_configuravel_chama_a_funcao_da_entrega_certa_com_fase1_e_n_certos():
    rec = recursos_falsos()
    idx_r, idx_m = rec.indice("regras"), rec.indice("manual")
    q = "como configurar carteira inativa"
    for hib in (False, True):
        # sem reranker: nenhum par é lido e o resultado é o da função da própria entrega
        vistos = []
        rr = reranker_falso(pares_vistos=vistos)
        cfg = cf.Config("regras", "hibrido" if hib else "vetor")
        a = cf.buscar_cfg(idx_r, q, cfg, rr, k=None)
        b = cf.c2.buscar_regras(idx_r, q, k=None, hibrido=hib)
        assert vistos == [] and [(n.node.metadata["regra_id"], n.score) for n in a] == \
            [(n.node.metadata["regra_id"], n.score) for n in b]
        cfg = cf.Config("manual", "hibrido" if hib else "vetor")
        a = cf.buscar_cfg(idx_m, q, cfg, rr, k=None)
        b = cf.c3.buscar(idx_m, q, k=None, hibrido=hib)
        assert vistos == [] and [(n.node.node_id, n.score) for n in a] == [(n.node.node_id, n.score) for n in b]
        # com reranker: o reranker lê exatamente N pares
        for indice, idx in (("regras", idx_r), ("manual", idx_m)):
            vistos.clear()
            cfg = cf.Config(indice, "hibrido" if hib else "vetor", 5, 2048)
            a = cf.buscar_cfg(idx, q, cfg, rr, k=None)
            assert vistos == [5], vistos
            assert len(a) == 12                                   # o ranking continua completo
            assert [n.score for n in a[:5]] == sorted((n.score for n in a[:5]), reverse=True)
    # k corta o ranking no fim
    assert len(cf.buscar_cfg(idx_r, q, cf.Config("regras", "vetor"), None, k=3)) == 3


@teste
def aquecimento_usa_hibrido_n_2_e_nao_entra_na_latencia_medida():
    vistos = []
    rec = recursos_falsos(pares_vistos=vistos)
    cf.aquecer(rec, "regras", 512)
    assert vistos == [2]                                          # N = 2
    assert "aquecimento_regras_512" in rec.tempos_carga_s
    vistos.clear()
    cf.aquecer(rec, "manual", 0)                                  # sem reranker: só embedding e BM25
    assert vistos == []
    assert cf.CONSULTA_AQUECIMENTO == "teste de aquecimento"


# ------------------------------------------------------------ cronômetro e poda ----
@teste
def cronometro_vale_a_menor_repeticao_e_o_ranking_vem_da_primeira():
    rel = Relogio()
    duracoes = iter([7, 5])
    chamadas = []

    def chamar():
        chamadas.append(1)
        rel.avanca(next(duracoes))
        return [f"r{len(chamadas)}"]

    ranking, tempos, estourou = cf.cronometrar(chamar, 2, 20.0, rel)
    assert ranking == ["r1"] and tempos == [7, 5] and min(tempos) == 5 and not estourou and len(chamadas) == 2


@teste
def poda_so_quando_a_primeira_medicao_passa_do_teto():
    for primeira, esperado_estourou, n_chamadas in ((20, False, 2), (21, True, 1)):
        rel = Relogio()
        duracoes = iter([primeira, 1])
        chamadas = []

        def chamar():
            chamadas.append(1)
            rel.avanca(next(duracoes))
            return ["r"]

        _, tempos, estourou = cf.cronometrar(chamar, 2, 20.0, rel)
        assert estourou is esperado_estourou and len(chamadas) == n_chamadas, (primeira, chamadas)


@teste
def latencia_da_configuracao_e_a_maior_entre_as_consultas_das_menores_medidas():
    rel = Relogio()
    roteiro = iter([7, 5, 9, 12, 3, 4])                           # q1: 7,5  q2: 9,12  q3: 3,4
    consultas = [{"id": "q1", "consulta": "a"}, {"id": "q2", "consulta": "b"}, {"id": "q3", "consulta": "c"}]

    def chamar(texto):
        rel.avanca(next(roteiro))
        return [texto]

    r = cf.medir_configuracao(cf.Config("regras", "vetor"), consultas, chamar, lambda ranking, c: 1,
                              relogio=rel, avisar=nada)
    assert [p["min_s"] for p in r["por_consulta"]] == [5, 9, 3] and r["latencia_s"] == 9
    assert r["hit3_frac"] == "1" and r["mrr_frac"] == "1" and not r["excluida"]


@teste
def configuracao_lenta_e_excluida_na_primeira_consulta_que_estoura():
    rel = Relogio()
    roteiro = iter([4, 3, 25])                                    # q1 ok (4, 3); q2 estoura (25)
    consultas = [{"id": "q1", "consulta": "a"}, {"id": "q2", "consulta": "b"}, {"id": "q3", "consulta": "c"}]
    chamadas = []

    def chamar(texto):
        chamadas.append(texto)
        rel.avanca(next(roteiro))
        return [texto]

    r = cf.medir_configuracao(cf.Config("regras", "vetor"), consultas, chamar, lambda ranking, c: 2,
                              relogio=rel, avisar=nada)
    assert r["excluida"] and r["excluida_por"] == {"consulta": "q2", "tempo_s": 25, "teto_s": 20.0}
    assert chamadas == ["a", "a", "b"] and r["consultas_medidas"] == 1 and "latencia_s" not in r


# ------------------------------------------------------------- checkpoints ----
@teste
def checkpoint_e_exclusivo_e_arquivo_quebrado_e_recusado():
    cfg = cf.Config("regras", "hibrido", 5, 512)
    dado = {"config": cfg.to_dict(), "excluida": False, "metricas": {}, "hit3_frac": "1/2", "mrr_frac": "1/3",
            "latencia_s": 1.0, "por_consulta": []}
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp) / "ck"
        assert cf.carregar_checkpoint(pasta, cfg) is None
        cf.salvar_checkpoint(pasta, cfg, dado)
        assert cf.carregar_checkpoint(pasta, cfg) == dado
        try:
            cf.salvar_checkpoint(pasta, cfg, dado)
        except FileExistsError:
            pass
        else:
            raise AssertionError("sobrescreveu o checkpoint")
        cf.caminho_checkpoint(pasta, cfg).write_text("{quebrado", encoding="utf-8")
        try:
            cf.carregar_checkpoint(pasta, cfg)
        except ValueError as e:
            assert "Apague esse arquivo" in str(e)
        else:
            raise AssertionError("aceitou checkpoint quebrado")


# ------------------------------------------------------------ dev (orquestração) ----
def _dev_com_custos(pasta, custo_par=2.0, custo_emb=0.5):
    rel = Relogio()
    ESTADO.update(relogio=rel, custo_consulta=custo_emb)
    try:
        rec = recursos_falsos(relogio=rel, custo_par=custo_par)
        consultas = {"regras": consultas_regras(4), "manual": consultas_manual(5)}
        res = af.rodar_dev(rec, pasta, consultas, avisar=nada, relogio=rel)
    finally:
        ESTADO.update(relogio=None, custo_consulta=0.0)
    return rec, res


@teste
def dev_mede_as_28_configuracoes_com_a_latencia_inclindo_embedding_e_reranker_e_poda_as_lentas():
    with tempfile.TemporaryDirectory() as tmp:
        rec, res = _dev_com_custos(Path(tmp) / "ck")
        assert len(res) == 28 and len(list((Path(tmp) / "ck").glob("*.json"))) == 28
        # custo: 0,5 s de embedding + 2 s por par lido
        assert res["regras_vetor_sem-rerank"]["latencia_s"] == 0.5
        assert res["regras_hibrido_N5_L512"]["latencia_s"] == 10.5                # 0,5 + 5 x 2
        assert res["manual_vetor_N5_L2048"]["latencia_s"] == 10.5
        for nome in ("regras_vetor_N10_L2048", "manual_hibrido_N20_L2048", "regras_vetor_N50_L512"):
            e = res[nome]
            assert e["excluida"] and e["consultas_medidas"] == 0 and e["excluida_por"]["consulta"] in ("q1", "m1"), nome
            assert e["excluida_por"]["tempo_s"] > 20
        # o aquecimento não entra na medida: 0,5 + 2 pares x 2 s = 4,5 s, registrado à parte
        assert rec.tempos_carga_s["aquecimento_regras_512"] == 4.5
        # cada fase carregou o reranker certo e só um por vez
        assert rec.dispositivos.get("reranker_2048") and not rec.dispositivos.get("reranker_512")


@teste
def dev_retoma_pelas_configuracoes_que_faltam_e_nao_refaz_as_prontas():
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp) / "ck"
        _dev_com_custos(pasta)
        sumir = [cf.Config("regras", "vetor", 5, 512), cf.Config("manual", "hibrido"), cf.Config("manual", "vetor", 5, 2048)]
        for c in sumir:
            cf.caminho_checkpoint(pasta, c).unlink()
        medidas = []
        original = af._medir_indice
        af._medir_indice = lambda rec, cfg, *a, **k: (medidas.append(cfg.nome), original(rec, cfg, *a, **k))[1]
        try:
            rec = recursos_falsos()
            res = af.rodar_dev(rec, pasta, {"regras": consultas_regras(4), "manual": consultas_manual(5)}, avisar=nada)
        finally:
            af._medir_indice = original
        assert sorted(medidas) == sorted(c.nome for c in sumir), medidas
        assert len(res) == 28


# --------------------------------------------------------- regra de escolha ----
def _resultado(cfg, hit3, mrr, lat, excluida=False):
    d = {"config": cfg.to_dict(), "excluida": excluida}
    if excluida:
        d["excluida_por"] = {"consulta": "q1", "tempo_s": 30.0, "teto_s": 20.0}
    else:
        d.update({"hit3_frac": str(Fraction(hit3)), "mrr_frac": str(Fraction(mrr)), "latencia_s": lat,
                  "metricas": {}, "por_consulta": []})
    return d


def _todas(fabrica):
    return {c.nome: fabrica(c) for c in cf.todas_as_configs()}


@teste
def escolha_segue_a_ordem_dos_criterios():
    C = cf.Config
    meio = lambda c: _resultado(c, "1/2", "1/2", 1.0)               # todas empatadas em hit@3, MRR e latência
    # 1. maior soma de hit@3: vence mesmo com MRR maior em outra configuração e com latência pior
    r = _todas(lambda c: _resultado(c, "0", "0", 5.0))
    r["regras_hibrido_N5_L512"] = _resultado(C("regras", "hibrido", 5, 512), "13/14", "0", 9.0)
    r["manual_vetor_N10_L2048"] = _resultado(C("manual", "vetor", 10, 2048), "1/3", "0", 9.0)
    r["manual_hibrido_N5_L2048"] = _resultado(C("manual", "hibrido", 5, 2048), "0", "1", 0.1)   # MRR máximo, hit@3 zero
    e = cf.escolher(r)
    assert (e["escolha"]["regras"], e["escolha"]["manual"]) == ("regras_hibrido_N5_L512", "manual_vetor_N10_L2048")
    assert e["escolha"]["soma_hit3"] == str(Fraction(13, 14) + Fraction(1, 3))
    assert e["decidido_por"] == "soma dos hit@3"
    # 2. hit@3 empatado: maior soma de MRR, mesmo com latência pior (18 s contra 2 s das demais duplas)
    r = _todas(meio)
    r["regras_hibrido_N5_L512"] = _resultado(C("regras", "hibrido", 5, 512), "1/2", "3/4", 9.0)
    r["manual_vetor_N10_L2048"] = _resultado(C("manual", "vetor", 10, 2048), "1/2", "3/4", 9.0)
    e = cf.escolher(r)
    assert (e["escolha"]["regras"], e["escolha"]["manual"]) == ("regras_hibrido_N5_L512", "manual_vetor_N10_L2048")
    assert (e["escolha"]["soma_hit3"], e["escolha"]["soma_mrr"]) == ("1", "3/2")
    assert e["decidido_por"] == "soma dos MRR"
    # 3. hit@3 e MRR empatados: menor latência da dupla, mesmo que a configuração não seja a mais simples
    r = _todas(meio)
    r["regras_vetor_sem-rerank"] = _resultado(C("regras", "vetor"), "1/2", "1/2", 0.25)
    r["manual_hibrido_sem-rerank"] = _resultado(C("manual", "hibrido"), "1/2", "1/2", 0.5)   # o vetor é o mais simples
    e = cf.escolher(r)
    assert (e["escolha"]["regras"], e["escolha"]["manual"]) == ("regras_vetor_sem-rerank", "manual_hibrido_sem-rerank")
    assert e["escolha"]["latencia_dupla_s"] == 0.75 and e["decidido_por"] == "menor latência da dupla"
    # 4. empate em tudo: a mais simples, comparando primeiro a de regras e depois a do manual
    e = cf.escolher(_todas(meio))
    assert (e["escolha"]["regras"], e["escolha"]["manual"]) == ("regras_vetor_sem-rerank", "manual_vetor_sem-rerank")
    assert (e["melhores"][1]["regras"], e["melhores"][1]["manual"]) == ("regras_vetor_sem-rerank",
                                                                         "manual_hibrido_sem-rerank")
    assert e["decidido_por"] == "configuração mais simples (manual)"       # a 2ª colocada só difere no manual
    r = _todas(meio)
    r["regras_vetor_sem-rerank"] = _resultado(C("regras", "vetor"), "1/2", "1/2", 1.5)   # latência pior: sai da frente
    assert cf.escolher(r)["escolha"]["regras"] == "regras_hibrido_sem-rerank"


@teste
def escolha_compara_fracoes_exatas_nao_floats():
    C = cf.Config
    # O teto acopla os dois lados: B (a melhor regra) não pode ficar com M (o melhor manual), 15 + 10 > 20 s.
    # Sobram (A, M) e (B, qualquer outro manual), que somam 3/10 EXATO. Em float, 0.1 + 0.2 > 0.3, e (A, M) ganharia
    # no passo 1 sem chegar ao MRR, que é onde a regra manda desempatar.
    A, B, M = C("regras", "vetor", 5, 512), C("regras", "hibrido", 5, 512), C("manual", "vetor", 5, 2048)
    r = _todas(lambda c: _resultado(c, "0", "0", 1.0))
    r[A.nome] = _resultado(A, "1/10", "0", 1.0)
    r[B.nome] = _resultado(B, "3/10", "1/10", 15.0)
    r[M.nome] = _resultado(M, "2/10", "0", 10.0)
    assert 0.1 + 0.2 > 0.3 and Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10)
    esc = cf.escolher(r)["escolha"]
    assert esc["regras"] == B.nome and esc["manual"] != M.nome, esc
    assert (esc["soma_hit3"], esc["soma_mrr"]) == ("3/10", "1/10")


@teste
def escolha_ignora_excluidas_e_duplas_acima_do_teto_mesmo_com_acerto_maior():
    C = cf.Config
    r = _todas(lambda c: _resultado(c, "1/2", "1/2", 1.0))
    # a melhor de cada lado acerta mais, mas junta 11 + 10 = 21 s (> 20)
    r["regras_hibrido_N5_L512"] = _resultado(C("regras", "hibrido", 5, 512), "1", "1", 11.0)
    r["manual_hibrido_N5_L2048"] = _resultado(C("manual", "hibrido", 5, 2048), "1", "1", 10.0)
    # e uma excluída por latência não pode ser escolhida
    r["manual_vetor_N10_L2048"] = _resultado(C("manual", "vetor", 10, 2048), "1", "1", 0, excluida=True)
    e = cf.escolher(r)
    esc = e["escolha"]
    assert esc["latencia_dupla_s"] <= 20 and "manual_vetor_N10_L2048" not in (esc["regras"], esc["manual"])
    assert not (esc["regras"] == "regras_hibrido_N5_L512" and esc["manual"] == "manual_hibrido_N5_L2048")
    assert "manual_vetor_N10_L2048" in e["excluidas_por_latencia"]
    assert e["n_duplas_total"] == 180 and e["n_duplas_viaveis"] < 180
    # exatamente no teto ainda cabe (<=)
    r["manual_hibrido_N5_L2048"] = _resultado(C("manual", "hibrido", 5, 2048), "1", "1", 9.0)
    assert cf.escolher(r)["escolha"] == {**cf.escolher(r)["escolha"], "regras": "regras_hibrido_N5_L512",
                                         "manual": "manual_hibrido_N5_L2048"}


@teste
def sem_dupla_viavel_o_desenvolvimento_termina_sem_escolha():
    e = cf.escolher(_todas(lambda c: _resultado(c, "1/2", "1/2", 15.0)))     # 15 + 15 > 20 em toda dupla
    assert e["escolha"] is None and e["melhores"] == [] and e["n_duplas_viaveis"] == 0
    assert "NENHUMA dupla" in af.formatar_escolha(e)
    todas_excluidas = _todas(lambda c: _resultado(c, 0, 0, 0, excluida=True))
    assert cf.escolher(todas_excluidas)["escolha"] is None


@teste
def top_5_vem_ordenado_pela_mesma_chave_da_escolha():
    r = _todas(lambda c: _resultado(c, "1/2", "1/2", 1.0 + 0.01 * len(c.nome)))
    e = cf.escolher(r)
    assert len(e["melhores"]) == 5 and e["melhores"][0] == e["escolha"]
    lats = [d["latencia_dupla_s"] for d in e["melhores"]]
    assert lats == sorted(lats)


# --------------------------------------------------- ponta a ponta do dev ao fluxo ----
class Args(SimpleNamespace):
    sem_git = False
    aceitar_insumos = False


@contextlib.contextmanager
def _gate_liberado():
    """Isola cmd_dev da regra commitada e dos insumos reais: o que se testa aqui é o encanamento."""
    commit = {"disponivel": True, "commitada": True, "commit": "abc123", "data": "2026-11-08T10:00:00-03:00", "erro": None}
    with mock.patch.object(af, "estado_git_da_regra", lambda *_: commit), mock.patch.object(af, "conferir_insumos", lambda: []):
        yield


@teste
def dev_so_roda_com_a_regra_commitada_e_os_insumos_conferidos():
    with tempfile.TemporaryDirectory() as tmp:
        saidas = af.Saidas(Path(tmp))

        class Bomba:
            def __getattr__(self, _):
                raise AssertionError("carregou modelo antes de a regra estar commitada")

        nao_commitada = {"disponivel": True, "commitada": False, "commit": None, "data": None,
                         "erro": "a regra nunca foi commitada"}
        with mock.patch.object(af, "estado_git_da_regra", lambda *_: nao_commitada):
            estado, _, err = silencio(af.cmd_dev, saidas, Args(), Bomba())
        assert estado == 2 and "commit" in err and not list(Path(tmp).iterdir())
        # insumo divergente também barra
        commit = {**nao_commitada, "commitada": True, "commit": "x", "erro": None}
        diverge = [{"arquivo": "entrega2/comum.py", "esperado": "a", "obtido": "b", "ok": False}]
        with mock.patch.object(af, "estado_git_da_regra", lambda *_: commit), \
                mock.patch.object(af, "conferir_insumos", lambda: diverge):
            estado, _, err = silencio(af.cmd_dev, saidas, Args(), Bomba())
        assert estado == 2 and "entrega2/comum.py" in err and not list(Path(tmp).iterdir())
        # regra alterada barra tudo
        with mock.patch.object(af, "conferir_regra", lambda: (False, "0" * 64)):
            estado, _, err = silencio(af.cmd_dev, saidas, Args(), Bomba())
        assert estado == 2 and "regra mudou" in err


@teste
def dev_escolher_e_teste_de_ponta_a_ponta_com_modelos_falsos_e_o_teste_roda_uma_vez():
    with tempfile.TemporaryDirectory() as tmp:
        saidas = af.Saidas(Path(tmp))
        rec = recursos_falsos()
        with _gate_liberado():
            estado, _, _ = silencio(af.cmd_teste, saidas, rec)
            assert estado == 2 and not saidas.teste_json.exists()           # sem escolha, o teste não roda
            estado, _, err = silencio(af.cmd_escolher, saidas)
            assert estado == 2 and "dev" in err                              # sem dev, não escolhe
            estado, _, _ = silencio(af.cmd_dev, saidas, Args(), rec)
            assert estado == 0 and saidas.dev_json.exists() and saidas.dev_md.exists()
            dev = json.loads(saidas.dev_json.read_text(encoding="utf-8"))
            assert len(dev["configs"]) == 28 and dev["regra_sha256"] == cf.HASH_REGRA and dev["git_regra"]["commit"] == "abc123"
            assert dev["n_consultas"] == {"regras": 14, "manual": 15} and len(dev["execucoes"]) == 1
            estado, out, _ = silencio(af.cmd_dev, saidas, Args(), rec)       # já terminou: não refaz
            assert estado == 0 and "já existe" in out
            estado, out, _ = silencio(af.cmd_escolher, saidas)
            assert estado == 0 and saidas.config.exists()
            cfg_json = json.loads(saidas.config.read_text(encoding="utf-8"))
            assert cfg_json["regra_sha256"] == cf.HASH_REGRA and len(cfg_json["melhores"]) == 5
            assert cfg_json["resultados_dev_sha256"] == cf.sha256_arquivo(saidas.dev_json)
            assert set(cfg_json["configs"]) == {"regras", "manual"}
            estado, _, err = silencio(af.cmd_escolher, saidas)               # a escolha se faz uma vez
            assert estado == 2 and "já existe" in err
            cfgs = cf.carregar_config(saidas.config)
            assert cfgs["regras"].indice == "regras" and cfgs["manual"].indice == "manual"
            estado, out, _ = silencio(af.cmd_teste, saidas, rec)
            assert estado == 0 and saidas.teste_json.exists() and saidas.teste_md.exists(), out
            teste_json = json.loads(saidas.teste_json.read_text(encoding="utf-8"))
            assert teste_json["config_sha256"] == cf.sha256_arquivo(saidas.config)
            assert teste_json["indices"]["regras"]["metricas"]["n"] == 20 and teste_json["indices"]["manual"]["metricas"]["n"] == 20
            assert {"latencia_mediana_s", "latencia_max_s"} <= set(teste_json["indices"]["regras"])
            estado, _, err = silencio(af.cmd_teste, saidas, rec)             # o teste roda UMA vez
            assert estado == 2 and "já rodou" in err
            saidas.dev_md.unlink()                                           # relatório refeito a partir do JSON
            assert silencio(af.cmd_relatorio, saidas, "dev")[0] == 0 and saidas.dev_md.exists()
            assert silencio(af.cmd_relatorio, saidas, "dev")[0] == 2         # não sobrescreve


@teste
def teste_nao_roda_se_nao_houve_dupla_viavel():
    with tempfile.TemporaryDirectory() as tmp:
        saidas = af.Saidas(Path(tmp))
        dev = {"teto_s": 20.0, "configs": _todas(lambda c: _resultado(c, "1/2", "1/2", 15.0))}
        saidas.dev_json.write_text(json.dumps(dev), encoding="utf-8")
        saida = af.aplicar_escolha(dev, saidas, cf.HASH_REGRA)
        assert saida["escolha"] is None and saida["configs"] is None
        estado, _, err = silencio(af.cmd_teste, saidas, recursos_falsos())
        assert estado == 3 and "nenhuma dupla coube" in err and not saidas.teste_json.exists()
        try:
            fluxo.carregar_config(saidas.config)
        except ValueError:
            return
        raise AssertionError("o fluxo aceitou uma configuração sem escolha")


@teste
def desenvolvimento_incompleto_nao_gera_escolha():
    with tempfile.TemporaryDirectory() as tmp:
        saidas = af.Saidas(Path(tmp))
        parcial = _todas(lambda c: _resultado(c, "1/2", "1/2", 1.0))
        parcial.pop("manual_hibrido_N20_L2048")
        saidas.dev_json.write_text(json.dumps({"teto_s": 20.0, "configs": parcial}), encoding="utf-8")
        estado, _, err = silencio(af.cmd_escolher, saidas)
        assert estado == 2 and "manual_hibrido_N20_L2048" in err and not saidas.config.exists()


@teste
def grade_lista_as_28_e_mostra_o_que_ja_foi_medido():
    with tempfile.TemporaryDirectory() as tmp:
        saidas = af.Saidas(Path(tmp))
        estado, out, _ = silencio(af.cmd_grade, saidas)
        assert estado == 0 and out.count("a medir") == 28
        cfg = cf.Config("regras", "vetor")
        cf.salvar_checkpoint(saidas.checkpoints, cfg, {"config": cfg.to_dict(), "excluida": True,
                                                         "excluida_por": {"consulta": "q1", "tempo_s": 30, "teto_s": 20}})
        _, out, _ = silencio(af.cmd_grade, saidas)
        assert out.count("a medir") == 27 and "excluída por latência" in out


# ------------------------------------------------------------------- contexto ----
@teste
def contexto_leva_o_gobr_completo_sem_cortar_e_cita_secao_e_paginas():
    gobr = "version 1.0\n```\nbloco com crases\n```\n" + "linha de regra grande\n" * 1500      # ~30 mil caracteres
    regras = [{"posicao": 1, "regra_id": "exemplos/A.gobr", "titulo": "Regra A", "nota": 0.9,
               "texto": "Explicação da regra A.", "gobr": gobr},
              {"posicao": 2, "regra_id": "exemplos/B.gobr", "titulo": "", "nota": 0.5, "texto": "B.", "gobr": "x = 1"}]
    trechos = [{"posicao": 1, "folha": "6.2", "caminho": "Cap. 6 › 6.2 Filtros", "pagina_ini": 22, "pagina_fim": 23,
                "nota": 0.5, "texto": "Cap. 6 › 6.2 Filtros\nO gorules permite filtros."},
               {"posicao": 2, "folha": "6.0", "caminho": "Cap. 6", "pagina_ini": 20, "pagina_fim": 20, "nota": 0.4,
                "texto": "Texto sem a trilha."}]
    ctx = cf.montar_contexto(regras, trechos)
    assert len(gobr) > 25000 and gobr.rstrip() in ctx                                  # nada cortado
    assert "````" in ctx                                                               # cerca maior que as crases do GOBR
    assert "### Regra 1: Regra A (exemplos/A.gobr)" in ctx and "### Regra 2: exemplos/B.gobr" in ctx
    assert "## Regras de exemplo" in ctx and "## Manual do GOBR" in ctx
    assert "### Trecho 1: seção 6.2, p. 22-23\n" in ctx                               # trilha já está no texto: não repete
    assert "### Trecho 2: capítulo 6 (abertura), p. 20 (Cap. 6)" in ctx               # trilha ausente no texto: entra no título
    assert "gorules" in ctx                                                            # o trecho do manual conserva a grafia dele
    assert cf.montar_contexto([], []).count("(nenhum") == 2


@teste
def textos_do_fluxo_dizem_gobr_e_o_prompt_e_o_da_celula_8_adaptado():
    assert "GOBR" in cf.SYSTEM_PROMPT and "gorules" not in cf.SYSTEM_PROMPT.lower()
    for trecho in ("Responda em português, de forma objetiva.", "Use apenas informações presentes no contexto",
                   'diga "Não encontrei nos documentos"', "Não repita informações."):
        assert trecho in cf.SYSTEM_PROMPT, trecho
    assert cf.USER_PROMPT == "Contexto recuperado:\n---------------------\n{context_str}\n" \
        "---------------------\nPergunta: {query_str}"
    s, u = cf.montar_prompt("minha pergunta {x}", "contexto com {chaves} e {context_str}")
    assert "contexto com {chaves} e {context_str}" in u and u.endswith("Pergunta: minha pergunta {x}")


# ----------------------------------------------------------------- o fluxo ----
CFGS = {"regras": cf.Config("regras", "hibrido", 5, 512), "manual": cf.Config("manual", "vetor")}


@teste
def fluxo_devolve_3_regras_3_trechos_contexto_e_zero_token_de_llm():
    vistos = []
    rec = recursos_falsos(pares_vistos=vistos)
    fluxo.preparar(rec, CFGS)
    vistos.clear()
    res = fluxo.perguntar(rec, CFGS, "como configurar carteira inativa")
    assert len(res["regras"]) == 3 and len(res["manual"]) == 3 and res["llm"] is None
    assert vistos == [5]                                                # reranker só nas regras, 5 pares
    assert res["regras"][0]["gobr"].startswith("version 1.0") and res["manual"][0]["pagina_ini"] is not None
    assert res["tokens_contexto"] == len(res["contexto"].split())       # contador injetado
    assert set(res["tempos_s"]) == {"regras", "manual", "busca", "contexto"}
    assert res["dupla"] == {"regras": "regras_hibrido_N5_L512", "manual": "manual_vetor_sem-rerank"}
    texto = fluxo.formatar_saida(res)
    assert "tokens de LLM: 0 (sem --responder)" in texto and "=== Contexto ===" in texto and "teto 20 s" in texto
    assert "=== Contexto ===" not in fluxo.formatar_saida(res, so_fontes=True)
    json.dumps(res, ensure_ascii=False)                                  # serializável (Entrega 5 vai consumir)


@teste
def preparar_carrega_so_o_que_a_dupla_usa_uma_vez():
    contagem = {}
    rec = recursos_falsos(contagem=contagem)
    fluxo.preparar(rec, CFGS)
    fluxo.perguntar(rec, CFGS, "x")
    fluxo.perguntar(rec, CFGS, "y")
    assert contagem == {"embedding": 1, "indice_regras": 1, "indice_manual": 1, "reranker_512": 1, "tokenizer": 1}, contagem


class ClienteFalso:
    def __init__(self, texto="Use o bloco filtro.", uso=(1200, 80, None, 1280)):
        self.chamadas = []
        resp = SimpleNamespace(text=texto, usage_metadata=SimpleNamespace(
            prompt_token_count=uso[0], candidates_token_count=uso[1], thoughts_token_count=uso[2],
            total_token_count=uso[3]))
        cliente = self

        class Modelos:
            def generate_content(self, *, model, contents, config):
                cliente.chamadas.append({"model": model, "contents": contents, "config": config})
                return resp

        self.models = Modelos()


@teste
def responder_faz_uma_chamada_com_o_prompt_da_celula_8_e_le_os_tokens_da_api():
    cliente = ClienteFalso()
    r = cf.responder("pergunta?", "CONTEXTO", modelo="m-teste", cliente=cliente)
    assert len(cliente.chamadas) == 1
    ch = cliente.chamadas[0]
    assert ch["model"] == "m-teste" and ch["config"] == {"system_instruction": cf.SYSTEM_PROMPT}
    assert ch["contents"] == cf.USER_PROMPT.format(context_str="CONTEXTO", query_str="pergunta?")
    assert (r["tokens_entrada"], r["tokens_saida"], r["tokens_raciocinio"], r["tokens_total"]) == (1200, 80, None, 1280)
    assert r["texto"] == "Use o bloco filtro." and r["modelo"] == "m-teste"
    sem_uso = cf.responder("p", "c", cliente=ClienteFalso(texto=None, uso=(None, None, None, None)))
    assert sem_uso["texto"] == "" and sem_uso["tokens_total"] is None


@teste
def sem_chave_o_gemini_falha_explicito_sem_tocar_na_rede():
    with mock.patch.dict(os.environ, {}, clear=True):
        assert cf.chave_gemini() is None
        try:
            cf.criar_cliente_gemini()
        except RuntimeError as e:
            assert "GEMINI_API_KEY" in str(e)
        else:
            raise AssertionError("criou cliente sem chave")
    assert cf.chave_gemini({"GOOGLE_API_KEY": "k2"}) == "k2" and cf.chave_gemini({"GEMINI_API_KEY": "k1", "GOOGLE_API_KEY": "k2"}) == "k1"
    assert cf.MODELO_GEMINI_PADRAO == "gemini-3.8-flash"                 # o default da Entrega 1


def _config_tmp(tmp: str) -> Path:
    caminho = Path(tmp) / "config_escolhida.json"
    caminho.write_text(json.dumps({"escolha": {"regras": CFGS["regras"].nome, "manual": CFGS["manual"].nome},
                                   "configs": {i: c.to_dict() for i, c in CFGS.items()}}), encoding="utf-8")
    return caminho


@teste
def fluxo_main_avisa_e_sai_com_2_sem_config_sem_chave_ou_sem_dupla():
    with tempfile.TemporaryDirectory() as tmp:
        estado, _, err = silencio(fluxo.main, ["pergunta", "--config", str(Path(tmp) / "nao_existe.json")])
        assert estado == 2 and "avaliar_fluxo.py dev" in err
        sem_dupla = Path(tmp) / "sem.json"
        sem_dupla.write_text(json.dumps({"escolha": None, "configs": None}), encoding="utf-8")
        estado, _, err = silencio(fluxo.main, ["pergunta", "--config", str(sem_dupla)])
        assert estado == 2 and "nenhuma dupla coube" in err

        class Bomba:
            def __getattr__(self, _):
                raise AssertionError("carregou modelo antes de checar a chave")

        with mock.patch.dict(os.environ, {}, clear=True):
            estado, _, err = silencio(fluxo.main, ["pergunta", "--responder", "--config", str(_config_tmp(tmp))],
                                      recursos=Bomba())
        assert estado == 2 and "GEMINI_API_KEY" in err
        estado, _, err = silencio(fluxo.main, [])                           # sem pergunta e sem --sessao: erro de uso
        assert estado == 2 and "informe a pergunta" in err


@teste
def fluxo_main_uma_pergunta_com_e_sem_responder_e_em_json():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = str(_config_tmp(tmp))
        estado, out, _ = silencio(fluxo.main, ["como configurar carteira inativa", "--config", cfg], recursos=recursos_falsos())
        assert estado == 0 and "=== Contexto ===" in out and "=== Resposta" not in out
        cliente = ClienteFalso()
        estado, out, _ = silencio(fluxo.main, ["como configurar carteira inativa", "--responder", "--config", cfg],
                                  recursos=recursos_falsos(), cliente=cliente)
        assert estado == 0 and "=== Resposta (gemini-3.8-flash) ===" in out and "Tokens da API: entrada 1.200" in out
        assert len(cliente.chamadas) == 1 and "Contexto recuperado:" in cliente.chamadas[0]["contents"]
        estado, out, _ = silencio(fluxo.main, ["x", "--json", "--responder", "--config", cfg], recursos=recursos_falsos(),
                                  cliente=ClienteFalso())
        dados = json.loads(out[out.index("{"):])
        assert estado == 0 and dados["llm"]["tokens_total"] == 1280 and len(dados["regras"]) == 3 and dados["erro_llm"] is None


@teste
def falha_do_gemini_nao_perde_o_contexto_ja_mostrado():
    class Quebrado:
        class models:
            @staticmethod
            def generate_content(**_):
                raise ConnectionError("sem rede")

    with tempfile.TemporaryDirectory() as tmp:
        estado, out, err = silencio(fluxo.main, ["como configurar carteira inativa", "--responder", "--config",
                                                 str(_config_tmp(tmp))], recursos=recursos_falsos(), cliente=Quebrado())
        assert estado == 1 and "=== Contexto ===" in out and "ConnectionError" in err


@teste
def modo_sessao_carrega_uma_vez_e_responde_varias_perguntas():
    contagem = {}
    with tempfile.TemporaryDirectory() as tmp:
        respostas = iter(["como configurar carteira inativa", "quais as opcoes de pedido minimo", "sair"])
        with mock.patch.object(builtins, "input", lambda *_: next(respostas)):
            estado, out, _ = silencio(fluxo.main, ["--sessao", "--so-fontes", "--config", str(_config_tmp(tmp))],
                                      recursos=recursos_falsos(contagem=contagem))
    assert estado == 0 and out.count("Busca: regras") == 2, out
    assert contagem["embedding"] == contagem["indice_regras"] == contagem["reranker_512"] == 1


# ------------------------------------------------ índices reais, sem modelo ----
def _dim(persist: Path) -> int:
    d = json.loads((persist / "default__vector_store.json").read_text(encoding="utf-8"))
    return len(next(iter(d["embedding_dict"].values())))


@teste
def integracao_com_os_indices_e_conjuntos_reais_com_embedding_e_reranker_falsos():
    p2, p3 = cf.c2.caminho_indice(cf.VARIANTE_REGRAS), cf.c3.caminho_indice(cf.ESTRATEGIA_MANUAL)
    if not (p2 / "default__vector_store.json").exists() or not (p3 / "default__vector_store.json").exists():
        raise Pulado(f"índices ausentes ({p2}, {p3})")
    emb2, emb3 = EmbeddingFalso(dim=_dim(p2)), EmbeddingFalso(dim=_dim(p3))
    rec = cf.Recursos(fabrica_embedding=lambda: (emb2, "falso"), fabrica_reranker=lambda ml: (reranker_falso(), "falso"),
                      carregar_regras=lambda e: cf.c2.carregar_indice(cf.VARIANTE_REGRAS, emb2),
                      carregar_manual=lambda e: cf.c3.carregar_indice(cf.ESTRATEGIA_MANUAL, emb3),
                      fabrica_contador=lambda: (lambda t: len(t.split())))
    fluxo.preparar(rec, CFGS)
    for pergunta in ("como separo os clientes inadimplentes?", "quais tipos de bloco um arquivo GOBR pode ter?"):
        res = fluxo.perguntar(rec, CFGS, pergunta)
        assert len(res["regras"]) == 3 and len(res["manual"]) == 3
        for r in res["regras"]:
            assert r["regra_id"] and r["texto"].strip() and r["gobr"].strip() and isinstance(r["titulo"], str), r["regra_id"]
        for t in res["manual"]:
            assert t["folha"] and t["texto"].strip() and isinstance(t["pagina_ini"], int), t["folha"]
        assert res["contexto"].count("### Regra ") == 3 and res["contexto"].count("### Trecho ") == 3
    # os conjuntos reais, pelas funções das Entregas 2 e 3
    tam = {(i, c): len(cf.carregar_consultas(i, c)) for i in ("regras", "manual") for c in ("dev", "teste")}
    assert tam == cf.N_CONSULTAS, tam
    # uma configuração medida de verdade no conjunto de dev, sem modelo: as posições batem com avaliar_indice da Entrega 2
    cfg = cf.Config("regras", "vetor")
    r = af._medir_indice(rec, cfg, cf.carregar_consultas("regras", "dev"), avisar=nada, relogio=__import__("time").perf_counter,
                         repeticoes=1, teto=20.0)
    ref = cf.av2.avaliar_indice(rec.indice("regras"), cf.carregar_consultas("regras", "dev"))
    assert [p["posicao"] for p in r["por_consulta"]] == [l["posicao"] for l in ref]
    cfg = cf.Config("manual", "hibrido", 5, 2048)
    r = af._medir_indice(rec, cfg, cf.carregar_consultas("manual", "dev"), avisar=nada, relogio=__import__("time").perf_counter,
                         repeticoes=1, teto=20.0)
    assert len(r["por_consulta"]) == 15 and all(p["posicao"] is None or p["posicao"] >= 1 for p in r["por_consulta"])


# ------------------------------------------------------------------------ main ----
def main():
    falhas = passaram = puladas = 0
    for f in TESTES:
        try:
            f()
            passaram += 1
            print(f"ok     {f.__name__}")
        except Pulado as e:
            puladas += 1
            print(f"PULADO {f.__name__}: {e}")
        except AssertionError as e:
            falhas += 1
            print(f"FALHA  {f.__name__}: {e}")
            traceback.print_exc(limit=-3)
        except SystemExit as e:                                  # um teste não pode encerrar o processo
            falhas += 1
            print(f"SAIU   {f.__name__}: SystemExit({e.code})")
        except Exception as e:
            falhas += 1
            print(f"ERRO   {f.__name__}: {type(e).__name__}: {e}")
            traceback.print_exc(limit=-4)
    print(f"\n{passaram}/{len(TESTES)} testes passaram; {falhas} falharam; {puladas} pulados")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
