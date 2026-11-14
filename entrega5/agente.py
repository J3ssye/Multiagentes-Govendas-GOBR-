# -*- coding: utf-8 -*-
"""Entrega 5 - fluxo agêntico que gera uma parametrização em GOBR (LangGraph).

Workflow condicional (regra_agente.md, seção 4): o código decide o próximo nó; nenhum LLM roteia.
  rotear               função pura, 0 token: regras | manual | ambos | nenhum
  buscar_regras        busca no índice de regras (Entrega 2), configuração escolhida no desenvolvimento
  buscar_manual        busca no índice do manual (Entrega 3), configuração da Entrega 4
  montar_contexto      o mesmo contexto do fluxo da Entrega 4
  gerar                uma chamada ao Gemini: JSON com gobr, premissas e perguntas
  validar              parser da Entrega 1 + critério da regra (seção 6), sem LLM
  responder_linguagem  rota manual: uma chamada ao Gemini com o prompt da Entrega 4
  encerrar             monta a saída e o status
O ciclo gerar -> validar -> gerar é limitado por MAX_TENTATIVAS. Na retentativa, se o manual ainda não foi
consultado, o grafo busca no manual com uma pergunta montada das recusas.

    python agente.py "Ativos a cada 14 dias e inativos a cada 30. Não agendar inadimplentes."
    python agente.py "Como separo os clientes inadimplentes?"
    python agente.py --sessao            # várias mensagens; modelos e índices carregados uma vez
    python agente.py "..." --sem-llm     # só roteamento, busca e contexto (0 token)

Fora desta entrega: imagem e memória entre turnos (Entrega 6).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import TypedDict

import comum_agente as ca
from comum_agente import cf


class Estado(TypedDict, total=False):
    mensagem: str
    excluir: list            # só na avaliação: ids das regras de referência escondidas (regra, seção 8)
    rota: str
    motivo_rota: str
    regras: list
    manual: list
    consulta_manual: str     # a consulta que foi (ou será) feita ao manual
    manual_consultado: bool
    contexto: str
    tokens_contexto: int
    tentativas: list         # uma por chamada de geração: gobr, premissas, perguntas, recusas, avisos, tokens
    gobr: str
    resposta: str            # texto da rota manual ou do fora de escopo
    status: str
    erro: str
    pontos_de_atencao: list
    tokens: dict
    tempos_s: dict


class Dependencias:
    """O que os nós usam, injetável nos testes: as buscas, as duas chamadas ao Gemini, o contador e o relógio.
    `gerar(sistema, usuario)` e `responder(pergunta, contexto)` devolvem o dicionário de comum_agente.gerar_json
    e de comum_fluxo.responder; None em qualquer uma = modo sem LLM."""

    def __init__(self, *, buscar_regras, buscar_manual, gerar=None, responder=None, contar=None,
                 relogio=time.perf_counter, dormir=time.sleep, avisar=None):
        self.buscar_regras, self.buscar_manual = buscar_regras, buscar_manual
        self.gerar, self.responder, self.contar = gerar, responder, contar
        self.relogio, self.dormir, self.avisar = relogio, dormir, avisar


def _tempo(estado: Estado, no: str, segundos: float) -> dict:
    tempos = dict(estado.get("tempos_s") or {})
    tempos[no] = round(tempos.get(no, 0.0) + segundos, 3)
    return tempos


def _soma_tokens(estado: Estado, chamada: dict) -> dict:
    tokens = dict(estado.get("tokens") or {"entrada": 0, "saida": 0, "raciocinio": 0, "total": 0, "chamadas": 0})
    for curto, campo in (("entrada", "tokens_entrada"), ("saida", "tokens_saida"),
                         ("raciocinio", "tokens_raciocinio"), ("total", "tokens_total")):
        tokens[curto] += chamada.get(campo) or 0
    tokens["chamadas"] += 1
    return tokens


# ------------------------------------------------------------------ nós ----
def criar_nos(d: Dependencias) -> dict:
    def rotear(e: Estado) -> dict:
        t0 = d.relogio()
        r = ca.rotear(e["mensagem"])
        return {"rota": r["rota"], "motivo_rota": r["motivo"], "regras": [], "manual": [], "tentativas": [],
                "manual_consultado": False, "tempos_s": _tempo(e, "rotear", d.relogio() - t0)}

    def buscar_regras(e: Estado) -> dict:
        t0 = d.relogio()
        regras = d.buscar_regras(e["mensagem"], excluir=tuple(e.get("excluir") or ()))
        return {"regras": regras, "tempos_s": _tempo(e, "buscar_regras", d.relogio() - t0)}

    def buscar_manual(e: Estado) -> dict:
        t0 = d.relogio()
        consulta = e.get("consulta_manual") or e["mensagem"]
        trechos = d.buscar_manual(consulta)
        return {"manual": trechos, "manual_consultado": True, "consulta_manual": consulta,
                "tempos_s": _tempo(e, "buscar_manual", d.relogio() - t0)}

    def montar_contexto(e: Estado) -> dict:
        t0 = d.relogio()
        contexto = cf.montar_contexto(e.get("regras") or [], e.get("manual") or [])
        return {"contexto": contexto, "tokens_contexto": d.contar(contexto) if d.contar else None,
                "tempos_s": _tempo(e, "montar_contexto", d.relogio() - t0)}

    def gerar(e: Estado) -> dict:
        t0 = d.relogio()
        anteriores = e.get("tentativas") or []
        ultima = anteriores[-1] if anteriores else None
        sistema, usuario = ca.montar_prompt_gerar(e["mensagem"], e["contexto"],
                                                  anterior=ultima["gobr"] if ultima else None,
                                                  recusas=ultima["recusas"] if ultima else None)
        chamada, erro = ca.com_retentativa_infra(lambda: d.gerar(sistema, usuario), dormir=d.dormir, avisar=d.avisar)
        if erro:
            return {"status": "erro_infra", "erro": erro, "tempos_s": _tempo(e, "gerar", d.relogio() - t0)}
        saida = ca.interpretar_saida(chamada["texto"])
        tentativa = {"n": len(anteriores) + 1, "gobr": saida["gobr"] if saida else "",
                     "premissas": saida["premissas"] if saida else [], "perguntas": saida["perguntas"] if saida else [],
                     "saida_valida": saida is not None, "recusas": [], "avisos": [], "aceita": None,
                     "consultou_manual": bool(e.get("manual_consultado")),
                     "tokens": {k: chamada.get(k) for k in ("tokens_entrada", "tokens_saida", "tokens_raciocinio",
                                                            "tokens_total")},
                     "segundos": chamada.get("segundos")}
        return {"tentativas": anteriores + [tentativa], "gobr": tentativa["gobr"],
                "tokens": _soma_tokens(e, chamada), "tempos_s": _tempo(e, "gerar", d.relogio() - t0)}

    def validar(e: Estado) -> dict:
        t0 = d.relogio()
        tentativas = [dict(t) for t in e["tentativas"]]
        ultima = tentativas[-1]
        v = ca.validar(ultima["gobr"] if ultima["saida_valida"] else "")
        ultima.update({"recusas": v["recusas"], "avisos": v["avisos"], "aceita": v["aceita"], "resumo": v["resumo"]})
        saida = {"tentativas": tentativas, "tempos_s": _tempo(e, "validar", d.relogio() - t0)}
        if not v["aceita"] and len(tentativas) < ca.MAX_TENTATIVAS and not e.get("manual_consultado"):
            consulta = ca.consulta_manual_das_recusas(v["recusas"], ultima["gobr"])
            if consulta:
                saida["consulta_manual"] = consulta
        return saida

    def responder_linguagem(e: Estado) -> dict:
        t0 = d.relogio()
        chamada, erro = ca.com_retentativa_infra(lambda: d.responder(e["mensagem"], e["contexto"]), dormir=d.dormir,
                                                 avisar=d.avisar)
        if erro:
            return {"status": "erro_infra", "erro": erro,
                    "tempos_s": _tempo(e, "responder_linguagem", d.relogio() - t0)}
        return {"resposta": chamada["texto"], "status": "resposta_linguagem", "tokens": _soma_tokens(e, chamada),
                "tempos_s": _tempo(e, "responder_linguagem", d.relogio() - t0)}

    def encerrar(e: Estado) -> dict:
        saida: dict = {"tokens": e.get("tokens") or {"entrada": 0, "saida": 0, "raciocinio": 0, "total": 0,
                                                      "chamadas": 0}}
        if e.get("status") in ("erro_infra", "resposta_linguagem"):
            status = e["status"]
        elif e["rota"] == "nenhum":
            status, saida["resposta"] = "fora_do_escopo", ca.MSG_FORA_DO_ESCOPO
        elif e.get("tentativas"):
            status = "aceita" if e["tentativas"][-1]["aceita"] else "invalida"
        else:
            status = None                                           # modo sem LLM: só busca e contexto
        saida["status"] = status
        pontos = []
        if e.get("tentativas"):
            ultima = e["tentativas"][-1]
            pontos += [{"origem": "validador", "codigo": a["codigo"], "texto": a["texto"]} for a in ultima["avisos"]]
            pontos += [{"origem": "premissa", "codigo": None, "texto": p} for p in ultima["premissas"]]
            pontos += [{"origem": "pergunta", "codigo": None, "texto": p} for p in ultima["perguntas"]]
        saida["pontos_de_atencao"] = pontos
        tempos = dict(e.get("tempos_s") or {})
        tempos["busca"] = round(tempos.get("buscar_regras", 0.0) + tempos.get("buscar_manual", 0.0), 3)
        tempos["turno"] = round(sum(v for k, v in tempos.items() if k not in ("busca", "turno")), 3)
        saida["tempos_s"] = tempos
        return saida

    return {"rotear": rotear, "buscar_regras": buscar_regras, "buscar_manual": buscar_manual,
            "montar_contexto": montar_contexto, "gerar": gerar, "validar": validar,
            "responder_linguagem": responder_linguagem, "encerrar": encerrar}


# ------------------------------------------------------------------ arestas (condições sobre o estado) ----
def depois_de_rotear(e: Estado) -> str:
    return {"regras": "buscar_regras", "ambos": "buscar_regras", "manual": "buscar_manual",
            "nenhum": "encerrar"}[e["rota"]]


def depois_de_buscar_regras(e: Estado) -> str:
    return "buscar_manual" if e["rota"] == "ambos" and not e.get("manual_consultado") else "montar_contexto"


def depois_de_validar(e: Estado) -> str:
    ultima = e["tentativas"][-1]
    if ultima["aceita"] or len(e["tentativas"]) >= ca.MAX_TENTATIVAS:
        return "encerrar"
    if not e.get("manual_consultado") and e.get("consulta_manual"):
        return "buscar_manual"
    return "gerar"


def construir_grafo(d: Dependencias):
    """O grafo compilado. Sem `d.gerar` (modo sem LLM), o contexto montado vai direto para `encerrar`."""
    from langgraph.graph import END, START, StateGraph

    def depois_do_contexto(e: Estado) -> str:
        if e["rota"] == "manual":
            return "responder_linguagem" if d.responder else "encerrar"
        return "gerar" if d.gerar else "encerrar"

    g = StateGraph(Estado)
    for nome, funcao in criar_nos(d).items():
        g.add_node(nome, funcao)
    g.add_edge(START, "rotear")
    g.add_conditional_edges("rotear", depois_de_rotear, ["buscar_regras", "buscar_manual", "encerrar"])
    g.add_conditional_edges("buscar_regras", depois_de_buscar_regras, ["buscar_manual", "montar_contexto"])
    g.add_edge("buscar_manual", "montar_contexto")
    g.add_conditional_edges("montar_contexto", depois_do_contexto, ["responder_linguagem", "gerar", "encerrar"])
    g.add_conditional_edges("gerar", lambda e: "encerrar" if e.get("status") == "erro_infra" else "validar",
                            ["validar", "encerrar"])
    g.add_conditional_edges("validar", depois_de_validar, ["encerrar", "buscar_manual", "gerar"])
    g.add_edge("responder_linguagem", "encerrar")
    g.add_edge("encerrar", END)
    return g.compile()


CAMPOS_SAIDA = ("mensagem", "rota", "motivo_rota", "regras", "manual", "consulta_manual", "contexto",
                "tokens_contexto", "tentativas", "gobr", "resposta", "status", "erro", "pontos_de_atencao", "tokens",
                "tempos_s")


def executar(grafo, mensagem: str, excluir=()) -> dict:
    """Um turno. Devolve um dicionário serializável em JSON com os campos da seção 4 da regra."""
    final = grafo.invoke({"mensagem": mensagem, "excluir": list(excluir)},
                         {"recursion_limit": 12 + 6 * ca.MAX_TENTATIVAS})
    return {c: final.get(c) for c in CAMPOS_SAIDA}


# ------------------------------------------------------------------ montagem real e saída ----
def dependencias_reais(buscador: ca.Buscador, cfg: ca.ConfigRegras, *, modelo: str = ca.MODELO_GEMINI_PADRAO,
                       cliente=None, sem_llm: bool = False, avisar=None) -> Dependencias:
    def gerar(sistema, usuario):
        return ca.gerar_json(sistema, usuario, modelo=modelo, cliente=cliente_())

    def responder(pergunta, contexto):
        return cf.responder(pergunta, contexto, modelo=modelo, cliente=cliente_())

    guardado = {"cliente": cliente}

    def cliente_():
        if guardado["cliente"] is None:
            guardado["cliente"] = ca.criar_cliente_gemini()
        return guardado["cliente"]

    return Dependencias(
        buscar_regras=lambda consulta, excluir=(): buscador.buscar_regras(consulta, cfg, excluir=excluir),
        buscar_manual=buscador.buscar_manual, gerar=None if sem_llm else gerar,
        responder=None if sem_llm else responder, contar=buscador.recursos.contador_tokens(), avisar=avisar)


def _n(v) -> str:
    return "n/d" if v is None else f"{v:,}".replace(",", ".")


def formatar_saida(res: dict, so_fontes: bool = False) -> str:
    t = res.get("tempos_s") or {}
    linhas = [f"Mensagem: {res['mensagem']}", f"Rota: {res['rota']} ({res['motivo_rota']})"]
    if res["regras"]:
        linhas.append("Regras de exemplo:")
        linhas += [f"  {r['posicao']}. {r['titulo'] or r['regra_id']} ({r['regra_id']}) - nota {r['nota']:.4f}"
                   for r in res["regras"]]
    if res["manual"]:
        linhas.append(f"Manual do GOBR (consulta: {res['consulta_manual']}):")
        linhas += [f"  {m['posicao']}. {cf.fonte_do_manual(m)} - nota {m['nota']:.4f}" for m in res["manual"]]
    if res["status"] is None and res.get("contexto") and not so_fontes:
        linhas += ["", "=== Contexto ===", res["contexto"].rstrip()]
    if res["status"] in ("aceita", "invalida"):
        ultima = res["tentativas"][-1]
        marca = "" if res["status"] == "aceita" else f" - {ca.MARCA_NAO_VALIDADO}"
        linhas += ["", f"=== GOBR ({len(res['tentativas'])} tentativa(s)){marca} ===", res["gobr"].rstrip()]
        if res["status"] == "invalida":
            linhas += ["", f"{ca.MARCA_NAO_VALIDADO}: a validação recusou esta regra. Problemas:",
                       ca.formatar_recusas(ultima["recusas"])]
        else:
            linhas += ["", "Validação: aceita (critério estrutural; não garante que o Govendas aceita a regra "
                           "nem que ela faz o que foi pedido)."]
        if res["pontos_de_atencao"]:
            linhas.append("\nPontos de atenção:")
            rotulo = {"validador": "validador", "premissa": "premissa assumida", "pergunta": "pergunta para você"}
            linhas += [f"  - [{rotulo[p['origem']]}] {p['texto']}" for p in res["pontos_de_atencao"]]
    elif res["status"] in ("resposta_linguagem", "fora_do_escopo"):
        linhas += ["", res["resposta"] or "(resposta vazia)"]
    elif res["status"] == "erro_infra":
        linhas += ["", f"Falha de infraestrutura na chamada ao Gemini: {res['erro']}"]
    tk = res.get("tokens") or {}
    linhas += ["", f"Status: {res['status'] or 'sem LLM (só busca e contexto)'} | busca {t.get('busca', 0):.2f} s "
                   f"(teto {ca.TETO_BUSCA_S:g} s) | turno {t.get('turno', 0):.1f} s",
               f"Tokens da API: entrada {_n(tk.get('entrada'))} | saída {_n(tk.get('saida'))} | raciocínio "
               f"{_n(tk.get('raciocinio'))} | total {_n(tk.get('total'))} | chamadas {_n(tk.get('chamadas'))}"]
    return "\n".join(linhas)


def _argumentos(argv):
    p = argparse.ArgumentParser(description="Agente que gera uma parametrização do Govendas em GOBR (LangGraph).")
    p.add_argument("mensagem", nargs="?", help="descrição das regras de negócio ou pergunta (sem ela, use --sessao)")
    p.add_argument("--sessao", action="store_true", help="várias mensagens; carrega os modelos uma vez")
    p.add_argument("--sem-llm", action="store_true", help="só roteamento, busca e contexto (0 token)")
    p.add_argument("--modelo", default=ca.MODELO_GEMINI_PADRAO, help="modelo do Gemini (padrão: o da Entrega 1)")
    p.add_argument("--config", default=str(ca.ARQ_CONFIG), help="configuração de busca (padrão: config_agente.json)")
    p.add_argument("--so-fontes", action="store_true", help="no modo --sem-llm, não mostra o corpo do contexto")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    a = p.parse_args(argv)
    if not a.sessao and not a.mensagem:
        p.error("informe a mensagem ou use --sessao")
    return a


def main(argv=None, buscador=None, cliente=None) -> int:
    cf.configurar_saida()
    a = _argumentos(argv)
    try:
        cfg = ca.carregar_config_agente(Path(a.config))
    except FileNotFoundError:
        print(f"Não achei {a.config}. Rode antes: python avaliar_agente.py dev", file=sys.stderr)
        return 2
    except (ValueError, KeyError) as e:
        print(f"{Path(a.config).name} inválido: {e}", file=sys.stderr)
        return 2
    if not a.sem_llm and cliente is None and not ca.chave_gemini():   # falha cedo, antes de carregar os modelos
        print("Defina GOOGLE_API_KEY (ou GEMINI_API_KEY) no ambiente, ou use --sem-llm.", file=sys.stderr)
        return 2
    buscador = buscador or ca.Buscador()
    cf.imprimir(f"Carregando modelos e índices (regras: {cfg.descricao()}; manual: {buscador.cfg_manual.descricao()})...")
    t0 = time.perf_counter()
    buscador.preparar(cfg)
    cf.imprimir(f"Carregado em {time.perf_counter() - t0:.0f} s (fora do teto de busca de {ca.TETO_BUSCA_S:g} s).\n")
    grafo = construir_grafo(dependencias_reais(buscador, cfg, modelo=a.modelo, cliente=cliente, sem_llm=a.sem_llm,
                                               avisar=None if a.json else cf.imprimir))

    def um_turno(mensagem: str) -> int:
        res = executar(grafo, mensagem)
        cf.imprimir(json.dumps(res, ensure_ascii=False, indent=1) if a.json else formatar_saida(res, a.so_fontes))
        return 1 if res["status"] in ("erro_infra", "invalida") else 0

    if not a.sessao:
        return um_turno(a.mensagem)
    cf.imprimir("Digite a mensagem (linha vazia ou 'sair' encerra). Cada mensagem é um turno sem memória.")
    estado = 0
    while True:
        try:
            mensagem = input("mensagem> ").strip()
        except EOFError:
            break
        if not mensagem or mensagem.lower() in ("sair", "exit", "quit"):
            break
        try:
            estado = max(estado, um_turno(mensagem))
        except Exception as e:  # noqa: BLE001
            print(f"Erro neste turno: {type(e).__name__}: {e}", file=sys.stderr)
            estado = 1
        cf.imprimir("")
    return estado


if __name__ == "__main__":
    sys.exit(main())
