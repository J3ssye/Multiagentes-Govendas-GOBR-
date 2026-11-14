# -*- coding: utf-8 -*-
"""Entrega 5 - desenvolvimento e teste do agente (regra_agente.md, seções 7 a 9).

    python avaliar_agente.py dev          # D1 a D5: confere, mede a busca, escolhe, roda roteamento e geração
    python avaliar_agente.py busca        # só D1 e D2 (medição da busca, com checkpoint por configuração)
    python avaliar_agente.py escolher     # só D3 (aplica a seção 7.5 e grava config_agente.json)
    python avaliar_agente.py roteamento   # roteamento do desenvolvimento (função pura; não grava nada)
    python avaliar_agente.py geracao      # D4 e D5 (precisa de config_agente.json)
    python avaliar_agente.py teste        # UMA vez, depois do commit da escolha; o código recusa fora disso
    python avaliar_agente.py relatorio dev|teste

Não existe atalho para a trava do git: nem opção de linha de comando, nem variável de ambiente.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import agente as ag
import comum_agente as ca
from comum_agente import cf

CONDICOES = "na tomada, tampa aberta, sem suspensão, sem outros programas, OneDrive pausado"


@dataclass
class Saidas:
    """Onde cada coisa é gravada. Os testes apontam tudo para uma pasta temporária."""

    base: Path = ca.AQUI
    regra: Path = ca.ARQ_REGRA
    mensagens: tuple = tuple(ca.ARQ_ROTEAMENTO.values())

    def __post_init__(self):
        b = Path(self.base)
        self.checkpoints, self.arquivada = b / ca.PASTA_CHECKPOINTS.name, b / ca.PASTA_ARQUIVADA.name
        self.config, self.dev_json, self.dev_md = b / ca.ARQ_CONFIG.name, b / ca.ARQ_DEV_JSON.name, b / ca.ARQ_DEV_MD.name
        self.checkpoints_teste = b / ca.PASTA_CHECKPOINTS_TESTE.name
        self.teste_json, self.teste_md = b / ca.ARQ_TESTE_JSON.name, b / ca.ARQ_TESTE_MD.name


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1)


def _ler(arq: Path):
    return json.loads(Path(arq).read_text(encoding="utf-8")) if Path(arq).exists() else None


def _checkpoint(pasta: Path, nome: str, dados: dict | None = None):
    """Lê (dados=None) ou grava com abertura exclusiva: um item concluído nunca é regravado."""
    arq = Path(pasta) / f"{nome}.json"
    if dados is None:
        return _ler(arq)
    Path(pasta).mkdir(parents=True, exist_ok=True)
    ca.gravar_exclusivo(arq, _json(dados))
    return dados


# ------------------------------------------------------------------ D1: conferências ----
def conferir_tudo(saidas: Saidas, para_teste: bool = False) -> list[str]:
    problemas = (ca.trava_teste(regra=saidas.regra, mensagens=saidas.mensagens, config=saidas.config, dev=saidas.dev_json,
                                saidas=(saidas.teste_json, saidas.teste_md))
                 if para_teste else ca.trava_dev(saidas.regra, saidas.mensagens))
    problemas += [f"insumo diferente do registrado na seção 13 da regra: {i['arquivo']}"
                  for i in ca.conferir_insumos(caminho_regra=saidas.regra) if not i["ok"]]
    return problemas


def confirmar_condicoes(entrada=input) -> dict:
    """Regra, seção 7.4: a medição de latência pede a confirmação das condições e a grava no resultado."""
    ca.imprimir(f"Medição de latência. Condições exigidas: {CONDICOES}.")
    resposta = entrada("As condições valem agora? Digite sim para continuar: ").strip().lower()
    na_tomada = None
    try:
        import psutil
        bateria = psutil.sensors_battery()
        na_tomada = None if bateria is None else bool(bateria.power_plugged)
    except Exception:  # noqa: BLE001  (psutil ausente ou sem sensor)
        pass
    return {"confirmado": resposta == "sim", "resposta": resposta, "condicoes": CONDICOES, "na_tomada_psutil": na_tomada,
            "em": ca.agora()}


# ------------------------------------------------------------------ D2: medição da busca ----
def medir_busca(buscador: ca.Buscador, saidas: Saidas, consultas: dict[str, list[dict]], *, avisar=ca.imprimir,
                relogio=time.perf_counter, parede=time.time, repeticoes: int = ca.REPETICOES,
                teto: float = ca.TETO_BUSCA_S) -> dict[str, dict]:
    """Mede M (manual), R0 e R1 a R4, nessa ordem, com checkpoint por configuração. A carga e o aquecimento de
    cada modelo ficam fora das medidas. Devolve nome -> resultado (os nomes: M, R0, ..., R4)."""
    medidas: dict[str, dict] = {}
    m = _checkpoint(saidas.checkpoints, "busca_M")
    if m is None:
        avisar(f"[M] manual: {buscador.cfg_manual.descricao()}")
        buscador.preparar_manual()
        chamar = ca.ChamadaMedida(lambda t: buscador.ranking_manual(t, k=None), relogio, parede)
        m = cf.medir_configuracao(buscador.cfg_manual, consultas["manual"], chamar, cf.posicao_manual,
                                  repeticoes=repeticoes, teto=teto, relogio=relogio, avisar=avisar)
        m.update({"divergencias": ca.divergencias(chamar.registros), "medido_em": ca.agora()})
        _checkpoint(saidas.checkpoints, "busca_M", m)
    medidas["M"] = m
    if m["excluida"]:
        raise RuntimeError("a configuração do manual passou do teto sozinha: caso que a regra não prevê. Pare e relate.")
    limite = teto - m["latencia_s"]
    for rid, cfg in ca.grade_regras().items():
        r = _checkpoint(saidas.checkpoints, f"busca_{rid}")
        if r is None:
            avisar(f"[{rid}] regras: {cfg.descricao()} (limite {limite:.2f} s = {teto:g} s - manual {m['latencia_s']:.2f} s)")
            try:
                buscador.preparar(cfg, manual=False)
            except Exception as e:  # noqa: BLE001  (download ou carga do reranker)
                if not cfg.n or cfg.modelo != ca.MODELO_RERANKER_MENOR:
                    raise
                r = {"config": cfg.to_dict(), "indisponivel": True, "motivo": f"{type(e).__name__}: {e}"[:300],
                     "medido_em": ca.agora()}
                avisar(f"    {rid} saiu da grade (modelo indisponível): {r['motivo'][:120]}")
            else:
                chamar = ca.ChamadaMedida(lambda t, c=cfg: buscador.ranking_regras(t, c, k=None), relogio, parede)
                r = ca.medir_regras(cfg, consultas["regras"], chamar, cf.posicao_regras, limite=limite,
                                    repeticoes=repeticoes, relogio=relogio, avisar=avisar)
                r.update({"divergencias": ca.divergencias(chamar.registros), "medido_em": ca.agora()})
            _checkpoint(saidas.checkpoints, f"busca_{rid}", r)
        medidas[rid] = r
    return medidas


def arquivar_se_divergiu(saidas: Saidas, medidas: dict[str, dict], avisar=ca.imprimir) -> list[str]:
    """Regra, seção 7.4: com divergência de relógio em qualquer configuração, a execução INTEIRA é arquivada e
    repetida do zero. Decide-se pelos tempos, antes de aplicar a regra de escolha."""
    achadas = [f"{nome}: {d}" for nome, r in medidas.items() for d in r.get("divergencias", [])]
    if achadas:
        destino, i = saidas.arquivada, 1
        while destino.exists():
            i += 1
            destino = saidas.arquivada.with_name(f"{saidas.arquivada.name}_{i}")
        saidas.checkpoints.rename(destino)
        avisar(f"Divergência de relógio ({len(achadas)}): a execução foi arquivada em {destino.name}/ e nada foi "
               f"escolhido. Confira as condições ({CONDICOES}) e rode de novo, do zero.")
        for a in achadas[:10]:
            avisar(f"  - {a}")
    return achadas


# ------------------------------------------------------------------ D3: escolha ----
def aplicar_escolha(saidas: Saidas, medidas: dict[str, dict], extras: dict | None = None) -> dict:
    escolha = ca.escolher_regras({k: v for k, v in medidas.items() if k != "M"}, medidas["M"]["latencia_s"])
    cfg = ca.grade_regras()[escolha["escolhida"]]
    dados = {"gerado_em": ca.agora(), "regra_sha256": ca.sha256_arquivo(saidas.regra, lf=True), "k": ca.K,
             "escolhida": cfg.id, "config": cfg.to_dict(), "config_manual": buscador_cfg_manual_dict(),
             **escolha, "medidas": medidas, **(extras or {})}
    ca.gravar_exclusivo(saidas.config, _json(dados))
    return dados


def buscador_cfg_manual_dict() -> dict:
    return ca.config_manual().to_dict()


# ------------------------------------------------------------------ D4: geração ----
def _g8(resumo: dict | None, referencia: dict | None) -> dict | None:
    if not resumo or not referencia:
        return None
    return {"mesmo_n_blocos": resumo["blocos_parametros"] == referencia["blocos_parametros"],
            "mesmos_tipos_de_acao": resumo["tipos_de_acao"] == referencia["tipos_de_acao"],
            "mesmas_frequencias": resumo["frequencias"] == referencia["frequencias"],
            "gerada": resumo, "referencia": referencia}


def resumo_da_referencia(regra_id: str, raiz: Path = ca.RAIZ) -> dict | None:
    arq = Path(raiz) / regra_id
    if not arq.is_file():
        return None
    return ca.validar(arq.read_text(encoding="utf-8", errors="replace"))["resumo"]


def item_de_geracao(consulta: dict, res: dict) -> dict:
    tent = res["tentativas"] or []
    ultima = tent[-1] if tent else None
    ref = resumo_da_referencia(consulta["relevantes"][0]) if consulta.get("relevantes") else None
    return {"id": consulta["id"], "rota": res["rota"], "status": res["status"], "erro": res.get("erro"),
            "n_tentativas": len(tent), "aceita_na_1a": bool(tent and tent[0]["aceita"]),
            "aceita_ao_fim": res["status"] == "aceita",
            "retentativa_consultou_manual": len(tent) > 1 and tent[1]["consultou_manual"] and not tent[0]["consultou_manual"],
            "consulta_manual": res.get("consulta_manual"), "tokens": res["tokens"], "tempos_s": res["tempos_s"],
            "regras": [{"regra_id": r["regra_id"], "nota": r["nota"]} for r in res["regras"]],
            "manual": [{"folha": m["folha"], "nota": m["nota"]} for m in res["manual"]],
            "g8": _g8(ultima.get("resumo") if ultima else None, ref),
            "g9": ({"premissas": len(ultima["premissas"]), "perguntas": len(ultima["perguntas"]),
                    "avisos": len(ultima["avisos"])} if ultima and ultima["saida_valida"] else None),
            "tentativas": tent}


def rodar_geracao(grafo, consultas: list[dict], pasta: Path, *, avisar=ca.imprimir, detalhar: bool = True) -> list[dict]:
    """Um turno do grafo completo por consulta, com a regra de referência escondida e checkpoint por item.
    detalhar=False (teste): só o progresso, sem rota, aceitação, tentativas nem GOBR de nenhum item."""
    itens = []
    for i, c in enumerate(consultas, 1):
        item = _checkpoint(pasta, f"geracao_{c['id']}")
        if item is None:
            res = ag.executar(grafo, c["consulta"], excluir=c.get("relevantes") or ())
            item = _checkpoint(pasta, f"geracao_{c['id']}", item_de_geracao(c, res))
        avisar(f"  geração {i} de {len(consultas)}" + (f": {c['id']} -> {item['status']} em {item['n_tentativas']} "
                                                       f"tentativa(s), {item['tempos_s'].get('turno', 0):.0f} s"
                                                       if detalhar else ""))
        itens.append(item)
    return itens


def _med_max(valores: list) -> dict:
    v = [x for x in valores if x is not None]
    return {"mediana": statistics.median(v) if v else None, "maximo": max(v) if v else None, "n": len(v)}


def metricas_geracao(itens: list[dict]) -> dict:
    """G1 a G9 (regra, seção 8). Denominador: todas as consultas menos as de erro de infraestrutura."""
    validos = [x for x in itens if x["status"] != "erro_infra"]
    com_gobr = [x for x in validos if x["g9"] is not None]
    nos = sorted({k for x in validos for k in x["tempos_s"]})
    g8 = [x["g8"] for x in validos if x["g8"]]
    return {"n": len(itens), "erro_infra": len(itens) - len(validos), "denominador": len(validos),
            "G1_aceita_na_1a": sum(x["aceita_na_1a"] for x in validos),
            "G2_aceita_ao_fim": sum(x["aceita_ao_fim"] for x in validos),
            "G3_tentativas": {str(n): sum(1 for x in validos if x["n_tentativas"] == n)
                              for n in sorted({x["n_tentativas"] for x in validos})},
            "G4_retentativas_com_manual": sum(bool(x["retentativa_consultou_manual"]) for x in validos),
            "G5_tokens": {c: {**_med_max([x["tokens"][c] for x in validos]),
                              "total": sum(x["tokens"][c] for x in validos)}
                          for c in ("entrada", "saida", "raciocinio", "total", "chamadas")},
            "G6_tempos_s": {no: _med_max([x["tempos_s"].get(no) for x in validos]) for no in nos},
            "G7_busca_regras_acima_do_teto": sum(1 for x in validos
                                                 if x["tempos_s"].get("buscar_regras", 0) > ca.TETO_BUSCA_S),
            "G8_estrutura": {"comparadas": len(g8), "mesmo_n_blocos": sum(x["mesmo_n_blocos"] for x in g8),
                             "mesmos_tipos_de_acao": sum(x["mesmos_tipos_de_acao"] for x in g8),
                             "mesmas_frequencias": sum(x["mesmas_frequencias"] for x in g8)},
            "G9_pontos_de_atencao": {"respostas_com_gobr": len(com_gobr),
                                     "com_premissa_ou_pergunta": sum(1 for x in com_gobr if x["g9"]["premissas"]
                                                                     or x["g9"]["perguntas"]),
                                     **{c: _med_max([x["g9"][c] for x in com_gobr])
                                        for c in ("premissas", "perguntas", "avisos")}},
            "status": {s: sum(1 for x in itens if x["status"] == s) for s in sorted({str(x["status"]) for x in itens})},
            "rotas": {r: sum(1 for x in itens if x["rota"] == r) for r in sorted({x["rota"] for x in itens})}}


# ------------------------------------------------------------------ relatório em Markdown ----
def formatar_md(res: dict, titulo: str) -> str:
    linhas = [f"# {titulo}", "", f"Gerado em {res['gerado_em']}. Regra: sha256 `{res['regra_sha256'][:16]}...`, commit "
              f"`{(res['git'].get('commit') or '')[:7]}`. Configuração de regras: **{res['escolhida']}** "
              f"({res['config']['descricao']}).", ""]
    if res.get("medidas"):
        linhas += ["## Busca (desenvolvimento)", "", "| id | configuração | hit@3 | MRR | latência (s) | situação |",
                   "|---|---|---|---|---|---|"]
        for nome, m in res["medidas"].items():
            desc = m["config"].get("descricao") or m["config"].get("nome")
            if m.get("indisponivel"):
                linhas.append(f"| {nome} | {desc} | | | | indisponível |")
            elif m["excluida"]:
                p = m["excluida_por"]
                tempos = p.get("tempos_s") or [p.get("tempo_s")]
                linhas.append(f"| {nome} | {desc} | | | | excluída em `{p['consulta']}` "
                              f"({', '.join(f'{t:.1f}' for t in tempos)} s) |")
            else:
                linhas.append(f"| {nome} | {desc} | {m['hit3_frac']} | {float(m['metricas']['MRR']):.3f} | "
                              f"{m['latencia_s']:.2f} | {res.get('situacao', {}).get(nome, '')} |")
        linhas += ["", f"Escolha: **{res['escolhida']}**, decidida por: {res['decidido_por']}.", ""]
    if res.get("busca_relato"):
        b = res["busca_relato"]
        linhas += ["## Busca (relato da configuração escolhida)", "",
                   " | ".join(f"{k} {v:.3f}" for k, v in b["metricas"].items() if k != "n") + f" | latência {b['latencia_s']:.2f} s", ""]
    r = res["roteamento"]
    linhas += ["## Roteamento", "", f"Rota: {r['acertos']} de {r['n']}. Desfecho: {r['acertos_desfecho']} de {r['n']}. "
               f"Foram ao manual sem precisar: {r['manual_sem_precisar']}.", "",
               "| origem | n | rota | desfecho |", "|---|---|---|---|"]
    linhas += [f"| {o} | {v['n']} | {v['acertos']} | {v['acertos_desfecho']} |" for o, v in r["por_origem"].items()]
    linhas += ["", "Confusão (esperada->obtida): " + ", ".join(f"{k}: {v}" for k, v in r["confusao"].items()), ""]
    g = res["geracao"]
    d = g["denominador"]
    t = g["G5_tokens"]["total"]
    linhas += ["## Geração", "", f"Consultas: {g['n']} (erro de infraestrutura: {g['erro_infra']}; denominador {d}).", "",
               f"- G1 aceita na 1ª tentativa: {g['G1_aceita_na_1a']} de {d}",
               f"- G2 aceita ao fim: {g['G2_aceita_ao_fim']} de {d}",
               f"- G3 tentativas: {g['G3_tentativas']}",
               f"- G4 retentativas que consultaram o manual: {g['G4_retentativas_com_manual']}",
               f"- G5 tokens por turno (total da API): mediana {t['mediana']}, máximo {t['maximo']}, soma {t['total']}",
               f"- G6 turno (s): mediana {g['G6_tempos_s'].get('turno', {}).get('mediana')}, "
               f"máximo {g['G6_tempos_s'].get('turno', {}).get('maximo')}",
               f"- G7 buscas de regras acima do teto de {ca.TETO_BUSCA_S:g} s: {g['G7_busca_regras_acima_do_teto']}",
               f"- G8 estrutura contra a referência: {g['G8_estrutura']}",
               f"- G9 pontos de atenção: {g['G9_pontos_de_atencao']}", "",
               "Todas descritivas; nenhuma decide configuração. \"Aceita\" é estrutural (regra, seção 6).", ""]
    return "\n".join(linhas)


# ------------------------------------------------------------------ comandos ----
def _barrar(saidas: Saidas, para_teste: bool = False) -> bool:
    problemas = conferir_tudo(saidas, para_teste)
    if problemas:
        print("Nada foi executado. A trava da regra não passou:", file=sys.stderr)
        for p in problemas:
            print(f"  - {p}", file=sys.stderr)
    return bool(problemas)


def _consultas(conjunto: str) -> dict[str, list[dict]]:
    c = {"regras": cf.carregar_consultas("regras", conjunto), "manual": cf.carregar_consultas("manual", conjunto)}
    if len(c["regras"]) != ca.N_GERACAO[conjunto]:
        raise RuntimeError(f"o conjunto de regras ({conjunto}) tem {len(c['regras'])} consultas, não "
                           f"{ca.N_GERACAO[conjunto]}")
    return c


def cmd_busca(saidas: Saidas, buscador=None, entrada=input) -> tuple[int, dict | None]:
    if _barrar(saidas):
        return 2, None
    cond = _ler(saidas.checkpoints / "condicoes.json")
    if cond is None:
        cond = confirmar_condicoes(entrada)
        if not cond["confirmado"]:
            print("Sem a confirmação das condições a latência não é medida.", file=sys.stderr)
            return 2, None
        _checkpoint(saidas.checkpoints, "condicoes", cond)
    buscador = buscador or ca.Buscador()
    medidas = medir_busca(buscador, saidas, _consultas("dev"))
    if arquivar_se_divergiu(saidas, medidas):
        return 3, None
    return 0, {"medidas": medidas, "condicoes": cond, "dispositivos": dict(buscador.recursos.dispositivos),
               "tempos_carga_s": dict(buscador.recursos.tempos_carga_s)}


def cmd_escolher(saidas: Saidas, busca: dict | None = None) -> int:
    if saidas.config.exists():
        ca.imprimir(f"{saidas.config.name} já existe: escolhida {_ler(saidas.config)['escolhida']}. Nada foi regravado.")
        return 0
    if busca is None:
        nomes = ["M", *ca.GRADE_REGRAS]
        medidas = {n: _checkpoint(saidas.checkpoints, f"busca_{n}") for n in nomes}
        if any(v is None for v in medidas.values()):
            print("Faltam medidas da busca. Rode antes: python avaliar_agente.py busca", file=sys.stderr)
            return 2
        if any(m.get("divergencias") for m in medidas.values()):
            print("Há divergência de relógio nas medidas: rode `busca` de novo (ela arquiva e recomeça).", file=sys.stderr)
            return 3
        busca = {"medidas": medidas, "condicoes": _ler(saidas.checkpoints / "condicoes.json")}
    dados = aplicar_escolha(saidas, busca["medidas"], {k: v for k, v in busca.items() if k != "medidas"})
    ca.imprimir(f"Escolhida: {dados['escolhida']} ({dados['config']['descricao']}); decidida por: {dados['decidido_por']}.")
    for rid, s in dados["situacao"].items():
        ca.imprimir(f"  {rid}: {s}")
    return 0


def cmd_roteamento(conjunto: str = "dev") -> dict:
    r = ca.medir_roteamento(ca.carregar_roteamento(conjunto))
    return r


def cmd_geracao(saidas: Saidas, buscador=None, cliente=None, modelo: str = ca.MODELO_GEMINI_PADRAO) -> int:
    if _barrar(saidas):
        return 2
    if saidas.dev_json.exists():
        ca.imprimir(f"{saidas.dev_json.name} já existe. Nada foi regravado.")
        return 0
    escolha = _ler(saidas.config)
    if escolha is None:
        print("Falta config_agente.json. Rode antes: python avaliar_agente.py escolher", file=sys.stderr)
        return 2
    if cliente is None and not ca.chave_gemini():
        print("Defina GOOGLE_API_KEY (ou GEMINI_API_KEY) no ambiente.", file=sys.stderr)
        return 2
    cfg = ca.carregar_config_agente(saidas.config)
    buscador = buscador or ca.Buscador()
    buscador.preparar(cfg)
    grafo = ag.construir_grafo(ag.dependencias_reais(buscador, cfg, modelo=modelo, cliente=cliente, avisar=ca.imprimir))
    roteamento = cmd_roteamento("dev")
    ca.imprimir(f"Roteamento (dev): rota {roteamento['acertos']} de {roteamento['n']}, desfecho "
                f"{roteamento['acertos_desfecho']} de {roteamento['n']}.")
    itens = rodar_geracao(grafo, _consultas("dev")["regras"], saidas.checkpoints)
    res = {"gerado_em": ca.agora(), "conjunto": "dev", "regra_sha256": ca.sha256_arquivo(saidas.regra, lf=True),
           "git": ca.estado_git(saidas.regra), "modelo": modelo, "escolhida": escolha["escolhida"],
           "config": escolha["config"], "config_sha256": ca.sha256_arquivo(saidas.config),
           "medidas": escolha["medidas"], "situacao": escolha["situacao"], "decidido_por": escolha["decidido_por"],
           "roteamento": roteamento, "geracao": metricas_geracao(itens), "itens_geracao": itens}
    ca.gravar_exclusivo(saidas.dev_json, _json(res))
    ca.gravar_exclusivo(saidas.dev_md, formatar_md(res, "Entrega 5 - resultados do desenvolvimento"))
    ca.imprimir(f"\nGravados {saidas.dev_json.name} e {saidas.dev_md.name}.\n")
    ca.imprimir(formatar_md(res, "Entrega 5 - resultados do desenvolvimento"))
    return 0


def cmd_dev(saidas: Saidas, buscador=None, cliente=None, entrada=input) -> int:
    if cliente is None and not ca.chave_gemini():   # falha cedo: a geração (D4) vai precisar da chave
        print("Defina GOOGLE_API_KEY (ou GEMINI_API_KEY) no ambiente antes de começar.", file=sys.stderr)
        return 2
    buscador = buscador or (ca.Buscador() if not _barrar(saidas) else None)
    if buscador is None:
        return 2
    rc, busca = cmd_busca(saidas, buscador, entrada)
    if rc:
        return rc
    rc = cmd_escolher(saidas, busca)
    return rc or cmd_geracao(saidas, buscador, cliente)


def cmd_teste(saidas: Saidas, buscador=None, cliente=None, modelo: str = ca.MODELO_GEMINI_PADRAO) -> int:
    """Regra, seção 9. Roda uma vez. Não imprime rota, aceitação, tentativas nem GOBR de nenhum item."""
    if _barrar(saidas, para_teste=True):
        return 2
    if cliente is None and not ca.chave_gemini():
        print("Defina GOOGLE_API_KEY (ou GEMINI_API_KEY) no ambiente.", file=sys.stderr)
        return 2
    escolha = _ler(saidas.config)
    cfg = ca.carregar_config_agente(saidas.config)
    buscador = buscador or ca.Buscador()
    buscador.preparar(cfg)
    consultas = _consultas("teste")
    ca.imprimir("Teste: roteamento, busca (relato) e geração. Só o progresso é impresso.")
    roteamento = cmd_roteamento("teste")
    relato = _checkpoint(saidas.checkpoints_teste, "busca_relato")
    if relato is None:
        relato = ca.medir_regras(cfg, consultas["regras"], lambda t: buscador.ranking_regras(t, cfg, k=None),
                                 cf.posicao_regras, limite=float("inf"))
        _checkpoint(saidas.checkpoints_teste, "busca_relato", relato)
    grafo = ag.construir_grafo(ag.dependencias_reais(buscador, cfg, modelo=modelo, cliente=cliente))
    itens = rodar_geracao(grafo, consultas["regras"], saidas.checkpoints_teste, detalhar=False)
    res = {"gerado_em": ca.agora(), "conjunto": "teste", "regra_sha256": ca.sha256_arquivo(saidas.regra, lf=True),
           "git": ca.estado_git(saidas.regra), "git_escolha": ca.estado_git(saidas.config), "modelo": modelo,
           "escolhida": escolha["escolhida"], "config": escolha["config"],
           "config_sha256": ca.sha256_arquivo(saidas.config), "busca_relato": relato, "roteamento": roteamento,
           "geracao": metricas_geracao(itens), "itens_geracao": itens}
    ca.gravar_exclusivo(saidas.teste_json, _json(res))
    ca.gravar_exclusivo(saidas.teste_md, formatar_md(res, "Entrega 5 - resultados do teste (uma execução)"))
    ca.imprimir(f"\nGravados {saidas.teste_json.name} e {saidas.teste_md.name}. Depois do teste nada se ajusta.\n")
    ca.imprimir(formatar_md(res, "Entrega 5 - resultados do teste (uma execução)"))
    return 0


def main(argv=None, saidas: Saidas | None = None, buscador=None, cliente=None, entrada=input) -> int:
    cf.configurar_saida()
    p = argparse.ArgumentParser(description="Desenvolvimento e teste do agente da Entrega 5.")
    p.add_argument("comando", choices=["dev", "busca", "escolher", "roteamento", "geracao", "teste", "relatorio"])
    p.add_argument("qual", nargs="?", choices=["dev", "teste"], help="só para `relatorio`")
    a = p.parse_args(argv)
    saidas = saidas or Saidas()
    if a.comando == "dev":
        return cmd_dev(saidas, buscador, cliente, entrada)
    if a.comando == "busca":
        return cmd_busca(saidas, buscador, entrada)[0]
    if a.comando == "escolher":
        return 2 if _barrar(saidas) else cmd_escolher(saidas)
    if a.comando == "roteamento":
        r = cmd_roteamento("dev")
        ca.imprimir(f"Roteamento (dev): rota {r['acertos']} de {r['n']}, desfecho {r['acertos_desfecho']} de {r['n']}.")
        for e in r["erros"]:
            ca.imprimir(f"  {e['id']}: esperada {e['esperada']}, obtida {e['obtida']}")
        return 0
    if a.comando == "geracao":
        return cmd_geracao(saidas, buscador, cliente)
    if a.comando == "teste":
        return cmd_teste(saidas, buscador, cliente)
    arq = saidas.dev_md if (a.qual or "dev") == "dev" else saidas.teste_md
    if not arq.exists():
        print(f"{arq.name} ainda não existe.", file=sys.stderr)
        return 2
    ca.imprimir(arq.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
