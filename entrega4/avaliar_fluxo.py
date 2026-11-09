# -*- coding: utf-8 -*-
"""Entrega 4 - avaliação e escolha da configuração do fluxo, pela regra pré-registrada em regra_escolha_fluxo.md.

    python avaliar_fluxo.py grade       # lista as 28 configurações, a ordem de execução e o que já foi medido (sem modelo)
    python avaliar_fluxo.py insumos     # confere os sha256 da seção 11 da regra (sem modelo)
    python avaliar_fluxo.py dev         # desenvolvimento: grade, acerto e latência; checkpoint por configuração
    python avaliar_fluxo.py escolher    # aplica a regra da seção 6 e grava config_escolhida.json
    python avaliar_fluxo.py teste       # teste, UMA vez, só com a dupla escolhida (só relata)
    python avaliar_fluxo.py tudo        # dev -> escolher -> teste, na mesma execução
    python avaliar_fluxo.py relatorio dev|teste   # refaz o .md a partir do .json (se faltar)

O desenvolvimento decide; o teste só relata. Depois de ver o teste, não se ajusta nada.
O dev só roda se: o arquivo da regra tem o sha256 registrado; a regra está commitada (a data do commit, feito pela
aluna, é a prova); e os insumos da seção 11 conferem.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from comum_fluxo import (ARQ_REGRA, AQUI, HASH_REGRA, K, N_CONSULTAS, REPETICOES, TETO_S, Config,
                         Recursos, agora, aquecer, buscar_cfg, carregar_checkpoint, carregar_config,
                         carregar_consultas, configurar_saida, conferir_insumos, conferir_regra, escolher,
                         estado_git_da_regra, gravar_exclusivo, imprimir, medir_configuracao, plano_execucao,
                         posicao_manual, posicao_regras, salvar_checkpoint, sha256_arquivo, todas_as_configs)


@dataclass(frozen=True)
class Saidas:
    """Onde ficam os arquivos gerados. O padrão é a pasta da Entrega 4; os testes passam uma pasta temporária."""

    pasta: Path = AQUI

    @property
    def checkpoints(self) -> Path:
        return self.pasta / "dev_checkpoints"

    @property
    def execucoes(self) -> Path:
        return self.checkpoints / "_execucoes.jsonl"

    @property
    def dev_json(self) -> Path:
        return self.pasta / "resultados_fluxo_dev.json"

    @property
    def dev_md(self) -> Path:
        return self.pasta / "resultados_fluxo_dev.md"

    @property
    def config(self) -> Path:
        return self.pasta / "config_escolhida.json"

    @property
    def teste_json(self) -> Path:
        return self.pasta / "resultados_fluxo_teste.json"

    @property
    def teste_md(self) -> Path:
        return self.pasta / "resultados_fluxo_teste.md"


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1)


def _posicao_de(indice: str):
    return posicao_regras if indice == "regras" else posicao_manual


def _medir_indice(recursos: Recursos, cfg: Config, consultas: list[dict], *, avisar, relogio, repeticoes, teto) -> dict:
    idx = recursos.indice(cfg.indice)
    rr = recursos.reranker_de(cfg)

    def chamar(texto):
        return buscar_cfg(idx, texto, cfg, rr, k=None)

    return medir_configuracao(cfg, consultas, chamar, _posicao_de(cfg.indice), repeticoes=repeticoes, teto=teto,
                              relogio=relogio, avisar=avisar)


# ---------------------------------------------------------------- desenvolvimento ----
def rodar_dev(recursos: Recursos, pasta_ckpt: Path, consultas: dict[str, list[dict]], *, avisar=imprimir,
              relogio=time.perf_counter, repeticoes: int = REPETICOES, teto: float = TETO_S) -> dict[str, dict]:
    """Mede as 28 configurações no conjunto de desenvolvimento, uma fase por vez (sem reranker; max_length 512;
    max_length 2048), com checkpoint por configuração. Retoma pelo que falta. Devolve nome -> resultado."""
    resultados: dict[str, dict] = {}
    total = len(todas_as_configs())
    for max_length, cfgs in plano_execucao():
        pendentes = []
        for cfg in cfgs:
            ck = carregar_checkpoint(pasta_ckpt, cfg)
            if ck is None:
                pendentes.append(cfg)
            else:
                resultados[cfg.nome] = ck
        titulo = "sem reranker" if max_length == 0 else f"reranker com max_length {max_length}"
        avisar(f"\n== Fase: {titulo} ({len(cfgs) - len(pendentes)} já medidas, {len(pendentes)} a medir) ==")
        if not pendentes:
            continue
        if max_length:
            recursos.liberar_rerankers(exceto={max_length})
        for indice in ("regras", "manual"):
            if any(c.indice == indice for c in pendentes):
                avisar(f"  aquecimento ({indice}, max_length {max_length or 'sem reranker'})")
                aquecer(recursos, indice, max_length)
        for cfg in pendentes:
            avisar(f"  [{len(resultados) + 1}/{total}] {cfg.nome}: {cfg.descricao()}")
            inicio = agora()
            dados = _medir_indice(recursos, cfg, consultas[cfg.indice], avisar=avisar, relogio=relogio,
                                  repeticoes=repeticoes, teto=teto)
            dados.update({"inicio": inicio, "fim": agora(), "dispositivo": dict(recursos.dispositivos)})
            salvar_checkpoint(pasta_ckpt, cfg, dados)
            resultados[cfg.nome] = dados
            if dados["excluida"]:
                avisar(f"    -> excluída por latência (consulta {dados['excluida_por']['consulta']}: "
                       f"{dados['excluida_por']['tempo_s']:.1f} s)")
            else:
                m = dados["metricas"]
                avisar(f"    -> hit@3 {m['hit@3']:.3f} | MRR {m['MRR']:.3f} | latência máx. {dados['latencia_s']:.2f} s")
    return resultados


def registrar_execucao(saidas: Saidas, info: dict) -> None:
    saidas.checkpoints.mkdir(parents=True, exist_ok=True)
    with open(saidas.execucoes, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")


def ler_execucoes(saidas: Saidas) -> list[dict]:
    if not saidas.execucoes.exists():
        return []
    return [json.loads(l) for l in saidas.execucoes.read_text(encoding="utf-8").splitlines() if l.strip()]


def montar_dev(resultados: dict[str, dict], saidas: Saidas, git: dict, insumos: list[dict], regra_sha: str) -> dict:
    return {"gerado_em": agora(), "regra_sha256": regra_sha, "git_regra": git, "insumos": insumos,
            "teto_s": TETO_S, "repeticoes": REPETICOES, "k": K,
            "n_consultas": {"regras": N_CONSULTAS[("regras", "dev")], "manual": N_CONSULTAS[("manual", "dev")]},
            "execucoes": ler_execucoes(saidas),
            "configs": {c.nome: resultados[c.nome] for c in todas_as_configs()}}


def _celulas(d: dict) -> str:
    if d["excluida"]:
        e = d["excluida_por"]
        return f"excluída por latência ({e['consulta']}: {e['tempo_s']:.1f} s) | - | - | - | - | - | -"
    m = d["metricas"]
    return (f"medida | {m['hit@1']:.2f} | {m['hit@3']:.2f} | {m['hit@5']:.2f} | {m['hit@10']:.2f} | "
            f"{m['MRR']:.3f} | {d['latencia_s']:.2f}")


def formatar_md_dev(dev: dict) -> str:
    n = dev["n_consultas"]
    g = dev["git_regra"]
    linhas = [f"# Desenvolvimento do fluxo (Entrega 4) - regras: {n['regras']} consultas; manual: {n['manual']} consultas",
              "",
              f"Gerado em {dev['gerado_em']}. Teto {dev['teto_s']:g} s por pergunta (regras + manual somados); "
              f"{dev['repeticoes']} repetições por consulta, vale a menor; a latência da configuração é a maior "
              f"entre as consultas. Acerto e MRR vêm da 1ª repetição, sobre o ranking completo.",
              "",
              f"Regra: sha256 `{dev['regra_sha256']}`. Commit da regra: "
              f"{(g.get('commit') or 'não verificado')[:12]} em {g.get('data') or 'n/d'}.",
              ""]
    for titulo, indice in (("Regras (Entrega 2, com_pontos)", "regras"), ("Manual (Entrega 3, estratégia C)", "manual")):
        linhas += [f"## {titulo}", "",
                   "| configuração | situação | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência máx. (s) |",
                   "|---|---|---|---|---|---|---|---|"]
        for c in todas_as_configs():
            if c.indice == indice:
                linhas.append(f"| {c.nome} | {_celulas(dev['configs'][c.nome])} |")
        linhas.append("")
    linhas += ["## Carregamento e aquecimento (fora do teto; segundos, por execução)", ""]
    if not dev["execucoes"]:
        linhas.append("(sem registro)")
    for i, e in enumerate(dev["execucoes"], 1):
        carga = ", ".join(f"{k} {v}" for k, v in e.get("tempos_carga_s", {}).items())
        linhas.append(f"- Execução {i} ({e.get('inicio')} a {e.get('fim')}; dispositivo: "
                      f"{e.get('dispositivos')}): {carga}")
    linhas += ["", "## Insumos (sha256 da seção 11 da regra)", ""]
    linhas.append("Todos conferem." if all(i["ok"] for i in dev["insumos"])
                  else "Divergências: " + ", ".join(i["arquivo"] for i in dev["insumos"] if not i["ok"]))
    return "\n".join(linhas) + "\n"


def formatar_escolha(res: dict) -> str:
    linhas = [f"Duplas: {res['n_duplas_total']} no total; {res['n_duplas_viaveis']} sem exclusão por latência e "
              f"dentro de {res['teto_s']:g} s."]
    if not res["escolha"]:
        linhas.append("NENHUMA dupla coube no teto: o desenvolvimento termina sem escolha (regra, seção 6).")
        return "\n".join(linhas)
    linhas += [f"Decidida por: {res['decidido_por']} (primeiro critério em que a escolhida difere da 2ª colocada).", "",
               "| # | regras | manual | soma hit@3 | soma MRR | latência da dupla (s) |", "|---|---|---|---|---|---|"]
    for i, d in enumerate(res["melhores"], 1):
        linhas.append(f"| {i} | {d['regras']} | {d['manual']} | {d['soma_hit3_float']:.4f} ({d['soma_hit3']}) | "
                      f"{d['soma_mrr_float']:.4f} | {d['latencia_dupla_s']:.2f} |")
    return "\n".join(linhas)


def aplicar_escolha(dev: dict, saidas: Saidas, regra_sha: str) -> dict:
    """Seção 6. Grava config_escolhida.json (abertura exclusiva), com a dupla, as medidas do dev, as 5 melhores
    duplas e o sha256 da regra. Sem dupla viável, grava o mesmo arquivo com escolha = null e o motivo."""
    esperados = {c.nome for c in todas_as_configs()}
    if set(dev["configs"]) != esperados:
        faltam = sorted(esperados - set(dev["configs"]))
        raise ValueError(f"o desenvolvimento não está completo; faltam: {faltam}")
    res = escolher(dev["configs"], teto=dev["teto_s"])
    saida = {"gerado_em": agora(), "regra_sha256": regra_sha, "teto_s": dev["teto_s"], "k": K,
             "resultados_dev_sha256": sha256_arquivo(saidas.dev_json), **res, "configs": None, "medidas_dev": None}
    if res["escolha"]:
        e = res["escolha"]
        saida["configs"] = {i: dev["configs"][e[i]]["config"] for i in ("regras", "manual")}
        saida["medidas_dev"] = {i: {k: dev["configs"][e[i]][k] for k in ("metricas", "hit3_frac", "mrr_frac", "latencia_s")}
                                for i in ("regras", "manual")}
    gravar_exclusivo(saidas.config, _json(saida))
    return saida


# ---------------------------------------------------------------- teste ----
def rodar_teste(recursos: Recursos, cfgs: dict[str, Config], consultas: dict[str, list[dict]], *, avisar=imprimir,
                relogio=time.perf_counter, repeticoes: int = REPETICOES) -> dict:
    """Seção 7: uma vez, só com a dupla escolhida. Sem poda por latência: se passar do teto, relata-se."""
    for indice in ("regras", "manual"):
        avisar(f"aquecimento ({indice})")
        aquecer(recursos, indice, cfgs[indice].max_length)
    saida = {}
    for indice in ("regras", "manual"):
        cfg = cfgs[indice]
        avisar(f"\n== Teste: {cfg.nome} ({cfg.descricao()}) ==")
        d = _medir_indice(recursos, cfg, consultas[indice], avisar=avisar, relogio=relogio, repeticoes=repeticoes,
                          teto=float("inf"))
        lat = [p["min_s"] for p in d["por_consulta"]]
        d["latencia_mediana_s"] = round(statistics.median(lat), 3)
        d["latencia_max_s"] = round(max(lat), 3)
        saida[indice] = d
    return saida


def formatar_md_teste(teste: dict) -> str:
    c = teste["dupla"]
    linhas = [f"# Teste do fluxo (Entrega 4) - dupla escolhida no desenvolvimento", "",
              f"Gerado em {teste['gerado_em']}. Rodou uma vez. Só relata: nada foi ajustado depois de ver estes números.",
              f"Regra: sha256 `{teste['regra_sha256']}`. config_escolhida.json: sha256 `{teste['config_sha256']}`.",
              f"Dispositivo: {teste['dispositivos']}.", "",
              "| índice | configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência mediana (s) | latência máx. (s) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for indice in ("regras", "manual"):
        d = teste["indices"][indice]
        m = d["metricas"]
        linhas.append(f"| {indice} | {c[indice]} | {m['n']} | {m['hit@1']:.2f} | {m['hit@3']:.2f} | {m['hit@5']:.2f} | "
                      f"{m['hit@10']:.2f} | {m['MRR']:.3f} | {d['latencia_mediana_s']:.2f} | {d['latencia_max_s']:.2f} |")
    pior = teste["indices"]["regras"]["latencia_max_s"] + teste["indices"]["manual"]["latencia_max_s"]
    linhas += ["", f"Teto: {teste['teto_s']:g} s por pergunta. Pior caso de cada índice somado: {pior:.2f} s "
                   f"(as consultas dos dois índices são diferentes; o teto vale para a soma na mesma pergunta).", "",
               "## Posição do primeiro acerto, por consulta", ""]
    for indice in ("regras", "manual"):
        linhas.append(f"**{indice}**: " + "; ".join(
            f"{p['id']} {p['posicao'] if p['posicao'] else 'fora'} ({p['min_s']:.1f} s)"
            for p in teste["indices"][indice]["por_consulta"]))
        linhas.append("")
    linhas += ["## Carregamento e aquecimento (fora do teto; segundos)", "",
               ", ".join(f"{k} {v}" for k, v in teste["tempos_carga_s"].items())]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- comandos ----
def _barrar_regra() -> str | None:
    ok, obtido = conferir_regra()
    if not ok:
        print(f"A regra mudou desde o pré-registro: sha256 {obtido} (esperado {HASH_REGRA}). Mudança vira desvio "
              f"declarado no README e não reescreve a regra; nada foi executado.", file=sys.stderr)
        return None
    return obtido


def cmd_grade(saidas: Saidas) -> int:
    n = 0
    for max_length, cfgs in plano_execucao():
        imprimir(f"\nFase: {'sem reranker' if max_length == 0 else f'reranker com max_length {max_length}'}")
        for cfg in cfgs:
            n += 1
            try:
                ck = carregar_checkpoint(saidas.checkpoints, cfg)
            except ValueError as e:
                ck, situacao = None, f"CHECKPOINT INVÁLIDO ({e})"
            else:
                situacao = "a medir" if ck is None else ("excluída por latência" if ck["excluida"] else
                                                          f"medida (latência {ck['latencia_s']:.2f} s)")
            imprimir(f"  {n:2d}. {cfg.nome:<34} {cfg.descricao():<52} {situacao}")
    return 0


def cmd_insumos() -> int:
    saida = conferir_insumos()
    for i in saida:
        imprimir(f"{'ok   ' if i['ok'] else 'DIFERE'} {i['arquivo']}" + ("" if i["ok"] else f" (obtido {i['obtido']})"))
    imprimir(f"\n{sum(i['ok'] for i in saida)}/{len(saida)} conferem.")
    return 0 if all(i["ok"] for i in saida) else 1


def cmd_dev(saidas: Saidas, args, recursos: Recursos | None = None) -> int:
    regra_sha = _barrar_regra()
    if regra_sha is None:
        return 2
    if saidas.dev_json.exists():
        imprimir("resultados_fluxo_dev.json já existe: o desenvolvimento terminou. Próximo passo: "
                 "python avaliar_fluxo.py escolher")
        return 0
    git = estado_git_da_regra(ARQ_REGRA)
    if not git["commitada"] and not args.sem_git:
        print(f"A regra não está commitada ({git['erro']}). A data do commit, feito por você, é a prova do "
              f"pré-registro: faça o commit de entrega4\\regra_escolha_fluxo.md antes do desenvolvimento. "
              f"(--sem-git ignora esta checagem e registra que o commit não foi verificado.)", file=sys.stderr)
        return 2
    if not git["commitada"]:
        git = {**git, "commit": None, "data": None}
    insumos = conferir_insumos()
    if not all(i["ok"] for i in insumos) and not args.aceitar_insumos:
        for i in insumos:
            if not i["ok"]:
                print(f"insumo diferente do registrado na regra: {i['arquivo']}", file=sys.stderr)
        print("Nada foi executado. (--aceitar-insumos roda mesmo assim e registra a divergência.)", file=sys.stderr)
        return 2
    consultas = {i: carregar_consultas(i, "dev") for i in ("regras", "manual")}
    for i in consultas:
        if len(consultas[i]) != N_CONSULTAS[(i, "dev")]:
            print(f"conjunto de desenvolvimento de {i}: {len(consultas[i])} consultas, a regra diz "
                  f"{N_CONSULTAS[(i, 'dev')]}. Nada foi executado.", file=sys.stderr)
            return 2
    recursos = recursos or Recursos()
    inicio = agora()
    imprimir(f"Desenvolvimento ({len(todas_as_configs())} configurações, teto {TETO_S:g} s). "
             f"Deixe o computador acordado e sem outras tarefas pesadas.")
    resultados = rodar_dev(recursos, saidas.checkpoints, consultas)
    registrar_execucao(saidas, {"inicio": inicio, "fim": agora(), "tempos_carga_s": recursos.tempos_carga_s,
                                "dispositivos": recursos.dispositivos, "erros": recursos.erros})
    dev = montar_dev(resultados, saidas, git, insumos, regra_sha)
    gravar_exclusivo(saidas.dev_json, _json(dev))
    gravar_exclusivo(saidas.dev_md, formatar_md_dev(dev))
    imprimir(f"\nGravados: {saidas.dev_json.name} e {saidas.dev_md.name}. Próximo passo: "
             f"python avaliar_fluxo.py escolher")
    return 0


def cmd_escolher(saidas: Saidas) -> int:
    regra_sha = _barrar_regra()
    if regra_sha is None:
        return 2
    if not saidas.dev_json.exists():
        print("Falta resultados_fluxo_dev.json: rode antes python avaliar_fluxo.py dev", file=sys.stderr)
        return 2
    if saidas.config.exists():
        print("config_escolhida.json já existe: a escolha é feita uma vez e não se refaz.", file=sys.stderr)
        return 2
    dev = json.loads(saidas.dev_json.read_text(encoding="utf-8"))
    try:
        saida = aplicar_escolha(dev, saidas, regra_sha)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    imprimir(formatar_escolha(saida))
    if not saida["escolha"]:
        return 3
    imprimir(f"\nGravado: {saidas.config.name}. Próximo passo: python avaliar_fluxo.py teste (roda uma vez)")
    return 0


def cmd_teste(saidas: Saidas, recursos: Recursos | None = None) -> int:
    regra_sha = _barrar_regra()
    if regra_sha is None:
        return 2
    if not saidas.config.exists():
        print("Falta config_escolhida.json: o teste só roda depois da escolha no desenvolvimento.", file=sys.stderr)
        return 2
    try:
        cfgs = carregar_config(saidas.config)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 3
    if saidas.teste_json.exists() or saidas.teste_md.exists():
        print("O teste já rodou (resultados_fluxo_teste.* existe). Ele roda uma vez; depois de ver os resultados "
              "não se repete.", file=sys.stderr)
        return 2
    consultas = {i: carregar_consultas(i, "teste") for i in ("regras", "manual")}
    for i in consultas:
        if len(consultas[i]) != N_CONSULTAS[(i, "teste")]:
            print(f"conjunto de teste de {i}: {len(consultas[i])} consultas, a regra diz "
                  f"{N_CONSULTAS[(i, 'teste')]}. Nada foi executado.", file=sys.stderr)
            return 2
    recursos = recursos or Recursos()
    imprimir(f"Teste, uma vez: regras {cfgs['regras'].nome}; manual {cfgs['manual'].nome}.")
    indices = rodar_teste(recursos, cfgs, consultas)
    teste = {"gerado_em": agora(), "regra_sha256": regra_sha, "config_sha256": sha256_arquivo(saidas.config),
             "dupla": {i: cfgs[i].nome for i in cfgs}, "teto_s": TETO_S, "repeticoes": REPETICOES,
             "dispositivos": dict(recursos.dispositivos), "tempos_carga_s": dict(recursos.tempos_carga_s),
             "indices": indices}
    gravar_exclusivo(saidas.teste_json, _json(teste))      # o JSON primeiro: se o .md falhar, o número já está salvo
    gravar_exclusivo(saidas.teste_md, formatar_md_teste(teste))
    imprimir("\n" + formatar_md_teste(teste))
    imprimir(f"Gravados: {saidas.teste_json.name} e {saidas.teste_md.name}. Nada se ajusta depois de ver o teste.")
    return 0


def cmd_relatorio(saidas: Saidas, qual: str) -> int:
    json_, md, formatar = ((saidas.dev_json, saidas.dev_md, formatar_md_dev) if qual == "dev"
                           else (saidas.teste_json, saidas.teste_md, formatar_md_teste))
    if not json_.exists():
        print(f"Falta {json_.name}.", file=sys.stderr)
        return 2
    if md.exists():
        print(f"{md.name} já existe.", file=sys.stderr)
        return 2
    gravar_exclusivo(md, formatar(json.loads(json_.read_text(encoding="utf-8"))))
    imprimir(f"Gravado: {md.name}")
    return 0


def _argumentos(argv):
    p = argparse.ArgumentParser(description="Avaliação e escolha da configuração do fluxo (regra pré-registrada).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("grade")
    sub.add_parser("insumos")
    for nome in ("dev", "tudo"):
        s = sub.add_parser(nome)
        s.add_argument("--sem-git", action="store_true", help="não exige a regra commitada (registra 'não verificado')")
        s.add_argument("--aceitar-insumos", action="store_true", help="roda mesmo se um insumo da seção 11 diferir")
    sub.add_parser("escolher")
    sub.add_parser("teste")
    r = sub.add_parser("relatorio")
    r.add_argument("qual", choices=["dev", "teste"])
    return p.parse_args(argv)


def main(argv=None, saidas: Saidas | None = None, recursos: Recursos | None = None) -> int:
    configurar_saida()
    a = _argumentos(argv)
    saidas = saidas or Saidas()
    if a.cmd == "grade":
        return cmd_grade(saidas)
    if a.cmd == "insumos":
        return cmd_insumos()
    if a.cmd == "dev":
        return cmd_dev(saidas, a, recursos)
    if a.cmd == "escolher":
        return cmd_escolher(saidas)
    if a.cmd == "teste":
        return cmd_teste(saidas, recursos)
    if a.cmd == "relatorio":
        return cmd_relatorio(saidas, a.qual)
    if a.cmd == "tudo":
        recursos = recursos or Recursos()
        for passo in (lambda: cmd_dev(saidas, a, recursos), lambda: cmd_escolher(saidas),
                      lambda: cmd_teste(saidas, recursos)):
            estado = passo()
            if estado != 0:
                return estado
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
