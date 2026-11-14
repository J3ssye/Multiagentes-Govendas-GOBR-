# -*- coding: utf-8 -*-
"""Entrega 5 - partes compartilhadas do agente que gera uma parametrização em GOBR.

Reaproveita as entregas anteriores SÓ por import; nenhum arquivo delas é alterado:
  Entrega 4 (comum_fluxo.py): Recursos, Config, buscar_cfg, aquecer, descrever_regra, descrever_trecho,
    montar_contexto, medir_configuracao, metricas_exatas, carregar_consultas, gravar_exclusivo, responder.
  Entrega 1 (gobr_parser.py): parse_texto e as funções auxiliares do parser.
Aqui fica o que é novo: as constantes da regra pré-registrada (regra_agente.md), o roteador, o validador,
a tabela de consultas ao manual na retentativa, a chamada ao Gemini com saída JSON, a grade de regras, a
medição com confirmação, a regra de escolha e a trava do git.

Nenhuma função daqui carrega modelo ao ser importada: os imports pesados ficam dentro das funções.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent                    # trabalho/
ENTREGA1 = RAIZ / "entrega1"
ENTREGA4 = RAIZ / "entrega4"
for _pasta in (ENTREGA4, ENTREGA1):   # no FIM do caminho de busca: a pasta da Entrega 5 continua na frente
    if str(_pasta) not in sys.path:
        sys.path.append(str(_pasta))

import comum_fluxo as cf              # noqa: E402  (Entrega 4, sem alteração)
import gobr_parser as gp              # noqa: E402  (Entrega 1, sem alteração)

# ------------------------------------------------ constantes da regra (seção 3 de regra_agente.md) ----
# Os testes leem o bloco da seção 3 do arquivo da regra e comparam com estes valores.
K = 3
TETO_BUSCA_S = 20.0
REPETICOES = 2
FATOR_CONFIRMACAO = 1.25
MAX_TENTATIVAS = 2
TIMEOUT_GEMINI_S = 300
RETENTATIVAS_INFRA = 2
DIVERGENCIA_CHAMADA_S = 2
DIVERGENCIA_CHAMADA_FRACAO = 0.10
LACUNA_ENTRE_CHAMADAS_S = 60
CHARS_TEXTO_CURTO = 1000
MODELO_RERANKER_MENOR = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
MAX_LENGTH_RERANKER_MENOR = 512
ROTAS = ("regras", "manual", "ambos", "nenhum")
STATUS = ("aceita", "invalida", "resposta_linguagem", "fora_do_escopo", "erro_infra")
RECUSAS = ("saida_invalida", "linha_nao_reconhecida", "sem_bloco_parametros", "bloco_sem_fonte", "bloco_sem_acao",
           "nao_agendar_com_frequencia", "linha_de_corpo_nao_classificada", "cabecalho_parametros_invalido")
AVISOS = ("sem_version", "cabecalho_nao_reconhecido", "bloco_inalcancavel", "sem_regra_final",
          "nome_diverge_do_codigo", "fonte_indefinida")
GRADE_REGRAS = ("R0", "R1", "R2", "R3", "R4")
DOMINIO = ("gobr", "govendas", "gorules", "linguagem", "regra", "parametr", "cliente", "vendedor", "carteira",
           "equipe", "time", "segmentac", "frequencia", "agend", "bloco", "filtro", "alerta", "aviso", "notifica",
           "mensagem", "whatsapp", "ramo", "prospect", "inadimpl", "inativo", "ativo", "roteiro", "rota", "visita",
           "supervisor", "televendas")
DESC = (r"\ba cada \d+",
        r"\b\d+\s*(?:dias?|semanas?|meses|mes|anos?)\b",
        r"\b(?:toda|todo|todas|todos)\s+(?:a\s+|o\s+)?(?:semana|dia|mes|segunda|terca|quarta|quinta|sexta)\b",
        r"\b(?:semanal|quinzenal|mensal|diari[ao]|bimestral|trimestral|semestral)\b",
        r"\bnao\s+(?:agendar|agenda|sao agendad\w+)\b|\bbloque(?:ar|ando|ados?)\b")
PEDIDO_1 = r"\b(?:cri|ger|escrev|mont|fac|faz|elabor)\w*\s+(?:uma|outra)\s+(?:nova\s+)?regra\b"
INTERROGATIVA = r"^\s*(?:e\s+)?(?:como|qual|quais|que|o que|onde|quando|quanto|quantos|quantas|por que|porque)\b"

MODELO_GEMINI_PADRAO = cf.MODELO_GEMINI_PADRAO      # o mesmo das Entregas 1 e 4 (regra, seção 2, item 4)
N_ROTEAMENTO = {"dev": 15, "teste": 15}             # mensagens novas de roteamento (regra, seção 8)
N_GERACAO = {"dev": 14, "teste": 20}                # consultas de regras da Entrega 2 (regra, seção 8)

ARQ_REGRA = AQUI / "regra_agente.md"
# sha256 do arquivo da regra com fins de linha LF, do commit 0c681b5 (14/11/2026). Se mudar, nada roda.
HASH_REGRA = "77c0529959f7a09bf707aa14ba063dde0a979d136b5e42e9570b1f828868a203"
ARQ_ROTEAMENTO = {"dev": AQUI / "consultas_roteamento_dev.json", "teste": AQUI / "consultas_roteamento_teste.json"}
PASTA_CHECKPOINTS = AQUI / "dev_checkpoints_agente"
PASTA_ARQUIVADA = AQUI / "dev_1a_execucao_agente"
ARQ_CONFIG = AQUI / "config_agente.json"
ARQ_DEV_JSON = AQUI / "resultados_agente_dev.json"
ARQ_DEV_MD = AQUI / "resultados_agente_dev.md"
PASTA_CHECKPOINTS_TESTE = AQUI / "teste_checkpoints_agente"
ARQ_TESTE_JSON = AQUI / "resultados_agente_teste.json"
ARQ_TESTE_MD = AQUI / "resultados_agente_teste.md"

imprimir = cf.imprimir
agora = cf.agora
gravar_exclusivo = cf.gravar_exclusivo
sha256_arquivo = cf.sha256_arquivo


def ler_constantes_regra(caminho: Path = ARQ_REGRA) -> dict[str, str]:
    """Bloco da seção 3 da regra: nome -> valor (texto cru, do jeito que está escrito)."""
    texto = Path(caminho).read_text(encoding="utf-8")
    m = re.search(r"## 3\. Constantes.*?```\n(.*?)```", texto, re.S)
    if not m:
        raise ValueError("bloco de constantes (seção 3) não encontrado na regra")
    return dict(linha.split(" = ", 1) for linha in m.group(1).splitlines() if " = " in linha)


# ---------------------------------------------------------------- roteador (regra, seção 5) ----
_RE_DOMINIO = re.compile(r"\b(?:" + "|".join(map(re.escape, DOMINIO)) + r")\w*")
_RE_DESC = tuple(re.compile(p) for p in DESC)
_RE_PEDIDO = re.compile(PEDIDO_1)
_RE_INTERROGATIVA = re.compile(INTERROGATIVA)


def normalizar(texto: str) -> str:
    """Minúsculas e sem acento (regra, seção 5)."""
    return "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))


def frases(texto: str) -> list[str]:
    """Uma frase é um trecho terminado em '.', '!', '?' ou quebra de linha."""
    return re.findall(r"[^.!?\n]+[.!?]*", texto)


def rotear(mensagem: str) -> dict:
    """Função pura, 0 token. Devolve a rota e as quatro características que a decidiram."""
    t = normalizar(mensagem)
    fr = frases(t)
    com_interrogacao = [f for f in fr if f.strip().endswith("?")]
    eh_pedido = [bool(_RE_PEDIDO.search(f)) and not _RE_INTERROGATIVA.search(f) for f in com_interrogacao]
    dominio = bool(_RE_DOMINIO.search(t))
    pedido = any(eh_pedido)
    pergunta = any(not p for p in eh_pedido)
    descricao = any(any(r.search(f) for r in _RE_DESC) or bool(_RE_PEDIDO.search(f)) for f in fr)
    if not dominio:
        rota, motivo = "nenhum", "nenhum termo do domínio na mensagem"
    elif not pergunta:
        rota = "regras"
        motivo = "pedido de regra em forma de pergunta" if pedido else "mensagem declarativa com termos do domínio"
    elif descricao:
        rota, motivo = "ambos", "pergunta junto com uma descrição de regra"
    else:
        rota, motivo = "manual", "pergunta sobre a linguagem, sem descrição de regra"
    return {"rota": rota, "motivo": motivo, "dominio": dominio, "pedido": pedido, "pergunta": pergunta,
            "descricao": descricao}


def desfecho(rota: str) -> str:
    """Regra, seção 8: gera regra = regras ou ambos; responde = manual; recusa = nenhum."""
    return {"regras": "gera", "ambos": "gera", "manual": "responde", "nenhum": "recusa"}[rota]


def carregar_roteamento(conjunto: str, caminho: Path | None = None) -> list[dict]:
    """As mensagens de roteamento do conjunto: as de regras (Entrega 2, rota esperada `regras`), as do manual
    (Entrega 3, `manual`) e as novas desta entrega (rota no arquivo). Cada item: id, consulta, rota_esperada, origem."""
    itens = [{"id": c["id"], "consulta": c["consulta"], "rota_esperada": "regras", "origem": "entrega2"}
             for c in cf.carregar_consultas("regras", conjunto)]
    itens += [{"id": c["id"], "consulta": c["consulta"], "rota_esperada": "manual", "origem": "entrega3"}
              for c in cf.carregar_consultas("manual", conjunto)]
    novas = json.loads(Path(caminho or ARQ_ROTEAMENTO[conjunto]).read_text(encoding="utf-8"))["consultas"]
    itens += [{"id": c["id"], "consulta": c["consulta"], "rota_esperada": c["rota_esperada"], "origem": "entrega5",
               "tipo": c.get("tipo")} for c in novas]
    return itens


def medir_roteamento(itens: list[dict]) -> dict:
    """Acerto exato de rota e de desfecho (k de n), por origem, matriz de confusão e idas desnecessárias ao manual."""
    linhas, confusao, por_origem = [], {}, {}
    for it in itens:
        obtida = rotear(it["consulta"])["rota"]
        ok = obtida == it["rota_esperada"]
        ok_desf = desfecho(obtida) == desfecho(it["rota_esperada"])
        linhas.append({"id": it["id"], "origem": it["origem"], "esperada": it["rota_esperada"], "obtida": obtida,
                       "acerto": ok, "acerto_desfecho": ok_desf})
        chave = f"{it['rota_esperada']}->{obtida}"
        confusao[chave] = confusao.get(chave, 0) + 1
        o = por_origem.setdefault(it["origem"], {"n": 0, "acertos": 0, "acertos_desfecho": 0})
        o["n"] += 1
        o["acertos"] += ok
        o["acertos_desfecho"] += ok_desf
    return {"n": len(linhas), "acertos": sum(x["acerto"] for x in linhas),
            "acertos_desfecho": sum(x["acerto_desfecho"] for x in linhas), "por_origem": por_origem,
            "confusao": dict(sorted(confusao.items())),
            "manual_sem_precisar": sum(1 for x in linhas if x["obtida"] in ("manual", "ambos")
                                       and x["esperada"] in ("regras", "nenhum")),
            "erros": [x for x in linhas if not x["acerto"]], "itens": linhas}


# ---------------------------------------------------------------- validador (regra, seção 6) ----
_CABECALHO = re.compile(r"^(limpar|time|carteira|segmentacao|parametros|alertas?|tags?)\b")
_CABECALHO_PARAMETROS = re.compile(r"^(?:limpar\s+)?parametros\b")
_ACHADOS_QUE_AVISAM = ("bloco_inalcancavel", "sem_regra_final", "nome_diverge_do_codigo", "fonte_indefinida")


def _varrer(texto: str) -> dict:
    """Reproduz o 1º laço de parse_texto e o laço de cláusulas de _monta_bloco (Entrega 1) para achar o que o
    parser absorve sem avisar: linha de corpo anexada à cláusula anterior (ramo `elif clausulas:`), cabeçalho que
    o HEADER_RE não reconhece e, entre esses, o de `parametros`."""
    texto = re.sub(r"(\S)(version\s+\d+\.\d+)", r"\1\n\2", texto)
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", texto)
    blocos, atual = [], None
    cab_parametros, cab_outros, corpo = [], [], []
    for n, bruta in enumerate(texto.splitlines(), 1):
        if bruta.strip().startswith("#"):
            continue
        linha = gp.tira_comentario(bruta).rstrip()
        if not linha.strip():
            continue
        tem_indent = linha[:1] in (" ", "\t")
        c = linha.strip()
        if not tem_indent:
            if gp.VERSION_RE.match(c):
                continue
            mh = gp.HEADER_RE.match(c)
            if mh:
                atual = {"cat": gp.normaliza(mh.group("cat")), "linhas": []}
                blocos.append(atual)
                continue
            if _CABECALHO_PARAMETROS.match(gp.normaliza(c)):
                cab_parametros.append((n, c))
            elif atual is not None and _CABECALHO.match(gp.normaliza(c)):
                cab_outros.append((n, c))
        if atual is None:
            continue
        atual["linhas"].append((n, c))
    for b in blocos:
        clausulas, viu_quando, viu_acao = [], False, False
        for n, c in b["linhas"]:
            l = gp.normaliza(c)
            if clausulas and gp.parenteses_abertos(clausulas[-1]["texto"]) > 0:
                clausulas[-1]["texto"] += " " + c
                continue
            tipo = gp._classifica(l)
            if tipo is None:
                if re.match(r"^(e|ou)\b", l) and clausulas:
                    clausulas[-1]["texto"] += " " + c
                    continue
                ult = clausulas[-1]["tipo"] if clausulas else None
                if b["cat"] == "parametros" and ult in ("fonte", "temporal") and not viu_quando and not viu_acao:
                    tipo = "temporal"
                elif clausulas:
                    if not _CABECALHO.match(l):
                        corpo.append((n, c))
                    clausulas[-1]["texto"] += " " + c
                    continue
                else:
                    tipo = "desconhecido"
            if tipo == "quando":
                viu_quando = True
            if tipo.startswith("acao:"):
                viu_acao = True
            clausulas.append({"tipo": tipo, "texto": c})
    return {"cabecalho_parametros": cab_parametros, "cabecalho_outros": cab_outros, "corpo": corpo}


def validar(gobr: str) -> dict:
    """Critério de aceite da regra (seção 6). Estrutural: "aceita" não quer dizer que o Govendas aceita a regra.
    Devolve aceita, recusas [{codigo, linha, texto}] na ordem de RECUSAS, avisos [{codigo, texto}] e um resumo."""
    recusas, avisos = [], []
    if not isinstance(gobr, str) or not gobr.strip():
        return {"aceita": False, "recusas": [{"codigo": "saida_invalida", "linha": None,
                                              "texto": "a resposta não trouxe GOBR"}], "avisos": [], "resumo": None}
    ir = gp.parse_texto(gobr, "<gerado>")
    for a in ir["avisos"]:
        m = re.search(r"linha (\d+)", a)
        recusas.append({"codigo": "linha_nao_reconhecida", "linha": int(m.group(1)) if m else None, "texto": a})
    blocos = [p for p in ir["parametros"] if p["categoria"] == "parametros"]
    if not blocos:
        recusas.append({"codigo": "sem_bloco_parametros", "linha": None, "texto": "nenhum bloco parametros"})
    achados = ir["analise"]["achados"]
    for a in achados:
        if a["tipo"] == "sem_fonte":
            recusas.append({"codigo": "bloco_sem_fonte", "linha": None, "texto": a["texto"]})
    for p in ir["parametros"]:
        if not p["acoes"]:
            recusas.append({"codigo": "bloco_sem_acao", "linha": p["linha"],
                            "texto": f"o bloco \"{p['nome']}\" (linha {p['linha']}) não tem nenhuma ação"})
    for a in achados:
        if a["tipo"] == "nao_agendar_com_frequencia":
            recusas.append({"codigo": "nao_agendar_com_frequencia", "linha": None, "texto": a["texto"]})
    v = _varrer(gobr)
    for n, c in v["corpo"]:
        recusas.append({"codigo": "linha_de_corpo_nao_classificada", "linha": n,
                        "texto": f"linha {n} não é uma cláusula reconhecida: {c!r}"})
    for n, c in v["cabecalho_parametros"]:
        recusas.append({"codigo": "cabecalho_parametros_invalido", "linha": n,
                        "texto": f"linha {n}: cabeçalho de bloco parametros malformado: {c!r}"})
    recusas.sort(key=lambda r: RECUSAS.index(r["codigo"]))          # estável: mantém a ordem dentro do código
    if ir["versao"] is None:
        avisos.append({"codigo": "sem_version", "texto": "o arquivo não declara a versão (linha `version`)"})
    for n, c in v["cabecalho_outros"]:
        avisos.append({"codigo": "cabecalho_nao_reconhecido",
                       "texto": f"linha {n}: cabeçalho que o parser não reconhece: {c!r}"})
    for a in achados:
        if a["tipo"] in _ACHADOS_QUE_AVISAM:
            avisos.append({"codigo": a["tipo"], "texto": a["texto"]})
    resumo = {"blocos_parametros": len(blocos), "tipos_de_acao": sorted({a["tipo"] for p in blocos for a in p["acoes"]}),
              "frequencias": sorted({int(x) for p in blocos for a in p["acoes"] if a["tipo"] == "frequencia"
                                     for x in re.findall(r"\d+", a["texto"])})}
    return {"aceita": not recusas, "recusas": recusas, "avisos": avisos, "resumo": resumo}


# Regra, seção 6, tabela da retentativa: recusa -> pergunta ao manual (None = não busca).
CONSULTA_MANUAL = {
    "linha_nao_reconhecida": "Como escrevo em GOBR a linha: {linha}?",
    "linha_de_corpo_nao_classificada": "Como escrevo em GOBR a linha: {linha}?",
    "sem_bloco_parametros": "Como declaro um bloco parametros em GOBR?",
    "cabecalho_parametros_invalido": "Como escrevo o cabeçalho de um bloco parametros em GOBR?",
    "bloco_sem_fonte": "Como declaro a fonte de clientes (do time ou da carteira) de um bloco parametros?",
    "bloco_sem_acao": "Que ações posso usar dentro de um bloco parametros?",
    "nao_agendar_com_frequencia": "Posso combinar nao agendar com frequencia no mesmo bloco?",
    "saida_invalida": None,
}


def consulta_manual_das_recusas(recusas: list[dict], gobr: str = "") -> str | None:
    """A consulta ao manual da retentativa, montada das DUAS primeiras recusas. None = não busca."""
    linhas = gobr.splitlines()
    perguntas = []
    for r in recusas[:2]:
        modelo = CONSULTA_MANUAL[r["codigo"]]
        if modelo is None:
            continue
        n = r.get("linha")
        trecho = linhas[n - 1].strip() if n and 0 < n <= len(linhas) else ""
        if "{linha}" in modelo and not trecho:
            continue
        p = modelo.format(linha=trecho)
        if p not in perguntas:
            perguntas.append(p)
    return " ".join(perguntas) or None


# ---------------------------------------------------------------- geração (Gemini, saída JSON) ----
SCHEMA_GERACAO = {
    "type": "OBJECT",
    "properties": {"gobr": {"type": "STRING"},
                   "premissas": {"type": "ARRAY", "items": {"type": "STRING"}},
                   "perguntas": {"type": "ARRAY", "items": {"type": "STRING"}}},
    "required": ["gobr", "premissas", "perguntas"],
}

# A redação dos prompts é escolha de engenharia: não encontrei no material. As regras de resposta seguem as do
# prompt da Entrega 4 (usar só o contexto) e o enunciado geral (devolver GOBR; ser proativo e apontar pontos falhos).
SISTEMA_GERAR = """Você escreve regras de parametrização do Govendas na linguagem GOBR.
Regras:
- Use só a sintaxe que aparece no contexto (regras de exemplo e trechos do manual). Não invente palavras-chave.
- Responda um JSON com três campos:
  "gobr": o arquivo GOBR completo (linha `version`, blocos `time` ou `carteira` quando forem usados, e os blocos
    `parametros` na ordem em que devem ser avaliados). Só o GOBR, sem cercas de código e sem explicação.
  "premissas": o que você assumiu porque a descrição não dizia (códigos, nomes de time, prazos, ordem dos blocos).
  "perguntas": pontos falhos ou ambíguos da modelagem comercial descrita que o usuário deveria decidir
    (clientes que ficam sem regra, critérios que se sobrepõem, casos que a descrição não cobre).
- Premissas e perguntas em português, curtas, uma ideia por item. Lista vazia se não houver.
- Cada bloco `parametros` precisa de uma fonte de clientes e de pelo menos uma ação.
- Não combine `nao agendar` com `frequencia` no mesmo bloco."""

USUARIO_GERAR = """Contexto recuperado:
---------------------
{contexto}
---------------------
Descrição das regras de negócio: {mensagem}"""

USUARIO_CORRIGIR = """

A tentativa anterior foi recusada pela validação. GOBR anterior:
---------------------
{anterior}
---------------------
Problemas encontrados:
{problemas}
Corrija esses problemas e devolva o JSON completo de novo."""

MSG_FORA_DO_ESCOPO = ("Não encontrei nos documentos. Eu ajudo a escrever regras de parametrização do Govendas em GOBR: "
                      "descreva a regra de negócio (quem é agendado, com que frequência, quem fica de fora) ou "
                      "pergunte sobre a linguagem.")
MARCA_NAO_VALIDADO = "NÃO VALIDADO"


def formatar_recusas(recusas: list[dict]) -> str:
    return "\n".join(f"- [{r['codigo']}] {r['texto']}" for r in recusas)


def montar_prompt_gerar(mensagem: str, contexto: str, anterior: str | None = None,
                        recusas: list[dict] | None = None) -> tuple[str, str]:
    usuario = USUARIO_GERAR.format(contexto=contexto, mensagem=mensagem)
    if recusas:
        usuario += USUARIO_CORRIGIR.format(anterior=anterior or "(vazio)", problemas=formatar_recusas(recusas))
    return SISTEMA_GERAR, usuario


def interpretar_saida(texto: str) -> dict | None:
    """O JSON do nó `gerar`. None se não for o JSON esperado ou se `gobr` vier vazio (recusa saida_invalida)."""
    try:
        d = json.loads(texto)
    except (TypeError, ValueError):
        return None
    if not isinstance(d, dict) or not isinstance(d.get("gobr"), str) or not d["gobr"].strip():
        return None

    def lista(chave):
        v = d.get(chave) or []
        return [str(x).strip() for x in v if str(x).strip()] if isinstance(v, list) else []

    return {"gobr": d["gobr"].strip("\n") + "\n", "premissas": lista("premissas"), "perguntas": lista("perguntas")}


def chave_gemini(env=None):
    """Regra, seção 2, item 4: GOOGLE_API_KEY e, na falta dela, GEMINI_API_KEY. O valor não sai daqui."""
    env = os.environ if env is None else env
    return env.get("GOOGLE_API_KEY") or env.get("GEMINI_API_KEY")


def criar_cliente_gemini(env=None):
    chave = chave_gemini(env)
    if not chave:
        raise RuntimeError("Defina GOOGLE_API_KEY (ou GEMINI_API_KEY) no ambiente.")
    try:
        from google import genai
    except ImportError as e:
        raise RuntimeError("Instale o SDK: pip install -r requirements.txt (pacote google-genai)") from e
    return genai.Client(api_key=chave, http_options={"timeout": TIMEOUT_GEMINI_S * 1000})


def _contagens(resp) -> dict:
    uso = getattr(resp, "usage_metadata", None)

    def c(campo):
        v = getattr(uso, campo, None) if uso is not None else None
        return int(v) if v is not None else None

    return {"tokens_entrada": c("prompt_token_count"), "tokens_saida": c("candidates_token_count"),
            "tokens_raciocinio": c("thoughts_token_count"), "tokens_total": c("total_token_count")}


def gerar_json(sistema: str, usuario: str, *, modelo: str = MODELO_GEMINI_PADRAO, cliente=None,
               relogio=time.perf_counter) -> dict:
    """UMA chamada ao Gemini com os parâmetros da Entrega 1: temperatura 0,2, JSON com schema, 32768 tokens."""
    cliente = cliente or criar_cliente_gemini()
    t0 = relogio()
    resp = cliente.models.generate_content(
        model=modelo, contents=usuario,
        config={"system_instruction": sistema, "temperature": 0.2, "response_mime_type": "application/json",
                "response_schema": SCHEMA_GERACAO, "max_output_tokens": 32768})
    return {"modelo": modelo, "texto": getattr(resp, "text", None) or "", **_contagens(resp),
            "segundos": round(relogio() - t0, 2)}


def _sem_segredo(msg: str, env=None) -> str:
    env = os.environ if env is None else env
    for nome in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        v = env.get(nome)
        if v:
            msg = msg.replace(v, "***")
    return msg


def com_retentativa_infra(chamar, *, retentativas: int = RETENTATIVAS_INFRA, dormir=time.sleep, avisar=None):
    """Rede, cota, autenticação e tempo esgotado não contam como tentativa de geração (regra, seção 6): repete a
    chamada até `retentativas` vezes. Devolve (resultado, None) ou (None, texto do último erro)."""
    erro = None
    for i in range(retentativas + 1):
        try:
            return chamar(), None
        except Exception as e:  # noqa: BLE001  (qualquer falha da chamada é infraestrutura)
            erro = _sem_segredo(f"{type(e).__name__}: {e}")
            if any(s in erro for s in ("API key", "API_KEY", "PERMISSION_DENIED", "UNAUTHENTICATED", "401", "403")):
                erro += " | Autenticação: defina a variável GOOGLE_API_KEY de novo no ambiente."
            if avisar:
                avisar(f"   falha de infraestrutura ({i + 1} de {retentativas + 1}): {erro[:160]}")
            if i < retentativas:
                dormir(2 * (i + 1))
    return None, erro


# ---------------------------------------------------------------- grade de regras (regra, seção 7.3) ----
@dataclass(frozen=True)
class ConfigRegras:
    """Uma configuração de busca no índice de regras: fase 1 híbrida e, opcionalmente, um reranker."""

    id: str
    n: int = 0                 # candidatos que o reranker relê; 0 = sem reranker
    modelo: str = ""           # modelo do reranker
    max_length: int = 0
    chars: int = 0             # texto curto: só os primeiros `chars` caracteres do nó vão ao reranker; 0 = tudo

    @property
    def nome(self) -> str:
        return self.id

    def descricao(self) -> str:
        if not self.n:
            return "híbrido, sem reranker"
        curto = f", texto curto ({self.chars} caracteres)" if self.chars else f", max_length={self.max_length}"
        return f"híbrido + {self.modelo} (N={self.n}{curto})"

    @property
    def origem_da_nota(self) -> str:
        return "reranker" if self.n else "RRF"

    def cfg_e4(self) -> cf.Config:
        return cf.Config("regras", "hibrido", self.n, self.max_length)

    def to_dict(self) -> dict:
        return {"id": self.id, "n": self.n, "modelo": self.modelo, "max_length": self.max_length,
                "chars": self.chars, "nome": self.nome, "descricao": self.descricao()}


def grade_regras() -> dict[str, ConfigRegras]:
    grande, ml = cf.c2.MODELO_RERANKER, cf.c2.RERANKER_MAX_LENGTH
    return {"R0": ConfigRegras("R0"),
            "R1": ConfigRegras("R1", 5, grande, ml, CHARS_TEXTO_CURTO),
            "R2": ConfigRegras("R2", 10, grande, ml, CHARS_TEXTO_CURTO),
            "R3": ConfigRegras("R3", 10, MODELO_RERANKER_MENOR, MAX_LENGTH_RERANKER_MENOR),
            "R4": ConfigRegras("R4", 20, MODELO_RERANKER_MENOR, MAX_LENGTH_RERANKER_MENOR)}


def config_manual() -> cf.Config:
    """A do manual é a da Entrega 4 (config_escolhida.json) e não é reaberta (regra, seção 4)."""
    return cf.carregar_config()["manual"]


def reranker_texto_curto(base, chars: int = CHARS_TEXTO_CURTO):
    """O mesmo reranker, lendo só os primeiros `chars` caracteres de cada texto (regra, seção 7.3)."""
    return cf.c2.Reranker(lambda pares: base.prever([(q, t[:chars]) for q, t in pares]), nome=base.nome)


def criar_reranker_menor():
    """R3 e R4: cross-encoder menor. Baixa o modelo na 1ª vez (precisa de rede). Devolve (Reranker, dispositivo)."""
    import torch
    from sentence_transformers import CrossEncoder

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    modelo = CrossEncoder(MODELO_RERANKER_MENOR, max_length=MAX_LENGTH_RERANKER_MENOR, device=dispositivo)
    return (cf.c2.Reranker(lambda pares: modelo.predict(pares, batch_size=4, show_progress_bar=False),
                           nome=MODELO_RERANKER_MENOR), dispositivo)


class Buscador:
    """As duas buscas do agente sobre os Recursos da Entrega 4. As fábricas são injetáveis nos testes."""

    def __init__(self, recursos: cf.Recursos | None = None, *, cfg_manual: cf.Config | None = None,
                 fabrica_reranker_menor=None):
        self.recursos = recursos or cf.Recursos()
        self.cfg_manual = cfg_manual or config_manual()
        self._fab_menor = fabrica_reranker_menor or criar_reranker_menor
        self._rerankers: dict[str, object] = {}

    def reranker_de(self, cfg: ConfigRegras):
        if not cfg.n:
            return None
        chave = f"{cfg.modelo}|{cfg.max_length}|{cfg.chars}"
        if chave not in self._rerankers:
            if cfg.modelo == MODELO_RERANKER_MENOR:
                t0 = self.recursos.relogio()
                rr, disp = self._fab_menor()
                self.recursos.tempos_carga_s["reranker_menor"] = round(self.recursos.relogio() - t0, 2)
                self.recursos.dispositivos["reranker_menor"] = disp
            else:
                rr = self.recursos.reranker(cfg.max_length)
            self._rerankers[chave] = reranker_texto_curto(rr, cfg.chars) if cfg.chars else rr
        return self._rerankers[chave]

    def preparar(self, cfg: ConfigRegras, manual: bool = True) -> None:
        """Carrega índices e modelos e faz o aquecimento, fora de qualquer medida (regra, seção 7.4)."""
        indice = self.recursos.indice("regras")
        cf.aquecer(self.recursos, "regras", 0)
        rr = self.reranker_de(cfg)
        if rr is not None:
            cf.buscar_cfg(indice, cf.CONSULTA_AQUECIMENTO, cf.Config("regras", "hibrido", cf.N_AQUECIMENTO,
                                                                     cfg.max_length), rr, k=None)
        if manual:
            self.preparar_manual()

    def preparar_manual(self) -> None:
        self.recursos.indice("manual")
        cf.aquecer(self.recursos, "manual", self.cfg_manual.max_length)

    def ranking_regras(self, consulta: str, cfg: ConfigRegras, k: int | None = None):
        return cf.buscar_cfg(self.recursos.indice("regras"), consulta, cfg.cfg_e4(), self.reranker_de(cfg), k=k)

    def ranking_manual(self, consulta: str, k: int | None = None):
        return cf.buscar_cfg(self.recursos.indice("manual"), consulta, self.cfg_manual,
                             self.recursos.reranker_de(self.cfg_manual), k=k)

    def buscar_regras(self, consulta: str, cfg: ConfigRegras, k: int = K, excluir=()) -> list[dict]:
        """As k melhores regras. `excluir` esconde a regra de referência (regra, seção 8): busca k + len(excluir)
        e corta em k depois de tirar as escondidas."""
        ranking = self.ranking_regras(consulta, cfg, k=k + len(excluir))
        visiveis = [n for n in ranking if n.node.metadata["regra_id"] not in set(excluir)][:k]
        return [cf.descrever_regra(n, i) for i, n in enumerate(visiveis, 1)]

    def buscar_manual(self, consulta: str, k: int = K) -> list[dict]:
        return [cf.descrever_trecho(n, i) for i, n in enumerate(self.ranking_manual(consulta, k=k), 1)]


# ---------------------------------------------------------------- medição (regra, seção 7.4) ----
class ChamadaMedida:
    """Embrulha a função de busca e guarda, por chamada, o relógio de desempenho e o de parede."""

    def __init__(self, chamar, relogio=time.perf_counter, parede=time.time):
        self._chamar, self._relogio, self._parede = chamar, relogio, parede
        self.registros: list[dict] = []

    def __call__(self, texto):
        p0, w0 = self._relogio(), self._parede()
        resultado = self._chamar(texto)
        self.registros.append({"perf_s": self._relogio() - p0, "parede_ini": w0, "parede_fim": self._parede()})
        return resultado


def divergencias(registros: list[dict]) -> list[str]:
    """Divergência de relógio nas chamadas medidas de UMA configuração (regra, seção 7.4)."""
    achadas = []
    for i, r in enumerate(registros):
        parede = r["parede_fim"] - r["parede_ini"]
        if parede - r["perf_s"] > max(DIVERGENCIA_CHAMADA_S, DIVERGENCIA_CHAMADA_FRACAO * r["perf_s"]):
            achadas.append(f"chamada {i + 1}: relógio de parede {parede:.1f} s contra {r['perf_s']:.1f} s medidos")
        if i and r["parede_ini"] - registros[i - 1]["parede_fim"] > LACUNA_ENTRE_CHAMADAS_S:
            achadas.append(f"lacuna de {r['parede_ini'] - registros[i - 1]['parede_fim']:.0f} s antes da chamada {i + 1}")
    return achadas


def medir_regras(cfg: ConfigRegras, consultas: list[dict], chamar, posicao, *, limite: float,
                 repeticoes: int = REPETICOES, fator: float = FATOR_CONFIRMACAO, relogio=time.perf_counter,
                 avisar=None) -> dict:
    """Mede UMA configuração de regras. Mesmas definições do medir_configuracao da Entrega 4 (cada consulta vale a
    MENOR das repetições; a latência é a MAIOR entre as consultas; o acerto vem da 1ª repetição), com a poda desta
    regra: 1ª medição acima de fator × limite encerra de imediato; entre o limite e esse valor, só encerra se a
    repetição seguinte também passar do limite."""
    por_consulta, posicoes = [], []

    def excluida(c, tempos):
        if avisar:
            avisar(f"    {c['id']}: {', '.join(f'{t:.1f}' for t in tempos)} s > {limite:.2f} s -> excluída por latência")
        return {"config": cfg.to_dict(), "excluida": True,
                "excluida_por": {"consulta": c["id"], "tempos_s": [round(t, 3) for t in tempos],
                                 "limite_s": round(limite, 3)},
                "n_consultas": len(consultas), "consultas_medidas": len(por_consulta)}

    for i, c in enumerate(consultas, 1):
        t0 = relogio()
        ranking = chamar(c["consulta"])
        tempos = [relogio() - t0]
        if tempos[0] > limite and (tempos[0] > fator * limite or repeticoes < 2):
            return excluida(c, tempos)
        for _ in range(max(0, repeticoes - 1)):
            t0 = relogio()
            chamar(c["consulta"])
            tempos.append(relogio() - t0)
            if tempos[0] > limite and len(tempos) == 2 and tempos[1] > limite:
                return excluida(c, tempos)
        pos = posicao(ranking, c)
        posicoes.append(pos)
        por_consulta.append({"id": c["id"], "posicao": pos, "tempos_s": [round(t, 3) for t in tempos],
                             "min_s": round(min(tempos), 3)})
        if avisar:
            avisar(f"    {i}/{len(consultas)} {c['id']}: posição {pos if pos else 'fora'}, {min(tempos):.2f} s")
    exatas = cf.metricas_exatas(posicoes)
    return {"config": cfg.to_dict(), "excluida": False, "excluida_por": None, "n_consultas": len(consultas),
            "metricas": cf.av2.metricas(posicoes), "hit3_frac": str(exatas["hit@3"]), "mrr_frac": str(exatas["MRR"]),
            "latencia_s": max(p["min_s"] for p in por_consulta) if por_consulta else 0.0,
            "por_consulta": por_consulta}


# ---------------------------------------------------------------- regra de escolha (regra, seção 7.5) ----
def escolher_regras(medidas: dict[str, dict], lat_manual: float, teto: float = TETO_BUSCA_S) -> dict:
    """`medidas`: id (R0..R4) -> resultado de medir_regras, ou {"indisponivel": True, "motivo": ...}.
    1. Só substitui R0 uma candidata viável com hit@3 ESTRITAMENTE maior. 2. Entre elas: maior hit@3, maior MRR,
    menor latência, a mais simples (ordem da grade). 3. Nenhuma supera: fica R0. Comparações em fração exata."""
    def viavel(d):
        return not d.get("indisponivel") and not d["excluida"] and d["latencia_s"] + lat_manual <= teto

    r0 = medidas.get("R0")
    if r0 is None or not viavel(r0):
        raise ValueError("R0 (linha de base) não foi medida ou não coube no teto: caso que a regra não prevê. "
                         "Pare e relate; não escolha outra configuração por conta própria.")
    base = Fraction(r0["hit3_frac"])
    situacao, candidatas = {}, []
    for i, rid in enumerate(GRADE_REGRAS):
        d = medidas.get(rid)
        if d is None:
            situacao[rid] = "não medida"
        elif d.get("indisponivel"):
            situacao[rid] = f"indisponível: {d.get('motivo', '')}"
        elif d["excluida"]:
            situacao[rid] = "excluída por latência"
        elif not viavel(d):
            situacao[rid] = f"inviável: {d['latencia_s']:.2f} s + manual {lat_manual:.2f} s > {teto:g} s"
        elif rid == "R0":
            situacao[rid] = "linha de base"
        elif Fraction(d["hit3_frac"]) > base:
            situacao[rid] = "supera R0"
            candidatas.append(((-Fraction(d["hit3_frac"]), -Fraction(d["mrr_frac"]), d["latencia_s"], i), rid))
        else:
            situacao[rid] = "não supera R0 em hit@3"
    candidatas.sort()
    escolhida = candidatas[0][1] if candidatas else "R0"
    if not candidatas:
        decidido = "nenhuma candidata viável tem hit@3 maior que o de R0"
    elif len(candidatas) == 1:
        decidido = "única candidata que supera R0"
    else:
        a, b = candidatas[0][0], candidatas[1][0]
        decidido = ("maior hit@3", "maior MRR", "menor latência", "mais simples")[
            next(j for j in range(4) if a[j] != b[j])]
    return {"escolhida": escolhida, "decidido_por": decidido, "situacao": situacao, "lat_manual_s": lat_manual,
            "teto_s": teto, "hit3_r0": str(base)}


def carregar_config_agente(caminho: Path = ARQ_CONFIG) -> ConfigRegras:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    cfg = grade_regras()[dados["escolhida"]]
    if dados.get("config") and dados["config"] != cfg.to_dict():
        raise ValueError(f"{Path(caminho).name}: a configuração gravada não é a {cfg.id} da grade do código")
    return cfg


# ---------------------------------------------------------------- insumos e trava do git ----
def conferir_regra(caminho: Path = ARQ_REGRA, esperado: str = HASH_REGRA) -> tuple[bool, str]:
    obtido = sha256_arquivo(caminho, lf=True)
    return obtido == esperado, obtido


def conferir_insumos(raiz: Path = RAIZ, caminho_regra: Path = ARQ_REGRA) -> list[dict]:
    """Tabela da seção 13 da regra. Aceita o sha256 do arquivo cru ou com fins de linha LF (o git do Windows pode
    trocar LF por CRLF num checkout; o conteúdo é o mesmo)."""
    saida = []
    for rel, esperado in cf.insumos_da_regra(caminho_regra):
        arq = Path(raiz) / rel
        obtidos = {sha256_arquivo(arq), sha256_arquivo(arq, lf=True)} if arq.exists() else set()
        saida.append({"arquivo": rel, "esperado": esperado, "ok": esperado in obtidos,
                      "obtido": None if not obtidos else (esperado if esperado in obtidos else sorted(obtidos)[0])})
    return saida


def _git(pasta: Path, *args) -> tuple[int, str]:
    r = subprocess.run(["git", "--no-optional-locks", "-C", str(pasta), *args], capture_output=True, text=True,
                       timeout=30)
    return r.returncode, (r.stdout if r.returncode == 0 else r.stderr).strip()


def estado_git(caminho: Path) -> dict:
    """Só leitura. commitado = existe, tem commit e não tem mudança pendente."""
    caminho = Path(caminho)
    if not caminho.exists():
        return {"commitado": False, "commit": None, "erro": f"{caminho.name} não existe"}
    try:
        rc1, log = _git(caminho.parent, "log", "-1", "--format=%H|%cI", "--", caminho.name)
        rc2, st = _git(caminho.parent, "status", "--porcelain", "--", caminho.name)
    except Exception as e:  # git ausente, sem permissão, tempo esgotado
        return {"commitado": False, "commit": None, "erro": f"git indisponível: {e}"}
    if rc1 or rc2:
        return {"commitado": False, "commit": None, "erro": f"git falhou: {log or st}"}
    commit, _, data = log.partition("|")
    if not commit:
        return {"commitado": False, "commit": None, "erro": f"{caminho.name} nunca foi commitado"}
    if st:
        return {"commitado": False, "commit": commit, "data": data,
                "erro": f"{caminho.name} tem mudanças não commitadas"}
    return {"commitado": True, "commit": commit, "data": data, "erro": None}


def trava_dev(regra: Path = ARQ_REGRA, mensagens=None, esperado: str = HASH_REGRA) -> list[str]:
    """Regra, cabeçalho e D1: a regra e os dois arquivos de mensagens commitados, sem mudanças, e o sha256 da
    regra igual ao do código. Lista vazia = pode rodar. Não existe atalho."""
    problemas = []
    for arq in [regra, *(mensagens if mensagens is not None else ARQ_ROTEAMENTO.values())]:
        e = estado_git(arq)
        if not e["commitado"]:
            problemas.append(e["erro"])
    if Path(regra).exists():
        ok, obtido = conferir_regra(regra, esperado)
        if not ok:
            problemas.append(f"o sha256 da regra ({obtido[:12]}...) não é o registrado no código ({esperado[:12]}...)")
    return problemas


def trava_teste(*, regra: Path = ARQ_REGRA, mensagens=None, config: Path = ARQ_CONFIG, dev: Path = ARQ_DEV_JSON,
                saidas=None, esperado: str = HASH_REGRA) -> list[str]:
    """Regra, seção 9: (a) regra commitada e com o sha256 do código; (b) config_agente.json e
    resultados_agente_dev.json commitados, sem mudanças; (c) o commit de (b) é posterior ao da regra;
    (d) os resultados do teste não existem. Lista vazia = pode rodar. Não existe atalho."""
    problemas = trava_dev(regra, mensagens, esperado)                                       # (a)
    estados = [estado_git(config), estado_git(dev)]                                          # (b)
    problemas += [e["erro"] for e in estados if not e["commitado"]]
    c_regra = estado_git(regra).get("commit")
    if c_regra and all(e["commitado"] for e in estados):                                     # (c)
        for e, arq in zip(estados, (config, dev)):
            rc, _ = _git(Path(regra).parent, "merge-base", "--is-ancestor", c_regra, e["commit"])
            if rc != 0 or e["commit"] == c_regra:
                problemas.append(f"o commit de {Path(arq).name} não é posterior ao commit da regra")
    for arq in (saidas if saidas is not None else (ARQ_TESTE_JSON, ARQ_TESTE_MD)):          # (d)
        if Path(arq).exists():
            problemas.append(f"{Path(arq).name} já existe: o teste roda uma vez só")
    return problemas
