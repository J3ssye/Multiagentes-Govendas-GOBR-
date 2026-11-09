# -*- coding: utf-8 -*-
"""Entrega 4 - o fluxo básico de busca (RAG) do agente que ajuda a escrever regras GOBR.

Workflow determinístico em Python, sem agente e sem LLM no caminho padrão:
  entrada   uma pergunta em português (texto livre);
  etapa 1   busca nas regras de exemplo (índice da Entrega 2, variante com_pontos): as 3 melhores regras;
  etapa 2   busca no manual do GOBR (índice da Entrega 3, estratégia C): os 3 melhores trechos;
  etapa 3   montagem do contexto: as regras com o GOBR completo e os trechos com seção e páginas;
  etapa 4   (só com --responder) uma chamada ao Gemini com esse contexto.
  saída     o contexto (0 token de LLM) e, com --responder, a resposta com os tokens que a API contou.

A configuração de busca de cada índice (fase 1, candidatos e max_length do reranker) é a da dupla escolhida no
desenvolvimento, em config_escolhida.json (python avaliar_fluxo.py escolher).

    python fluxo.py "como separo os clientes inadimplentes?"
    python fluxo.py "como separo os clientes inadimplentes?" --responder
    python fluxo.py --sessao [--responder]       # várias perguntas; modelos e índices carregados uma vez

Fora desta entrega: imagem, grafo de agentes, escolher em qual índice buscar e gerar a regra GOBR (Entrega 5).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from comum_fluxo import (ARQ_CONFIG, K, MODELO_GEMINI_PADRAO, TETO_S, Config, Recursos, aquecer, buscar_cfg,
                         carregar_config, configurar_saida, descrever_regra, descrever_trecho, fonte_do_manual,
                         imprimir, montar_contexto, responder)


def preparar(recursos: Recursos, cfgs: dict[str, Config], relogio=time.perf_counter) -> float:
    """Carrega o que a dupla usa e faz o aquecimento (BM25 e reranker), para a 1ª pergunta não pagar isso.
    Devolve os segundos gastos. O teto de latência vale para a pergunta depois disto, não para o carregamento."""
    t0 = relogio()
    for indice in ("regras", "manual"):
        cfg = cfgs[indice]
        recursos.indice(indice)
        aquecer(recursos, indice, cfg.max_length)
    recursos.contador_tokens()
    return relogio() - t0


def perguntar(recursos: Recursos, cfgs: dict[str, Config], pergunta: str, *, k: int = K,
              relogio=time.perf_counter) -> dict:
    """Etapas 1 a 3. Devolve um dicionário (serializável em JSON) com as fontes, o contexto e os tempos."""
    t0 = relogio()
    r_rank = buscar_cfg(recursos.indice("regras"), pergunta, cfgs["regras"], recursos.reranker_de(cfgs["regras"]), k=k)
    t1 = relogio()
    m_rank = buscar_cfg(recursos.indice("manual"), pergunta, cfgs["manual"], recursos.reranker_de(cfgs["manual"]), k=k)
    t2 = relogio()
    regras = [descrever_regra(n, i) for i, n in enumerate(r_rank, 1)]
    trechos = [descrever_trecho(n, i) for i, n in enumerate(m_rank, 1)]
    contexto = montar_contexto(regras, trechos)
    t3 = relogio()
    contar = recursos.contador_tokens()
    return {"pergunta": pergunta,
            "dupla": {"regras": cfgs["regras"].nome, "manual": cfgs["manual"].nome},
            "descricao": {"regras": cfgs["regras"].descricao(), "manual": cfgs["manual"].descricao()},
            "origem_da_nota": {"regras": cfgs["regras"].origem_da_nota, "manual": cfgs["manual"].origem_da_nota},
            "regras": regras, "manual": trechos, "contexto": contexto,
            "tokens_contexto": contar(contexto) if contar else None,
            "tempos_s": {"regras": round(t1 - t0, 3), "manual": round(t2 - t1, 3), "busca": round(t2 - t0, 3),
                         "contexto": round(t3 - t2, 3)},
            "llm": None}


def completar_com_llm(res: dict, *, modelo: str = MODELO_GEMINI_PADRAO, cliente=None) -> dict:
    """Etapa 4: uma chamada ao Gemini com o contexto da etapa 3. Guarda a resposta e os tokens em res["llm"]."""
    res["llm"] = responder(res["pergunta"], res["contexto"], modelo=modelo, cliente=cliente)
    return res


def _n(v) -> str:
    return "n/d" if v is None else f"{v:,}".replace(",", ".")


def formatar_fontes(res: dict) -> str:
    t = res["tempos_s"]
    linhas = [f"Pergunta: {res['pergunta']}",
              f"Busca: regras {t['regras']:.2f} s ({res['descricao']['regras']}) | "
              f"manual {t['manual']:.2f} s ({res['descricao']['manual']}) | total {t['busca']:.2f} s "
              f"(teto {TETO_S:g} s)",
              f"Contexto: {_n(res['tokens_contexto'])} tokens (bge-m3, só contagem) | "
              f"tokens de LLM: {'0 (sem --responder)' if res['llm'] is None else 'ver abaixo'}",
              "", f"Regras de exemplo (nota do {res['origem_da_nota']['regras']}):"]
    for r in res["regras"]:
        linhas.append(f"  {r['posicao']}. {r['titulo'] or r['regra_id']} ({r['regra_id']}) - nota {r['nota']:.4f}")
    linhas.append(f"Manual do GOBR (nota do {res['origem_da_nota']['manual']}):")
    for m in res["manual"]:
        linhas.append(f"  {m['posicao']}. {fonte_do_manual(m)} - nota {m['nota']:.4f}")
    return "\n".join(linhas)


def formatar_llm(llm: dict) -> str:
    return "\n".join([f"=== Resposta ({llm['modelo']}) ===", llm["texto"] or "(resposta vazia)", "",
                      f"Tokens da API: entrada {_n(llm['tokens_entrada'])} | saída {_n(llm['tokens_saida'])} | "
                      f"raciocínio {_n(llm['tokens_raciocinio'])} | total {_n(llm['tokens_total'])} | "
                      f"{llm['segundos']:.1f} s"])


def formatar_saida(res: dict, so_fontes: bool = False) -> str:
    partes = [formatar_fontes(res)]
    if not so_fontes:
        partes += ["", "=== Contexto ===", res["contexto"].rstrip()]
    if res["llm"] is not None:
        partes += ["", formatar_llm(res["llm"])]
    return "\n".join(partes)


def _argumentos(argv):
    p = argparse.ArgumentParser(description="Fluxo básico de busca (RAG): regras de exemplo + manual do GOBR.")
    p.add_argument("pergunta", nargs="?", help="pergunta em português (sem ela, use --sessao)")
    p.add_argument("--sessao", action="store_true", help="várias perguntas; carrega os modelos uma vez")
    p.add_argument("--responder", action="store_true", help="uma chamada ao Gemini com o contexto")
    p.add_argument("--modelo", default=MODELO_GEMINI_PADRAO, help="modelo do Gemini (padrão: o da Entrega 1)")
    p.add_argument("--config", default=str(ARQ_CONFIG), help="dupla de configurações (padrão: config_escolhida.json)")
    p.add_argument("--so-fontes", action="store_true", help="mostra só as fontes, sem o corpo do contexto")
    p.add_argument("--json", action="store_true", help="saída em JSON (para o agente da Entrega 5)")
    a = p.parse_args(argv)
    if not a.sessao and not a.pergunta:
        p.error("informe a pergunta ou use --sessao")
    return a


def _uma_pergunta(recursos, cfgs, pergunta, a, cliente=None) -> int:
    res = perguntar(recursos, cfgs, pergunta)
    erro = None
    if not a.json:
        imprimir(formatar_saida(res, so_fontes=a.so_fontes))
    if a.responder:
        try:
            completar_com_llm(res, modelo=a.modelo, cliente=cliente)
            if not a.json:
                imprimir("\n" + formatar_llm(res["llm"]))
        except Exception as e:  # chave ausente, rede, cota: o contexto já foi mostrado
            erro = f"{type(e).__name__}: {e}"
            print(f"\nFalha na chamada ao Gemini ({erro}). O contexto acima não depende dela.", file=sys.stderr)
    if a.json:
        imprimir(json.dumps({**res, "erro_llm": erro}, ensure_ascii=False, indent=1))
    return 1 if erro else 0


def main(argv=None, recursos=None, cliente=None) -> int:
    configurar_saida()
    a = _argumentos(argv)
    try:
        cfgs = carregar_config(Path(a.config))
    except FileNotFoundError:
        print(f"Não achei {a.config}. Rode antes: python avaliar_fluxo.py dev  e  python avaliar_fluxo.py escolher",
              file=sys.stderr)
        return 2
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    if a.responder:  # falha cedo, antes de carregar os modelos, se não há chave nem SDK
        from comum_fluxo import chave_gemini
        if cliente is None and not chave_gemini():
            print("Defina GEMINI_API_KEY (ou GOOGLE_API_KEY) para usar --responder.", file=sys.stderr)
            return 2
    recursos = recursos or Recursos()
    imprimir(f"Carregando modelos e índices (regras: {cfgs['regras'].descricao()}; "
             f"manual: {cfgs['manual'].descricao()})...")
    seg = preparar(recursos, cfgs)
    imprimir(f"Carregado em {seg:.0f} s (fora do teto de {TETO_S:g} s, que vale por pergunta).\n")
    if not a.sessao:
        return _uma_pergunta(recursos, cfgs, a.pergunta, a, cliente)
    imprimir("Digite a pergunta (linha vazia ou 'sair' encerra).")
    estado = 0
    while True:
        try:
            pergunta = input("pergunta> ").strip()
        except EOFError:
            break
        if not pergunta or pergunta.lower() in ("sair", "exit", "quit"):
            break
        try:
            estado = max(estado, _uma_pergunta(recursos, cfgs, pergunta, a, cliente))
        except Exception as e:
            print(f"Erro nesta pergunta: {type(e).__name__}: {e}", file=sys.stderr)
            estado = 1
        imprimir("")
    return estado


if __name__ == "__main__":
    sys.exit(main())
