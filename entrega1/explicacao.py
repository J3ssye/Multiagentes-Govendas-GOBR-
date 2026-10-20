# -*- coding: utf-8 -*-
"""
explicacao.py — monta a FICHA de cada regra (entrada do LLM), a explicação determinística
(sem LLM), o texto indexável e a VERIFICAÇÃO automática de fidelidade/completude.
"""
from __future__ import annotations

import re

from gobr_parser import normaliza
from glossario import (explica_acao, explica_filtro, explica_selecao_clientes, explica_temporal,
                       explica_vendedores)


# --------------------------------------------------------------------------------------
# enriquecimento: anexa o significado (glossário) a cada elemento da IR
# --------------------------------------------------------------------------------------

def enriquece(ir: dict) -> dict:
    for t in ir["times"]:
        t["significado"] = explica_vendedores(t.get("selecao"))
    for c in ir["carteiras"]:
        c["significado_selecao"] = explica_selecao_clientes(c.get("selecao"))
        for f in c.get("filtros", []):
            f.update(explica_filtro(f["texto"]))
    for p in ir["parametros"]:
        for f in p.get("filtros", []):
            f.update(explica_filtro(f["texto"]))
        p["temporais_explicados"] = [explica_temporal(t) for t in p.get("temporais", [])]
        for a in p.get("acoes", []):
            a.update(explica_acao(a["tipo"], a["texto"]))
    return ir


def _fonte_txt(p: dict) -> str:
    f = p.get("fonte")
    if not f:
        return "(fonte não declarada)"
    rot = {"time": "time", "carteira": "carteira", "segmentacao": "segmentação"}.get(f["tipo"], f["tipo"])
    nomes = ", ".join(f'"{n}"' for n in f["nomes"])
    return f"clientes do(a) {rot} {nomes}"


def _filtros_txt(p: dict, com_gobr: bool) -> list[str]:
    if not p.get("filtros"):
        return ["(sem filtro de cliente: pega TODOS os clientes da fonte que ainda não foram parametrizados por blocos anteriores)"]
    linhas = []
    for f in p["filtros"]:
        con = {"e": "E ", "ou": "OU "}.get(f.get("conector"), "")
        sig = f.get("significado") or "(sem tradução no glossário — interpretar pelo texto GOBR)"
        sec = f" [{f['secao']}]" if f.get("secao") else ""
        gobr = f'   <- GOBR: {f["texto"]}' if com_gobr else ""
        linhas.append(f"{con}{sig}{sec}{gobr}")
    return linhas


# --------------------------------------------------------------------------------------
# FICHA (entrada do LLM): tudo o que o LLM pode usar — e nada além disso
# --------------------------------------------------------------------------------------

def ficha(ir: dict) -> str:
    L = [f"ARQUIVO: {ir['arquivo']}"]
    if ir.get("comentarios"):
        L.append("COMENTÁRIOS DO AUTOR (contexto, não são regras): " + " | ".join(c for c in ir["comentarios"] if c)[:600])
    L.append("TIMES DE VENDEDORES [Manual §3]:")
    for t in ir["times"] or []:
        L.append(f'- "{t["nome"]}": {t["significado"]}   <- GOBR: vendedores {t.get("selecao")}')
    if not ir["times"]:
        L.append("- (nenhum)")
    if ir["carteiras"]:
        L.append("CARTEIRAS / SEGMENTAÇÕES [Manual §4]:")
        for c in ir["carteiras"]:
            L.append(f'- {c["categoria"]} "{c["nome"]}": {c["significado_selecao"]}   <- GOBR: clientes {c.get("selecao")}')
            for f in _filtros_txt(c, True) if c.get("filtros") else []:
                L.append(f"    filtro: {f}")
    L.append("BLOCOS DE PARAMETRIZAÇÃO, NA ORDEM EM QUE SÃO AVALIADOS [Manual §7]:")
    L.append("(Regra 'sem repetição', Manual §7.6: um cliente parametrizado por um bloco NÃO é reprocessado pelos blocos seguintes da mesma fonte.)")
    for p in ir["parametros"]:
        L.append(f'[{p["ordem"]}] "{p["nome"]}"')
        L.append(f"    Fonte: {_fonte_txt(p)}")
        for t in p.get("temporais_explicados", []):
            L.append(f"    Quando a regra roda: {t['significado']} [{t['secao']}]")
        fl = _filtros_txt(p, True)
        L.append(f"    Filtros: {fl[0]}")
        for x in fl[1:]:
            L.append(f"             {x}")
        if not p.get("acoes"):
            L.append("    Ações: (nenhuma ação declarada)")
        for a in p.get("acoes", []):
            sec = f" [{a['secao']}]" if a.get("secao") else ""
            L.append(f"    Ação: {a.get('significado') or a['texto']}{sec}   <- GOBR: {a['texto']}")
        for c in p.get("conflito", []):
            L.append(f"    Conflito: evitar choque de dias com {c[len('sem choque'):].strip()} [§7.3.8]   <- GOBR: {c}")
    ach = ir.get("analise", {}).get("achados", [])
    L.append("PONTOS DE ATENÇÃO DETECTADOS AUTOMATICAMENTE:")
    L.extend(f"- {a['texto']}" for a in ach) if ach else L.append("- (nenhum)")
    return "\n".join(L)


# --------------------------------------------------------------------------------------
# EXPLICAÇÃO DETERMINÍSTICA (sem LLM) — no mesmo formato JSON que o LLM devolve
# --------------------------------------------------------------------------------------

def _acao_curta(p: dict) -> str:
    partes = []
    for a in p.get("acoes", []):
        if a["tipo"] == "nao_agendar":
            partes.append("Não agendar")
        elif a["tipo"] == "frequencia" and a.get("dias"):
            partes.append(f"{a['dias']} dias")
        else:
            partes.append(a.get("significado") or a["texto"])
    return "; ".join(partes) or "(sem ação)"


def explicacao_deterministica(ir: dict) -> dict:
    times = "; ".join(f'"{t["nome"]}" = {t["significado"]}' for t in ir["times"]) or "nenhum time definido"
    segs = []
    for p in ir["parametros"]:
        crit = " ".join(_filtros_txt(p, False))
        obs = "; ".join(t["significado"] for t in p.get("temporais_explicados", []))
        segs.append({"bloco": p["ordem"], "nome": p["nome"], "criterio": f"{_fonte_txt(p)}: {crit}",
                     "acao": _acao_curta(p), "observacao": obs})
    return {
        "titulo": ir["arquivo"].split("/")[-1].rsplit(".", 1)[0],
        "resumo": (f"Times: {times}. {len(ir['parametros'])} bloco(s) de parametrização avaliados em ordem; "
                   f"um cliente parametrizado em um bloco não é reprocessado nos seguintes (Manual §7.6)."),
        "segmentos": segs,
        "pontos_de_atencao": [a["texto"] for a in ir.get("analise", {}).get("achados", [])],
    }


# --------------------------------------------------------------------------------------
# TEXTO INDEXÁVEL (o que será transformado em embedding na entrega de 27/10)
# --------------------------------------------------------------------------------------

def texto_indexavel(exp: dict) -> str:
    L = [exp.get("titulo", "").strip(), exp.get("resumo", "").strip()]
    for s in exp.get("segmentos", []):
        linha = f"- {s.get('nome', '').strip()}: {s.get('criterio', '').strip()} -> {s.get('acao', '').strip()}"
        if s.get("observacao"):
            linha += f" ({s['observacao'].strip()})"
        L.append(linha)
    if exp.get("pontos_de_atencao"):
        L.append("Pontos de atenção: " + " ".join(p.strip() for p in exp["pontos_de_atencao"]))
    return "\n".join(x for x in L if x)


# --------------------------------------------------------------------------------------
# VERIFICAÇÃO automática (fidelidade + completude, AIMA §28.3.4)
# --------------------------------------------------------------------------------------

def _sem_milhar(txt: str) -> str:
    # "25.000" / "25,000" -> "25000" (o LLM pode formatar valores monetários)
    return re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", txt)


def _numeros_fora_de_aspas(txt: str) -> set[str]:
    txt = _sem_milhar(txt)
    sem_listas = re.sub(r'"[^"]*"', " ", txt)
    sem_listas = re.sub(r"'[^']*'", " ", sem_listas)
    return {n.lstrip("0") or "0" for n in re.findall(r"\d+", sem_listas)} - {"0"}


def _numeros_texto(txt: str) -> set[str]:
    return {n.lstrip("0") or "0" for n in re.findall(r"\d+", _sem_milhar(txt))}


_DIAS = ("segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo", "uteis", "prefer")


def verifica(ir: dict, exp: dict) -> list[str]:
    """Lista de problemas (vazia = passou). Compara a explicação gerada com a IR determinística."""
    problemas = []
    blocos = {p["ordem"]: p for p in ir["parametros"]}
    segs = exp.get("segmentos") or []
    por_bloco = {}
    for s in segs:
        try:
            por_bloco.setdefault(int(s.get("bloco")), []).append(s)
        except (TypeError, ValueError):
            problemas.append(f"segmento sem número de bloco válido: {s.get('nome')!r}")
    faltando = sorted(set(blocos) - set(por_bloco))
    sobrando = sorted(set(por_bloco) - set(blocos))
    if faltando:
        problemas.append(f"blocos sem segmento correspondente: {faltando}")
    if sobrando:
        problemas.append(f"segmentos com número de bloco inexistente: {sobrando}")
    for k, ss in por_bloco.items():
        if len(ss) > 1 and k in blocos:
            problemas.append(f"bloco {k} aparece em {len(ss)} segmentos (deve ser 1)")
    for k, p in blocos.items():
        if k not in por_bloco:
            continue
        s = por_bloco[k][0]
        acao = normaliza(f"{s.get('acao', '')} {s.get('observacao', '')}")
        criterio = normaliza(f"{s.get('criterio', '')} {s.get('observacao', '')}")
        tudo = normaliza(" ".join(str(s.get(c, "")) for c in ("nome", "criterio", "acao", "observacao")))
        for a in p.get("acoes", []):
            t = a["tipo"]
            if t == "nao_agendar" and "nao agend" not in acao and "nao sera agend" not in acao and "nao e agend" not in acao:
                problemas.append(f"bloco {k}: a ação 'não agendar' não aparece no texto")
            if t == "frequencia":
                nums = _numeros_fora_de_aspas(a["texto"])
                faltam = sorted(n for n in nums if n not in _numeros_texto(acao))
                if faltam:
                    problemas.append(f"bloco {k}: número(s) da frequência ausentes na ação: {faltam} (GOBR: {a['texto']})")
                elif a.get("dias") and not nums:  # semanal(), mensal()...
                    palavra = normaliza(a["texto"]).split()[-1].rstrip("()")
                    if str(a["dias"]) not in _numeros_texto(acao) and palavra not in acao:
                        problemas.append(f"bloco {k}: frequência ({a['texto']}) não aparece na ação")
            if t == "preferencia" and not any(d in tudo for d in _DIAS):
                problemas.append(f"bloco {k}: a preferência de dias não foi mencionada (GOBR: {a['texto']})")
            if t == "fixo" and "fix" not in tudo:
                problemas.append(f"bloco {k}: a marcação 'fixo' não foi mencionada")
            if t == "roteirizavel" and "roteiriz" not in tudo:
                problemas.append(f"bloco {k}: 'roteirizável' não foi mencionado")
        nums_filtro = set()
        for f in p.get("filtros", []):
            nums_filtro |= _numeros_fora_de_aspas(f["texto"])
        for tmp in p.get("temporais", []):
            nums_filtro |= _numeros_fora_de_aspas(tmp)
        faltam = sorted(n for n in nums_filtro if n not in _numeros_texto(criterio))
        if faltam:
            problemas.append(f"bloco {k}: número(s) dos filtros ausentes no critério/observação: {faltam}")
    for campo in ("titulo", "resumo"):
        if not str(exp.get(campo, "")).strip():
            problemas.append(f"campo '{campo}' vazio")
    return problemas
