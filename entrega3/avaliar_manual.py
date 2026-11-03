# -*- coding: utf-8 -*-
"""Entrega 3, passo 5.4 - avalia a recuperação no manual.

Para cada consulta, ordena TODOS os chunks do índice (sem agrupar) e anota a posição do primeiro que
acerta. Regra oficial (fixada no Passo 4, antes de indexar): o chunk acerta se a sua folha principal
está no gabarito. Regra de sensibilidade, só relatada: também acerta o chunk que contém pelo menos
metade dos caracteres de uma folha do gabarito. Métricas hit@k e MRR: as funções da Entrega 2
(avaliar.py), sem alteração.

Regra de escolha do padrão, fixada ANTES de rodar o desenvolvimento: maior MRR no dev (regra oficial)
entre as combinações estratégia x configuração; empate -> maior hit@1 -> configuração mais simples
(vetor, híbrido, vetor + rerank, híbrido + rerank) -> estratégia C. O teste só relata.

Uso (PowerShell, na pasta trabalho\\entrega3):
    python avaliar_manual.py --rerank --hibrido                     # dev: 2 estratégias x 4 configurações
    python avaliar_manual.py --conjunto teste --rerank --hibrido    # teste: rodar uma vez, sem ajustar nada depois
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime

from comum_manual import (AQUI, COBERTURA_MINIMA, CONJUNTOS, ESTRATEGIAS, N_CANDIDATOS, RerankerComCache, acerta,
                          buscar, caminho_indice, carregar_consultas, carregar_indice, criar_embedding,
                          criar_reranker)
from avaliar import metricas, resumo_configs  # Entrega 2, sem alteração

SIMPLICIDADE = ("vetor", "híbrido", "vetor + rerank", "híbrido + rerank")
TIPOS = ("conceito", "opcoes", "sintaxe")


def posicao(ranking, gabarito, regra: str):
    for i, n in enumerate(ranking, 1):
        if acerta(n.node.metadata, gabarito, regra):
            return i
    return None


def avaliar(index, consultas, reranker=None, n_candidatos: int = N_CANDIDATOS, hibrido: bool = False):
    linhas = []
    for c in consultas:
        r = buscar(index, c["consulta"], k=None, reranker=reranker, n_candidatos=n_candidatos, hibrido=hibrido)
        linhas.append({"id": c["id"], "tipo": c["tipo"], "gabarito": c["gabarito"],
                       "posicao": posicao(r, c["gabarito"], "principal"),
                       "posicao_cobertura": posicao(r, c["gabarito"], "cobertura"),
                       "top3": [(n.node.metadata["folha"], round(float(n.score), 4)) for n in r[:3]]})
    return linhas


def escolher_padrao(resultados: dict):
    """(estratégia, configuração, métricas) pela regra fixada; desempates na docstring do módulo."""
    cands = [(e, nome, metricas([l["posicao"] for l in linhas]))
             for e, cfgs in resultados.items() for nome, linhas in cfgs]
    cands.sort(key=lambda x: (-round(x[2]["MRR"], 9), -round(x[2]["hit@1"], 9),
                              SIMPLICIDADE.index(x[1]), ESTRATEGIAS.index(x[0])))
    return cands[0]


def _por_tipo(cfgs) -> str:
    saida = ["| configuração | " + " | ".join(f"MRR {t}" for t in TIPOS) + " |", "|---|" + "---|" * len(TIPOS)]
    for nome, linhas in cfgs:
        celulas = []
        for t in TIPOS:
            ps = [l["posicao"] for l in linhas if l["tipo"] == t]
            celulas.append(f"{metricas(ps)['MRR']:.3f} (n={len(ps)})" if ps else "-")
        saida.append(f"| {nome} | " + " | ".join(celulas) + " |")
    return "\n".join(saida) + "\n"


def _posicoes(cfgs) -> str:
    nomes = [n for n, _ in cfgs]
    saida = ["| consulta | tipo | gabarito | " + " | ".join(nomes) + " |", "|---|---|---|" + "---|" * len(nomes)]
    for i, l0 in enumerate(cfgs[0][1]):
        pos = [str(linhas[i]["posicao"] or "fora") for _, linhas in cfgs]
        saida.append(f"| {l0['id']} | {l0['tipo']} | {', '.join(l0['gabarito'])} | " + " | ".join(pos) + " |")
    return "\n".join(saida) + "\n"


def _erros(cfgs) -> str:
    saida = []
    for nome, linhas in cfgs:
        ruins = [l for l in linhas if l["posicao"] != 1]
        if not ruins:
            continue
        saida.append(f"**{nome}**\n")
        for l in ruins:
            top = "; ".join(f"{f} ({s})" for f, s in l["top3"])
            saida.append(f"- {l['id']} (posição {l['posicao'] or 'fora'}; gabarito {', '.join(l['gabarito'])}): {top}")
        saida.append("")
    return "\n".join(saida) + "\n" if saida else "Nenhuma: todas no 1º lugar.\n"


def relatorio(conjunto: str, n_consultas: int, candidatos: int, resultados: dict, completo: bool) -> str:
    todas = [(f"{e} · {nome}", linhas) for e, cfgs in resultados.items() for nome, linhas in cfgs]
    md = [f"# Avaliação da recuperação no manual (Entrega 3) - conjunto: {conjunto} ({n_consultas} consultas)\n",
          f"Gerado em {datetime.now():%d/%m/%Y %H:%M}. Ranking de chunks, sem agrupar; candidatos do reranker: {candidatos}.\n",
          "## Resumo - regra oficial (a folha principal do chunk está no gabarito)\n",
          resumo_configs(todas),
          f"## Sensibilidade - acerta também o chunk com pelo menos {COBERTURA_MINIMA:.0%} de uma folha do gabarito "
          "(só relata; não decide)\n",
          resumo_configs([(nome, [{**l, "posicao": l["posicao_cobertura"]} for l in linhas]) for nome, linhas in todas])]
    for e, cfgs in resultados.items():
        md += [f"## Estratégia {e}\n", "### MRR por tipo de consulta (regra oficial)\n", _por_tipo(cfgs),
               "### Posição do primeiro acerto, por consulta (regra oficial)\n", _posicoes(cfgs),
               "### Consultas fora do 1º lugar: top-3 devolvido (folha e nota)\n", _erros(cfgs)]
    if conjunto == "dev":
        e, nome, m = escolher_padrao(resultados)
        aviso = "" if completo else " ATENÇÃO: nem todas as 8 combinações foram rodadas; a regra vale só entre as rodadas."
        md += ["## Padrão pela regra fixada\n",
               f"**{e} · {nome}**: MRR {m['MRR']:.3f}, hit@1 {m['hit@1']:.2f} (maior MRR no dev; desempates: hit@1, "
               f"configuração mais simples, estratégia C).{aviso}\n"]
    else:
        md += ["## Teste\n", "O teste só relata; o padrão foi escolhido no desenvolvimento.\n"]
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conjunto", choices=sorted(CONJUNTOS), default="dev")
    ap.add_argument("--estrategia", choices=[*ESTRATEGIAS, "ambas"], default="ambas")
    ap.add_argument("--rerank", action="store_true", help="avalia também as configurações com cross-encoder")
    ap.add_argument("--hibrido", action="store_true", help="avalia também a busca híbrida (vetor + BM25)")
    ap.add_argument("--candidatos", type=int, default=N_CANDIDATOS)
    args = ap.parse_args()
    estrategias = ESTRATEGIAS if args.estrategia == "ambas" else (args.estrategia,)
    faltam = [e for e in estrategias if not caminho_indice(e).exists()]
    if faltam:
        raise SystemExit(f"Índice não encontrado para {faltam}. Rode antes: python indexar_manual.py")

    consultas = carregar_consultas(args.conjunto)
    emb, _ = criar_embedding()
    reranker = None
    if args.rerank:
        base, disp = criar_reranker()
        reranker = RerankerComCache(base)
        print(f"Reranker: {base.nome} em {disp} | candidatos = {args.candidatos}")
    configs = [("vetor", {})]
    if args.rerank:
        configs.append(("vetor + rerank", {"reranker": reranker}))
    if args.hibrido:
        configs.append(("híbrido", {"hibrido": True}))
        if args.rerank:
            configs.append(("híbrido + rerank", {"reranker": reranker, "hibrido": True}))
    completo = len(estrategias) == len(ESTRATEGIAS) and len(configs) == len(SIMPLICIDADE)

    sufixo = ("_rerank" if args.rerank else "") + ("_hibrido" if args.hibrido else "")
    destino = AQUI / f"resultados_manual_{args.conjunto}{sufixo}.md"
    resultados: dict = {}
    for e in estrategias:
        index = carregar_indice(e, emb)
        print(f"\n[{e}] {len(index.docstore.docs)} chunks | {len(consultas)} consultas ({args.conjunto})")
        cfgs = []
        for nome, kw in configs:
            t0 = time.time()
            linhas = avaliar(index, consultas, n_candidatos=args.candidatos, **kw)
            m = metricas([l["posicao"] for l in linhas])
            print(f"[{e}] {nome:<16} MRR {m['MRR']:.3f} | hit@1 {m['hit@1']:.2f} | hit@10 {m['hit@10']:.2f}"
                  f" | {time.time() - t0:.0f} s")
            cfgs.append((nome, linhas))
        resultados[e] = cfgs
        # grava a cada estratégia: uma queda no meio não perde o que já rodou
        destino.write_text(relatorio(args.conjunto, len(consultas), args.candidatos, resultados,
                                     completo and len(resultados) == len(estrategias)), encoding="utf-8")
        destino.with_suffix(".json").write_text(json.dumps(
            {"conjunto": args.conjunto, "candidatos": args.candidatos, "resultados": resultados},
            ensure_ascii=False, indent=1), encoding="utf-8")

    if args.conjunto == "dev":
        e, nome, m = escolher_padrao(resultados)
        print(f"\nPadrão pela regra fixada: estratégia {e} + {nome} (MRR {m['MRR']:.3f}, hit@1 {m['hit@1']:.2f})")
    else:
        print("\nTeste: só relata; o padrão vem do desenvolvimento.")
    if reranker is not None:
        print(f"Reranker: {reranker.pares_avaliados} pares (consulta, chunk) lidos; o cache evitou repetir os comuns.")
    print(f"Resultado gravado em {destino}")


if __name__ == "__main__":
    main()
