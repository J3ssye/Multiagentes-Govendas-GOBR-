# -*- coding: utf-8 -*-
"""
gerar_explicacoes.py — Entrega 1 (Geração de explicações): GOBR -> explicação em linguagem de negócio.

Pipeline:
  1. PARSE      .gobr -> representação estruturada (gobr_parser.py), remove duplicatas por hash
  2. GLOSSÁRIO  cada filtro/ação -> significado + seção do manual (glossario.py)
  3. FICHA      texto estruturado que é a ÚNICA entrada do LLM (explicacao.py)
  4. LLM        Gemini redige a explicação em JSON, com few-shot dos 3 exemplos (leave-one-out)
  5. VERIFICA   checagem automática de completude/fidelidade; se falhar, 1 nova tentativa com o feedback
  6. SAÍDAS     saida/explicacoes.jsonl (para indexar em 27/10), explicacoes.md, relatorio.md

Uso (PowerShell, na pasta entrega1):
    pip install -r requirements.txt
    $env:GEMINI_API_KEY = "sua-chave"
    python gerar_explicacoes.py --limite 3        # teste rápido com 3 regras
    python gerar_explicacoes.py                   # todas (retoma de onde parou se for interrompido)
Sem chave (só a parte determinística):
    python gerar_explicacoes.py --provedor nenhum
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import threading
import time
from collections import Counter
from pathlib import Path

from gobr_parser import normaliza, parse_arquivo
from explicacao import enriquece, explicacao_deterministica, ficha, texto_indexavel, verifica

AQUI = Path(__file__).resolve().parent
PARAR = threading.Event()   # ligado por Ctrl+C ou cota esgotada: todas as threads param
ESPERA_MAXIMA = 180         # segundos; se a API pedir mais que isso, não é limite por minuto, é cota


class CotaEsgotada(Exception):
    """A API recusou por cota (provavelmente diária): não adianta esperar, é preciso parar."""


class Interrompido(Exception):
    """Execução interrompida (Ctrl+C ou outra thread achou cota esgotada)."""
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "titulo": {"type": "STRING"},
        "resumo": {"type": "STRING"},
        "segmentos": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "bloco": {"type": "INTEGER"},
                    "nome": {"type": "STRING"},
                    "criterio": {"type": "STRING"},
                    "acao": {"type": "STRING"},
                    "observacao": {"type": "STRING"},
                },
                "required": ["bloco", "nome", "criterio", "acao", "observacao"],
            },
        },
        "pontos_de_atencao": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["titulo", "resumo", "segmentos", "pontos_de_atencao"],
}


# --------------------------------------------------------------------------------------
# 1-3: parse, dedup, enriquecimento
# --------------------------------------------------------------------------------------

def carrega_regras(dados: Path):
    arquivos = sorted((dados / "exemplos").glob("*.gobr")) + sorted((dados / "referencias").glob("*.gobr"))
    if not arquivos:
        sys.exit(f"Nenhum .gobr encontrado em {dados}/exemplos ou {dados}/referencias. Use --dados.")
    unicas, por_hash = [], {}
    for a in arquivos:
        ir = enriquece(parse_arquivo(a, dados))
        ir["arquivo"] = ir["arquivo"].replace("\\", "/")
        h = ir["sha1"]
        if h in por_hash:
            por_hash[h]["duplicatas"].append(ir["arquivo"])
            continue
        ir["duplicatas"] = []
        ir["ficha"] = ficha(ir)
        por_hash[h] = ir
        unicas.append(ir)
    return arquivos, unicas


# --------------------------------------------------------------------------------------
# 4: LLM
# --------------------------------------------------------------------------------------

def monta_contents(ir: dict, fewshot: dict, irs_por_arquivo: dict, feedback: list[str] | None = None, anterior: str | None = None):
    contents = []
    for arq, alvo in fewshot.items():
        if arq.startswith("_") or arq == ir["arquivo"] or arq not in irs_por_arquivo:
            continue  # leave-one-out: um exemplo nunca é few-shot de si mesmo
        contents.append({"role": "user", "parts": [{"text": "FICHA:\n" + irs_por_arquivo[arq]["ficha"]}]})
        contents.append({"role": "model", "parts": [{"text": json.dumps(alvo, ensure_ascii=False)}]})
    contents.append({"role": "user", "parts": [{"text": "FICHA:\n" + ir["ficha"]}]})
    if feedback:
        contents.append({"role": "model", "parts": [{"text": anterior or "{}"}]})
        contents.append({"role": "user", "parts": [{"text": (
            "A verificação automática encontrou estes problemas na sua resposta:\n- " + "\n- ".join(feedback) +
            "\nCorrija TODOS e devolva o JSON completo novamente, seguindo as regras.")}]})
    return contents


def _extrai_json(txt: str) -> dict:
    txt = (txt or "").strip()
    txt = re.sub(r"^```(?:json)?|```$", "", txt).strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        i, j = txt.find("{"), txt.rfind("}")
        if i >= 0 and j > i:
            return json.loads(txt[i:j + 1])
        raise


class Gemini:
    def __init__(self, modelo: str, sistema: str, pensamento: str = "low"):
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            sys.exit("Instale o SDK:  pip install -r requirements.txt   (pacote google-genai)")
        chave = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not chave:
            sys.exit("Defina a variável de ambiente GEMINI_API_KEY (PowerShell: $env:GEMINI_API_KEY = \"...\").")
        self.types = types
        self.client = genai.Client(api_key=chave)
        self.modelo = modelo
        self.sistema = sistema
        self.usa_schema = True
        # nível de "raciocínio" do Gemini 3.x: menos raciocínio = resposta bem mais rápida.
        # A tarefa é redigir a partir de uma ficha já interpretada, então "low" basta.
        self.pensamento = None if pensamento == "padrao" else pensamento.upper()

    def gera(self, contents) -> str:
        espera = 10
        for tentativa in range(7):
            if PARAR.is_set():
                raise Interrompido()
            try:
                cfg = dict(system_instruction=self.sistema, temperature=0.2,
                           response_mime_type="application/json", max_output_tokens=32768)
                if self.usa_schema:
                    cfg["response_schema"] = SCHEMA
                if self.pensamento:
                    cfg["thinking_config"] = self.types.ThinkingConfig(thinking_level=self.pensamento)
                r = self.client.models.generate_content(
                    model=self.modelo, contents=contents, config=self.types.GenerateContentConfig(**cfg))
                if not r.text:
                    raise RuntimeError(f"resposta vazia (finish_reason={getattr(r.candidates[0], 'finish_reason', '?') if r.candidates else '?'})")
                return r.text
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if self.usa_schema and ("schema" in msg.lower()) and ("400" in msg or "invalid" in msg.lower()):
                    print("   ! modelo recusou o response_schema; seguindo só com JSON mode")
                    self.usa_schema = False
                    continue
                if self.pensamento and "thinking" in msg.lower() and "400" in msg:
                    print("   ! modelo recusou thinking_level; seguindo com o padrão do modelo")
                    self.pensamento = None
                    continue
                transitorio = any(c in msg for c in ("429", "RESOURCE_EXHAUSTED", "500", "502", "503", "504",
                                                     "UNAVAILABLE", "DEADLINE", "timed out", "resposta vazia"))
                if not transitorio or tentativa == 6:
                    raise
                m = re.search(r"retry in ([\d.]+)s|retryDelay['\": ]+(\d+)", msg)
                pausa = float(m.group(1) or m.group(2)) + 1 if m else espera
                cota = "429" in msg or "RESOURCE_EXHAUSTED" in msg
                if cota and (pausa > ESPERA_MAXIMA or "PerDay" in msg or "per day" in msg.lower()):
                    # ex.: 'retryDelay': '63497s' (~17 h) = cota DIÁRIA do modelo; esperar não resolve
                    raise CotaEsgotada(f"cota esgotada para {self.modelo} (a API pediu {pausa:.0f}s de espera)")
                pausa = min(pausa, ESPERA_MAXIMA)
                print(f"   ... erro transitório ({msg[:80]}); aguardando {pausa:.0f}s", flush=True)
                if PARAR.wait(pausa):  # espera interrompível: acorda na hora se PARAR for ligado
                    raise Interrompido()
                espera = min(espera * 2, 120)
        raise RuntimeError("falhou após várias tentativas")


class Teste:
    """Provedor falso para testar o pipeline sem chave: devolve a explicação determinística."""
    modelo = "teste-deterministico"

    def __init__(self, irs_por_arquivo):
        self.irs = irs_por_arquivo

    def gera(self, contents) -> str:
        ficha_txt = contents[-1]["parts"][0]["text"] if contents[-1]["role"] == "user" else ""
        arq = re.search(r"ARQUIVO: (.+)", ficha_txt)
        if not arq:  # rodada de correção: procura a ficha original
            arq = re.search(r"ARQUIVO: (.+)", contents[-3]["parts"][0]["text"])
        return json.dumps(explicacao_deterministica(self.irs[arq.group(1).strip()]), ensure_ascii=False)


def gera_uma(ir, provedor, fewshot, irs_por_arquivo, max_tentativas=2):
    contents = monta_contents(ir, fewshot, irs_por_arquivo)
    resposta, exp, problemas = None, None, ["sem resposta"]
    for t in range(1, max_tentativas + 1):
        try:
            resposta = provedor.gera(contents)
            exp = _extrai_json(resposta)
            problemas = verifica(ir, exp)
        except (CotaEsgotada, Interrompido):
            raise
        except Exception as e:  # noqa: BLE001
            problemas = [f"erro: {str(e)[:300]}"]
            exp = exp or None
        if not problemas:
            return exp, problemas, t
        if t < max_tentativas and exp is not None:
            contents = monta_contents(ir, fewshot, irs_por_arquivo, feedback=problemas, anterior=resposta)
    return exp, problemas, max_tentativas


# --------------------------------------------------------------------------------------
# 6: saídas
# --------------------------------------------------------------------------------------

def registro(ir, exp, origem, modelo, problemas, tentativas):
    return {
        "id": ir["arquivo"],
        "arquivo": ir["arquivo"],
        "duplicatas": ir["duplicatas"],
        "origem": origem,
        "modelo": modelo,
        "explicacao": exp,
        "texto_indexavel": texto_indexavel(exp) if exp else "",
        "verificacao": {"ok": not problemas, "problemas": problemas, "tentativas": tentativas},
        "achados_automaticos": ir["analise"]["achados"],
        "n_blocos": ir["analise"]["n_blocos_parametros"],
        "gobr": ir["fonte_gobr"],
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
    }


def le_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def escreve_jsonl(p: Path, regs: list[dict]):
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in regs) + "\n", encoding="utf-8")


def _md_celula(s: str) -> str:
    return str(s or "").replace("|", "/").replace("\n", " ").strip()


def escreve_markdown(p: Path, regs: list[dict]):
    L = ["# Explicações das regras GOBR", "",
         f"Gerado em {dt.datetime.now():%d/%m/%Y %H:%M}. Uma seção por regra única; cópias idênticas aparecem em 'Duplicatas'.", ""]
    for r in regs:
        e = r["explicacao"] or {}
        L += [f"## {e.get('titulo') or r['arquivo']}", "",
              f"`{r['arquivo']}` · origem: {r['origem']} ({r['modelo']}) · verificação: "
              f"{'OK' if r['verificacao']['ok'] else 'FALHOU'}"]
        if r["duplicatas"]:
            L.append(f"Duplicatas: {', '.join(r['duplicatas'])}")
        L += ["", e.get("resumo", ""), "", "| # | Segmento | Critério | Ação | Observação |", "|---|---|---|---|---|"]
        for s in e.get("segmentos", []):
            L.append(f"| {s.get('bloco')} | {_md_celula(s.get('nome'))} | {_md_celula(s.get('criterio'))} | "
                     f"{_md_celula(s.get('acao'))} | {_md_celula(s.get('observacao'))} |")
        if e.get("pontos_de_atencao"):
            L += ["", "**Pontos de atenção**", ""] + [f"- {x}" for x in e["pontos_de_atencao"]]
        if not r["verificacao"]["ok"]:
            L += ["", "**Problemas da verificação**", ""] + [f"- {x}" for x in r["verificacao"]["problemas"]]
        L.append("")
    p.write_text("\n".join(L), encoding="utf-8")


def _acao_chave(a) -> str | None:
    if a is None:
        return None
    n = normaliza(str(a))
    if "nao agend" in n:
        return "nao_agendar"
    m = re.search(r"(\d+)\s*dias?", n)
    return m.group(1) if m else None


def _tokens(s: str) -> set[str]:
    stop = {"clientes", "cliente", "com", "dias", "nos", "das", "dos", "que", "para", "regra", "mas", "estao", "sem"}
    return {t for t in re.findall(r"[a-z0-9]+", normaliza(s)) if len(t) > 2 and t not in stop}


def avalia_contra_imagens(regs_por_id: dict, imagens: dict) -> list[str]:
    """Compara cada item da imagem (regra de negócio original) com a explicação gerada a partir do .gobr."""
    L = []
    for arq, itens in imagens.items():
        if arq.startswith("_") or arq not in regs_por_id:
            continue
        segs = (regs_por_id[arq]["explicacao"] or {}).get("segmentos", [])
        usados = set()
        L += [f"### {arq}", "", "| Item da imagem | Ação na imagem | Segmento gerado (a partir do .gobr) | Resultado |", "|---|---|---|---|"]
        cobertos = total = 0
        for it in itens:
            ch = _acao_chave(it.get("acao"))
            cands = [s for s in segs if ch and _acao_chave(s.get("acao")) == ch and s.get("bloco") not in usados]
            tk = _tokens(it["nome"] + " " + it.get("criterio", ""))
            melhor = max(cands, key=lambda s: len(tk & _tokens(f"{s.get('nome')} {s.get('criterio')}")), default=None)
            if ch is None:
                res, alvo = "não existe no .gobr (requisito sem bloco correspondente)", "-"
            elif melhor and (len(tk & _tokens(f"{melhor.get('nome')} {melhor.get('criterio')}")) > 0):
                usados.add(melhor.get("bloco"))
                res, alvo = "coberto", f"[{melhor.get('bloco')}] {melhor.get('nome')} -> {melhor.get('acao')}"
                cobertos += 1
            else:
                res, alvo = "NÃO encontrado", "-"
            total += 1 if ch else 0
            L.append(f"| {_md_celula(it['nome'])} | {_md_celula(it.get('acao') or '-')} | {_md_celula(alvo)} | {res} |")
        extras = [s for s in segs if s.get("bloco") not in usados]
        L += ["", f"Cobertura dos itens da imagem que têm ação: **{cobertos}/{total}**.", ""]
        if extras:
            L.append("Blocos do .gobr que a imagem não mostra: " + "; ".join(f"[{s.get('bloco')}] {s.get('nome')} -> {s.get('acao')}" for s in extras))
            L.append("")
    return L


def escreve_relatorio(p: Path, arquivos, unicas, regs, imagens, modelo):
    blocos = sum(i["analise"]["n_blocos_parametros"] for i in unicas)
    filtros = [f for i in unicas for b in i["parametros"] + i["carteiras"] for f in b.get("filtros", [])]
    sem_trad = [f["texto"] for f in filtros if not f.get("significado")]
    aprox = sum(1 for f in filtros if "aprox" in (f.get("secao") or ""))
    achados = Counter(a["tipo"] for i in unicas for a in i["analise"]["achados"])
    ok = sum(r["verificacao"]["ok"] for r in regs)
    origem = Counter(r["origem"] for r in regs)
    tent = Counter(r["verificacao"]["tentativas"] for r in regs if r["verificacao"]["ok"])
    probs = Counter(re.sub(r"bloco \d+", "bloco N", x).split(":")[0] for r in regs for x in r["verificacao"]["problemas"])
    L = [
        "# Relatório — Entrega 1: Geração de explicações", "",
        f"Gerado em {dt.datetime.now():%d/%m/%Y %H:%M} · modelo: {modelo}", "",
        "## Corpus", "",
        f"- Arquivos .gobr lidos: **{len(arquivos)}** (exemplos + referências)",
        f"- Regras únicas (após remover cópias idênticas): **{len(unicas)}**",
        f"- Blocos `parametros` interpretados: **{blocos}**",
        f"- Linhas não classificadas pelo parser: **{sum(len(i['avisos']) for i in unicas)}**",
        f"- Filtros de cliente: **{len(filtros)}**; com tradução no glossário: **{len(filtros) - len(sem_trad)}** "
        f"({(len(filtros) - len(sem_trad)) / max(len(filtros), 1):.1%}); marcados como aproximação do manual: {aprox}",
        "",
        "## Verificação automática das explicações", "",
        f"- Explicações geradas: **{len(regs)}** (origem: {dict(origem)})",
        f"- Passaram na verificação: **{ok}/{len(regs)}** ({ok / max(len(regs), 1):.1%})",
        f"- Tentativas necessárias (entre as aprovadas): {dict(sorted(tent.items()))}",
    ]
    if probs:
        L += ["- Problemas mais comuns nas reprovadas:"] + [f"  - {k}: {v}" for k, v in probs.most_common(8)]
    L += ["", "## Pontos de atenção detectados automaticamente (regras únicas)", ""]
    nomes = {"sem_regra_final": "sem bloco final (clientes não cobertos mantêm a configuração anterior) — §7.6",
             "nome_diverge_do_codigo": "nome do bloco cita número que não está no código",
             "fonte_indefinida": "usa time/carteira não definido no arquivo",
             "bloco_inalcancavel": "bloco inalcançável (depois de um bloco sem filtro) — §7.6",
             "nao_agendar_com_frequencia": "'nao agendar' junto com frequência — §7.3.4",
             "sem_fonte": "bloco sem fonte de clientes"}
    L += [f"- {nomes.get(k, k)}: **{v}**" for k, v in achados.most_common()] or ["- nenhum"]
    L += ["", "## Avaliação contra as imagens (regra de negócio original)", "",
          "Para os 3 exemplos, cada item da imagem é procurado na explicação gerada **a partir do .gobr** "
          "(mesma ação e pelo menos uma palavra em comum no nome/critério).", ""]
    L += avalia_contra_imagens({r["id"]: r for r in regs}, imagens)
    p.write_text("\n".join(L), encoding="utf-8")


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Gera explicações em linguagem de negócio para as regras GOBR.")
    ap.add_argument("--dados", type=Path, default=AQUI.parent, help="pasta com exemplos/ e referencias/ (padrão: pasta acima)")
    ap.add_argument("--saida", type=Path, default=AQUI / "saida")
    ap.add_argument("--provedor", choices=["gemini", "nenhum", "teste"], default=None,
                    help="gemini (padrão se houver GEMINI_API_KEY), nenhum (só determinístico) ou teste")
    ap.add_argument("--modelo", default="gemini-3.8-flash")
    ap.add_argument("--limite", type=int, default=None, help="processa só as N primeiras regras pendentes")
    ap.add_argument("--apenas", default=None, help="processa só arquivos cujo caminho contém este texto")
    ap.add_argument("--intervalo", type=float, default=4.0, help="segundos entre o início das primeiras chamadas paralelas")
    ap.add_argument("--paralelo", type=int, default=4, help="quantas regras processar ao mesmo tempo")
    ap.add_argument("--pensamento", choices=["minimal", "low", "medium", "high", "padrao"], default="low",
                    help="nível de raciocínio do Gemini 3.x (menor = mais rápido)")
    ap.add_argument("--refazer-falhas", action="store_true", help="reprocessa regras que falharam na verificação")
    args = ap.parse_args()
    provedor_nome = args.provedor or ("gemini" if (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")) else "nenhum")

    args.saida.mkdir(parents=True, exist_ok=True)
    arquivos, unicas = carrega_regras(args.dados)
    irs_por_arquivo = {i["arquivo"]: i for i in unicas}
    print(f"[1-3] {len(arquivos)} arquivos lidos, {len(unicas)} regras únicas, "
          f"{sum(i['analise']['n_blocos_parametros'] for i in unicas)} blocos.")

    # representação estruturada + explicação determinística (sempre geradas)
    escreve_jsonl(args.saida / "regras_ir.jsonl", [{k: v for k, v in i.items()} for i in unicas])
    det = [registro(i, explicacao_deterministica(i), "deterministica", "-", verifica(i, explicacao_deterministica(i)), 0)
           for i in unicas]
    escreve_jsonl(args.saida / "explicacoes_deterministicas.jsonl", det)
    print(f"      saida/regras_ir.jsonl e saida/explicacoes_deterministicas.jsonl gravados.")

    fewshot = json.loads((AQUI / "prompts" / "exemplos_fewshot.json").read_text(encoding="utf-8"))
    imagens = json.loads((AQUI / "prompts" / "referencias_imagens.json").read_text(encoding="utf-8"))
    sistema = (AQUI / "prompts" / "sistema.md").read_text(encoding="utf-8")

    destino = args.saida / "explicacoes.jsonl"
    feitos = {r["id"]: r for r in le_jsonl(destino)}
    motivo_parada = ""
    if provedor_nome != "nenhum":
        provedor = Gemini(args.modelo, sistema, args.pensamento) if provedor_nome == "gemini" else Teste(irs_por_arquivo)
        pend = [i for i in unicas if i["arquivo"] not in feitos
                or (args.refazer_falhas and not feitos[i["arquivo"]]["verificacao"]["ok"])]
        if args.apenas:
            pend = [i for i in pend if args.apenas in i["arquivo"]]
        if args.limite:
            pend = pend[:args.limite]
        print(f"[4-5] {provedor_nome} ({provedor.modelo}): {len(pend)} regra(s) a processar; {len(feitos)} já feitas; "
              f"{args.paralelo} em paralelo.")
        ordem = {i["arquivo"]: k for k, i in enumerate(unicas)}

        def tarefa(ir):
            if PARAR.is_set():
                raise Interrompido()
            t0 = time.time()
            exp, problemas, tent = gera_uma(ir, provedor, fewshot, irs_por_arquivo)
            return ir, exp, problemas, tent, time.time() - t0

        from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
        pool = ThreadPoolExecutor(max_workers=max(1, args.paralelo))
        nonlocal_n = [0]  # contador de regras concluídas nesta execução
        try:
            pendentes = set()
            for k, ir in enumerate(pend):
                pendentes.add(pool.submit(tarefa, ir))
                if provedor_nome == "gemini" and k < args.paralelo:
                    time.sleep(args.intervalo)  # escalona o início para não estourar o limite por minuto
            def processa(fut):
                nonlocal_n[0] += 1
                ir, exp, problemas, tent, dur = fut.result()
                if exp is None:  # falha total: guarda a determinística, marcada como tal
                    exp, origem = explicacao_deterministica(ir), "deterministica (LLM falhou)"
                else:
                    origem = "llm" if provedor_nome == "gemini" else "teste"
                feitos[ir["arquivo"]] = registro(ir, exp, origem, provedor.modelo, problemas, tent)
                escreve_jsonl(destino, sorted(feitos.values(), key=lambda r: ordem.get(r["id"], 1e9)))  # salva a cada regra
                status = "OK" if not problemas else f"FALHOU ({len(problemas)} problema(s): {problemas[0][:90]})"
                print(f"   [{nonlocal_n[0]}/{len(pend)}] {ir['arquivo']}: {status}  tentativas={tent}  {dur:.1f}s", flush=True)

            while pendentes and not PARAR.is_set():
                # espera com timeout de 1 s (e não indefinidamente) para o Ctrl+C funcionar no Windows
                prontos, pendentes = wait(pendentes, timeout=1, return_when=FIRST_COMPLETED)
                for fut in prontos:
                    try:
                        processa(fut)
                    except CotaEsgotada as e:
                        nonlocal_n[0] -= 1
                        motivo_parada = str(e)
                        PARAR.set()
                    except Interrompido:
                        nonlocal_n[0] -= 1
            # aproveita o que terminou enquanto parava
            for fut in [f for f in pendentes if f.done() and not f.cancelled()]:
                try:
                    processa(fut)
                except (CotaEsgotada, Interrompido):
                    nonlocal_n[0] -= 1
        except KeyboardInterrupt:
            motivo_parada = "interrompido pelo usuário (Ctrl+C)"
            PARAR.set()
        finally:
            pool.shutdown(wait=not PARAR.is_set(), cancel_futures=True)
        if PARAR.is_set():
            print(f"\n[!] Parada: {motivo_parada}. {nonlocal_n[0]} regra(s) concluída(s) nesta execução; tudo já está salvo.")
            print("    Rode o mesmo comando de novo para continuar de onde parou"
                  + (" (outro --modelo, outra chave ou amanhã)." if "cota" in motivo_parada else "."), flush=True)

    # consolida: LLM quando houver, senão a determinística
    ordem = {i["arquivo"]: k for k, i in enumerate(unicas)}
    finais = {r["id"]: r for r in det}
    finais.update(feitos)
    regs = sorted(finais.values(), key=lambda r: ordem.get(r["id"], 1e9))
    escreve_markdown(args.saida / "explicacoes.md", regs)
    modelo = ", ".join(sorted({r["modelo"] for r in regs}))
    escreve_relatorio(args.saida / "relatorio.md", arquivos, unicas, regs, imagens, modelo)
    print(f"[6] saida/explicacoes.md e saida/relatorio.md gravados "
          f"({sum(r['origem'] == 'llm' for r in regs)} por LLM, {sum(r['origem'] != 'llm' for r in regs)} sem LLM).", flush=True)
    if PARAR.is_set():
        os._exit(1)  # não espera chamadas HTTP penduradas nas threads


if __name__ == "__main__":
    main()
