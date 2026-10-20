# -*- coding: utf-8 -*-
"""
glossario.py — Tradução determinística de cada construção GOBR para linguagem de negócio,
com a seção do Manual GoBR de onde o significado foi tirado.

Uso no pipeline:
  1) gera a "ficha" de cada regra (explicação-base, 100% determinística), que é a ENTRADA do LLM;
  2) se o LLM falhar/ficar sem cota, a ficha já é uma explicação utilizável;
  3) informa quais construções NÃO estão no glossário (cobertura), para revisão humana.

Quando o manual não define exatamente a expressão usada no corpus, o significado vem marcado com
"(aprox.)" e a seção mais próxima — lacuna declarada, não preenchida por suposição.
"""
from __future__ import annotations

import re

from gobr_parser import normaliza

# --------------------------------------------------------------------------------------
# auxiliares
# --------------------------------------------------------------------------------------
_DIAS_SEMANA = {"segunda": "segunda", "terca": "terça", "quarta": "quarta", "quinta": "quinta",
                "sexta": "sexta", "sabado": "sábado", "domingo": "domingo"}


def valores(texto_original: str, maximo: int = 6) -> str:
    """Extrai os valores entre aspas (mantendo grafia original) e resume listas longas."""
    vs = re.findall(r'"([^"]*)"', texto_original)
    if not vs:
        m = re.search(r"\((.*)\)", texto_original)
        return m.group(1).strip() if m else ""
    if len(vs) > maximo:
        return ", ".join(vs[:maximo]) + f" e mais {len(vs) - maximo}"
    return ", ".join(vs)


def tempo(t: str) -> str:
    """Traduz condicionais de tempo (Manual §6.11.1, §6.11.2, §6.12, §6.13)."""
    t = t.strip()
    m = re.fullmatch(r"em (\d+) (dias?|semanas?|meses|mes|anos?|bimestres?|trimestres?|semestres?)", t)
    if m:
        return f"nos últimos {m.group(1)} {m.group(2).replace('mes', 'mês') if m.group(2) == 'mes' else m.group(2)}"
    m = re.fullmatch(r"entre '([^']+)' e '([^']+)'", t)
    if m:
        return f"entre as datas {m.group(1)} e {m.group(2)}"
    m = re.fullmatch(r"entre (\d+) (?:dias? )?e (\d+) dias?", t)
    if m:
        return f"entre {m.group(1)} e {m.group(2)} dias atrás"
    m = re.fullmatch(r"nos proximos (\d+) (dias?|semanas?|meses)", t)
    if m:
        return f"nos próximos {m.group(1)} {m.group(2)}"
    m = re.fullmatch(r"em (\d+) (dias?|semanas?|meses) a frente", t)
    if m:
        return f"somente depois de {m.group(1)} {m.group(2)} a partir de hoje"
    m = re.fullmatch(r"ha (\d+) (dias?|semanas?|meses|anos?) atras", t)
    if m:
        return f"antes dos últimos {m.group(1)} {m.group(2)}"
    fixos = {
        "na semana": "na semana atual", "no mes": "no mês atual", "no ano": "no ano atual",
        "na quinzena": "na quinzena atual", "no dia": "hoje", "hoje": "hoje", "de ontem": "ontem",
        "ontem": "ontem", "na semana anterior": "na semana anterior", "no mes anterior": "no mês anterior",
        "no ano passado": "no ano anterior", "no ano anterior": "no ano anterior",
        "no bimestre": "no bimestre atual", "no trimestre": "no trimestre atual", "no semestre": "no semestre atual",
    }
    return fixos.get(t, t)


def _escopo_recencia(esc: str | None) -> str:
    # Manual §6.2: sem qualificador = "algum vendedor do mesmo grupo do vendedor que tem o cliente na carteira"
    return {
        "global": "com qualquer vendedor da empresa",
        "do vendedor": "com o próprio vendedor dono da carteira",
        None: "com algum vendedor do mesmo grupo do dono da carteira",
    }[esc]


def _cmp(t: str) -> str:
    t = t.replace("r$", "R$")
    t = t.replace("maior que", "acima de").replace("menor que", "abaixo de").replace("igual a", "igual a")
    t = t.replace(" ou indefinido", " (ou valor desconhecido)").replace(" ou indefinida", " (ou não calculada)")
    return t


# --------------------------------------------------------------------------------------
# FILTROS DE CLIENTE (§6) — lista de (regex sobre texto normalizado, função -> significado, seção)
# --------------------------------------------------------------------------------------
REGRAS_FILTRO = []


def regra(padrao, secao):
    def deco(fn):
        REGRAS_FILTRO.append((re.compile(padrao), fn, secao))
        return fn
    return deco


@regra(r"^(?P<fora>fora da )?recencia de (?P<ev>positivacao|visita|venda)(?: (?P<esc>global|do vendedor))? (?P<t>.+)$", "§6.2")
def _recencia(m, orig):
    ev = {"positivacao": "compra (positivação)", "visita": "visita", "venda": "venda"}[m["ev"]]
    esc = _escopo_recencia(m["esc"])
    t = tempo(m["t"])
    if m["fora"]:
        return f"a última {ev} {esc} NÃO ocorreu {t}"
    return f"a última {ev} {esc} ocorreu {t}"


@regra(r"^(?P<st>ativos|inativos)(?: para (?P<q>o vendedor|a empresa))?$", "§6.1")
def _ativos(m, orig):
    st = "ativo" if m["st"] == "ativos" else "inativo"
    q = {"o vendedor": "segundo o histórico de compras com o próprio vendedor",
         "a empresa": "segundo o histórico de compras com qualquer vendedor da empresa",
         None: "pelos critérios padrão do sistema"}[m["q"]]
    return f"cliente {st} {q}"


@regra(r"^inatividade(?P<g> global)? (?:de|maior que) (?P<n>\d+) dias?$", "§6.1")
def _inatividade(m, orig):
    return f"sem compra há pelo menos {m['n']} dias" + (" com a empresa toda" if m["g"] else "")


@regra(r"^atividade(?: (?P<q>global|do vendedor))? de (?P<t>.+)$", "§6.1")
def _atividade(m, orig):
    q = {"global": "de qualquer vendedor", "do vendedor": "do próprio vendedor", None: "de algum vendedor do grupo"}[m["q"]]
    t = m["t"]
    t = f"nos últimos {t}" if re.fullmatch(r"\d+ \w+", t) else tempo(t)
    return f"comprou {q} {t}"


@regra(r"^sem vendas?(?: (?P<q>do vendedor|da empresa))?$", "§6.1 (aprox.)")
def _sem_venda(m, orig):
    q = {"do vendedor": " com o próprio vendedor", "da empresa": " com a empresa", None: ""}[m["q"]]
    return f"cliente sem nenhuma venda registrada{q} (nunca comprou)"


@regra(r"^prospects?(?: (?P<q>do vendedor|da empresa))?$", "§6.1")
def _prospects(m, orig):
    q = {"do vendedor": " com o próprio vendedor", "da empresa": " com a empresa", None: ""}[m["q"]]
    return f"prospect: nunca comprou{q}"


@regra(r"^unica compra com (?P<q>o vendedor|a empresa)$", "§6.1")
def _unica(m, orig):
    return "comprou uma única vez " + ("com o próprio vendedor" if m["q"] == "o vendedor" else "com a empresa")


@regra(r"^(?P<nao>nao )?tem venda(?: (?P<q>do vendedor|da empresa))?(?: (?P<t>.+))?$", "§6.1")
def _tem_venda(m, orig):
    q = {"do vendedor": "do próprio vendedor", "da empresa": "de qualquer vendedor da empresa",
         None: "de algum vendedor do grupo"}[m["q"]]
    t = tempo(m["t"]) if m["t"] else ""
    return ("NÃO teve venda " if m["nao"] else "teve venda ") + f"{q} {t}".rstrip()


@regra(r"^no ciclo de vida (?P<f>\w+) com (?P<q>o vendedor|a empresa)$", "§6.7")
def _ciclo(m, orig):
    fase = {"prospect": "prospect (nunca comprou)", "ativo": "ativo (fez alguma compra)", "inativo": "inativo",
            "ativado": "ativado (fez a primeira compra quando era prospect)",
            "reativado": "reativado (voltou a comprar quando estava inativo)"}.get(m["f"], m["f"])
    q = "com o próprio vendedor" if m["q"] == "o vendedor" else "com a empresa"
    return f"no ciclo de vida, está na fase {fase} {q}"


@regra(r"^curva (?P<c>[abc]) com (?P<q>o vendedor|a empresa)$", "§6.7")
def _curva(m, orig):
    q = "com o próprio vendedor" if m["q"] == "o vendedor" else "com a empresa"
    return f"cliente da curva {m['c'].upper()} de faturamento {q}"


@regra(r"^(?P<i>in)?adimplentes$", "§6.3")
def _adimpl(m, orig):
    return "inadimplente (tem pendências financeiras em aberto)" if m["i"] else "adimplente (sem pendências financeiras)"


@regra(r"^(?P<nao>nao )?tem credito$", "§6.3")
def _credito(m, orig):
    return "sem crédito disponível" if m["nao"] else "com crédito disponível"


@regra(r"^com (?P<n>\d+)% de credito$", "§6.3")
def _pct_credito(m, orig):
    return f"crédito disponível de pelo menos {m['n']}% do limite"


@regra(r"^com menos de r\$ ?(?P<v>[\d.,]+) de credito disponivel$", "§6.3")
def _menos_credito(m, orig):
    return f"crédito disponível abaixo de R$ {m['v']}"


@regra(r"^com (?:limite de )?r\$ ?(?P<v>[\d.,]+) de credito$", "§6.3")
def _limite_credito(m, orig):
    return f"crédito/limite de pelo menos R$ {m['v']}"


@regra(r"^com ticket medio (?P<c>.+)$", "§6.3")
def _ticket(m, orig):
    return f"ticket médio {_cmp(m['c'])}"


@regra(r"^(?P<k>total faturado|media faturada) no (?P<p>\w+) com a empresa (?P<c>.+)$", "§6.3")
def _faturado(m, orig):
    k = "faturamento total" if m["k"] == "total faturado" else "faturamento médio mensal"
    return f"{k} no {m['p'].replace('mes', 'mês')} com a empresa {_cmp(m['c'])}"


@regra(r"^queda de faturamento (?P<c>maior|menor) que (?P<n>\d+)%$", "§6.11")
def _queda(m, orig):
    return f"queda de faturamento {'acima de' if m['c'] == 'maior' else 'de até'} {m['n']}%"


@regra(r"^status na receita federal definido como (?P<s>\w+)$", "§6.5")
def _receita(m, orig):
    return f"empresa com situação '{m['s']}' na Receita Federal"


@regra(r"^pessoa (?P<t>fisica|juridica)$", "§6.5")
def _pessoa(m, orig):
    return "pessoa física (CPF)" if m["t"] == "fisica" else "pessoa jurídica (CNPJ)"


@regra(r"^(?:(?:e|é) )?(?:o )?cliente (?P<t>filial|principal)$", "§6.5")
def _filial(m, orig):
    return "o cadastro é uma filial" if m["t"] == "filial" else "o cadastro é o cliente principal (não é filial)"


@regra(r"^(?P<nao>nao )?(?P<t>bloqueados|excluidos)$", "§6.5")
def _bloq(m, orig):
    t = "bloqueado para atendimento" if m["t"] == "bloqueados" else "excluído do sistema"
    return ("NÃO " if m["nao"] else "") + t


@regra(r"^(?P<nao>nao )?tem coordenada confiavel$", "§6.5")
def _coord(m, orig):
    return ("sem" if m["nao"] else "com") + " geolocalização confiável"


_CAMPOS_TEXTO = {"nome da cidade": "cidade", "nome do bairro": "bairro", "uf do estado": "UF",
                 "nome da rota": "nome da rota", "o rotulo": "rótulo de classificação",
                 "conteudo da nota": "conteúdo da nota", "nome da nota": "nome da nota",
                 "cnae": "CNAE (Govendas)", "cnae do erp": "CNAE do ERP", "cnae da receita": "CNAE da Receita",
                 "nome do cnae da receita": "nome do CNAE da Receita"}
_CAMPOS_ID = {"ramo de atividade": "ramo de atividade", "codigo da rota": "código da rota",
              "id do cliente": "id do cliente", "id do cliente principal": "id do cliente principal",
              "tipo de pagamento": "tipo de pagamento (id)", "tipo de cobranca": "tipo de cobrança (id)"}
_OPS = {"igual": "é um destes", "diferente": "NÃO é nenhum destes", "contem": "contém",
        "inicia com": "começa com"}


@regra(r"^(?P<campo>nome da cidade|nome do bairro|uf do estado|nome da rota|o rotulo|conteudo da nota|nome da nota|"
       r"nome do cnae da receita|cnae do erp|cnae da receita|cnae)(?: e| é)? (?P<op>igual|diferente|contem|inicia com)\s*\(", "§6.5")
def _campo_texto(m, orig):
    return f"{_CAMPOS_TEXTO[m['campo']]} {_OPS[m['op']]}: {valores(orig)}"


@regra(r"^(?P<campo>ramo de atividade|codigo da rota|id do cliente principal|id do cliente|tipo de pagamento|tipo de cobranca)"
       r"(?: e| é)? (?P<op>igual|diferente)\s*\(", "§6.6")
def _campo_id(m, orig):
    return f"{_CAMPOS_ID[m['campo']]} {_OPS[m['op']]}: {valores(orig)}"


@regra(r"^(?P<nao>nao )?contido na segmentacao\s*\(", "§6.9")
def _segm(m, orig):
    return ("NÃO " if m["nao"] else "") + f"pertence à segmentação {valores(orig)}"


@regra(r"^frequencia historica (?P<c>.+)$", "§6.8")
def _freq_hist(m, orig):
    c = m["c"]
    mm = re.fullmatch(r"entre (\d+) dias? e (\d+) dias?", c)
    if mm:
        return f"frequência histórica de compra entre {mm.group(1)} e {mm.group(2)} dias"
    mm = re.fullmatch(r"de (\d+) dias?", c)
    if mm:
        return f"frequência histórica de compra de {mm.group(1)} dias"
    return f"frequência histórica de compra {_cmp(c)}"


@regra(r"^(?P<nao>nao )?tem parametro(?P<man> manual)?$", "§6.8")
def _tem_param(m, orig):
    return ("sem" if m["nao"] else "com") + " parametrização" + (" manual" if m["man"] else "")


@regra(r"^fora da frequencia de venda(?P<r>.*)$", "§6.8")
def _fora_freq(m, orig):
    return f"recência atual fora da frequência de venda calculada{(' ' + _cmp(m['r'].strip())) if m['r'].strip() else ''}"


@regra(r"^em ruptura global do (?P<p>bimestre|trimestre|semestre|ano)$", "§6.10")
def _ruptura(m, orig):
    faixa = {"bimestre": "30 e 60", "trimestre": "61 e 90", "semestre": "91 e 180", "ano": "181 e 365"}[m["p"]]
    return f"em ruptura: sem compra entre {faixa} dias"


@regra(r"^cadastrado (?:faz|ha) (?P<n>\d+) dias?$", "§6.11")
def _cad(m, orig):
    return f"cadastrado no ERP há pelo menos {m['n']} dias"


@regra(r"^cadastrado a partir do dia '(?P<d>[^']+)'$", "§6.11")
def _cad_data(m, orig):
    return f"cadastrado a partir de {m['d']}"


@regra(r"^data da rota(?: (?P<fut>futura))?(?: (?P<v>do vendedor))? (?P<t>.+)$", "§6.11")
def _rota(m, orig):
    quem = " do próprio vendedor" if m["v"] else ""
    t = m["t"]
    mm = re.fullmatch(r"em (\d+) dias?", t)
    if mm:  # o manual não diz se "em N dias" é para trás ou para frente quando aplicado à data de rota
        return (f"tem data de rota (visita presencial programada{quem}) dentro de um intervalo de {mm.group(1)} dias"
                f"{' à frente' if m['fut'] else ''} (aprox.: o manual não detalha esta forma)")
    mm = re.fullmatch(r"ha (\d+) dias? atras", t)
    if mm:
        return f"tem data de rota (visita presencial{quem}) anterior aos últimos {mm.group(1)} dias"
    return f"tem data de rota (visita presencial programada{quem}) {tempo(t)}"


@regra(r"^data da (?P<q>ultima|proxima) visita do representante (?P<t>.+)$", "§6.11")
def _visita_rep(m, orig):
    return f"a {'última' if m['q'] == 'ultima' else 'próxima'} visita do representante externo (registrada no ERP) ocorre {tempo(m['t'])}"


@regra(r"^tem visita(?: (?P<q>da empresa|do vendedor))? (?P<t>.+)$", "§6.1/§6.2 (aprox.)")
def _tem_visita(m, orig):
    q = {"da empresa": "de qualquer vendedor", "do vendedor": "do próprio vendedor", None: ""}[m["q"]]
    return f"recebeu visita {q} {tempo(m['t'])}".replace("  ", " ")


@regra(r"^(?P<nao>nao )?(?:na agenda|agendavel|reagendado)(?P<r>.*)$", "§6.4")
def _agenda(m, orig):
    return f"situação de agenda: {orig}"


@regra(r"^elegivel(?P<r> incluindo roteirizavel)?$", "§6.11")
def _elegivel(m, orig):
    return "não excluído, ativo e marcado para agendar" + (" e para roteirizar" if m["r"] else "")


@regra(r"^sem perfil com (?P<q>o vendedor|a empresa)$", "§6.11")
def _perfil(m, orig):
    return "não está marcado para 'não agendar' nem excluído nem baixado na Receita"


@regra(r"^(?:total de )?compras(?: no (?P<p>\w+))? com (?P<q>o vendedor|a empresa) (?P<c>.+)$", "§6.11")
def _compras(m, orig):
    per = f" no {m['p'].replace('mes', 'mês')}" if m["p"] else ""
    return f"número de compras{per} com {'o vendedor' if m['q'] == 'o vendedor' else 'a empresa'} {_cmp(m['c'])}"


def explica_filtro(texto: str) -> dict:
    n = normaliza(texto)
    n = re.sub(r"^(?:e|ou)\s+", "", n)
    for rx, fn, secao in REGRAS_FILTRO:
        m = rx.match(n)
        if m:
            return {"significado": fn(m, texto), "secao": secao}
    return {"significado": None, "secao": None}


# --------------------------------------------------------------------------------------
# FILTROS TEMPORAIS (§5) — dizem QUANDO a regra roda, não quais clientes
# --------------------------------------------------------------------------------------

def explica_temporal(texto: str) -> dict:
    n = normaliza(texto)
    partes = []
    for p in re.split(r"\s+e\s+(?=(?:no|na|nos|nas|a partir|antes|depois|entre|em)\b)", n):
        m = re.fullmatch(r"a partir do dia (\d+)", p)
        if m:
            partes.append(f"do dia {m.group(1)} até o fim do mês"); continue
        m = re.fullmatch(r"no dia (\d+)", p)
        if m:
            partes.append(f"no dia {m.group(1)} do mês"); continue
        m = re.fullmatch(r"antes do dia (\d+)", p)
        if m:
            partes.append(f"antes do dia {m.group(1)}"); continue
        m = re.fullmatch(r"depois do dia (\d+)", p)
        if m:
            partes.append(f"depois do dia {m.group(1)}"); continue
        m = re.fullmatch(r"entre os dias (\d+) e (\d+)", p)
        if m:
            partes.append(f"entre os dias {m.group(1)} e {m.group(2)}"); continue
        m = re.fullmatch(r"n[ao]s? (segunda|terca|quarta|quinta|sexta|sabado|domingo)", p)
        if m:
            partes.append(f"às {_DIAS_SEMANA[m.group(1)]}s"); continue
        fixos = {"nos dias uteis": "em dias úteis (segunda a sexta)", "no fim de semana": "no fim de semana",
                 "todos os dias": "todos os dias", "na ultima semana": "na última semana do mês",
                 "na primeira semana": "na primeira semana do mês (dias 1-7)",
                 "na segunda semana": "na segunda semana do mês (dias 8-14)",
                 "na terceira semana": "na terceira semana do mês (dias 15-21)",
                 "na quarta semana": "na quarta semana do mês (dias 22-28)",
                 "na primeira quinzena": "na primeira quinzena", "na segunda quinzena": "na segunda quinzena"}
        partes.append(fixos.get(p, p))
    return {"significado": "a regra só é aplicada " + " e ".join(partes), "secao": "§5"}


# --------------------------------------------------------------------------------------
# AÇÕES (§7)
# --------------------------------------------------------------------------------------
_FREQ_FIXA = {"diaria()": 1, "semanal()": 7, "quinzenal()": 15, "mensal()": 30, "bimestral()": 60,
              "trimestral()": 90, "semestral()": 180, "anual()": 365}
_FREQ_DIN = {"do govendas": "a frequência padrão do Govendas",
             "do vendedor": "a frequência que o vendedor configurou para o cliente",
             "do historico": "a frequência calculada pelo histórico de visitas do cliente",
             "de qualquer vendedor": "a frequência configurada por qualquer vendedor para o cliente",
             "de ativos da empresa": "a frequência média dos clientes ativos da empresa",
             "de inativos da empresa": "a frequência média dos clientes inativos da empresa",
             "de ativos do vendedor": "a frequência média dos clientes ativos do vendedor",
             "de inativos do vendedor": "a frequência média dos clientes inativos do vendedor",
             "remover": "remover a frequência configurada"}


def _alternativa_freq(a: str):
    """Uma alternativa da cascata 'X ou Y ou Z' (§7.3.6). Retorna (texto, dias|None)."""
    a = a.strip()
    m = re.fullmatch(r"de (\d+) dias?", a)
    if m:
        return f"a cada {m.group(1)} dias", int(m.group(1))
    if a in _FREQ_FIXA:
        return f"a cada {_FREQ_FIXA[a]} dias ({a.rstrip('()')})", _FREQ_FIXA[a]
    m = re.fullmatch(r"no minimo de (\d+) dias? e no maximo de (\d+) dias?", a)
    if m:
        return f"com limite mínimo de {m.group(1)} e máximo de {m.group(2)} dias", None
    m = re.fullmatch(r"no maximo de (\d+) dias?", a)
    if m:
        return f"com limite máximo de {m.group(1)} dias", None
    m = re.fullmatch(r"no (maximo|minimo) (\w+\(\))", a)
    if m:
        return f"com limite {'máximo' if m.group(1) == 'maximo' else 'mínimo'} {m.group(2).rstrip('()')} ({_FREQ_FIXA.get(m.group(2), '?')} dias)", None
    m = re.fullmatch(r"(do vendedor|do historico) (mais|menos) (\d+) dias?", a)
    if m:
        return f"{_FREQ_DIN[m.group(1)]} {'mais' if m.group(2) == 'mais' else 'menos'} {m.group(3)} dias", None
    if a in _FREQ_DIN:
        return _FREQ_DIN[a], None
    return a, None


def explica_acao(tipo: str, texto: str) -> dict:
    n = normaliza(texto)
    if tipo == "nao_agendar":
        return {"significado": "NÃO agendar (o cliente fica fora da agenda)", "secao": "§7.3.4", "dias": None}
    if tipo == "fixo":
        return {"significado": "parametrização fixa (restrição rígida de frequência/preferência no gerador de agendas)",
                "secao": "§7.3.10", "dias": None}
    if tipo == "roteirizavel":
        return {"significado": "incluir na roteirização de visitas presenciais", "secao": "§7.3.10", "dias": None}
    if tipo == "nao_roteirizavel":
        return {"significado": "não incluir na roteirização de visitas presenciais", "secao": "§7.3.10", "dias": None}
    if tipo == "restricao_semana":
        r = n[len("restrito"):].strip()
        return {"significado": f"só pode entrar na agenda {r} do mês", "secao": "§7.5", "dias": None}
    if tipo == "frequencia":
        corpo = n[len("frequencia"):].strip()
        alts = re.split(r"\s+ou\s+", corpo)
        textos, dias = [], None
        for i, a in enumerate(alts):
            t, d = _alternativa_freq(a)
            if d is not None and dias is None and len(alts) == 1:
                dias = d
            textos.append(t)
        if len(textos) == 1:
            sig = f"frequência de atendimento: {textos[0]}"
        else:
            sig = "frequência de atendimento: " + textos[0] + "".join(
                f"; {('se não houver, ' if not t.startswith('com limite') else '')}{t}" for t in textos[1:])
        secao = "§7.4.1" if dias else ("§7.4.3" if any(k in corpo for k in ("historico", "vendedor", "empresa", "govendas")) else "§7.4")
        return {"significado": sig, "secao": secao, "dias": dias}
    if tipo == "preferencia":
        corpo = n[len("preferencia"):].strip()
        if corpo in ("do vendedor",):
            return {"significado": "mantém a preferência de dias configurada pelo vendedor", "secao": "§7.3.5 (aprox.)", "dias": None}
        if corpo.startswith("do historico"):
            return {"significado": "preferência de dias calculada pelo histórico de visitas" +
                    (" (se não houver histórico: " + corpo.split(" ou ", 1)[1] + ")" if " ou " in corpo else ""),
                    "secao": "§7.3.6", "dias": None}
        itens = []
        for p in re.split(r"\s+e\s+", corpo):
            m = re.fullmatch(r"(?:(maior|normal|menor) )?n[ao]s? (segunda|terca|quarta|quinta|sexta|sabado|domingo)(?:-feira)?", p)
            if m:
                peso = {"maior": "prioritária (3)", "menor": "baixa (1)"}.get(m.group(1), "normal (2)")
                itens.append(f"{_DIAS_SEMANA[m.group(2)]} [{peso}]")
            elif p == "nos dias uteis":
                itens.append("segunda a sexta [normal (2)]")
            elif p:
                itens.append(p)
        return {"significado": "preferência de dias: " + ", ".join(itens) + "; demais dias com valor 0 (não atender)",
                "secao": "§7.2/§7.3.2", "dias": None}
    return {"significado": None, "secao": None, "dias": None}


# --------------------------------------------------------------------------------------
# TIMES (§3) e SELEÇÃO DE CLIENTES (§4.6)
# --------------------------------------------------------------------------------------

def explica_vendedores(sel: str | None) -> str:
    if not sel:
        return "(seleção de vendedores não informada)"
    n = normaliza(sel)
    base = {"todostelevendas": "vendedores do tipo televendas", "todosdecampo": "vendedores de campo (presenciais)",
            "todos": "todos os vendedores da empresa"}
    partes = []
    m = re.match(r"^(todostelevendas|todosdecampo|todos)\b", n)
    if m:
        partes.append(base[m.group(1)])
    elif n.startswith("porid"):
        partes.append(f"os vendedores de id {valores(sel)}")
    else:
        partes.append(sel)
    if " ativados" in f" {n}":
        partes.append("somente os ativados")
    if " inativados" in f" {n}":
        partes.append("somente os inativados")
    m = re.search(r"dos supervisores\s*\(", n)
    if m:
        partes.append(f"dos supervisores {valores(sel[m.start():].split(')')[0] + ')')}")
    m = re.search(r"menos\s*\(", n)
    if m:
        partes.append(f"exceto os de id {valores(sel[m.start():])}")
    return ", ".join(partes)


def explica_selecao_clientes(sel: str | None) -> str:
    if not sel:
        return "(sem seleção)"
    n = normaliza(sel)
    mapa = [
        (r"^carteirafixa\(", "a carteira fixa de cada vendedor do time {v}"),
        (r"^carteiraacessivel\(", "a carteira acessível de cada vendedor do time {v}"),
        (r"^carteiraruptura\(", "a carteira de ruptura pré-calculada do time {v}"),
        (r"^portfolio\(", "o portfólio completo dos vendedores do time {v}"),
        (r"^segmentados\(", "os clientes da segmentação {v}"),
        (r"^todos\(", "todos os clientes do sistema, para o time {v}"),
        (r"^ruptura\(", "clientes em ruptura do time de origem para o time de destino ({v}): " + sel.split(")", 1)[-1].strip()),
    ]
    for rx, tpl in mapa:
        if re.match(rx, n):
            return tpl.format(v=valores(sel.split(")")[0] + ")"))
    return sel
