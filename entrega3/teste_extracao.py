# -*- coding: utf-8 -*-
"""
Testes do passo 5.1 (extracao do manual), sem modelo. Rodam sobre o PDF real.

    python teste_extracao.py
"""
import sys
from collections import Counter

from extrair_manual import PDF_PADRAO, RE_PONTILHADO, extrair

BLOCOS = extrair(PDF_PADRAO)
TESTES = []


def teste(f):
    TESTES.append(f)
    return f


def titulo(ident):
    return next(b for b in BLOCOS if b["tipo"] == "titulo" and b["id"] == ident)


@teste
def hierarquia_completa():
    n = Counter(b["nivel"] for b in BLOCOS if b["tipo"] == "titulo")
    assert (n[1], n[2], n[3]) == (10, 51, 34), dict(n)


@teste
def sem_capa_sumario_cabecalho_rodape_pontilhado():
    for b in BLOCOS:
        assert b["pagina_pdf_ini"] >= 5, b["ordem"]
        assert "ALL RIGHTS RESERVED" not in b["texto"], b["ordem"]
        assert not any(RE_PONTILHADO.match(l.strip()) for l in b["texto"].splitlines()), b["ordem"]


@teste
def pagina_impressa_igual_pdf_menos_4():
    for b in BLOCOS:
        assert b["pagina_impressa_ini"] == b["pagina_pdf_ini"] - 4, b["ordem"]
        assert b["pagina_impressa_fim"] == b["pagina_pdf_fim"] - 4, b["ordem"]
    assert titulo("6.2")["pagina_impressa_ini"] == 23


@teste
def continuacao_de_tabela_unida_a_anterior():
    alvo = [b for b in BLOCOS if b["tipo"] == "tabela"
            and any(l[0].startswith("unica compra com o vendedor") for l in b["linhas"])]
    assert len(alvo) == 1, len(alvo)
    t = alvo[0]
    assert t["cabecalho"] == ["Filtro", "Descrição"], t["cabecalho"]
    assert t["folha"] == "6.1", t["folha"]
    assert (t["pagina_pdf_ini"], t["pagina_pdf_fim"]) == (26, 27)


@teste
def toda_tabela_tem_cabecalho():
    sem = [(b["pagina_pdf_ini"], b["linhas"][0][:1]) for b in BLOCOS if b["tipo"] == "tabela" and not b["cabecalho"]]
    assert not sem, sem


@teste
def tabela_so_com_cabecalho_recebe_linhas_da_pagina_seguinte():
    vazias = [(b["pagina_pdf_ini"], b["cabecalho"]) for b in BLOCOS if b["tipo"] == "tabela" and not b["linhas"]]
    assert not vazias, vazias


@teste
def todo_version_1_0_do_pdf_abre_um_bloco_de_codigo():
    import pdfplumber
    with pdfplumber.open(str(PDF_PADRAO)) as pdf:   # contagem direta, sem o agrupamento em blocos
        n_pdf = sum(1 for pg in pdf.pages for ln in pg.extract_text_lines(strip=True)
                    if ln["text"].strip() == "version 1.0")
    cods = [b for b in BLOCOS if b["tipo"] == "codigo" and "version 1.0" in b["texto"]]
    assert len(cods) == n_pdf, (len(cods), n_pdf)
    assert all(c["texto"].startswith("version 1.0") and c["texto"].count("version 1.0") == 1 for c in cods)


@teste
def transbordo_de_celula_volta_para_a_linha_certa():
    linha = next(l for b in BLOCOS if b["tipo"] == "tabela" for l in b["linhas"]
                 if l[0].startswith("data da última visita do representante"))
    assert len(linha) == 2, linha
    assert linha[1].startswith("clientes cuja data de visitas mapeada"), linha[1]


@teste
def celula_invadida_por_outra_coluna_remontada():
    linha = next(l for b in BLOCOS if b["tipo"] == "tabela" for l in b["linhas"] if l[0] == "WhatsApp")
    assert linha == ["WhatsApp", 'whatsapp("nome_do_template")',
                     "Mensagem via WhatsApp usando um template pré-aprovado"], linha


@teste
def tabela_de_tres_paginas_unida():
    t = next(b for b in BLOCOS if b["tipo"] == "tabela"
             and any(l[0].startswith("data da rota futura do vendedor") for l in b["linhas"]))
    assert t["cabecalho"] == ["Filtro", "Descrição"] and t["folha"] == "6.11", (t["cabecalho"], t["folha"])
    assert (t["pagina_pdf_ini"], t["pagina_pdf_fim"]) == (35, 37), (t["pagina_pdf_ini"], t["pagina_pdf_fim"])


@teste
def titulo_quebrado_em_duas_linhas():
    assert titulo("2.1")["texto"].endswith("consegue expressar"), titulo("2.1")["texto"]
    assert titulo("4")["titulo_capitulo"].endswith("segmentações de clientes"), titulo("4")["titulo_capitulo"]
    assert all(b["titulo_capitulo"].endswith("segmentações de clientes") for b in BLOCOS if b["capitulo"] == "4")


@teste
def hifen_de_prefixo_preservado():
    assert not any("pré- " in b["texto"] for b in BLOCOS)
    assert any("pré-" in b["texto"] for b in BLOCOS)


@teste
def folha_coerente_com_a_hierarquia():
    for b in BLOCOS:
        esperada = b["subsecao"] or b["secao"] or f"{b['capitulo']}.0"
        assert b["folha"] == esperada, b["ordem"]


def main():
    falhas = 0
    for f in TESTES:
        try:
            f()
            print(f"ok    {f.__name__}")
        except AssertionError as e:
            falhas += 1
            print(f"FALHA {f.__name__}: {e}")
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes passaram")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
