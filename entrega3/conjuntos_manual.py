# -*- coding: utf-8 -*-
"""
Entrega 3, passo 4 - conjuntos de avaliacao do manual (desenvolvimento e teste), definidos ANTES de indexar.

O gabarito e uma lista de FOLHAS do manual (subsecao x.y.z, secao x.y ou abertura n.0 do capitulo), nunca
um id de chunk, para nao depender da estrategia de chunking.
  - criterio "chave": folhas cujo texto contem todas as construcoes-chave da resposta (busca exata no
    texto extraido, feita ao montar o conjunto, antes de existir indice);
  - criterio "manual": folhas decididas na leitura, quando a resposta e um conceito sem construcao unica.
Um chunk acerta se a sua folha principal esta no gabarito (estrategia C: a folha do no; estrategia B:
a folha com mais caracteres dentro do chunk).

Uso (na pasta trabalho/entrega3):
    python conjuntos_manual.py sortear   # sorteia as folhas do teste (rodado uma vez, em 02/11/2026)
    python conjuntos_manual.py validar   # confere os dois arquivos contra saida/manual_blocos.jsonl
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BLOCOS = AQUI / "saida" / "manual_blocos.jsonl"
DEV = AQUI / "consultas_manual_dev.json"
TESTE = AQUI / "consultas_manual_teste.json"
SEMENTE = 20261102
N_TESTE = 20


def ordem_folha(folha: str):
    return tuple(int(x) for x in folha.split("."))


def carregar_blocos(caminho: Path = BLOCOS) -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def texto_por_folha(blocos) -> dict[str, str]:
    t = defaultdict(str)
    for b in blocos:
        if b["tipo"] != "titulo":
            t[b["folha"]] += "\n" + b["texto"]
    return dict(t)


def paginas_por_folha(blocos) -> dict[str, list[int]]:
    p = defaultdict(set)
    for b in blocos:
        if b["tipo"] != "titulo":
            p[b["folha"]].update(range(b["pagina_impressa_ini"], b["pagina_impressa_fim"] + 1))
    return {f: [min(v), max(v)] for f, v in p.items()}


def folhas_com_chaves(blocos, chaves) -> list[str]:
    t = texto_por_folha(blocos)
    return sorted((f for f, tx in t.items() if all(k.lower() in tx.lower() for k in chaves)), key=ordem_folha)


def populacao_teste(blocos, consultas_dev) -> list[str]:
    """Folhas com conteudo alem do titulo, menos TODAS as folhas que aparecem em algum gabarito do dev."""
    com_conteudo = {f for f, tx in texto_por_folha(blocos).items() if tx.strip()}
    usadas_no_dev = {f for c in consultas_dev for f in c["gabarito"]}
    return sorted(com_conteudo - usadas_no_dev, key=ordem_folha)


def sortear(populacao, semente: int = SEMENTE, n: int = N_TESTE) -> list[str]:
    return sorted(random.Random(semente).sample(populacao, n), key=ordem_folha)


def validar(caminho: Path, blocos) -> list[str]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    t, pags = texto_por_folha(blocos), paginas_por_folha(blocos)
    erros = []
    ids = [c["id"] for c in dados["consultas"]]
    if len(ids) != len(set(ids)):
        erros.append("ids repetidos")
    for c in dados["consultas"]:
        cid = c["id"]
        faltam = [f for f in c["gabarito"] if f not in t]
        if faltam:
            erros.append(f"{cid}: folhas inexistentes {faltam}")
            continue
        if c["folha_origem"] not in c["gabarito"]:
            erros.append(f"{cid}: folha de origem fora do gabarito")
        if c["evidencia"] not in t[c["folha_origem"]]:
            erros.append(f"{cid}: evidencia nao esta na folha de origem")
        if c["criterio"] == "chave" and c["gabarito"] != folhas_com_chaves(blocos, c["chave"]):
            erros.append(f"{cid}: gabarito difere da busca pelas chaves {folhas_com_chaves(blocos, c['chave'])}")
        if c["paginas_impressas"] != {f: pags[f] for f in c["gabarito"]}:
            erros.append(f"{cid}: paginas nao conferem")
    return erros


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validar"
    blocos = carregar_blocos()
    dev = json.loads(DEV.read_text(encoding="utf-8"))["consultas"]
    if cmd == "sortear":
        pop = populacao_teste(blocos, dev)
        print(json.dumps({"semente": SEMENTE, "n": N_TESTE, "tamanho_populacao": len(pop),
                          "populacao": pop, "sorteadas": sortear(pop)}, ensure_ascii=False))
        return
    falhas = 0
    for caminho in (DEV, TESTE):
        if not caminho.exists():
            print(f"{caminho.name}: ainda nao existe")
            continue
        erros = validar(caminho, blocos)
        if caminho == TESTE:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            s = dados["_sobre"]["sorteio"]
            origens = sorted((c["folha_origem"] for c in dados["consultas"]), key=ordem_folha)
            if sortear(s["populacao"], s["semente"], s["n"]) != s["sorteadas"]:
                erros.append("o sorteio registrado nao se reproduz com a semente e a populacao registradas")
            if origens != s["sorteadas"]:
                erros.append("as folhas de origem do teste nao sao as sorteadas")
            no_dev = sorted({f for c in dados["consultas"] for f in c["gabarito"]} & {f for c in dev for f in c["gabarito"]})
            if no_dev:
                erros.append(f"folhas em gabarito do teste e do dev ao mesmo tempo: {no_dev}")
        falhas += len(erros)
        print(f"{caminho.name}: " + ("ok" if not erros else "; ".join(erros)))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
