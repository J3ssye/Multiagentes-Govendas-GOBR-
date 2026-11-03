# -*- coding: utf-8 -*-
"""
Entrega 3, passo 5.1 - extrai o manual do GoBR (govendas-rules.pdf) em blocos limpos, na ordem de leitura.

Cada bloco e um titulo, um paragrafo, um bloco de codigo ou uma tabela, com capitulo, secao, subsecao,
"folha" (a unidade mais especifica da hierarquia: subsecao x.y.z, senao secao x.y, senao abertura n.0
do capitulo) e paginas (do PDF e impressa).

O que sai do texto (diagnostico do Passo 2, ver README):
  - paginas 1 a 4 (capa, pagina em branco, sumario, pagina em branco);
  - cabecalho corrente (faixa superior) e rodape de copyright (faixa inferior);
  - linhas pontilhadas de abertura de capitulo.
Tabelas sao lidas por celula (find_tables), porque a leitura por linha mistura as colunas; uma tabela
sem cabecalho no topo da pagina e continuacao da tabela anterior e e unida a ela.

Nao usa modelo. Saidas: saida/manual_blocos.jsonl e saida/manual_limpo.md (leitura humana).

Uso (na pasta trabalho/entrega3):
    python extrair_manual.py
    python extrair_manual.py --pdf ../govendas-rules.pdf
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pdfplumber

AQUI = Path(__file__).resolve().parent
PDF_PADRAO = AQUI.parent / "govendas-rules.pdf"
SAIDA = AQUI / "saida"

# Valores medidos no diagnostico (Passo 2) deste PDF; nao valem para outro documento.
PRIMEIRA_PAGINA_CORPO = 5          # p. 1 capa, p. 2 em branco, p. 3 sumario, p. 4 em branco
DESLOCAMENTO_PAGINA = 4            # pagina impressa = pagina do PDF - 4 (conferido no cabecalho)
FAIXA_TOPO, FAIXA_BASE = 60, 780   # cabecalho em top~45; rodape em top~790 (pontos)
LIMIAR_PARAGRAFO = 7.0             # espaco entre linhas: 5,5 no paragrafo; 8,1 ou mais entre paragrafos
LIMIAR_CODIGO = 30.0               # espaco entre linhas de codigo: 6,0 normal; 22,0 = uma linha em branco
PASSO_LINHA_CODIGO = 16.0          # topo a topo entre linhas de codigo (corpo 10 + espaco 6)
NEGRITO = "Helvetica-Bold"
NIVEL_POR_TAMANHO = {16.0: 1, 12.0: 2, 9.5: 3}   # titulo em negrito: capitulo, secao, subsecao
RE_TITULO = {
    1: re.compile(r"^(\d+)\s+(\S.*)$"),
    2: re.compile(r"^(\d+\.\d+)\s+(\S.*)$"),
    3: re.compile(r"^(\d+\.\d+\.\d+)\s+(\S.*)$"),
}
CAMPO_TITULO = {1: "titulo_capitulo", 2: "titulo_secao", 3: "titulo_subsecao"}
RE_PONTILHADO = re.compile(r"^\.{8,}$")
RE_PAGINA = re.compile(r"(\d+)\s*$")
FIM_DE_FRASE = (".", ":", ";", "!", "?")


def juntar_linhas(partes) -> str:
    """Junta linhas quebradas pelo layout; 'pre-' + 'definido' vira 'pre-definido'."""
    texto = ""
    for p in partes:
        p = " ".join(p.split())
        if not p:
            continue
        if not texto:
            texto = p
        elif texto.endswith("-") and p[:1].islower():
            texto += p
        else:
            texto += " " + p
    return texto


def fonte_dominante(chars):
    cont = Counter((c["fontname"], round(c["size"], 1)) for c in chars if c["text"].strip())
    return cont.most_common(1)[0][0] if cont else (None, None)


def pagina_impressa(page):
    for ln in page.extract_text_lines(strip=True):
        if ln["top"] < FAIXA_TOPO:
            m = RE_PAGINA.search(ln["text"])
            if m:
                return int(m.group(1))
    return None


def linhas_fora_de_tabelas(page, caixas):
    def fora(obj):
        cx, cy = (obj["x0"] + obj["x1"]) / 2, (obj["top"] + obj["bottom"]) / 2
        return not any(x0 <= cx <= x1 and t <= cy <= b for x0, t, x1, b in caixas)

    alvo = page.filter(fora) if caixas else page
    saida = []
    for ln in alvo.extract_text_lines(return_chars=True, strip=True):
        fonte, tam = fonte_dominante(ln["chars"])
        if fonte is None or ln["top"] < FAIXA_TOPO or ln["top"] > FAIXA_BASE:
            continue
        texto = ln["text"].strip()
        if RE_PONTILHADO.match(texto):
            continue
        saida.append({"top": ln["top"], "bottom": ln["bottom"], "x0": ln["x0"],
                      "texto": texto, "fonte": fonte, "tam": tam})
    return saida


def agrupar_linhas(chars, tolerancia=3.0):
    """Agrupa caracteres em linhas visuais pela altura (Courier e Helvetica na mesma linha variam ~1 pt)."""
    linhas = []
    for c in sorted(chars, key=lambda c: c["top"]):
        if linhas and abs(c["top"] - linhas[-1][0]["top"]) < tolerancia:
            linhas[-1].append(c)
        else:
            linhas.append([c])
    return linhas


def tem_sobreposicao(chars) -> bool:
    """Na mesma linha, um caractere de outra fonte comeca antes do anterior terminar (texto invadiu a coluna)."""
    for ln in agrupar_linhas(chars):
        ln = sorted(ln, key=lambda c: c["x0"])
        if any(a["fontname"] != b["fontname"] and b["x0"] < a["x1"] - 1.0 for a, b in zip(ln, ln[1:])):
            return True
    return False


def celulas_por_fonte(page, linha_tabela):
    """Remonta as celulas de uma linha de tabela em que o texto de uma coluna invadiu a seguinte
    (p. 57 do PDF: 'whatsapp("nome_do_template")' sobre 'Mensagem'). As palavras sao montadas por
    fonte, para Courier e Helvetica nao se intercalarem, e cada palavra vai para a celula onde comeca."""
    cells = linha_tabela.cells
    chars = [c for c in page.within_bbox(linha_tabela.bbox).chars if c["text"].strip()]
    por_celula = [[] for _ in cells]

    def guardar(i, palavra):
        x = (palavra[0]["x0"] + palavra[0]["x1"]) / 2
        for j, cel in enumerate(cells):
            if cel is not None and cel[0] <= x <= cel[2]:
                por_celula[j].append((i, palavra[0]["x0"], "".join(c["text"] for c in palavra)))
                return

    for i, ln in enumerate(agrupar_linhas(chars)):
        for fonte in sorted({c["fontname"] for c in ln}):
            seq = sorted((c for c in ln if c["fontname"] == fonte), key=lambda c: c["x0"])
            palavra = [seq[0]]
            for a, b in zip(seq, seq[1:]):
                if b["x0"] - a["x1"] > 0.15 * a["size"]:
                    guardar(i, palavra)
                    palavra = []
                palavra.append(b)
            guardar(i, palavra)
    saida = []
    for itens in por_celula:
        linhas = {}
        for i, _, palavra in sorted(itens):
            linhas.setdefault(i, []).append(palavra)
        saida.append("\n".join(" ".join(ps) for _, ps in sorted(linhas.items())))
    return saida


def ler_tabela(page, tabela):
    """(cabecalho ou None, linhas). Cabecalho = 1a linha em negrito.

    Linha com texto de uma coluna invadindo a seguinte e remontada por fonte (celulas_por_fonte).
    Colunas vazias em todas as linhas saem. Uma coluna em que toda celula preenchida tem no maximo
    2 caracteres e transbordo do layout (p. 36 do PDF: o 's' de 'visitas' caiu na coluna ao lado);
    o fragmento volta para a mesma linha visual da celula da esquerda, conferida pela posicao vertical.
    """
    brutas = [[c or "" for c in row] for row in tabela.extract()]
    for i, linha in enumerate(tabela.rows):
        if tem_sobreposicao([c for c in page.within_bbox(linha.bbox).chars if c["text"].strip()]):
            brutas[i] = celulas_por_fonte(page, linha)
    ncol = max(len(r) for r in brutas)
    brutas = [r + [""] * (ncol - len(r)) for r in brutas]
    for j in range(ncol - 1, 0, -1):
        frags = [r[j].strip() for r in brutas if r[j].strip()]
        if frags and all(len(f) <= 2 for f in frags):
            for i, r in enumerate(brutas):
                if r[j].strip():
                    r[j - 1] = devolver_transbordo(page, tabela.rows[i], j, r[j - 1], r[j].strip())
                    r[j] = ""
    manter = [j for j in range(ncol) if any(r[j].strip() for r in brutas)]
    brutas = [[juntar_linhas(r[j].split("\n")) for j in manter] for r in brutas]
    fonte, _ = fonte_dominante(page.within_bbox(tabela.rows[0].bbox).chars)
    if fonte == NEGRITO:
        return brutas[0], brutas[1:]
    return None, brutas


def devolver_transbordo(page, linha_tabela, j, texto_esq, fragmento):
    """Cola o fragmento no fim da linha visual da celula da esquerda que esta na mesma altura."""
    cel_frag, cel_esq = linha_tabela.cells[j], linha_tabela.cells[j - 1]
    if cel_frag is None or cel_esq is None:
        return texto_esq + " " + fragmento
    topo = min(c["top"] for c in page.within_bbox(cel_frag).chars if c["text"].strip())
    tops = []
    for t in sorted(c["top"] for c in page.within_bbox(cel_esq).chars if c["text"].strip()):
        if not tops or t - tops[-1] > 1.5:
            tops.append(t)
    linhas = texto_esq.split("\n")
    k = next((i for i, t in enumerate(tops) if abs(t - topo) < 1.5), None)
    if k is None or k >= len(linhas):
        return texto_esq + " " + fragmento
    linhas[k] += fragmento
    return "\n".join(linhas)


def texto_tabela(cabecalho, linhas) -> str:
    saida = [" | ".join(cabecalho)] if cabecalho else []
    saida += [" | ".join(l) for l in linhas]
    return "\n".join(saida)


def texto_codigo(linhas, tam) -> str:
    """Reconstroi a indentacao pelo x0 (Courier: largura do caractere = 0,6 x tamanho)."""
    x_min, largura = min(x for x, t in linhas if t), 0.6 * tam
    return "\n".join("" if not t else " " * round((x - x_min) / largura) + t for x, t in linhas)


def extrair(pdf_path=PDF_PADRAO) -> list[dict]:
    blocos: list[dict] = []
    est = {"capitulo": None, "titulo_capitulo": None, "secao": None, "titulo_secao": None,
           "subsecao": None, "titulo_subsecao": None}

    def folha():
        return est["subsecao"] or est["secao"] or f"{est['capitulo']}.0"

    def novo(tipo, npag, impressa, **extra):
        b = {"tipo": tipo, **est, "folha": folha(),
             "pagina_pdf_ini": npag, "pagina_pdf_fim": npag,
             "pagina_impressa_ini": impressa, "pagina_impressa_fim": impressa, **extra}
        blocos.append(b)
        return b

    with pdfplumber.open(str(pdf_path)) as pdf:
        for npag, page in enumerate(pdf.pages, 1):
            if npag < PRIMEIRA_PAGINA_CORPO:
                continue
            impressa = pagina_impressa(page)
            if impressa != npag - DESLOCAMENTO_PAGINA:
                raise ValueError(f"p. {npag} do PDF: pagina impressa {impressa}, esperava {npag - DESLOCAMENTO_PAGINA}")
            tabelas = page.find_tables()
            itens = [(t.bbox[1], "tabela", t) for t in tabelas]
            itens += [(ln["top"], "linha", ln) for ln in linhas_fora_de_tabelas(page, [t.bbox for t in tabelas])]
            itens.sort(key=lambda i: i[0])
            aberto = None         # paragrafo ou codigo que ainda recebe linhas
            ultimo_titulo = None  # titulo que pode continuar na linha seguinte
            primeiro = True       # 1o item do corpo desta pagina
            for _, tipo, obj in itens:
                if tipo == "tabela":
                    cab, linhas = ler_tabela(page, obj)
                    ant = blocos[-1] if blocos else None
                    ncol_ant = None
                    if ant is not None and ant["tipo"] == "tabela":
                        ncol_ant = len(ant["cabecalho"] or (ant["linhas"][0] if ant["linhas"] else []))
                    if cab is None and primeiro and ncol_ant == len(linhas[0]):
                        ant["linhas"].extend(linhas)   # continuacao da tabela da pagina anterior
                        ant["pagina_pdf_fim"], ant["pagina_impressa_fim"] = npag, impressa
                    else:
                        novo("tabela", npag, impressa, cabecalho=cab, linhas=linhas)
                    aberto = ultimo_titulo = None
                    primeiro = False
                    continue

                ln = obj
                f, s, t = ln["fonte"], ln["tam"], ln["texto"]
                nivel = NIVEL_POR_TAMANHO.get(s) if f == NEGRITO else None
                if nivel:
                    m = RE_TITULO[nivel].match(t)
                    if m:
                        ident, titulo = m.group(1), m.group(2)
                        if nivel == 1:
                            est.update(capitulo=ident, titulo_capitulo=titulo, secao=None, titulo_secao=None,
                                       subsecao=None, titulo_subsecao=None)
                        elif nivel == 2:
                            est.update(secao=ident, titulo_secao=titulo, subsecao=None, titulo_subsecao=None)
                        else:
                            est.update(subsecao=ident, titulo_subsecao=titulo)
                        ultimo_titulo = novo("titulo", npag, impressa, nivel=nivel, id=ident, texto=t)
                        aberto = None
                        primeiro = False
                        continue
                    if ultimo_titulo is not None and ultimo_titulo["nivel"] == nivel:
                        campo = CAMPO_TITULO[nivel]   # titulo que quebrou em duas linhas
                        est[campo] = f"{est[campo]} {t}"
                        ultimo_titulo[campo] = est[campo]
                        ultimo_titulo["texto"] += " " + t
                        continue
                ultimo_titulo = None

                if f.startswith("Courier"):
                    if aberto is not None and aberto["tipo"] == "codigo" and ln["top"] - aberto["_bottom"] <= LIMIAR_CODIGO:
                        brancos = max(0, round((ln["top"] - aberto["_bottom"] - 6.0) / PASSO_LINHA_CODIGO))
                        aberto["_linhas"] += [(None, "")] * brancos + [(ln["x0"], t)]
                    else:
                        aberto = novo("codigo", npag, impressa, _linhas=[(ln["x0"], t)], _tam=s)
                    aberto["_bottom"] = ln["bottom"]
                    primeiro = False
                    continue

                ant = blocos[-1] if blocos else None
                continua_da_pagina_anterior = (
                    aberto is None and primeiro and ant is not None and ant["tipo"] == "paragrafo"
                    and ant["folha"] == folha() and not ant["_partes"][-1].endswith(FIM_DE_FRASE)
                    and not t.startswith("•") and t[:1].islower())
                if continua_da_pagina_anterior:
                    aberto = ant
                    aberto["pagina_pdf_fim"], aberto["pagina_impressa_fim"] = npag, impressa
                elif (aberto is None or aberto["tipo"] != "paragrafo" or s != aberto["_tam"]
                      or ln["top"] - aberto["_bottom"] > LIMIAR_PARAGRAFO or t.startswith("•")):
                    aberto = novo("paragrafo", npag, impressa, _partes=[], _tam=s)
                aberto["_partes"].append(t)
                aberto["_bottom"] = ln["bottom"]
                primeiro = False

    for i, b in enumerate(blocos):
        if b["tipo"] == "paragrafo":
            b["texto"] = juntar_linhas(b["_partes"])
        elif b["tipo"] == "codigo":
            b["texto"] = texto_codigo(b["_linhas"], b["_tam"])
        elif b["tipo"] == "tabela":
            b["texto"] = texto_tabela(b["cabecalho"], b["linhas"])
        for k in [k for k in b if k.startswith("_")]:
            del b[k]
        b["ordem"] = i
    return blocos


def markdown(blocos) -> str:
    def esc(s):
        return s.replace("|", "\\|")

    out = ["# Manual GoBR - texto extraido\n",
           "<!-- Gerado por extrair_manual.py a partir de govendas-rules.pdf. Nao editar a mao. -->\n"]
    pag = None
    for b in blocos:
        if b["pagina_impressa_ini"] != pag:
            pag = b["pagina_impressa_ini"]
            out.append(f"<!-- p. {pag} (PDF {b['pagina_pdf_ini']}) -->\n")
        if b["tipo"] == "titulo":
            out.append("#" * (b["nivel"] + 1) + " " + b["texto"] + "\n")
        elif b["tipo"] == "paragrafo":
            out.append(b["texto"] + "\n")
        elif b["tipo"] == "codigo":
            out.append("```\n" + b["texto"] + "\n```\n")
        else:
            cab = b["cabecalho"] or [""] * len(b["linhas"][0])
            linhas = ["| " + " | ".join(esc(c) for c in cab) + " |", "|" + "---|" * len(cab)]
            linhas += ["| " + " | ".join(esc(c) for c in l) + " |" for l in b["linhas"]]
            out.append("\n".join(linhas) + "\n")
    return "\n".join(out)


def escrever(blocos, destino: Path = SAIDA) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    with open(destino / "manual_blocos.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for b in blocos:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")
    with open(destino / "manual_limpo.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown(blocos))


def resumo(blocos) -> str:
    tipos = Counter(b["tipo"] for b in blocos)
    niveis = Counter(b["nivel"] for b in blocos if b["tipo"] == "titulo")
    chars = Counter()
    for b in blocos:
        chars[b["tipo"]] += len(b["texto"])
    folhas = {b["folha"] for b in blocos}
    return (f"blocos: {dict(tipos)}\n"
            f"titulos: {niveis[1]} capitulos, {niveis[2]} secoes, {niveis[3]} subsecoes | folhas: {len(folhas)}\n"
            f"caracteres por tipo: {dict(chars)} | total: {sum(chars.values())}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", type=Path, default=PDF_PADRAO)
    args = ap.parse_args()
    blocos = extrair(args.pdf)
    escrever(blocos)
    print(resumo(blocos))
    print(f"Gravado em {SAIDA / 'manual_blocos.jsonl'} e {SAIDA / 'manual_limpo.md'}")


if __name__ == "__main__":
    main()
