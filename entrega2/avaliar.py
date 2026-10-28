# -*- coding: utf-8 -*-
"""Avalia a recuperação: a regra certa volta entre as primeiras?

Para cada consulta do conjunto escolhido (--conjunto dev|teste), pega o ranking de TODAS as regras
(partes agrupadas por regra) e anota a posição da primeira regra relevante.

Métricas (definição própria deste trabalho; não estão no material da disciplina):
  hit@k = fração das consultas cuja regra certa está entre as k primeiras
  MRR   = média de 1/posição da regra certa

Com --rerank, avalia também a busca em duas fases (vetorial + cross-encoder) e
mostra, para comparar, a busca só vetorial na mesma execução.

Uso:
    python avaliar.py                          # só vetorial, todas as variantes indexadas
    python avaliar.py --variante sem_pontos
    python avaliar.py --rerank                 # vetorial x vetorial+rerank (50 candidatos)
    python avaliar.py --rerank --candidatos 100
    python avaliar.py --conjunto teste --rerank --hibrido   # 4 configurações no conjunto de teste
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from comum import (
    AQUI,
    MODELO_RERANKER,
    VARIANTES,
    buscar_regras,
    caminho_indice,
    carregar_indice,
    criar_embedding,
    criar_reranker,
)

KS = (1, 3, 5, 10)
CONJUNTOS = {"dev": "consultas_avaliacao.json", "teste": "consultas_teste.json"}


def carregar_consultas(caminho: Path = AQUI / "consultas_avaliacao.json") -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)["consultas"]


def posicao_da_primeira_relevante(ranking_ids: list[str], relevantes: list[str]) -> int | None:
    for pos, id_ in enumerate(ranking_ids, 1):
        if id_ in relevantes:
            return pos
    return None


def metricas(posicoes: list[int | None], ks: tuple[int, ...] = KS) -> dict:
    n = len(posicoes)
    out = {"n": n}
    for k in ks:
        out[f"hit@{k}"] = sum(1 for p in posicoes if p is not None and p <= k) / n if n else 0.0
    out["MRR"] = sum(1 / p for p in posicoes if p) / n if n else 0.0
    return out


def avaliar_indice(index, consultas: list[dict], reranker=None, n_candidatos: int = 50, hibrido: bool = False):
    linhas = []
    for c in consultas:
        ranking = buscar_regras(index, c["consulta"], k=None, reranker=reranker,
                                n_candidatos=n_candidatos, hibrido=hibrido)
        ids = [n.node.metadata["regra_id"] for n in ranking]
        linhas.append({
            "id": c["id"],
            "tipo": c["tipo"],
            "posicao": posicao_da_primeira_relevante(ids, c["relevantes"]),
            "relevantes": c["relevantes"],
            "top3": [(n.node.metadata["titulo"], n.node.metadata["regra_id"], round(n.score, 4))
                     for n in ranking[:3]],
        })
    return linhas


def formatar(titulo: str, linhas: list[dict], ks: tuple[int, ...] = KS) -> str:
    conjuntos = {
        "todas": [l["posicao"] for l in linhas],
        "imagem": [l["posicao"] for l in linhas if l["tipo"] == "imagem"],
        "sintetica": [l["posicao"] for l in linhas if l["tipo"] == "sintetica"],
    }
    saida = [f"## {titulo}\n",
             "| conjunto | n | " + " | ".join(f"hit@{k}" for k in ks) + " | MRR |",
             "|---|---|" + "---|" * (len(ks) + 1)]
    for nome, posicoes in conjuntos.items():
        m = metricas(posicoes, ks)
        saida.append(f"| {nome} | {m['n']} | " + " | ".join(f"{m[f'hit@{k}']:.2f}" for k in ks)
                     + f" | {m['MRR']:.3f} |")
    saida += ["", "| consulta | tipo | posição da regra certa | top-3 devolvido |", "|---|---|---|---|"]
    for l in linhas:
        top = "<br>".join(f"{t} ({s})" for t, _, s in l["top3"])
        saida.append(f"| {l['id']} | {l['tipo']} | {l['posicao'] or 'fora do ranking'} | {top} |")
    return "\n".join(saida) + "\n"


def resumo_configs(configs: list[tuple[str, list[dict]]], ks: tuple[int, ...] = KS) -> str:
    """Uma linha por configuração, todas as consultas juntas."""
    saida = ["| configuração | n | " + " | ".join(f"hit@{k}" for k in ks) + " | MRR |",
             "|---|---|" + "---|" * (len(ks) + 1)]
    for nome, linhas in configs:
        m = metricas([l["posicao"] for l in linhas], ks)
        saida.append(f"| {nome} | {m['n']} | " + " | ".join(f"{m[f'hit@{k}']:.2f}" for k in ks)
                     + f" | {m['MRR']:.3f} |")
    return "\n".join(saida) + "\n"


def comparar(linhas_vet: list[dict], linhas_rr: list[dict], n_candidatos: int) -> str:
    """Tabela lado a lado: posição da regra certa só com vetor x com re-ranking."""
    teto = sum(1 for l in linhas_vet if l["posicao"] is not None and l["posicao"] <= n_candidatos)
    saida = [
        f"Teto do re-ranking: em **{teto}/{len(linhas_vet)}** consultas a regra certa está entre os "
        f"{n_candidatos} candidatos da busca vetorial (as outras o reranker não consegue resgatar).\n",
        "| consulta | tipo | só vetor | vetor + rerank | variação |",
        "|---|---|---|---|---|",
    ]
    for v, r in zip(linhas_vet, linhas_rr):
        pv, pr = v["posicao"], r["posicao"]
        if pv is None or pr is None:
            var = "-"
        else:
            var = "melhorou" if pr < pv else ("piorou" if pr > pv else "igual")
        saida.append(f"| {v['id']} | {v['tipo']} | {pv or '-'} | {pr or '-'} | {var} |")
    return "\n".join(saida) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variante", choices=VARIANTES)
    ap.add_argument("--conjunto", choices=sorted(CONJUNTOS), default="dev",
                    help="dev = consultas_avaliacao.json (usado para desenvolver); "
                         "teste = consultas_teste.json (não usado para ajustar nada)")
    ap.add_argument("--rerank", action="store_true", help="avalia também vetorial + re-ranking")
    ap.add_argument("--hibrido", action="store_true", help="avalia também a busca híbrida (vetor + BM25)")
    ap.add_argument("--candidatos", type=int, default=50, help="quantos candidatos o reranker relê (padrão 50)")
    args = ap.parse_args()

    variantes = [args.variante] if args.variante else [v for v in VARIANTES if caminho_indice(v).exists()]
    if not variantes:
        raise SystemExit("Nenhum índice encontrado. Rode antes: python indexar.py")

    consultas = carregar_consultas(AQUI / CONJUNTOS[args.conjunto])
    emb, _ = criar_embedding()
    reranker = None
    if args.rerank:
        reranker, disp = criar_reranker()
        print(f"Reranker: {MODELO_RERANKER} em {disp} | candidatos = {args.candidatos}")

    n = args.candidatos
    texto = [f"# Avaliação da recuperação (Entrega 2) - conjunto: {args.conjunto} ({len(consultas)} consultas)\n"]
    for v in variantes:
        index = carregar_indice(v, emb)
        configs = [("vetor", avaliar_indice(index, consultas))]
        if args.rerank:
            configs.append((f"vetor + rerank({n})", avaliar_indice(index, consultas, reranker, n)))
        if args.hibrido:
            configs.append(("híbrido (vetor+BM25)", avaliar_indice(index, consultas, hibrido=True)))
            if args.rerank:
                configs.append((f"híbrido + rerank({n})", avaliar_indice(index, consultas, reranker, n, hibrido=True)))
        blocos = [f"## Variante: {v}\n", resumo_configs(configs)]
        for nome, linhas in configs:
            blocos.append(formatar(f"{v} - {nome}", linhas))
        base = configs[0][1]
        for nome, linhas in configs[1:]:
            blocos.append(f"### vetor x {nome}\n")
            blocos.append(comparar(base, linhas, n))
        for b in blocos:
            print(b)
        texto += blocos

    sufixo = ("_rerank" if args.rerank else "") + ("_hibrido" if args.hibrido else "")
    nome = f"resultados_avaliacao{sufixo}.md" if args.conjunto == "dev" else f"resultados_teste{sufixo}.md"
    destino = AQUI / nome
    destino.write_text("\n".join(texto), encoding="utf-8")
    print(f"Resultado gravado em {destino}")


if __name__ == "__main__":
    main()
