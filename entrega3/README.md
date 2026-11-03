# Entrega 3 — Indexação do manual GoBR

Indexa o manual da linguagem (`../govendas-rules.pdf`, "Manual do Govendas Business Rules (GoBR)", v. 0.89.0, 62 páginas) para servir de apoio ao agente na hora de escrever a regra GOBR. Duas dicas do enunciado (p. 4) guiam a entrega: "Indexe com embeddings o manual do GOBR para que possa servir de apoio para escrever a saída" e "Atente-se para a quebra dos chunks". O índice é separado do das regras (Entrega 2) e devolve trechos do manual com seção e página.

## Como rodar (PowerShell, na pasta `trabalho\entrega3`)

```powershell
pip install -r requirements.txt
python extrair_manual.py                 # 5.1: PDF -> saida/manual_blocos.jsonl e saida/manual_limpo.md (sem modelo)
python teste_extracao.py                 # 13 testes da extração (sem modelo)
python conjuntos_manual.py validar       # confere os conjuntos de consultas contra a extração (sem modelo)
python teste_plumbing_manual.py          # 13 testes de chunking, busca e avaliação (sem modelo)
python indexar_manual.py                 # estratégias C e B com o bge-m3 local
python avaliar_manual.py --rerank --hibrido                     # desenvolvimento (decide)
python avaliar_manual.py --conjunto teste --rerank --hibrido    # teste (só relata)
python buscar_manual.py "como separo os clientes inadimplentes?" --rerank   # configuração padrão (C + vetor + rerank)
```

## Arquivos

| Arquivo | Papel |
|---|---|
| `extrair_manual.py`, `teste_extracao.py` | 5.1: extração e limpeza do PDF; 13 testes |
| `saida/manual_blocos.jsonl`, `saida/manual_limpo.md` | blocos extraídos (título, parágrafo, tabela, código) com folha e páginas; versão para leitura |
| `conjuntos_manual.py` | sorteio e validação dos conjuntos de consultas |
| `consultas_manual_dev.json`, `consultas_manual_teste.json` | 15 consultas de desenvolvimento e 20 de teste, com gabarito por folha |
| `comum_manual.py` | 5.2 e 5.4: folhas, estratégias C e B, regras de acerto, busca |
| `indexar_manual.py` | 5.3: grava `indices/indice_manual_C/` e `indices/indice_manual_B/` |
| `avaliar_manual.py`, `buscar_manual.py` | 5.4: avaliação e consulta pela linha de comando |
| `teste_plumbing_manual.py` | 5.5: 13 testes sem modelo |
| `resultados_manual_*.md` / `.json` | saídas da avaliação (dev e teste) |

## O manual (diagnóstico do Passo 2)

- 62 páginas A4. As páginas 1 a 4 são capa, página em branco, sumário e página em branco. **Página impressa = página do PDF − 4** (conferido no cabeçalho de cada página); o gabarito usa a impressa.
- 10 capítulos, 51 seções (x.y) e 34 subseções (x.y.z). Os títulos são reconhecidos pela fonte (Helvetica-Bold 16 / 12 / 9,5) e pelo número; o outline do PDF só marca os capítulos.
- Ruído retirado: cabeçalho corrente, rodapé "©2026, Govendas Assistente de Vendas Inteligente • ALL RIGHTS RESERVED.", linhas pontilhadas de abertura de capítulo e sumário.
- Extração: 380 blocos (191 parágrafos, 47 tabelas, 47 blocos de código, 95 títulos) em 90 folhas com conteúdo; 5 folhas só com título (4.0, 4.3, 7.3, 7.4, 8.4) não viram nó.
- Tabelas são lidas por célula (a leitura por linha mistura as colunas) e as continuações entre páginas são unidas; código mantém a indentação.
- Terminologia: o manual chama a linguagem de *gorules* e o produto de *GoBR*; o enunciado e os arquivos usam GOBR.

## Decisão de chunking (Passo 3)

| Estratégia | Papel | Como corta |
|---|---|---|
| **C — estrutural** | principal | um nó por folha (subseção, seção ou abertura do capítulo); texto = trilha ("Cap. 6 … › 6.2 …") + corpo; acima de 512 tokens divide só entre blocos, tabela em grupos de linhas com o cabeçalho repetido, parágrafo em frases; código nunca é cortado; sem sobreposição |
| **B — tamanho fixo** | controle | o texto limpo inteiro, cortado pelo `SentenceSplitter` do LlamaIndex (256 tokens, 32 de sobreposição) |
| A — semântica | descartada a priori | `SemanticSplitterNodeParser`: decide os cortes por similaridade e ignora os títulos, tabelas e código que o manual já marca; a receita da aula é para "artigos" |

| Parâmetro | Valor | Origem |
|---|---|---|
| Teto do nó C | 512 tokens (bge-m3, com especiais) | chunk_size da aula (`copy_of_rag_local_llamaindex.py`, l. 119–122); usar como **teto** é escolha de engenharia |
| Fronteiras de C | bloco; grupo de linhas de tabela; frase; código inteiro | enunciado, p. 4, dica 4; "nunca devolver meia unidade" vem da Entrega 2; o detalhe **não encontrei no material** (escolha de engenharia) |
| Sobreposição de C | 0 | **não encontrei no material**, escolha de engenharia: a aula usa sobreposição para "evitar que o contexto se perca entre quebras" (l. 118); aqui as quebras caem só em fronteira natural e a trilha se repete em cada parte |
| Trilha no texto do nó | sim | escolha de engenharia; equivale a repetir título e resumo nas partes de uma regra (Entrega 2) |
| chunk / overlap de B | 256 / 32 | atividade de RAG da disciplina, Célula 7, l. 165–166 (".docx (manuais): passos curtos → chunks menores") |
| Tokenizer que mede B | bge-m3, sem especiais | **não encontrei no material** (a aula fala em "tokens/palavras") |
| Metadados fora do embedding | todos | igual à Entrega 2 (DMAS §4.7.2, Listing 4.21; `excluded_embed_metadata_keys` é comportamento do LlamaIndex) |
| Embedding, reranker, BM25, RRF, candidatos | bge-m3; bge-reranker-v2-m3; k1 1,5 e b 0,75; k 60; 50 | os da Entrega 2, importados sem alteração |

## Conjuntos de avaliação (Passo 4, antes de indexar)

- **Desenvolvimento:** 15 consultas; folhas escolhidas à mão para cobrir os capítulos 2 a 10 e os três tipos de conteúdo (texto, tabela, código).
- **Teste:** 20 folhas sorteadas com `random.Random(20261102)` entre as 62 folhas com conteúdo que não aparecem em nenhum gabarito do desenvolvimento; uma consulta por folha, escrita lendo só a folha, antes de existir índice.
- **Gabarito por folha**, nunca por chunk: critério "chave" (busca exata das construções da resposta no texto extraído) ou "manual" (justificado na consulta). Nenhuma folha de gabarito do teste está no desenvolvimento; em 3 folhas (3.2, 7.3.6 e 8.7) a consulta foi redirecionada para outro aspecto da mesma folha, antes de qualquer busca.
- Os dois conjuntos foram commitados (`c7c956f`) antes de indexar; `python conjuntos_manual.py validar` confere tudo, inclusive o sorteio.
- **Limitação:** as consultas foram escritas por quem leu a folha. A paráfrase reduz, mas não elimina, a vantagem da busca por palavras (BM25).

## Regras de acerto e de escolha

- **Acerto (oficial, Passo 4):** o chunk acerta se a sua folha principal está no gabarito (C: a folha do nó; B: a folha com mais caracteres dentro do chunk).
- **Acerto (sensibilidade, só relatada):** também acerta o chunk que contém pelo menos 50% dos caracteres de uma folha do gabarito. Foi acrescentada depois de ver, com um tokenizer falso, que em B quase metade das folhas nunca seria a principal de um chunk, e antes de qualquer busca. O limite de 50%: **não encontrei no material**, escolha de engenharia.
- **Escolha do padrão:** maior MRR no desenvolvimento (regra oficial) entre as 8 combinações estratégia × configuração; empate → maior hit@1 → configuração mais simples → estratégia C. A regra ficou no código e foi commitada (`3250d98`, 03/11 12:47) antes da indexação (12:52) e do desenvolvimento (13:36). "O desenvolvimento decide, o teste só relata": AIMA cap. 19, parágrafos antes do §19.4.1. Os desempates são escolha de engenharia.
- **Métricas:** hit@k e MRR, as funções da Entrega 2; o ranking é de chunks, sem agrupar por folha (escolha de engenharia: o agente recebe chunks).

## Resultados

### Indexação

- **C:** 94 nós de 90 folhas; tokens: mediana 164,5, máximo 511 (teto 512); folhas divididas: 6.1 (2 partes), 6.5 (2 partes), 6.11 (2 partes), 6.13 (2 partes); 248,7 s de embedding.
- **B:** 84 chunks; tokens: mediana 233,0, máximo 256; nenhum caractere fora de chunk; 27 das 90 folhas nunca são a principal de um chunk; 164,3 s de embedding.
- Consultas que nenhum chunk pode acertar pela regra oficial: em C, nenhuma; em B, 1 do dev (mdev_10) e 5 do teste (mteste_01, mteste_02, mteste_05, mteste_10, mteste_16). Pela regra de cobertura, nenhuma nas duas.

### Desenvolvimento (15 consultas)

Regra oficial:

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 15 | 0,53 | 0,80 | 0,93 | 1,00 | 0,693 |
| **C · vetor + rerank** (padrão) | 15 | 0,60 | 0,93 | 1,00 | 1,00 | 0,772 |
| C · híbrido | 15 | 0,40 | 0,87 | 0,93 | 1,00 | 0,637 |
| C · híbrido + rerank | 15 | 0,60 | 0,93 | 1,00 | 1,00 | 0,772 |
| B · vetor | 15 | 0,33 | 0,67 | 0,73 | 0,80 | 0,518 |
| B · vetor + rerank | 15 | 0,47 | 0,80 | 0,87 | 0,87 | 0,630 |
| B · híbrido | 15 | 0,27 | 0,73 | 0,80 | 0,87 | 0,503 |
| B · híbrido + rerank | 15 | 0,47 | 0,80 | 0,87 | 0,87 | 0,625 |

Sensibilidade (acerta também o chunk com pelo menos 50% de uma folha do gabarito; só relata):

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 15 | 0,53 | 0,80 | 0,93 | 1,00 | 0,693 |
| C · vetor + rerank | 15 | 0,60 | 0,93 | 1,00 | 1,00 | 0,772 |
| C · híbrido | 15 | 0,40 | 0,87 | 0,93 | 1,00 | 0,637 |
| C · híbrido + rerank | 15 | 0,60 | 0,93 | 1,00 | 1,00 | 0,772 |
| B · vetor | 15 | 0,47 | 0,80 | 0,87 | 1,00 | 0,663 |
| B · vetor + rerank | 15 | 0,67 | 0,93 | 1,00 | 1,00 | 0,791 |
| B · híbrido | 15 | 0,40 | 0,93 | 0,93 | 1,00 | 0,633 |
| B · híbrido + rerank | 15 | 0,67 | 0,93 | 1,00 | 1,00 | 0,791 |

**Padrão pela regra fixada: C · vetor + rerank** (MRR 0,772, hit@1 0,60). Empatou em MRR e em hit@1 com C · híbrido + rerank, e o desempate "configuração mais simples" decidiu. As duas configurações deram a mesma posição nas 15 consultas; a explicação provável é que, com 94 nós e 50 candidatos, o reranker relê mais da metade do índice, e a primeira fase quase não muda o topo.

### Teste (20 consultas; só relata)

Regra oficial:

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 20 | 0,50 | 0,80 | 0,85 | 0,90 | 0,654 |
| **C · vetor + rerank** (padrão) | 20 | 0,75 | 0,75 | 0,85 | 0,90 | 0,785 |
| C · híbrido | 20 | 0,70 | 0,90 | 0,90 | 0,95 | 0,784 |
| C · híbrido + rerank | 20 | 0,75 | 0,75 | 0,85 | 0,90 | 0,783 |
| B · vetor | 20 | 0,25 | 0,40 | 0,45 | 0,55 | 0,353 |
| B · vetor + rerank | 20 | 0,40 | 0,55 | 0,55 | 0,65 | 0,491 |
| B · híbrido | 20 | 0,30 | 0,60 | 0,60 | 0,65 | 0,440 |
| B · híbrido + rerank | 20 | 0,40 | 0,55 | 0,55 | 0,65 | 0,491 |

Sensibilidade:

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 20 | 0,50 | 0,80 | 0,85 | 0,90 | 0,654 |
| C · vetor + rerank | 20 | 0,75 | 0,75 | 0,85 | 0,90 | 0,785 |
| C · híbrido | 20 | 0,70 | 0,90 | 0,90 | 0,95 | 0,784 |
| C · híbrido + rerank | 20 | 0,75 | 0,75 | 0,85 | 0,90 | 0,783 |
| B · vetor | 20 | 0,35 | 0,70 | 0,75 | 0,80 | 0,536 |
| B · vetor + rerank | 20 | 0,60 | 0,80 | 0,80 | 0,90 | 0,709 |
| B · híbrido | 20 | 0,50 | 0,85 | 0,85 | 0,85 | 0,659 |
| B · híbrido + rerank | 20 | 0,60 | 0,80 | 0,80 | 0,90 | 0,709 |

O padrão teve MRR 0,785 e hit@1 0,75 no teste (no desenvolvimento: 0,772 e 0,60).

### Custo (CPU do notebook)

- Embedding: C 248,7 s; B 164,3 s.
- Avaliação do teste (20 consultas), tempo por configuração na saída do terminal: C: vetor 6 s, vetor + rerank 1.019 s, híbrido 5 s, híbrido + rerank 191 s (pares já em cache); B: 5 s, 926 s, 6 s e 159 s.
- O re-ranking custa cerca de 1 s por par (consulta, chunk): com 50 candidatos, perto de 50 s por pergunta. Isso pesa no fluxo interativo das Entregas 4 a 6 e fica como ponto em aberto, sem decisão aqui.

### Leitura dos resultados (sem ajustar nada)

- Pela regra oficial, C supera B em todas as configurações, no desenvolvimento e no teste. Parte da diferença vem da própria regra: em B há consultas que nenhum chunk consegue acertar. Pela regra de cobertura, B com rerank empata com C no desenvolvimento (0,791 contra 0,772; 0,019 × 15 ≈ 0,29 de soma de rank recíproco, menos que uma consulta caindo do 1º para o 2º lugar) e fica atrás no teste (0,709 contra 0,785). Ou seja: "C é melhor" vale com folga pela regra oficial; pela de cobertura, a diferença no desenvolvimento é pequena.
- O re-ranking melhora C nos dois conjuntos (desenvolvimento 0,693 → 0,772; teste 0,654 → 0,785).
- O híbrido sem re-ranking piora C no desenvolvimento (0,637) e melhora no teste (0,784). Com 15 e 20 consultas não dá para concluir; **não encontrei no material** critério de significância.
- Consultas do teste mais longe do 1º lugar no padrão (só relato, nada foi ajustado por elas): mteste_10 (folha 6.9, posição 24: a consulta diz "grupo auxiliar"; a busca achou o assunto, com 4.7, 4.1.2 e 4.5 sobre segmentação, mas não a folha do filtro), mteste_04 (posição 16), mteste_18 (7), mteste_09 (5) e mteste_12 (4).

## Ajustes feitos olhando resultado

Nenhum ajuste foi feito depois de ver resultados de busca no manual. Mudanças feitas antes de qualquer busca, já declaradas acima: (1) a regra de sensibilidade; (2) as 3 consultas de teste redirecionadas pela regra de independência do validador. Depois do desenvolvimento, só se registrou a decisão no código (`ESTRATEGIA_PADRAO`, `RERANK_PADRAO` e `HIBRIDO_PADRAO`, em `comum_manual.py`).

## Lacunas e limites

- Tamanho e sobreposição de chunk não estão no AIMA nem no DMAS; os valores vêm da atividade de RAG da disciplina, que os usa sem discutir.
- O limite de 50% da sensibilidade, a sobreposição 0 em C, o tokenizer de B, o ranking sem agrupar e os desempates são escolhas de engenharia.
- Conjuntos pequenos (15 e 20 consultas): cada consulta vale 6,7 e 5 pontos percentuais de hit@k. **Não encontrei no material** critério de significância para MRR.
- Consultas escritas pela mesma autoria do índice; o gabarito por chave é lexical; a regra de independência deixa fora do gabarito do teste folhas do desenvolvimento que também respondem.
- Re-ranking no CPU: cerca de 1 s por par (ver Custo).
- BM25 (k1, b) e RRF (k = 60): valores da literatura, como na Entrega 2; não estão no material.

## Reaproveitamento da Entrega 2

Nenhum arquivo da Entrega 2 foi alterado. `comum_manual.py` importa de `entrega2/comum.py` o BM25, o `Reranker`, `reordenar_com_reranker` e as funções que carregam os modelos; `avaliar_manual.py` importa `metricas` e `resumo_configs` de `entrega2/avaliar.py`; `indexar_manual.py` importa `_com_tentativas` de `entrega2/indexar.py`. Só o RRF foi reescrito aqui, chaveado pelo id do nó, porque no manual não há "regra" a agrupar.
