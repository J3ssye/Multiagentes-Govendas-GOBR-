# -*- coding: utf-8 -*-
"""
gobr_parser.py — Leitor determinístico de arquivos GOBR (gorules) -> representação estruturada (JSON).

Por que determinístico: a explicação precisa ser FIEL e COMPLETA (AIMA §28.3.4). Um parser
lê 100% dos blocos e preserva a ordem; o LLM só entra depois, para redigir o texto.

Estrutura reconhecida (Manual GoBR §2.2 e §7.1):
    version 1.0
    time "nome":            vendedores <seleção>                         (§3)
    carteira "nome":        clientes <seleção> [quando <filtros>]        (§4)
    segmentacao "nome":     clientes <seleção> [quando <filtros>]        (§4)
    parametros "nome":      do time(...)|da carteira(...)|da segmentacao(...)   -> fonte      (§7.1 passo 1)
                            [filtros temporais]                                  -> temporais  (§7.1 passo 2, §5)
                            [quando <filtro> (e|ou <filtro>)*]                   -> filtros    (§7.1 passo 3, §6)
                            frequencia ... | preferencia ... | nao agendar | fixo | roteirizavel | restrito ...
                                                                                 -> acoes      (§7.1 passo 4, §7.3-7.5)
                            [sem choque ...]                                     -> conflito   (§7.1 passo 5, §7.3.8)

A indentação dos arquivos é inconsistente (tabs e espaços misturados), então o parser classifica
cada linha pela PALAVRA-CHAVE inicial, não pela indentação.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

# --------------------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------------------

def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normaliza(s: str) -> str:
    """minúsculas, sem acento, espaços colapsados — usado só para CLASSIFICAR, nunca para exibir."""
    return re.sub(r"\s+", " ", sem_acento(s).lower()).strip()


def colapsa(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def tira_comentario(linha: str) -> str:
    """Remove '#' até o fim da linha, ignorando '#' dentro de aspas."""
    dentro = False
    for i, c in enumerate(linha):
        if c == '"':
            dentro = not dentro
        elif c == "#" and not dentro:
            return linha[:i]
    return linha


def parenteses_abertos(s: str) -> int:
    n, dentro = 0, False
    for c in s:
        if c == '"':
            dentro = not dentro
        elif not dentro:
            n += (c == "(") - (c == ")")
    return n


HEADER_RE = re.compile(
    r'^(?P<cat>limpar\s+parametros|time|carteira|segmentacao|segmentação|parametros|parâmetros|alertas?|tags?)\s+"(?P<nome>[^"]*)"\s*:?\s*$',
    re.I,
)
VERSION_RE = re.compile(r"^version\s+(\S+)", re.I)
FONTE_RE = re.compile(r"^(do|da|dos|das|na|no)\s+(time|carteira|segmentacao|segmentação)\s*\((?P<args>.*)\)\s*$", re.I)
ARGS_RE = re.compile(r'"([^"]*)"')

# palavras que ABREM uma cláusula dentro de um bloco (comparadas sem acento/minúsculas)
INICIO_ACAO = [
    ("nao agendar", "nao_agendar"),
    ("frequencia", "frequencia"),
    ("preferencia", "preferencia"),
    ("nao roteirizavel", "nao_roteirizavel"),
    ("roteirizavel", "roteirizavel"),
    ("fixo", "fixo"),
    ("restrito", "restricao_semana"),
]


def _classifica(l: str):
    """Retorna o tipo de cláusula que a linha (normalizada) abre, ou None se for continuação."""
    if l.startswith("vendedores"):
        return "selecao_vendedores"
    if l.startswith("clientes "):
        return "selecao_clientes"
    if FONTE_RE.match(l):
        return "fonte"
    if l == "quando" or l.startswith("quando "):
        return "quando"
    if l.startswith("sem choque"):
        return "conflito"
    for prefixo, tipo in INICIO_ACAO:
        if l == prefixo or l.startswith(prefixo + " ") or l.startswith(prefixo + "("):
            return "acao:" + tipo
    return None


# --------------------------------------------------------------------------------------
# divisão de condições em átomos ligados por "e"/"ou"
# --------------------------------------------------------------------------------------
_UNIDADE = r"(?:dias?|semanas?|meses|mes|anos?|bimestres?|trimestres?|semestres?)"
_PROTEGE_ENTRE = re.compile(
    r"(entre\s+(?:'[^']*'|\d+(?:\s+" + _UNIDADE + r")?|os\s+dias\s+\d+))\s+e\s+", re.I
)
_JUNTA_AO_ANTERIOR = re.compile(r"^(maior que|menor que|igual a|indefinid|no maximo|no minimo)", re.I)


def divide_condicoes(texto: str):
    """'a e b ou c' -> [(None,'a'),('e','b'),('ou','c')], respeitando aspas, parênteses e 'entre X e Y'."""
    texto = colapsa(texto)
    texto = _PROTEGE_ENTRE.sub(lambda m: m.group(1) + " \x00 ", texto)
    partes, atual, conector = [], [], None
    prof, dentro, i = 0, False, 0
    while i < len(texto):
        c = texto[i]
        if c == '"':
            dentro = not dentro
        elif not dentro and c == "(":
            prof += 1
        elif not dentro and c == ")":
            prof -= 1
        if not dentro and prof == 0 and c == " ":
            resto = texto[i + 1:]
            m = re.match(r"(e|ou)\s+", resto)
            if m:
                partes.append((conector, "".join(atual).strip()))
                conector, atual = m.group(1), []
                i += 1 + m.end()
                continue
        atual.append(c)
        i += 1
    partes.append((conector, "".join(atual).strip()))
    # desfaz a proteção e junta pedaços que não são filtros sozinhos (ex.: "... menor que R$ 10 e maior que R$ 5")
    saida = []
    for con, at in partes:
        at = at.replace("\x00", "e")
        if not at:
            continue
        if saida and _JUNTA_AO_ANTERIOR.match(normaliza(at)):
            c0, a0 = saida[-1]
            saida[-1] = (c0, f"{a0} {con} {at}")
        else:
            saida.append((con, at))
    return saida


# --------------------------------------------------------------------------------------
# parser
# --------------------------------------------------------------------------------------

def parse_texto(texto: str, arquivo: str = "<texto>") -> dict:
    # corrige o caso de "version" grudado no fim de uma linha (há um arquivo assim no corpus)
    texto = re.sub(r"(\S)(version\s+\d+\.\d+)", r"\1\n\2", texto)
    # remove caracteres de controle invisíveis (há um \x01 perdido em regra_140)
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", texto)
    blocos_brutos, avisos, comentarios = [], [], []
    versao = None
    atual = None
    for n, bruta in enumerate(texto.splitlines(), 1):
        if bruta.strip().startswith("#"):
            comentarios.append(bruta.strip().lstrip("#").strip())
            continue
        linha = tira_comentario(bruta).rstrip()
        if not linha.strip():
            continue
        tem_indent = linha[:1] in (" ", "\t")
        conteudo = linha.strip()
        if not tem_indent:
            mv = VERSION_RE.match(conteudo)
            if mv:
                versao = mv.group(1)
                continue
            mh = HEADER_RE.match(conteudo)
            if mh:
                atual = {"categoria": normaliza(mh.group("cat")).replace("parametros", "parametros"),
                         "nome": mh.group("nome"), "linha": n, "linhas": []}
                blocos_brutos.append(atual)
                continue
            # linha sem indentação que não é cabeçalho: trata como continuação do bloco atual
            if atual is None:
                avisos.append(f"linha {n} fora de bloco ignorada: {conteudo!r}")
                continue
        if atual is None:
            avisos.append(f"linha {n} fora de bloco ignorada: {conteudo!r}")
            continue
        atual["linhas"].append((n, conteudo))

    blocos = [_monta_bloco(b, avisos) for b in blocos_brutos]
    times = [b for b in blocos if b["categoria"] == "time"]
    carteiras = [b for b in blocos if b["categoria"] in ("carteira", "segmentacao")]
    params = [b for b in blocos if b["categoria"] in ("parametros", "limpar parametros")]
    outros = [b for b in blocos if b not in times and b not in carteiras and b not in params]
    for i, p in enumerate(params, 1):
        p["ordem"] = i

    ir = {
        "arquivo": arquivo,
        "versao": versao,
        "comentarios": comentarios,
        "times": times,
        "carteiras": carteiras,
        "parametros": params,
        "outros_blocos": outros,
        "avisos": avisos,
    }
    ir["analise"] = analisa(ir)
    return ir


def _monta_bloco(b: dict, avisos: list) -> dict:
    # 1) agrupa linhas em cláusulas
    clausulas = []  # cada uma: {"tipo":..., "texto":...}
    viu_quando = viu_acao = False
    for n, conteudo in b["linhas"]:
        l = normaliza(conteudo)
        # continua cláusula com parênteses abertos (listas longas de cidades/ids quebradas em várias linhas)
        if clausulas and parenteses_abertos(clausulas[-1]["texto"]) > 0:
            clausulas[-1]["texto"] += " " + conteudo
            continue
        tipo = _classifica(l)
        if tipo is None:
            if re.match(r"^(e|ou)\b", l) and clausulas:
                clausulas[-1]["texto"] += " " + conteudo
                continue
            ult = clausulas[-1]["tipo"] if clausulas else None
            if b["categoria"] == "parametros" and ult in ("fonte", "temporal") and not viu_quando and not viu_acao:
                tipo = "temporal"  # §7.1 passo 2: filtros temporais vêm logo após a fonte
            elif clausulas:
                clausulas[-1]["texto"] += " " + conteudo
                continue
            else:
                tipo = "desconhecido"
                avisos.append(f"[{b['nome']}] linha {n} não classificada: {conteudo!r}")
        if tipo == "quando":
            viu_quando = True
        if tipo.startswith("acao:"):
            viu_acao = True
        clausulas.append({"tipo": tipo, "texto": conteudo, "linha": n})

    for c in clausulas:
        c["texto"] = colapsa(c["texto"])

    bloco = {"categoria": b["categoria"], "nome": b["nome"], "linha": b["linha"]}
    cat = b["categoria"]
    if cat == "time":
        sel = [c["texto"] for c in clausulas if c["tipo"] == "selecao_vendedores"]
        bloco["selecao"] = sel[0][len("vendedores"):].strip() if sel else None
        bloco["extras"] = [c["texto"] for c in clausulas if c["tipo"] != "selecao_vendedores"]
        return bloco

    fonte = None
    temporais, filtros, acoes, conflito, extras = [], [], [], [], []
    selecao = None
    for c in clausulas:
        t, txt = c["tipo"], c["texto"]
        if t == "fonte":
            m = FONTE_RE.match(normaliza(txt))
            fonte = {"tipo": sem_acento(m.group(2).lower()), "nomes": ARGS_RE.findall(txt), "texto": txt}
        elif t == "selecao_clientes":
            selecao = txt[len("clientes"):].strip()
        elif t == "temporal":
            temporais.append(txt)
        elif t == "quando":
            corpo = txt[len("quando"):].strip()
            for con, at in divide_condicoes(corpo):
                filtros.append({"conector": con if filtros or con else None, "texto": at})
        elif t.startswith("acao:"):
            acoes.append({"tipo": t.split(":", 1)[1], "texto": txt})
        elif t == "conflito":
            conflito.append(txt)
        else:
            extras.append(txt)
    if filtros:
        filtros[0]["conector"] = None
    bloco.update({
        "fonte": fonte,
        "selecao": selecao,
        "temporais": temporais,
        "filtros": filtros,
        "acoes": acoes,
        "conflito": conflito,
        "extras": extras,
    })
    return bloco


# --------------------------------------------------------------------------------------
# análise determinística (base para os "pontos de atenção" / proatividade do agente)
# --------------------------------------------------------------------------------------
_NUM_DIAS_NOME = re.compile(r"(\d+)\s*(?:d\b|dias?\b)", re.I)
_NUM_DIA_NOME = re.compile(r"\bdia\s+(\d+)\b", re.I)


def _chave_fonte(p):
    f = p.get("fonte") or {}
    return (f.get("tipo"), tuple(f.get("nomes") or []))


def analisa(ir: dict) -> dict:
    params = [p for p in ir["parametros"] if p["categoria"] == "parametros"]
    achados = []
    # (1) "Sem repetição: clientes parametrizados em uma regra anterior não são reprocessados
    #      por regras subsequentes. A ordem importa." (Manual §7.6)
    #     -> um bloco SEM filtro de cliente pega todos os restantes da fonte; blocos seguintes da
    #        mesma fonte ficam inalcançáveis (salvo se houver filtro temporal, que muda o dia de execução).
    vistos_pega_tudo = {}
    for p in params:
        k = _chave_fonte(p)
        if k in vistos_pega_tudo:
            achados.append({
                "tipo": "bloco_inalcancavel",
                "bloco": p["ordem"],
                "texto": (f"O bloco {p['ordem']} (\"{p['nome']}\") vem depois do bloco {vistos_pega_tudo[k]}, "
                          f"que não tem filtro de cliente e já parametriza todos os clientes restantes da mesma fonte. "
                          f"Pela regra 'sem repetição' (Manual §7.6), este bloco não deve alcançar nenhum cliente."),
            })
        if not p["filtros"] and not p["temporais"]:
            vistos_pega_tudo.setdefault(k, p["ordem"])
    # (2) fonte sem bloco final "pega-tudo": clientes que não se enquadram em nenhum bloco
    #     não recebem parametrização desta regra (regras incrementais, Manual §7.6)
    fontes = {}
    for p in params:
        fontes.setdefault(_chave_fonte(p), []).append(p)
    for k, ps in fontes.items():
        if not any(not p["filtros"] and not p["temporais"] for p in ps):
            nomes = ", ".join(k[1]) if k[1] else "?"
            achados.append({
                "tipo": "sem_regra_final",
                "bloco": None,
                "texto": (f"Não há bloco final sem filtro para a fonte {k[0]}({nomes}): clientes que não se "
                          f"enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a "
                          f"configuração que já tinham (regras incrementais, Manual §7.6)."),
            })
    # (3) números no NOME do bloco que não aparecem no código (o nome é uma 'história'; o filtro é a decisão).
    #     Considera também os blocos ANTERIORES da mesma fonte, porque a ordem cria intervalos
    #     (ex.: "em 90 dias" depois de "em 60 dias" = entre 60 e 90).
    for p in params:
        anteriores = [q for q in params if q["ordem"] <= p["ordem"] and _chave_fonte(q) == _chave_fonte(p)]
        codigo = " ".join(
            t for q in anteriores
            for t in [*(f["texto"] for f in q["filtros"]), *q["temporais"], *(a["texto"] for a in q["acoes"])]
        )
        nums_codigo = set(re.findall(r"\d+", codigo))
        # períodos nomeados equivalem a dias (Manual §7.4.1): "semanal()" = 7, "quinzenal()" = 15 ...
        for palavra, dias in (("diaria", "1"), ("semanal", "7"), ("quinzenal", "15"), ("mensal", "30"),
                              ("bimestral", "60"), ("trimestral", "90"), ("semestral", "180"), ("anual", "365")):
            if palavra in normaliza(codigo):
                nums_codigo.add(dias)
        nums_nome = set(_NUM_DIAS_NOME.findall(p["nome"])) | set(_NUM_DIA_NOME.findall(p["nome"]))
        faltam = sorted(n for n in nums_nome if n not in nums_codigo and n != "0")
        if faltam:
            achados.append({
                "tipo": "nome_diverge_do_codigo",
                "bloco": p["ordem"],
                "texto": (f"O nome do bloco {p['ordem']} (\"{p['nome']}\") cita {', '.join(faltam)} dia(s), "
                          f"mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale."),
            })
    # (4) nao agendar combinado com frequência/preferência no mesmo bloco (proibido, Manual §7.3.4)
    for p in params:
        tipos = {a["tipo"] for a in p["acoes"]}
        if "nao_agendar" in tipos and tipos & {"frequencia", "preferencia"}:
            achados.append({
                "tipo": "nao_agendar_com_frequencia",
                "bloco": p["ordem"],
                "texto": (f"O bloco {p['ordem']} combina 'nao agendar' com frequência/preferência, o que o "
                          f"Manual §7.3.4 diz não ser possível."),
            })
    # (5) referência a time/carteira não definidos no arquivo
    definidos = {("time", t["nome"]) for t in ir["times"]} | {(c["categoria"], c["nome"]) for c in ir["carteiras"]}
    indefinidos = {}
    for p in params:
        f = p.get("fonte")
        if not f:
            achados.append({"tipo": "sem_fonte", "bloco": p["ordem"],
                            "texto": f"O bloco {p['ordem']} não declara a fonte de clientes (do time/da carteira)."})
            continue
        for nome in f["nomes"]:
            if (f["tipo"], nome) not in definidos:
                indefinidos.setdefault((f["tipo"], nome), []).append(p["ordem"])
    for (tipo, nome), ords in indefinidos.items():
        achados.append({"tipo": "fonte_indefinida", "bloco": ords[0],
                        "texto": (f"{tipo}(\"{nome}\") é usado nos blocos {', '.join(map(str, ords))}, mas não é "
                                  f"definido neste arquivo (pode estar em outro arquivo de regras do cliente).")})
    return {
        "n_blocos_parametros": len(params),
        "n_nao_agendar": sum(any(a["tipo"] == "nao_agendar" for a in p["acoes"]) for p in params),
        "achados": achados,
    }


def parse_arquivo(caminho: Path, raiz: Path | None = None) -> dict:
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    rel = str(caminho.relative_to(raiz)) if raiz else caminho.name
    ir = parse_texto(texto, rel)
    ir["sha1"] = hashlib.sha1(re.sub(r"\s+", " ", texto).strip().encode()).hexdigest()
    ir["fonte_gobr"] = texto
    return ir


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(json.dumps(parse_arquivo(Path(arg)), ensure_ascii=False, indent=2))
