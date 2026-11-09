# -*- coding: utf-8 -*-
"""Entrega 4 - partes compartilhadas do fluxo básico de busca (RAG).

Reaproveita as Entregas 2 e 3 SÓ por import; nenhum arquivo delas é alterado:
  Entrega 2 (comum.py, avaliar.py): Reranker, buscar_regras, carregar_indice, criar_embedding, criar_reranker,
    criar_contador_tokens, posicao_da_primeira_relevante, metricas e o conjunto de consultas.
  Entrega 3 (comum_manual.py): buscar, acerta, carregar_indice, carregar_consultas.
Aqui fica só o que é novo: as constantes da regra de escolha (regra_escolha_fluxo.md), a grade de configurações,
a medição de latência, a regra de escolha em código, a montagem do contexto, o prompt do --responder e a
chamada ao Gemini.

Nenhuma função daqui carrega modelo ao ser importada: os imports pesados ficam dentro das funções.
"""
from __future__ import annotations

import gc
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent                    # trabalho/
ENTREGA2 = RAIZ / "entrega2"
ENTREGA3 = RAIZ / "entrega3"
for _pasta in (ENTREGA3, ENTREGA2):   # no FIM do caminho de busca: a pasta da Entrega 4 continua na frente
    if str(_pasta) not in sys.path:
        sys.path.append(str(_pasta))

import avaliar as av2                 # noqa: E402  (Entrega 2, sem alteração)
import comum as c2                    # noqa: E402  (Entrega 2, sem alteração)
import comum_manual as c3             # noqa: E402  (Entrega 3, sem alteração)

# ------------------------------------------------ constantes da regra (seção 3 de regra_escolha_fluxo.md) ----
# Os testes leem o bloco da seção 3 do arquivo da regra e comparam com estes valores.
K = 3
TETO_S = 20.0
REPETICOES = 2
FASE1 = ("vetor", "hibrido")
N_CANDIDATOS = (5, 10, 20, 50)
MAX_LENGTH_REGRAS = (512, 2048)
MAX_LENGTH_MANUAL = (2048,)
CONSULTA_AQUECIMENTO = "teste de aquecimento"
N_AQUECIMENTO = 2                     # seção 5: aquecimento com hibrido=True e N = 2

VARIANTE_REGRAS = "com_pontos"        # seção 2, item 4
ESTRATEGIA_MANUAL = "C"               # seção 2, item 4
MODELO_GEMINI_PADRAO = "gemini-3.8-flash"   # o mesmo default da Entrega 1 (gerar_explicacoes.py)

# Tamanho dos conjuntos (seção 5 da regra). Se o arquivo de consultas mudar, o dev e o teste não rodam.
N_CONSULTAS = {("regras", "dev"): 14, ("manual", "dev"): 15, ("regras", "teste"): 20, ("manual", "teste"): 20}

ARQ_REGRA = AQUI / "regra_escolha_fluxo.md"
# sha256 do arquivo da regra com fins de linha LF, gravado em 07/11/2026. Se o arquivo mudar, o dev não roda.
HASH_REGRA = "fa77637b72388657f92807e0d33007f8a42b1783fd1a114cef3c898623128b68"
PASTA_CHECKPOINTS = AQUI / "dev_checkpoints"
ARQ_DEV_JSON = AQUI / "resultados_fluxo_dev.json"
ARQ_DEV_MD = AQUI / "resultados_fluxo_dev.md"
ARQ_CONFIG = AQUI / "config_escolhida.json"
ARQ_TESTE_JSON = AQUI / "resultados_fluxo_teste.json"
ARQ_TESTE_MD = AQUI / "resultados_fluxo_teste.md"


# ---------------------------------------------------------------- utilidades ----
def imprimir(msg: str = "") -> None:
    print(msg, flush=True)


def configurar_saida() -> None:
    """Console do Windows e redirecionamento para arquivo: força UTF-8 para o GOBR e os acentos não quebrarem."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def agora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_arquivo(caminho: Path, lf: bool = False) -> str:
    dados = Path(caminho).read_bytes()
    if lf:
        dados = dados.replace(b"\r\n", b"\n")
    return hashlib.sha256(dados).hexdigest()


def gravar_exclusivo(caminho: Path, texto: str) -> str:
    """Abertura exclusiva ("xb"): nunca sobrescreve. Devolve o sha256 do que foi gravado."""
    dados = texto.encode("utf-8")
    with open(caminho, "xb") as f:
        f.write(dados)
        f.flush()
        os.fsync(f.fileno())
    return hashlib.sha256(dados).hexdigest()


def conferir_regra(caminho: Path = ARQ_REGRA, esperado: str = HASH_REGRA) -> tuple[bool, str]:
    obtido = sha256_arquivo(caminho, lf=True)
    return obtido == esperado, obtido


def ler_constantes_regra(caminho: Path = ARQ_REGRA) -> dict[str, list[str]]:
    """Bloco da seção 3 do arquivo da regra: nome -> lista de valores (texto)."""
    texto = Path(caminho).read_text(encoding="utf-8")
    m = re.search(r"## 3\. Constantes.*?```\n(.*?)```", texto, re.S)
    if not m:
        raise ValueError("bloco de constantes (seção 3) não encontrado na regra")
    saida = {}
    for linha in m.group(1).splitlines():
        if "=" in linha:
            nome, _, valor = linha.partition("=")
            saida[nome.strip()] = [v.strip() for v in valor.split(",")]
    return saida


def insumos_da_regra(caminho: Path = ARQ_REGRA) -> list[tuple[str, str]]:
    """Tabela da seção 11 da regra: (caminho relativo a trabalho/, sha256)."""
    texto = Path(caminho).read_text(encoding="utf-8")
    linhas = re.findall(r"^\|\s*`([^`]+)`[^|]*\|\s*`([0-9a-f]{64})`\s*\|", texto, re.M)
    return [(c, h) for c, h in linhas]


def conferir_insumos(raiz: Path = RAIZ, caminho_regra: Path = ARQ_REGRA) -> list[dict]:
    saida = []
    for rel, esperado in insumos_da_regra(caminho_regra):
        arq = Path(raiz) / rel
        obtido = sha256_arquivo(arq) if arq.exists() else None
        saida.append({"arquivo": rel, "esperado": esperado, "obtido": obtido, "ok": obtido == esperado})
    return saida


def estado_git_da_regra(caminho: Path = ARQ_REGRA) -> dict:
    """Só leitura (git --no-optional-locks). A data do commit da regra é a prova do pré-registro."""
    base = ["git", "--no-optional-locks", "-C", str(Path(caminho).parent)]
    try:
        log = subprocess.run(base + ["log", "-1", "--format=%H|%cI", "--", Path(caminho).name],
                             capture_output=True, text=True, timeout=30)
        st = subprocess.run(base + ["status", "--porcelain", "--", Path(caminho).name],
                            capture_output=True, text=True, timeout=30)
    except Exception as e:  # git ausente, sem permissão, tempo esgotado
        return {"disponivel": False, "commitada": False, "commit": None, "data": None, "erro": str(e)}
    if log.returncode != 0 or st.returncode != 0:
        return {"disponivel": False, "commitada": False, "commit": None, "data": None,
                "erro": (log.stderr or st.stderr).strip()}
    achado = log.stdout.strip()
    commit, _, data = achado.partition("|")
    limpa = st.stdout.strip() == ""
    return {"disponivel": True, "commitada": bool(commit) and limpa, "commit": commit or None,
            "data": data or None, "erro": None if (commit and limpa) else
            ("a regra nunca foi commitada" if not commit else "a regra tem mudanças não commitadas")}


# ---------------------------------------------------------------- configurações ----
@dataclass(frozen=True)
class Config:
    """Uma configuração de busca de UM índice (regra, seção 1): fase 1, N candidatos e max_length do reranker."""

    indice: str          # "regras" ou "manual"
    fase1: str           # "vetor" ou "hibrido"
    n: int = 0           # candidatos que o reranker relê; 0 = sem reranker
    max_length: int = 0  # max_length do reranker; 0 = sem reranker

    def __post_init__(self):
        if self.indice not in ("regras", "manual"):
            raise ValueError(f"índice desconhecido: {self.indice}")
        if self.fase1 not in FASE1:
            raise ValueError(f"fase 1 desconhecida: {self.fase1}")
        if (self.n == 0) != (self.max_length == 0):
            raise ValueError("n e max_length: os dois 0 (sem reranker) ou os dois maiores que 0")

    @property
    def hibrido(self) -> bool:
        return self.fase1 == "hibrido"

    @property
    def nome(self) -> str:
        if self.n == 0:
            return f"{self.indice}_{self.fase1}_sem-rerank"
        return f"{self.indice}_{self.fase1}_N{self.n}_L{self.max_length}"

    @property
    def simplicidade(self) -> tuple:
        """Desempate 4 da regra: sem reranker antes de com reranker; vetor antes de híbrido; menor N; max_length
        512 antes de 2048."""
        return (self.n > 0, self.hibrido, self.n, self.max_length)

    @property
    def origem_da_nota(self) -> str:
        return "reranker" if self.n else ("RRF" if self.hibrido else "similaridade")

    def descricao(self) -> str:
        fase = "híbrido" if self.hibrido else "vetor"
        if self.n == 0:
            return f"{fase}, sem reranker"
        return f"{fase} + reranker (N={self.n}, max_length={self.max_length})"

    def to_dict(self) -> dict:
        return {"indice": self.indice, "fase1": self.fase1, "n": self.n, "max_length": self.max_length,
                "nome": self.nome}

    @staticmethod
    def from_dict(d: dict) -> "Config":
        cfg = Config(d["indice"], d["fase1"], int(d["n"]), int(d["max_length"]))
        if "nome" in d and d["nome"] != cfg.nome:
            raise ValueError(f"nome incoerente: {d['nome']} != {cfg.nome}")
        return cfg


def grade(indice: str) -> list[Config]:
    """Todas as configurações do índice, na ordem da seção 5: sem reranker primeiro, depois N crescente e
    max_length 512 antes de 2048 (nas regras: 18; no manual: 10)."""
    tamanhos = MAX_LENGTH_REGRAS if indice == "regras" else MAX_LENGTH_MANUAL
    cfgs = [Config(indice, f) for f in FASE1]
    for n in sorted(N_CANDIDATOS):
        for ml in sorted(tamanhos):
            for f in FASE1:
                cfgs.append(Config(indice, f, n, ml))
    return cfgs


def todas_as_configs() -> list[Config]:
    return grade("regras") + grade("manual")


def plano_execucao() -> list[tuple[int, list[Config]]]:
    """Ordem de EXECUÇÃO: (max_length, configurações) por fase. 0 = sem reranker; depois cada max_length em ordem
    crescente. Agrupar por max_length mantém um reranker só na memória por vez. A seção 5 da regra diz que a ordem
    só afeta o tempo de execução; este agrupamento é um detalhe de execução, declarado no README."""
    todas = todas_as_configs()
    fases = [(0, [c for c in todas if c.n == 0])]
    for ml in sorted({c.max_length for c in todas if c.max_length}):
        fases.append((ml, [c for c in todas if c.max_length == ml]))
    return fases


def carregar_config(caminho: Path = ARQ_CONFIG) -> dict[str, "Config"]:
    """A dupla escolhida no desenvolvimento (config_escolhida.json). Sem dupla (nenhuma coube no teto), falha
    explícito."""
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if not dados.get("escolha") or not dados.get("configs"):
        raise ValueError(f"{Path(caminho).name} não tem dupla escolhida: nenhuma dupla coube no teto de "
                         f"{TETO_S:g} s no desenvolvimento")
    return {"regras": Config.from_dict(dados["configs"]["regras"]),
            "manual": Config.from_dict(dados["configs"]["manual"])}


# ---------------------------------------------------------------- recursos (modelos e índices) ----
def criar_reranker_cfg(max_length: int):
    """Seção 5 da regra: o de 2048 é o criar_reranker() da Entrega 2; outro valor é um CrossEncoder do mesmo modelo
    com esse max_length, na mesma classe Reranker da Entrega 2. Devolve (Reranker, dispositivo)."""
    if max_length == getattr(c2, "RERANKER_MAX_LENGTH", 2048):
        return c2.criar_reranker()
    import torch
    from sentence_transformers import CrossEncoder

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    modelo = CrossEncoder(c2.MODELO_RERANKER, max_length=max_length, device=dispositivo)
    return c2.Reranker(lambda pares: modelo.predict(pares, batch_size=4, show_progress_bar=False)), dispositivo


class Recursos:
    """Carrega sob demanda o embedding, os dois índices e os rerankers, e mede quanto cada carga leva (a regra
    manda relatar o carregamento à parte). As fábricas são injetáveis: os testes sem modelo passam as falsas."""

    def __init__(self, *, fabrica_embedding=None, fabrica_reranker=None, carregar_regras=None,
                 carregar_manual=None, fabrica_contador=None, relogio=time.perf_counter):
        self._fab_emb = fabrica_embedding or c2.criar_embedding
        self._fab_rr = fabrica_reranker or criar_reranker_cfg
        self._car_regras = carregar_regras or (lambda emb: c2.carregar_indice(VARIANTE_REGRAS, emb))
        self._car_manual = carregar_manual or (lambda emb: c3.carregar_indice(ESTRATEGIA_MANUAL, emb))
        self._fab_contador = fabrica_contador or c2.criar_contador_tokens
        self.relogio = relogio
        self._emb = None
        self._indices: dict[str, object] = {}
        self._rerankers: dict[int, object] = {}
        self._contador = None
        self.tempos_carga_s: dict[str, float] = {}
        self.dispositivos: dict[str, str] = {}
        self.erros: dict[str, str] = {}

    def _medir(self, chave: str, fabrica):
        t0 = self.relogio()
        resultado = fabrica()
        self.tempos_carga_s[chave] = round(self.relogio() - t0, 2)
        return resultado

    def embedding(self):
        if self._emb is None:
            self._emb, disp = self._medir("embedding", self._fab_emb)
            self.dispositivos["embedding"] = disp
        return self._emb

    def indice(self, nome: str):
        if nome not in self._indices:
            emb = self.embedding()
            carregar = self._car_regras if nome == "regras" else self._car_manual
            self._indices[nome] = self._medir(f"indice_{nome}", lambda: carregar(emb))
        return self._indices[nome]

    def reranker(self, max_length: int):
        if max_length not in self._rerankers:
            rr, disp = self._medir(f"reranker_{max_length}", lambda: self._fab_rr(max_length))
            self._rerankers[max_length] = rr
            self.dispositivos[f"reranker_{max_length}"] = disp
        return self._rerankers[max_length]

    def reranker_de(self, cfg: Config):
        return self.reranker(cfg.max_length) if cfg.n else None

    def liberar_rerankers(self, exceto=()) -> None:
        for ml in list(self._rerankers):
            if ml not in exceto:
                del self._rerankers[ml]
                self.dispositivos.pop(f"reranker_{ml}", None)
        gc.collect()

    def contador_tokens(self):
        """Contador de tokens do bge-m3 (Entrega 2). Se não carregar, devolve None e guarda o motivo."""
        if self._contador is None:
            try:
                self._contador = self._medir("tokenizer", self._fab_contador)
            except Exception as e:
                self._contador = False
                self.erros["tokenizer"] = f"{type(e).__name__}: {e}"
        return self._contador or None


# ---------------------------------------------------------------- busca e acerto ----
def buscar_cfg(index, consulta: str, cfg: Config, reranker, k: int | None = None):
    """Roda a busca da configuração com a função da Entrega 2 (regras) ou da Entrega 3 (manual).
    k=None devolve o ranking completo (a avaliação precisa dele); no fluxo, k = K."""
    rr = reranker if cfg.n else None
    n = cfg.n or 50                   # sem reranker o n não é usado
    if cfg.indice == "regras":
        return c2.buscar_regras(index, consulta, k=k, reranker=rr, n_candidatos=n, hibrido=cfg.hibrido)
    return c3.buscar(index, consulta, k=k, reranker=rr, n_candidatos=n, hibrido=cfg.hibrido)


def aquecer(recursos: Recursos, indice: str, max_length: int = 0) -> float:
    """Seção 5: uma chamada descartada por modelo carregado (cada max_length) e por índice, com
    CONSULTA_AQUECIMENTO, hibrido=True e N = 2: monta o BM25 e aquece o reranker. Devolve os segundos."""
    cfg = Config(indice, "hibrido", N_AQUECIMENTO if max_length else 0, max_length)
    t0 = recursos.relogio()
    buscar_cfg(recursos.indice(indice), CONSULTA_AQUECIMENTO, cfg, recursos.reranker_de(cfg), k=None)
    seg = recursos.relogio() - t0
    recursos.tempos_carga_s[f"aquecimento_{indice}_{max_length}"] = round(seg, 2)
    return seg


def posicao_regras(ranking, consulta: dict):
    """Regras: regra de `relevantes` (id exato) no ranking agrupado por regra (Entrega 2)."""
    ids = [n.node.metadata["regra_id"] for n in ranking]
    return av2.posicao_da_primeira_relevante(ids, consulta["relevantes"])


def posicao_manual(ranking, consulta: dict):
    """Manual: regra oficial da Entrega 3 (a folha principal do chunk está no gabarito), ranking de chunks sem
    agrupar. Posição do primeiro acerto (1 = primeiro) ou None."""
    for i, n in enumerate(ranking, 1):
        if c3.acerta(n.node.metadata, consulta["gabarito"]):
            return i
    return None


def carregar_consultas(indice: str, conjunto: str) -> list[dict]:
    """Os conjuntos das Entregas 2 e 3, pelas funções delas. conjunto: "dev" ou "teste"."""
    if indice == "regras":
        return av2.carregar_consultas(ENTREGA2 / av2.CONJUNTOS[conjunto])
    return c3.carregar_consultas(conjunto)


def metricas_exatas(posicoes: list) -> dict[str, Fraction]:
    """hit@3 e MRR em fração exata (a regra compara sem arredondar). Mesma definição de av2.metricas."""
    n = len(posicoes)
    if n == 0:
        return {"hit@3": Fraction(0), "MRR": Fraction(0)}
    return {"hit@3": Fraction(sum(1 for p in posicoes if p is not None and p <= 3), n),
            "MRR": sum((Fraction(1, p) for p in posicoes if p), Fraction(0)) / n}


# ---------------------------------------------------------------- latência e medição ----
def cronometrar(chamar, repeticoes: int = REPETICOES, teto: float = TETO_S, relogio=time.perf_counter):
    """Seção 5. A 1ª repetição dá o ranking (de onde vem o acerto) e o 1º tempo. Se esse tempo passar de `teto`,
    para ali. Senão repete até `repeticoes` vezes. Devolve (ranking, tempos, estourou)."""
    t0 = relogio()
    ranking = chamar()
    tempos = [relogio() - t0]
    if tempos[0] > teto:
        return ranking, tempos, True
    for _ in range(max(0, repeticoes - 1)):
        t0 = relogio()
        chamar()
        tempos.append(relogio() - t0)
    return ranking, tempos, False


def medir_configuracao(cfg: Config, consultas: list[dict], chamar, posicao, *, repeticoes: int = REPETICOES,
                       teto: float = TETO_S, relogio=time.perf_counter, avisar=None) -> dict:
    """Mede UMA configuração num conjunto de consultas (seções 5 e 6).
    chamar(texto) -> ranking completo; posicao(ranking, consulta) -> int | None.
    Cada consulta vale a MENOR de `repeticoes` medidas; a latência da configuração é a MAIOR entre as consultas.
    Se a 1ª medição de uma consulta passar do teto, a configuração é excluída por latência e para ali."""
    por_consulta, posicoes = [], []
    for i, c in enumerate(consultas, 1):
        ranking, tempos, estourou = cronometrar(lambda: chamar(c["consulta"]), repeticoes, teto, relogio)
        if estourou:
            if avisar:
                avisar(f"    {c['id']}: {tempos[0]:.1f} s > {teto:g} s -> excluída por latência")
            return {"config": cfg.to_dict(), "excluida": True,
                    "excluida_por": {"consulta": c["id"], "tempo_s": round(tempos[0], 3), "teto_s": teto},
                    "n_consultas": len(consultas), "consultas_medidas": len(por_consulta)}
        pos = posicao(ranking, c)
        posicoes.append(pos)
        por_consulta.append({"id": c["id"], "posicao": pos, "tempos_s": [round(t, 3) for t in tempos],
                             "min_s": round(min(tempos), 3)})
        if avisar:
            avisar(f"    {i}/{len(consultas)} {c['id']}: posição {pos if pos else 'fora'}, "
                   f"{min(tempos):.2f} s")
    exatas = metricas_exatas(posicoes)
    return {"config": cfg.to_dict(), "excluida": False, "excluida_por": None, "n_consultas": len(consultas),
            "metricas": av2.metricas(posicoes), "hit3_frac": str(exatas["hit@3"]), "mrr_frac": str(exatas["MRR"]),
            "latencia_s": max(p["min_s"] for p in por_consulta) if por_consulta else 0.0,
            "por_consulta": por_consulta}


# ---------------------------------------------------------------- checkpoints ----
def caminho_checkpoint(pasta: Path, cfg: Config) -> Path:
    return Path(pasta) / f"{cfg.nome}.json"


def salvar_checkpoint(pasta: Path, cfg: Config, dados: dict) -> str:
    """Abertura exclusiva: uma configuração concluída nunca é regravada."""
    Path(pasta).mkdir(parents=True, exist_ok=True)
    return gravar_exclusivo(caminho_checkpoint(pasta, cfg), json.dumps(dados, ensure_ascii=False, indent=1))


def carregar_checkpoint(pasta: Path, cfg: Config):
    """None se a configuração ainda não foi medida. ValueError se o arquivo existe mas não serve (apague-o)."""
    arq = caminho_checkpoint(pasta, cfg)
    if not arq.exists():
        return None
    try:
        dados = json.loads(arq.read_text(encoding="utf-8"))
        assert Config.from_dict(dados["config"]) == cfg
        assert isinstance(dados["excluida"], bool)
        if not dados["excluida"]:
            for chave in ("metricas", "hit3_frac", "mrr_frac", "latencia_s", "por_consulta"):
                assert chave in dados
    except Exception as e:
        raise ValueError(f"checkpoint inválido ({arq.name}): {type(e).__name__}: {e}. "
                         f"Apague esse arquivo e rode de novo para medir só essa configuração.") from e
    return dados


# ---------------------------------------------------------------- regra de escolha (seção 6) ----
CRITERIOS = ("soma dos hit@3", "soma dos MRR", "menor latência da dupla",
             "configuração mais simples (regras)", "configuração mais simples (manual)")


def escolher(configs: dict[str, dict], teto: float = TETO_S, top: int = 5) -> dict:
    """A regra da seção 6 em código. `configs`: nome -> resultado da medição (checkpoint).
    Entre as duplas (R, M) sem exclusão por latência e com lat(R) + lat(M) <= teto:
      1. maior hit@3(R) + hit@3(M);  2. maior MRR(R) + MRR(M);  3. menor lat(R) + lat(M);
      4. mais simples (a de regras primeiro, depois a do manual).
    hit@3 e MRR são comparados como frações exatas."""
    por_indice = {"regras": [], "manual": []}
    excluidas = []
    for d in configs.values():
        if d["excluida"]:
            excluidas.append(d["config"]["nome"])
        else:
            por_indice[d["config"]["indice"]].append(d)
    total = sum(1 for d in configs.values() if d["config"]["indice"] == "regras") * \
        sum(1 for d in configs.values() if d["config"]["indice"] == "manual")
    duplas = []
    for r in por_indice["regras"]:
        for m in por_indice["manual"]:
            lat = r["latencia_s"] + m["latencia_s"]
            if lat > teto:
                continue
            hit3 = Fraction(r["hit3_frac"]) + Fraction(m["hit3_frac"])
            mrr = Fraction(r["mrr_frac"]) + Fraction(m["mrr_frac"])
            cr, cm = Config.from_dict(r["config"]), Config.from_dict(m["config"])
            chave = (-hit3, -mrr, lat, cr.simplicidade, cm.simplicidade)
            duplas.append((chave, {"regras": cr.nome, "manual": cm.nome, "soma_hit3": str(hit3),
                                   "soma_hit3_float": float(hit3), "soma_mrr": str(mrr),
                                   "soma_mrr_float": float(mrr), "latencia_dupla_s": round(lat, 3),
                                   "lat_regras_s": r["latencia_s"], "lat_manual_s": m["latencia_s"]}))
    duplas.sort(key=lambda x: x[0])
    melhores = [d for _, d in duplas[:top]]
    decidido_por = None
    if len(duplas) >= 2:
        a, b = duplas[0][0], duplas[1][0]
        decidido_por = next((CRITERIOS[i] for i in range(5) if a[i] != b[i]), "duplas idênticas")
    elif len(duplas) == 1:
        decidido_por = "única dupla viável"
    return {"escolha": melhores[0] if melhores else None, "melhores": melhores, "decidido_por": decidido_por,
            "n_duplas_total": total, "n_duplas_viaveis": len(duplas), "excluidas_por_latencia": sorted(excluidas),
            "teto_s": teto}


# ---------------------------------------------------------------- contexto (saída do fluxo) ----
def descrever_regra(n, posicao: int) -> dict:
    m = n.node.metadata
    return {"posicao": posicao, "regra_id": m["regra_id"], "titulo": m.get("titulo", ""),
            "nota": float(n.score), "texto": n.node.text, "gobr": m["gobr"]}


def descrever_trecho(n, posicao: int) -> dict:
    m = n.node.metadata
    return {"posicao": posicao, "folha": m["folha"], "caminho": m.get("caminho", ""),
            "pagina_ini": m.get("pagina_impressa_ini"), "pagina_fim": m.get("pagina_impressa_fim"),
            "nota": float(n.score), "texto": n.node.text}


def rotulo_paginas(ini, fim) -> str:
    if ini is None:
        return ""
    return f"p. {ini}" if fim in (None, ini) else f"p. {ini}-{fim}"


def fonte_do_manual(t: dict) -> str:
    folha = str(t["folha"])
    base = f"capítulo {folha[:-2]} (abertura)" if folha.endswith(".0") else f"seção {folha}"
    pag = rotulo_paginas(t["pagina_ini"], t["pagina_fim"])
    return f"{base}, {pag}" if pag else base


def _cerca(texto: str) -> str:
    maior = max((len(m) for m in re.findall(r"`+", texto)), default=0)
    return "`" * max(3, maior + 1)


def montar_contexto(regras: list[dict], trechos: list[dict]) -> str:
    """Texto que o fluxo devolve (e que o --responder manda ao Gemini): as regras com o GOBR COMPLETO e os trechos
    do manual com seção e páginas. Nada é cortado (decisão herdada das Entregas 1 e 2). No texto voltado ao usuário
    a linguagem é GOBR; o trecho do manual conserva a grafia do próprio manual ("gorules", "GoBR")."""
    partes = ["## Regras de exemplo"]
    if not regras:
        partes.append("(nenhuma regra encontrada)")
    for r in regras:
        cerca = _cerca(r["gobr"])
        titulo = f"{r['titulo']} ({r['regra_id']})" if r["titulo"] else r["regra_id"]
        partes.append(f"### Regra {r['posicao']}: {titulo}\n{r['texto'].strip()}\n\n"
                      f"GOBR:\n{cerca}\n{r['gobr'].rstrip()}\n{cerca}")
    partes.append("## Manual do GOBR")
    if not trechos:
        partes.append("(nenhum trecho encontrado)")
    for t in trechos:
        corpo = t["texto"].strip()
        cabeca = f"### Trecho {t['posicao']}: {fonte_do_manual(t)}"
        if t["caminho"] and not corpo.startswith(t["caminho"]):
            cabeca += f" ({t['caminho']})"
        partes.append(f"{cabeca}\n{corpo}")
    return "\n\n".join(partes) + "\n"


# ---------------------------------------------------------------- --responder (Gemini) ----
# Adaptado da Célula 8 da atividade de RAG (rag_local_llamaindex_atividade.py, l. 190-201): mesma estrutura de
# system prompt e user prompt, mesmas regras de resposta. Só o domínio foi trocado (GOBR, regras e manual).
# A redação para esse domínio é escolha de engenharia: não encontrei no material.
SYSTEM_PROMPT = """Você é um assistente que ajuda a escrever regras do Govendas na linguagem GOBR.
Regras:
- Responda em português, de forma objetiva.
- Use apenas informações presentes no contexto (regras de exemplo e trechos do manual).
- Se a resposta não estiver no contexto, diga "Não encontrei nos documentos".
- Não repita informações."""

USER_PROMPT = """Contexto recuperado:
---------------------
{context_str}
---------------------
Pergunta: {query_str}"""


def montar_prompt(pergunta: str, contexto: str) -> tuple[str, str]:
    return SYSTEM_PROMPT, USER_PROMPT.format(context_str=contexto, query_str=pergunta)


def chave_gemini(env=None):
    env = os.environ if env is None else env
    return env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY")


def criar_cliente_gemini(env=None):
    """Como na Entrega 1: google-genai e chave em GEMINI_API_KEY ou GOOGLE_API_KEY. Sem chave, falha explícito."""
    chave = chave_gemini(env)
    if not chave:
        raise RuntimeError("Defina GEMINI_API_KEY (ou GOOGLE_API_KEY) para usar --responder.")
    try:
        from google import genai
    except ImportError as e:
        raise RuntimeError("Instale o SDK: pip install -r requirements.txt (pacote google-genai)") from e
    return genai.Client(api_key=chave)


def responder(pergunta: str, contexto: str, *, modelo: str = MODELO_GEMINI_PADRAO, cliente=None,
              relogio=time.perf_counter) -> dict:
    """UMA chamada ao Gemini com o contexto. Devolve o texto e os tokens que a API contou."""
    sistema, usuario = montar_prompt(pergunta, contexto)
    cliente = cliente or criar_cliente_gemini()
    t0 = relogio()
    resp = cliente.models.generate_content(model=modelo, contents=usuario,
                                           config={"system_instruction": sistema})
    seg = relogio() - t0
    uso = getattr(resp, "usage_metadata", None)

    def contagem(campo):
        v = getattr(uso, campo, None) if uso is not None else None
        return int(v) if v is not None else None

    return {"modelo": modelo, "texto": (getattr(resp, "text", None) or "").strip(),
            "tokens_entrada": contagem("prompt_token_count"), "tokens_saida": contagem("candidates_token_count"),
            "tokens_raciocinio": contagem("thoughts_token_count"), "tokens_total": contagem("total_token_count"),
            "segundos": round(seg, 2)}
