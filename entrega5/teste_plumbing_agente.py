# -*- coding: utf-8 -*-
"""Entrega 5 - testes de encanamento, SEM modelo e SEM rede: buscas falsas, Gemini falso, relógio falso.
Não medem qualidade. Rodam sobre os módulos reais das Entregas 1 e 4 (importados) e sobre a regra pré-registrada.

    python teste_plumbing_agente.py

Um teste "pulado" não passou nem falhou: não rodou porque falta um insumo (diz qual). Não escreve nada nas
pastas das entregas: tudo que grava vai para pastas temporárias. Não roda o roteador sobre as mensagens de teste.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import agente as ag
import avaliar_agente as aa
import comum_agente as ca
from comum_agente import cf

TESTES = []


class Pulado(Exception):
    pass


def teste(f):
    TESTES.append(f)
    return f


# ------------------------------------------------------------------ falsos ----
BOM = """version 1.0
time "campo":
  vendedores ativos
parametros "ativos":
  do time("campo")
  quando cliente ativo
  frequencia 14 dias
parametros "resto":
  do time("campo")
  frequencia 30 dias
"""
SEM_ACAO = 'version 1.0\nparametros "x":\n  do time("a")\n  quando cliente ativo\n'


class Relogio:
    """Relógio falso: só anda quando alguém manda."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def no(regra_id=None, folha=None, score=0.5):
    meta = {"regra_id": regra_id, "titulo": f"Regra {regra_id}", "gobr": BOM} if regra_id else \
        {"folha": folha, "caminho": "", "pagina_impressa_ini": 1, "pagina_impressa_fim": 2}
    return SimpleNamespace(node=SimpleNamespace(metadata=meta, text=f"texto de {regra_id or folha}"), score=score)


def saida_json(gobr, premissas=("p1",), perguntas=("q1", "q2")):
    return json.dumps({"gobr": gobr, "premissas": list(premissas), "perguntas": list(perguntas)})


def deps_falsas(saidas=(), log=None, sem_llm=False):
    """Dependências do grafo sem modelo: `saidas` é a fila de respostas do Gemini (texto ou exceção)."""
    log = log if log is not None else []
    fila = iter(saidas)

    def gerar(sistema, usuario):
        log.append(("gerar", usuario))
        x = next(fila)
        if isinstance(x, Exception):
            raise x
        return {"texto": x, "tokens_entrada": 10, "tokens_saida": 5, "tokens_raciocinio": 1, "tokens_total": 16,
                "segundos": 1.0}

    def responder(pergunta, contexto):
        log.append(("responder", pergunta))
        return {"texto": "resposta do manual", "tokens_entrada": 3, "tokens_saida": 2, "tokens_raciocinio": 0,
                "tokens_total": 5, "segundos": 0.5}

    def buscar_regras(consulta, excluir=()):
        log.append(("regras", consulta, tuple(excluir)))
        return [cf.descrever_regra(no(f"r{i}"), i) for i in (1, 2, 3)]

    def buscar_manual(consulta):
        log.append(("manual", consulta))
        return [cf.descrever_trecho(no(folha="7.1"), 1)]

    return ag.Dependencias(buscar_regras=buscar_regras, buscar_manual=buscar_manual,
                           gerar=None if sem_llm else gerar, responder=None if sem_llm else responder, contar=len,
                           dormir=lambda s: None)


def turno(mensagem, saidas=(), **k):
    log = []
    try:
        grafo = ag.construir_grafo(deps_falsas(saidas, log, **k))
    except ImportError as e:
        raise Pulado(f"langgraph não está instalado ({e})")
    return ag.executar(grafo, mensagem, excluir=["r9"]), log


class BuscadorFalso:
    """Buscador sem modelo para o avaliador: cada chamada custa `custo[id]` segundos no relógio falso."""

    def __init__(self, relogio, custo, quebra=()):
        self.relogio, self.custo, self.quebra = relogio, custo, set(quebra)
        self.cfg_manual = cf.Config("manual", "vetor", 5, 2048)
        self.recursos = SimpleNamespace(dispositivos={"embedding": "cpu"}, tempos_carga_s={},
                                        contador_tokens=lambda: len)
        self.chamadas = Counter()

    def preparar(self, cfg, manual=True):
        if cfg.id in self.quebra:
            raise OSError("sem rede para baixar o modelo")

    def preparar_manual(self):
        pass

    def ranking_manual(self, consulta, k=None):
        self.chamadas["M"] += 1
        self.relogio.t += self.custo["M"]
        return [no(folha="7.1"), no(folha="9.9")][:k]

    def ranking_regras(self, consulta, cfg, k=None):
        self.chamadas[cfg.id] += 1
        self.relogio.t += self.custo[cfg.id]
        ordem = ["certa", "x1", "x2", "x3"] if cfg.id != "R0" else ["x1", "x2", "x3", "certa"]
        return [no(r) for r in ordem][:k]

    def buscar_regras(self, consulta, cfg, k=ca.K, excluir=()):
        return ca.Buscador.buscar_regras(self, consulta, cfg, k, excluir)

    def buscar_manual(self, consulta, k=ca.K):
        return ca.Buscador.buscar_manual(self, consulta, k)


def consultas_falsas(n=3):
    return {"regras": [{"id": f"c{i}", "consulta": f"regra {i}", "relevantes": ["certa"]} for i in range(n)],
            "manual": [{"id": f"m{i}", "consulta": f"pergunta {i}", "gabarito": ["7.1"]} for i in range(n)]}


def silencio(f, *a, **k):
    """Roda f sem deixar a saída dela poluir o relatório dos testes."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return f(*a, **k)


def repo_git(pasta: Path):
    def git(*a):
        r = subprocess.run(["git", "-C", str(pasta), *a], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    try:
        git("init", "-q")
    except FileNotFoundError:
        raise Pulado("git não está instalado")
    git("config", "user.email", "t@t"), git("config", "user.name", "t"), git("config", "core.autocrlf", "false")
    return git


# ------------------------------------------------------------------ regra e constantes ----
@teste
def constantes_do_codigo_batem_com_o_bloco_da_regra():
    c = ca.ler_constantes_regra()
    lista = lambda nome: tuple(v.strip() for v in c[nome].split(","))
    for nome in ("K", "REPETICOES", "MAX_TENTATIVAS", "TIMEOUT_GEMINI_S", "RETENTATIVAS_INFRA", "DIVERGENCIA_CHAMADA_S",
                 "LACUNA_ENTRE_CHAMADAS_S", "CHARS_TEXTO_CURTO", "MAX_LENGTH_RERANKER_MENOR"):
        assert int(c[nome]) == getattr(ca, nome), nome
    for nome in ("TETO_BUSCA_S", "FATOR_CONFIRMACAO", "DIVERGENCIA_CHAMADA_FRACAO"):
        assert float(c[nome]) == getattr(ca, nome), nome
    assert c["MODELO_RERANKER_MENOR"] == ca.MODELO_RERANKER_MENOR
    for nome in ("ROTAS", "STATUS", "RECUSAS", "AVISOS", "GRADE_REGRAS", "DOMINIO"):
        assert lista(nome) == getattr(ca, nome), nome
    assert tuple(c[f"DESC_{i}"] for i in range(1, 6)) == ca.DESC
    assert c["PEDIDO_1"] == ca.PEDIDO_1 and c["INTERROGATIVA"] == ca.INTERROGATIVA
    assert len(c) == 26, f"o bloco da regra tem {len(c)} constantes"
    assert set(ca.CONSULTA_MANUAL) == set(ca.RECUSAS)


@teste
def regra_tem_o_sha256_registrado_no_codigo():
    ok, obtido = ca.conferir_regra()
    assert ok, f"sha256 da regra: {obtido}"


@teste
def insumos_das_entregas_anteriores_nao_mudaram():
    presentes = [i for i in ca.conferir_insumos() if i["obtido"] is not None]
    if len(presentes) < 19:
        faltam = 19 - len(presentes)
        assert all(i["ok"] for i in presentes), [i["arquivo"] for i in presentes if not i["ok"]]
        raise Pulado(f"{faltam} insumos da seção 13 não estão nesta máquina; os {len(presentes)} presentes conferem")
    assert all(i["ok"] for i in presentes), [i["arquivo"] for i in presentes if not i["ok"]]


@teste
def arquivos_prometidos_para_o_passo_5_existem():
    for nome in ("regra_agente.md", "consultas_roteamento_dev.json", "consultas_roteamento_teste.json",
                 "comum_agente.py", "agente.py", "avaliar_agente.py", "teste_plumbing_agente.py", "requirements.txt"):
        assert (ca.AQUI / nome).is_file(), nome


@teste
def nao_existe_atalho_para_a_trava():
    for arq in ("avaliar_agente.py", "agente.py"):
        fonte = (ca.AQUI / arq).read_text(encoding="utf-8")
        assert "environ" not in fonte and "sem-git" not in fonte, arq
    opcoes = [l for l in (ca.AQUI / "avaliar_agente.py").read_text(encoding="utf-8").splitlines() if "add_argument" in l]
    assert len(opcoes) == 2 and all("--" not in l for l in opcoes), opcoes


# ------------------------------------------------------------------ roteador ----
@teste
def roteador_reproduz_a_calibracao_da_regra_no_desenvolvimento():
    m = ca.medir_roteamento(ca.carregar_roteamento("dev"))
    assert (m["n"], m["acertos"], m["acertos_desfecho"]) == (44, 40, 42), m["erros"]
    assert {(e["id"], e["esperada"], e["obtida"]) for e in m["erros"]} == {
        ("rdev_06", "nenhum", "manual"), ("rdev_12", "regras", "ambos"), ("rdev_13", "regras", "ambos"),
        ("rdev_15", "manual", "ambos")}
    assert m["por_origem"]["entrega2"] == {"n": 14, "acertos": 14, "acertos_desfecho": 14}
    assert m["por_origem"]["entrega3"] == {"n": 15, "acertos": 15, "acertos_desfecho": 15}


@teste
def roteador_decide_pelas_quatro_caracteristicas():
    casos = {"Oi, tudo bem?": "nenhum",
             "Ativos a cada 14 dias e inativos a cada 30.": "regras",
             "Como separo os clientes inadimplentes?": "manual",
             "Clientes ativos a cada 14 dias. Qual a sintaxe do filtro?": "ambos",
             "Pode criar uma regra para visitar clientes novos?": "regras",        # pedido em forma de pergunta
             "Como faço uma regra para agendar clientes inativos?": "ambos",        # interrogativa: continua pergunta
             "CLIENTES ATIVOS: FREQUÊNCIA SEMANAL": "regras"}                       # maiúsculas e acento
    for msg, rota in casos.items():
        assert ca.rotear(msg)["rota"] == rota, (msg, ca.rotear(msg))
    r = ca.rotear("Pode criar uma regra para visitar clientes novos?")
    assert r["pedido"] and not r["pergunta"] and r["descricao"] and r["dominio"]
    assert [ca.desfecho(x) for x in ca.ROTAS] == ["gera", "responde", "gera", "recusa"]


@teste
def mensagens_de_teste_sao_15_e_o_roteador_nao_roda_sobre_elas():
    d = json.loads(ca.ARQ_ROTEAMENTO["teste"].read_text(encoding="utf-8"))["consultas"]
    assert len(d) == ca.N_ROTEAMENTO["teste"] == 15 and len({c["id"] for c in d}) == 15
    assert all(c["rota_esperada"] in ca.ROTAS for c in d)


# ------------------------------------------------------------------ validador ----
@teste
def validador_aceita_regra_boa_e_recusa_cada_caso_da_regra():
    v = ca.validar(BOM)
    assert v["aceita"] and v["recusas"] == [], v["recusas"]
    assert v["resumo"] == {"blocos_parametros": 2, "tipos_de_acao": ["frequencia"], "frequencias": [14, 30]}
    codigos = lambda g: [r["codigo"] for r in ca.validar(g)["recusas"]]
    assert codigos("") == ["saida_invalida"] and codigos(None) == ["saida_invalida"]
    assert "linha_nao_reconhecida" in codigos("frequencia 7 dias\n" + BOM)
    assert "sem_bloco_parametros" in codigos('version 1.0\ntime "campo":\n  vendedores ativos\n')
    assert "bloco_sem_fonte" in codigos('version 1.0\nparametros "x":\n  frequencia 7 dias\n')
    assert codigos(SEM_ACAO) == ["bloco_sem_acao"]
    assert "nao_agendar_com_frequencia" in codigos(BOM.replace("  frequencia 30 dias", "  nao agendar\n  frequencia 30 dias"))
    r = ca.validar(BOM.replace("  frequencia 14 dias", "  frequencia 14 dias\n  normal na segunda"))["recusas"]
    assert [(x["codigo"], x["linha"]) for x in r] == [("linha_de_corpo_nao_classificada", 8)], r
    r = ca.validar(BOM + 'parametros "nome com "aspas" dentro":\n  do time("campo")\n  frequencia 7 dias\n')["recusas"]
    assert ("cabecalho_parametros_invalido", 11) in [(x["codigo"], x["linha"]) for x in r], r


@teste
def validador_avisa_sem_recusar():
    v = ca.validar(BOM.replace("version 1.0\n", "") + 'carteira livre "c":\n  clientes ativos\n')
    assert v["aceita"], v["recusas"]
    assert {"sem_version", "cabecalho_nao_reconhecido"} <= {a["codigo"] for a in v["avisos"]}, v["avisos"]
    assert all(a["codigo"] in ca.AVISOS for a in v["avisos"])


@teste
def validador_no_corpus_reproduz_a_calibracao_da_regra():
    arqs = sorted((ca.RAIZ / "referencias").glob("*.gobr")) + sorted((ca.RAIZ / "exemplos").glob("*.gobr"))
    if len(arqs) != 249:
        raise Pulado(f"o corpus tem {len(arqs)} arquivos nesta máquina, não 249")
    recusados, avisos_arq, achados = {}, Counter(), Counter()
    for p in arqs:
        v = ca.validar(p.read_text(encoding="utf-8", errors="replace"))
        if not v["aceita"]:
            recusados[p.name] = sorted({r["codigo"] for r in v["recusas"]})
        for cod in {a["codigo"] for a in v["avisos"]}:
            avisos_arq[cod] += 1
        achados.update(a["codigo"] for a in v["avisos"])
    assert recusados == {"regra_032.gobr": ["bloco_sem_acao"], "regra_080.gobr": ["cabecalho_parametros_invalido"],
                         "regra_236.gobr": ["linha_de_corpo_nao_classificada"]}, recusados
    assert avisos_arq["sem_version"] == 1 and avisos_arq["cabecalho_nao_reconhecido"] == 12, avisos_arq
    assert (achados["sem_regra_final"], achados["fonte_indefinida"], achados["nome_diverge_do_codigo"],
            achados["bloco_inalcancavel"]) == (215, 46, 35, 1), achados


@teste
def consulta_ao_manual_vem_das_duas_primeiras_recusas():
    r = [{"codigo": "bloco_sem_acao", "linha": 2}, {"codigo": "linha_de_corpo_nao_classificada", "linha": 3},
         {"codigo": "bloco_sem_fonte", "linha": None}]
    q = ca.consulta_manual_das_recusas(r, "a\nb\n  normal na segunda\n")
    assert q == "Que ações posso usar dentro de um bloco parametros? Como escrevo em GOBR a linha: normal na segunda?", q
    assert ca.consulta_manual_das_recusas([{"codigo": "saida_invalida", "linha": None}]) is None
    assert ca.consulta_manual_das_recusas([r[0], r[0]]) == "Que ações posso usar dentro de um bloco parametros?"


# ------------------------------------------------------------------ Gemini (sem rede) ----
@teste
def saida_do_gemini_so_vale_se_for_o_json_esperado():
    s = ca.interpretar_saida(saida_json(BOM, premissas=[" p ", ""], perguntas=[]))
    assert s == {"gobr": BOM, "premissas": ["p"], "perguntas": []}, s
    for ruim in ("não é json", "[]", '{"gobr": ""}', '{"gobr": 3}', '{"premissas": []}', None):
        assert ca.interpretar_saida(ruim) is None, ruim


@teste
def prompt_de_correcao_leva_o_gobr_anterior_e_as_recusas():
    _, u1 = ca.montar_prompt_gerar("ativos a cada 14 dias", "CONTEXTO")
    assert "CONTEXTO" in u1 and "ativos a cada 14 dias" in u1 and "recusada" not in u1
    _, u2 = ca.montar_prompt_gerar("m", "CONTEXTO", anterior=SEM_ACAO, recusas=ca.validar(SEM_ACAO)["recusas"])
    assert SEM_ACAO in u2 and "[bloco_sem_acao]" in u2 and u2.startswith(u1.replace("ativos a cada 14 dias", "m"))


@teste
def chave_vem_do_ambiente_e_nunca_aparece_em_mensagem():
    assert ca.chave_gemini({"GOOGLE_API_KEY": "g", "GEMINI_API_KEY": "x"}) == "g"
    assert ca.chave_gemini({"GEMINI_API_KEY": "x"}) == "x" and ca.chave_gemini({}) is None
    try:
        ca.criar_cliente_gemini({})
        raise AssertionError("devia falhar sem chave")
    except RuntimeError as e:
        assert "GOOGLE_API_KEY" in str(e)
    with mock.patch.dict("os.environ", {"GOOGLE_API_KEY": "SEGREDO-123"}):
        def falha():
            raise RuntimeError("401 API key not valid: SEGREDO-123")
        avisos = []
        res, erro = ca.com_retentativa_infra(falha, dormir=lambda s: None, avisar=avisos.append)
    assert res is None and "SEGREDO-123" not in erro + "".join(avisos) and "defina a variável" in erro
    assert len(avisos) == ca.RETENTATIVAS_INFRA + 1


@teste
def chamada_ao_gemini_usa_os_parametros_da_entrega_1():
    visto = {}

    class Modelos:
        def generate_content(self, **k):
            visto.update(k)
            return SimpleNamespace(text="{}", usage_metadata=SimpleNamespace(
                prompt_token_count=7, candidates_token_count=3, thoughts_token_count=None, total_token_count=10))

    r = ca.gerar_json("S", "U", cliente=SimpleNamespace(models=Modelos()), relogio=Relogio())
    c = visto["config"]
    assert (c["temperature"], c["response_mime_type"], c["max_output_tokens"]) == (0.2, "application/json", 32768)
    assert c["response_schema"] == ca.SCHEMA_GERACAO and c["system_instruction"] == "S" and visto["contents"] == "U"
    assert visto["model"] == ca.MODELO_GEMINI_PADRAO == cf.MODELO_GEMINI_PADRAO
    assert (r["tokens_entrada"], r["tokens_saida"], r["tokens_raciocinio"], r["tokens_total"]) == (7, 3, None, 10)


# ------------------------------------------------------------------ grade, medição e escolha ----
@teste
def grade_tem_r0_a_r4_como_a_regra_diz():
    g = ca.grade_regras()
    assert tuple(g) == ca.GRADE_REGRAS
    assert [(c.n, c.max_length, c.chars) for c in g.values()] == [(0, 0, 0), (5, 2048, 1000), (10, 2048, 1000),
                                                                (10, 512, 0), (20, 512, 0)]
    assert g["R1"].modelo == "BAAI/bge-reranker-v2-m3" and g["R3"].modelo == ca.MODELO_RERANKER_MENOR
    assert all(c.cfg_e4().hibrido and c.cfg_e4().indice == "regras" for c in g.values())
    assert ca.carregar_config_agente.__defaults__[0] == ca.ARQ_CONFIG


@teste
def texto_curto_corta_em_1000_caracteres_so_o_que_vai_ao_reranker():
    vistos = []
    base = cf.c2.Reranker(lambda pares: [vistos.append(p) or 1.0 for p in pares])
    notas = ca.reranker_texto_curto(base).pontuar("consulta", ["a" * 3000, "b" * 10])
    assert notas == [1.0, 1.0] and [len(t) for _, t in vistos] == [1000, 10] and vistos[0][0] == "consulta"


@teste
def buscador_esconde_a_regra_de_referencia_e_corta_em_k():
    falso = SimpleNamespace(ranking_regras=lambda consulta, cfg, k=None: [no(r) for r in "abcde"][:k])
    f = lambda excluir: [r["regra_id"] for r in ca.Buscador.buscar_regras(falso, "q", ca.grade_regras()["R0"],
                                                                         excluir=excluir)]
    assert f(()) == ["a", "b", "c"] and f(("b",)) == ["a", "c", "d"] and f(("z",)) == ["a", "b", "c"]
    assert [r["posicao"] for r in ca.Buscador.buscar_regras(falso, "q", ca.grade_regras()["R0"], excluir=("a",))] == [1, 2, 3]


def _medir(tempos_por_consulta, limite=10.0):
    rel, fila = Relogio(), iter([t for ts in tempos_por_consulta for t in ts])

    def chamar(texto):
        rel.t += next(fila)
        return [no("certa")]

    cons = consultas_falsas(len(tempos_por_consulta))["regras"]
    return ca.medir_regras(ca.grade_regras()["R1"], cons, chamar, cf.posicao_regras, limite=limite, relogio=rel)


@teste
def medicao_vale_a_menor_repeticao_e_a_latencia_e_a_maior_entre_as_consultas():
    r = _medir([[3.0, 2.0], [5.0, 6.0]])
    assert not r["excluida"] and r["latencia_s"] == 5.0 and [p["min_s"] for p in r["por_consulta"]] == [2.0, 5.0]
    assert r["hit3_frac"] == "1" and r["metricas"]["hit@3"] == 1.0


@teste
def poda_com_confirmacao_segue_a_regra():
    assert _medir([[12.6]])["excluida_por"]["tempos_s"] == [12.6]              # acima de 1,25 x limite: na hora
    r = _medir([[11.0, 9.0], [1.0, 1.0]])                                      # entre o limite e 1,25x: confirma
    assert not r["excluida"] and r["latencia_s"] == 9.0
    r = _medir([[11.0, 10.5]])                                                 # a repetição também passou
    assert r["excluida"] and r["excluida_por"]["tempos_s"] == [11.0, 10.5] and r["consultas_medidas"] == 0
    assert not _medir([[9.0, 30.0]])["excluida"]                               # só a 1ª medição abre a poda


@teste
def divergencia_de_relogio_e_lacuna_sao_detectadas():
    ok = [{"perf_s": 5.0, "parede_ini": 0.0, "parede_fim": 5.1}, {"perf_s": 30.0, "parede_ini": 60.0, "parede_fim": 92.9}]
    assert ca.divergencias(ok) == []
    assert len(ca.divergencias([{"perf_s": 5.0, "parede_ini": 0.0, "parede_fim": 7.5}])) == 1      # 2,5 s > 2 s
    assert len(ca.divergencias([{"perf_s": 30.0, "parede_ini": 0.0, "parede_fim": 33.5}])) == 1    # 3,5 s > 10 %
    assert "lacuna" in ca.divergencias([ok[0], {"perf_s": 1.0, "parede_ini": 70.0, "parede_fim": 71.0}])[0]
    rel, par = Relogio(), Relogio()
    medida = ca.ChamadaMedida(lambda t: setattr(rel, "t", rel.t + 2) or setattr(par, "t", par.t + 9), rel, par)
    medida("q")
    assert medida.registros == [{"perf_s": 2.0, "parede_ini": 0.0, "parede_fim": 9.0}] and ca.divergencias(medida.registros)


def _m(hit, mrr, lat, excluida=False):
    return {"excluida": True} if excluida else {"excluida": False, "hit3_frac": hit, "mrr_frac": mrr, "latencia_s": lat}


@teste
def escolha_so_troca_r0_por_hit3_estritamente_maior():
    base = {"R0": _m("10/14", "3/5", 0.6)}
    e = ca.escolher_regras({**base, "R1": _m("10/14", "9/10", 5.0), "R2": _m("9/14", "1", 5.0)}, 9.8)
    assert e["escolhida"] == "R0" and e["situacao"]["R1"] == "não supera R0 em hit@3"       # MRR sozinho não decide
    e = ca.escolher_regras({**base, "R1": _m("11/14", "1/2", 9.0), "R3": _m("12/14", "1/2", 9.5)}, 9.8)
    assert e["escolhida"] == "R3" and e["decidido_por"] == "maior hit@3"
    e = ca.escolher_regras({**base, "R1": _m("11/14", "1/2", 9.0), "R3": _m("11/14", "3/5", 9.5)}, 9.8)
    assert e["escolhida"] == "R3" and e["decidido_por"] == "maior MRR"
    e = ca.escolher_regras({**base, "R2": _m("11/14", "1/2", 9.0), "R4": _m("11/14", "1/2", 8.0)}, 9.8)
    assert e["escolhida"] == "R4" and e["decidido_por"] == "menor latência"
    e = ca.escolher_regras({**base, "R2": _m("11/14", "1/2", 8.0), "R4": _m("11/14", "1/2", 8.0)}, 9.8)
    assert e["escolhida"] == "R2" and e["decidido_por"] == "mais simples"


@teste
def escolha_respeita_o_teto_com_a_latencia_do_manual_medida():
    medidas = {"R0": _m("10/14", "3/5", 0.6), "R1": _m("13/14", "1", 10.3), "R2": _m("", "", 0, excluida=True),
               "R3": {"indisponivel": True, "motivo": "sem rede"}}
    e = ca.escolher_regras(medidas, 9.8)                                       # 10,3 + 9,8 > 20
    assert e["escolhida"] == "R0" and e["situacao"]["R1"].startswith("inviável")
    assert e["situacao"]["R2"] == "excluída por latência" and e["situacao"]["R3"].startswith("indisponível")
    assert e["situacao"]["R4"] == "não medida"
    assert ca.escolher_regras(medidas, 9.7)["escolhida"] == "R1"               # 10,3 + 9,7 = 20: cabe
    for ruim in ({}, {"R0": _m("", "", 0, excluida=True)}):
        try:
            ca.escolher_regras(ruim, 9.8)
            raise AssertionError("sem R0 a escolha devia parar")
        except ValueError:
            pass


# ------------------------------------------------------------------ trava do git ----
@teste
def trava_do_desenvolvimento_exige_regra_e_mensagens_commitadas():
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp)
        git = repo_git(pasta)
        regra, msgs = pasta / "regra_agente.md", [pasta / "dev.json", pasta / "teste.json"]
        shutil.copy(ca.ARQ_REGRA, regra)
        for m in msgs:
            m.write_text("{}", encoding="utf-8")
        assert len(ca.trava_dev(regra, msgs)) == 3                                           # nada commitado
        git("add", "."), git("commit", "-qm", "regra")
        assert ca.trava_dev(regra, msgs) == []
        regra.write_bytes(regra.read_bytes().replace(b"\n", b"\r\n"))                        # CRLF: mesmo conteúdo
        assert ca.conferir_regra(regra)[0]
        regra.write_text(regra.read_text(encoding="utf-8") + "x", encoding="utf-8")
        p = ca.trava_dev(regra, msgs)
        assert len(p) == 2 and "mudanças não commitadas" in p[0] and "sha256" in p[1], p
        msgs[0].unlink()
        assert any("não existe" in x for x in ca.trava_dev(regra, msgs))


@teste
def trava_do_teste_exige_o_commit_da_escolha_depois_do_da_regra_e_roda_uma_vez():
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp)
        git = repo_git(pasta)
        regra, cfg, dev, saida = (pasta / n for n in ("regra_agente.md", "config.json", "dev.json", "teste.json"))
        trava = lambda: ca.trava_teste(regra=regra, mensagens=[], config=cfg, dev=dev, saidas=[saida])
        shutil.copy(ca.ARQ_REGRA, regra)
        cfg.write_text("{}", encoding="utf-8"), dev.write_text("{}", encoding="utf-8")
        git("add", "."), git("commit", "-qm", "tudo junto")
        assert len(trava()) == 2 and all("não é posterior" in x for x in trava()), trava()   # mesmo commit: não vale
        cfg.write_text("{ }", encoding="utf-8"), dev.write_text("{ }", encoding="utf-8")
        assert len(trava()) == 2 and all("não commitadas" in x for x in trava())             # escolha sem commit
        git("add", "."), git("commit", "-qm", "escolha")
        assert trava() == []
        saida.write_text("{}", encoding="utf-8")
        assert trava() == ["teste.json já existe: o teste roda uma vez só"]
    with tempfile.TemporaryDirectory() as tmp:                                               # fora de um repositório
        s = aa.Saidas(base=Path(tmp))
        assert silencio(aa.cmd_teste, s, buscador=object(), cliente=object()) == 2 and list(Path(tmp).iterdir()) == []


# ------------------------------------------------------------------ grafo ----
@teste
def grafo_aceita_na_primeira_e_devolve_os_campos_da_regra():
    res, log = turno("Ativos a cada 14 dias.", [saida_json(BOM)])
    assert (res["rota"], res["status"], len(res["tentativas"])) == ("regras", "aceita", 1)
    assert [l[0] for l in log] == ["regras", "gerar"] and log[0][2] == ("r9",)             # regra escondida
    assert res["gobr"] == BOM and res["tokens"] == {"entrada": 10, "saida": 5, "raciocinio": 1, "total": 16, "chamadas": 1}
    assert [p["origem"] for p in res["pontos_de_atencao"]] == ["premissa", "pergunta", "pergunta"]
    assert set(res) == set(ag.CAMPOS_SAIDA) and json.loads(json.dumps(res)) == res
    assert len(res["regras"]) == 3 and res["manual"] == [] and "## Regras de exemplo" in res["contexto"]
    assert res["status"] in ca.STATUS and "Validação: aceita" in ag.formatar_saida(res)


@teste
def grafo_corrige_com_uma_consulta_ao_manual_montada_das_recusas():
    res, log = turno("Ativos a cada 14 dias.", [saida_json(SEM_ACAO), saida_json(BOM)])
    assert (res["status"], len(res["tentativas"])) == ("aceita", 2)
    assert [l[0] for l in log] == ["regras", "gerar", "manual", "gerar"]
    assert log[2][1] == "Que ações posso usar dentro de um bloco parametros?" == res["consulta_manual"]
    assert "[bloco_sem_acao]" in log[3][1] and SEM_ACAO in log[3][1] and "## Manual do GOBR" in res["contexto"]
    t1, t2 = res["tentativas"]
    assert (t1["aceita"], t2["aceita"], t1["consultou_manual"], t2["consultou_manual"]) == (False, True, False, True)
    assert res["tokens"]["chamadas"] == 2 and res["tempos_s"]["busca"] >= 0


@teste
def grafo_para_em_max_tentativas_e_marca_nao_validado():
    res, log = turno("Ativos a cada 14 dias.", [saida_json(SEM_ACAO), "isto não é json", saida_json(BOM)])
    assert (res["status"], len(res["tentativas"])) == ("invalida", ca.MAX_TENTATIVAS)
    assert [l[0] for l in log].count("gerar") == ca.MAX_TENTATIVAS
    assert [r["codigo"] for r in res["tentativas"][-1]["recusas"]] == ["saida_invalida"]
    texto = ag.formatar_saida(res)
    assert texto.count(ca.MARCA_NAO_VALIDADO) == 2 and "[saida_invalida]" in texto


@teste
def grafo_saida_invalida_nao_consulta_o_manual_na_retentativa():
    res, log = turno("Ativos a cada 14 dias.", ["lixo", saida_json(BOM)])
    assert res["status"] == "aceita" and [l[0] for l in log] == ["regras", "gerar", "gerar"]


@teste
def grafo_rota_manual_responde_sem_gerar_nem_validar():
    res, log = turno("Como separo os clientes inadimplentes?")
    assert (res["rota"], res["status"], res["tentativas"]) == ("manual", "resposta_linguagem", [])
    assert [l[0] for l in log] == ["manual", "responder"] and res["resposta"] == "resposta do manual"
    assert res["regras"] == [] and res["tokens"]["chamadas"] == 1


@teste
def grafo_rota_ambos_busca_nos_dois_e_nao_repete_o_manual_na_retentativa():
    res, log = turno("Ativos a cada 14 dias. Como escrevo isso em GOBR?", [saida_json(SEM_ACAO), saida_json(BOM)])
    assert res["rota"] == "ambos" and [l[0] for l in log] == ["regras", "manual", "gerar", "gerar"]
    assert log[1][1] == "Ativos a cada 14 dias. Como escrevo isso em GOBR?" and res["status"] == "aceita"


@teste
def grafo_fora_do_escopo_gasta_zero_token_e_nao_busca():
    res, log = turno("Oi, tudo bem?")
    assert (res["rota"], res["status"], log) == ("nenhum", "fora_do_escopo", [])
    assert res["tokens"]["total"] == 0 and res["resposta"].startswith("Não encontrei nos documentos")


@teste
def grafo_erro_de_infraestrutura_nao_conta_como_tentativa():
    erro = RuntimeError("503 UNAVAILABLE")
    res, log = turno("Ativos a cada 14 dias.", [erro, erro, erro])
    assert (res["status"], res["tentativas"]) == ("erro_infra", []) and "503" in res["erro"]
    assert [l[0] for l in log].count("gerar") == ca.RETENTATIVAS_INFRA + 1
    res, log = turno("Ativos a cada 14 dias.", [erro, saida_json(BOM)])                     # a 2ª chamada passa
    assert (res["status"], len(res["tentativas"])) == ("aceita", 1)


@teste
def grafo_sem_llm_para_no_contexto():
    res, log = turno("Ativos a cada 14 dias.", sem_llm=True)
    assert res["status"] is None and [l[0] for l in log] == ["regras"] and res["tokens"]["total"] == 0
    assert "=== Contexto ===" in ag.formatar_saida(res)


# ------------------------------------------------------------------ avaliador ----
CUSTO = {"M": 9.0, "R0": 0.5, "R1": 4.0, "R2": 12.0, "R3": 2.0, "R4": 3.0}


def _medir_busca(tmp, quebra=(), custo=CUSTO, parede=None):
    rel = Relogio()
    b = BuscadorFalso(rel, custo, quebra)
    s = aa.Saidas(base=Path(tmp))
    return s, b, aa.medir_busca(b, s, consultas_falsas(), avisar=lambda m: None, relogio=rel, parede=parede or rel)


@teste
def medicao_da_busca_mede_m_e_a_grade_com_checkpoint_exclusivo():
    with tempfile.TemporaryDirectory() as tmp:
        s, b, med = _medir_busca(tmp, quebra=("R4",))
        assert list(med) == ["M", "R0", "R1", "R2", "R3", "R4"] and med["M"]["latencia_s"] == 9.0
        assert med["R2"]["excluida"] and med["R2"]["excluida_por"]["limite_s"] == 11.0       # 12 s > 20 - 9
        assert med["R4"]["indisponivel"] and "sem rede" in med["R4"]["motivo"]
        assert (med["R0"]["hit3_frac"], med["R1"]["hit3_frac"]) == ("0", "1")
        assert b.chamadas == {"M": 6, "R0": 6, "R1": 6, "R2": 2, "R3": 6}                    # 3 consultas x 2 repetições
        assert sorted(p.name for p in s.checkpoints.iterdir()) == [f"busca_{n}.json" for n in ("M", "R0", "R1", "R2", "R3", "R4")]
        antes = dict(b.chamadas)
        s2, b2, med2 = _medir_busca(tmp)                                                     # retomada: nada é remedido
        assert med2 == med and not b2.chamadas and antes == b.chamadas
        e = aa.aplicar_escolha(s, med, {"condicoes": {"confirmado": True}})
        assert e["escolhida"] == "R3" and ca.carregar_config_agente(s.config) == ca.grade_regras()["R3"]
        assert e["situacao"]["R1"] == "supera R0" and e["decidido_por"] == "menor latência"
        try:
            aa.aplicar_escolha(s, med)
            raise AssertionError("config_agente.json não pode ser regravado")
        except FileExistsError:
            pass


@teste
def divergencia_de_relogio_arquiva_a_execucao_inteira():
    with tempfile.TemporaryDirectory() as tmp:
        parede = Relogio()
        rel = Relogio()
        b = BuscadorFalso(rel, CUSTO)
        original = b.ranking_regras

        def lento(consulta, cfg, k=None):                # o relógio de parede anda 5 s a mais que o de desempenho
            parede.t += CUSTO[cfg.id] + (5.0 if cfg.id == "R1" else 0.0)
            return original(consulta, cfg, k)

        b.ranking_regras = lento
        b.ranking_manual = (lambda f: lambda c, k=None: (setattr(parede, "t", parede.t + CUSTO["M"]), f(c, k))[1])(b.ranking_manual)
        s = aa.Saidas(base=Path(tmp))
        med = aa.medir_busca(b, s, consultas_falsas(), avisar=lambda m: None, relogio=rel, parede=parede)
        assert med["R1"]["divergencias"] and not med["R0"]["divergencias"] and not med["M"]["divergencias"]
        avisos = []
        assert aa.arquivar_se_divergiu(s, med, avisos.append) and not s.checkpoints.exists() and s.arquivada.is_dir()
        assert not s.config.exists() and "arquivada" in avisos[0]


def _itens_de_geracao(tmp, detalhar=True):
    filas = {"regra 0": [saida_json(BOM)], "regra 1": [saida_json(SEM_ACAO), saida_json(BOM)],
             "regra 2": [saida_json(SEM_ACAO), "lixo"], "regra 3": [RuntimeError("503")] * 3}
    avisos = []

    class Grafo:                                         # um grafo novo por consulta, com a fila dela
        def invoke(self, estado, config):
            return ag.construir_grafo(deps_falsas(filas[estado["mensagem"]])).invoke(estado, config)

    try:
        ag.construir_grafo(deps_falsas())
    except ImportError as e:
        raise Pulado(f"langgraph não está instalado ({e})")
    itens = aa.rodar_geracao(Grafo(), consultas_falsas(4)["regras"], Path(tmp), avisar=avisos.append, detalhar=detalhar)
    return itens, avisos


@teste
def geracao_calcula_g1_a_g9_com_o_denominador_da_regra():
    with tempfile.TemporaryDirectory() as tmp:
        itens, avisos = _itens_de_geracao(tmp)
        g = aa.metricas_geracao(itens)
        assert (g["n"], g["erro_infra"], g["denominador"]) == (4, 1, 3)
        assert (g["G1_aceita_na_1a"], g["G2_aceita_ao_fim"], g["G3_tentativas"]) == (1, 2, {"1": 1, "2": 2})
        assert g["G4_retentativas_com_manual"] == 2 and g["G5_tokens"]["total"]["total"] == 16 * 5
        assert g["G9_pontos_de_atencao"]["respostas_com_gobr"] == 2 and g["G9_pontos_de_atencao"]["perguntas"]["mediana"] == 2
        assert g["status"] == {"aceita": 2, "erro_infra": 1, "invalida": 1}
        assert "c1 -> aceita em 2 tentativa(s)" in avisos[1]
        assert len(list(Path(tmp).glob("geracao_*.json"))) == 4
        de_novo, _ = _itens_de_geracao(tmp)                                                  # retomada lê o checkpoint
        assert de_novo == itens
        res = {"gerado_em": "x", "regra_sha256": "a" * 64, "git": {"commit": "b" * 40}, "escolhida": "R0",
               "config": ca.grade_regras()["R0"].to_dict(), "roteamento": ca.medir_roteamento(ca.carregar_roteamento("dev")),
               "geracao": g}
        md = aa.formatar_md(res, "Título")
        assert "G1 aceita na 1ª tentativa: 1 de 3" in md and "Rota: 40 de 44" in md


@teste
def no_teste_a_geracao_so_imprime_o_progresso():
    with tempfile.TemporaryDirectory() as tmp:
        _, avisos = _itens_de_geracao(tmp, detalhar=False)
        assert avisos == [f"  geração {i} de 4" for i in (1, 2, 3, 4)], avisos


@teste
def dev_de_ponta_a_ponta_com_falsos_grava_uma_vez_e_nao_regrava():
    try:
        ag.construir_grafo(deps_falsas())
    except ImportError as e:
        raise Pulado(f"langgraph não está instalado ({e})")
    with tempfile.TemporaryDirectory() as tmp:
        rel = Relogio()
        b = BuscadorFalso(rel, CUSTO)
        s = aa.Saidas(base=Path(tmp))
        cliente = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **k: SimpleNamespace(
            text=saida_json(BOM), usage_metadata=None)))
        consultas = consultas_falsas(14)
        original = aa.medir_busca
        with mock.patch.object(aa, "medir_busca", lambda bb, ss, cc: original(bb, ss, cc, relogio=rel, parede=rel,
                                                                            avisar=lambda m: None)), \
                mock.patch.object(aa, "conferir_tudo", lambda *a, **k: []), \
                mock.patch.object(aa, "_consultas", lambda conjunto: consultas), \
                mock.patch.object(ca, "imprimir", lambda *a: None):
            assert silencio(aa.cmd_dev, s, b, cliente, entrada=lambda p: "não") == 2 and not s.checkpoints.exists()
            assert silencio(aa.cmd_dev, s, b, cliente, entrada=lambda p: "sim") == 0
            dev = json.loads(s.dev_json.read_text(encoding="utf-8"))
            assert dev["escolhida"] == "R3" and dev["geracao"]["G2_aceita_ao_fim"] == 14 and s.dev_md.is_file()
            assert dev["roteamento"]["n"] == 44 and len(dev["itens_geracao"]) == 14
            marcas = {p.name: p.stat().st_mtime_ns for p in Path(tmp).rglob("*") if p.is_file()}
            assert silencio(aa.cmd_dev, s, b, cliente, entrada=lambda p: "sim") == 0          # 2ª vez: nada regravado
            assert marcas == {p.name: p.stat().st_mtime_ns for p in Path(tmp).rglob("*") if p.is_file()}

def main():
    cf.configurar_saida()
    passaram = falhas = puladas = 0
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
