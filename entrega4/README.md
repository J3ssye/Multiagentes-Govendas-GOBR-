# Entrega 4 — Fluxo básico de busca (RAG)

Um fluxo determinístico em Python que recebe uma pergunta em português e devolve o que o agente das próximas entregas precisa para escrever uma regra GOBR: as 3 regras de exemplo mais parecidas (índice da Entrega 2) e os 3 trechos do manual mais parecidos (índice da Entrega 3), montados num único contexto. Sem agente, sem grafo e, por padrão, sem LLM (0 token). Com `--responder`, uma chamada ao Gemini com esse contexto.

A única definição desta entrega é o título "Construção de um fluxo básico de busca - RAG" (informado em 07/11/2026): ele não fixa saída, métrica nem teto de latência. O que foi decidido por quem entrega (a saída e o teto de 20 s) e o que é proposta sem apoio no material está em "Decisão" e em `regra_escolha_fluxo.md`, o pré-registro commitado antes de qualquer execução com embedding ou reranker.

**Resultado em resumo**

- **Configuração escolhida no desenvolvimento, pela regra pré-registrada:** regras com busca híbrida (vetor + BM25) sem reranker; manual com vetor + reranker de 5 candidatos (`max_length` 2048). A latência da dupla no desenvolvimento ficou em 10,4 s (pior caso), e a escolha foi decidida pela soma dos hit@3.
- **Teste (rodou uma vez e só relata):**
  - regras: hit@3 0,75, MRR 0,640;
  - manual: hit@3 0,80, MRR 0,771;
  - pior caso somado: 11,2 s, abaixo do teto de 20 s.
- **Custo de LLM:** 0 token no modo padrão. Com `--responder`, uma chamada, com os tokens relatados.

## Como rodar (PowerShell, na pasta `trabalho\entrega4`)

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"         # não grava __pycache__ nas pastas das Entregas 1 a 3
pip install -r requirements.txt
python teste_plumbing_fluxo.py            # 41 testes sem modelo e sem rede
python avaliar_fluxo.py grade             # as 28 configurações e a ordem de execução (sem modelo)
python avaliar_fluxo.py insumos           # confere os sha256 da seção 11 da regra (sem modelo)
# commit de regra_escolha_fluxo.md ANTES do desenvolvimento: a data do commit é a prova do pré-registro
python avaliar_fluxo.py dev               # desenvolvimento: 28 configurações, acerto e latência (decide); retoma se cair
python avaliar_fluxo.py escolher          # aplica a regra da seção 6 e grava config_escolhida.json
python avaliar_fluxo.py teste             # teste, uma vez, só com a dupla escolhida (só relata)
python fluxo.py "como agendar ligações a cada 14 dias para clientes ativos?"            # contexto, 0 token de LLM
python fluxo.py "como agendar ligações a cada 14 dias para clientes ativos?" --responder # mais 1 chamada ao Gemini
python fluxo.py --sessao                  # várias perguntas; modelos e índices carregados uma vez
```

`python avaliar_fluxo.py tudo` roda `dev`, `escolher` e `teste` em sequência (nesta entrega os três foram rodados separados). `--responder` precisa de `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`) na sessão, como na Entrega 1: `$env:GEMINI_API_KEY = "..."`. Se as duas estiverem definidas, o SDK usa `GOOGLE_API_KEY` e avisa. Durante o `dev` e o `teste`, o computador deve ficar ligado na tomada, acordado e sem outras tarefas: a latência é parte do que se mede (ver "Desvios").

## Arquivos

| Arquivo | Papel |
|---|---|
| `regra_escolha_fluxo.md` | pré-registro: grade, medição, regra de escolha, uso do teste, limitações, insumos com sha256 |
| `comum_fluxo.py` | constantes da regra, grade de configurações, busca configurável, cronômetro, regra de escolha em código, montagem do contexto, prompt e chamada do `--responder` |
| `fluxo.py` | o fluxo: uma pergunta ou modo de sessão; `--responder`, `--json`, `--so-fontes` |
| `avaliar_fluxo.py` | `grade`, `insumos`, `dev`, `escolher`, `teste`, `tudo` e `relatorio` |
| `teste_plumbing_fluxo.py` | 41 testes sem modelo e sem rede |
| `requirements.txt` | dependências: as da Entrega 3 (por `-r`) e `google-genai` |
| `dev_checkpoints/` | uma configuração por arquivo `.json` (retomada) e `_execucoes.jsonl` (carregamento e dispositivo da execução) |
| `resultados_fluxo_dev.md` / `.json` | desenvolvimento: as 28 configurações |
| `config_escolhida.json` | a dupla escolhida, as medidas do desenvolvimento, as 5 melhores duplas e o sha256 da regra e do resultado do desenvolvimento |
| `resultados_fluxo_teste.md` / `.json` | teste, uma vez |
| `dev_1a_execucao/` | a 1ª execução do desenvolvimento, descartada e guardada inteira (ver "Desvios") |

## O fluxo

| Etapa | O que faz | De onde vem |
|---|---|---|
| 1. Regras | `buscar_regras` no índice `com_pontos`, na configuração escolhida (híbrido, sem reranker); 3 melhores regras, com as partes agrupadas por regra; o GOBR completo vem do metadado | Entrega 2 |
| 2. Manual | `buscar` no índice da estratégia C, na configuração escolhida (vetor + reranker, N = 5, `max_length` 2048); 3 melhores trechos, com seção e páginas impressas | Entrega 3 |
| 3. Contexto | um texto: "Regras de exemplo" (título, descrição e GOBR completo de cada regra, em bloco de código) e "Manual do GOBR" (seção, páginas e texto de cada trecho) | novo |
| 4. Resposta (só com `--responder`) | uma chamada `generate_content` ao Gemini; os tokens são os que a API contou | novo; SDK e modelo padrão como na Entrega 1 |

A saída é texto legível ou, com `--json`, um dicionário com as fontes, o contexto, os tempos e a resposta (para o agente da Entrega 5 consumir). Mesmo sem `--responder`, a saída informa quantos tokens o contexto tem (contados com o tokenizer do bge-m3, não com o do Gemini) e os segundos de cada busca. A configuração vem de `config_escolhida.json`; não há configuração escrita à mão no código.

## Decisão

| Escolha | Valor | Origem |
|---|---|---|
| Forma do fluxo | workflow determinístico em Python | proposta aceita em 07/11/2026; DMAS §2.2.1 e cap. 11, Tabela 11.1 (passos fixos e conhecidos pedem workflow). O agente e o grafo ficam para a Entrega 5 |
| Saída padrão | contexto: 3 regras com o GOBR completo e 3 trechos do manual com seção e páginas; 0 token de LLM | decisão de quem entrega, 07/11/2026 |
| `--responder` | uma chamada ao Gemini; os tokens são relatados; a resposta não é avaliada (não há gabarito para ela) | decisão de quem entrega, 07/11/2026; DMAS §10.5.1 lista tokens e chamadas de API como métrica de eficiência |
| Prompt do `--responder` | estrutura da Célula 8 da atividade de RAG (instrução de sistema, "Contexto recuperado", "Pergunta"), com o domínio trocado para GOBR | Célula 8 (`rag_local_llamaindex_atividade.py`, l. 190–201); a redação para GOBR: **não encontrei no material** |
| k | 3 itens por índice | exemplos do material: Célula 8 (`top_n=3`), aula (`similarity_top_k=3`), DMAS Listing 4.21 (`top_k=3`); a justificativa do valor: **não encontrei no material** |
| Teto de latência | 20 s por pergunta, regras e manual somados, no computador de quem entrega | decisão de quem entrega, 07/11/2026; o número: **não encontrei no material** (DMAS §3.5 só diz que o uso interativo exige baixa latência) |
| Quem escolhe a configuração | o desenvolvimento; o teste só relata e roda uma vez | AIMA cap. 19, parágrafos antes do §19.4.1; aplicar isso a um pipeline de busca é analogia: **não encontrei no material** |
| Grade | fase 1 (vetor, híbrido) × (sem reranker, ou N em 5, 10, 20, 50 com `max_length` 512 e 2048 nas regras e só 2048 no manual) = 18 + 10 = 28 configurações | N = 10: Célula 8; N = 50 e `max_length` 2048: Entregas 2 e 3; N = 5, N = 20 e `max_length` 512: escolha de engenharia, **não encontrei no material** |
| Regra de escolha | entre as duplas sem exclusão por latência e com `lat(R) + lat(M) ≤ 20 s`: maior soma de hit@3; empate: maior soma de MRR; empate: menor latência da dupla; empate: a mais simples (regras primeiro) | hit@3 como critério principal: métrica determinística quando há gabarito (DMAS §10.4.4); usá-lo como critério de escolha, os pesos iguais e a ordem dos desempates: **não encontrei no material** |
| Índices | `com_pontos` (Entrega 2) e estratégia C (Entrega 3); bge-m3 e bge-reranker-v2-m3 | herdados; as constantes `ESTRATEGIA_PADRAO`, `RERANK_PADRAO` e `HIBRIDO_PADRAO` da Entrega 3 não mudam |

N = 3 não entra na grade: com k = 3 o reranker só reordenaria os mesmos 3 itens. As configurações padrão das Entregas 2 (híbrido, N = 50, `max_length` 2048) e 3 (vetor, N = 50, `max_length` 2048) fazem parte da grade; a expectativa de que a latência as excluísse vinha de um custo medido no teste da Entrega 3 (cerca de 1 s por par; herdado do README da Entrega 3 e do handoff de 03/11) e se confirmou aqui: as duas foram excluídas (94,3 s e 63,3 s na primeira consulta medida). O `max_length` 512 entra como alternativa mais barata nas regras porque o custo do reranker cresce com o tamanho do texto: 50 dos 199 nós do índice (25%) têm mais de 512 tokens do bge-m3 (medido em 07/11/2026; `regra_escolha_fluxo.md`, seção 4).

## Como a latência é medida

- Relógio: `time.perf_counter()` em volta da chamada de busca, com modelos e índices já carregados. Entram o embedding da consulta, a fase 1, a fusão e o reranker. Ficam fora o carregamento (relatado à parte), a montagem do contexto e o Gemini.
- Sem cache de notas: o reranker da medição não é o `RerankerComCache` da Entrega 3.
- Aquecimento: uma chamada descartada por modelo carregado (cada `max_length`) e por índice, com "teste de aquecimento", `hibrido=True` e N = 2 (monta o BM25 e aquece o reranker).
- Cada consulta é cronometrada 2 vezes e vale a menor. O acerto vem da 1ª repetição, sobre o ranking completo (`k = None`).
- Latência de uma configuração: a maior entre as consultas do desenvolvimento. Latência da dupla: a das regras mais a do manual.
- Poda: se a 1ª medição de uma consulta passar de 20 s, a configuração é encerrada como "excluída por latência" (fica gravada a consulta e o tempo) e não se mede mais nada dela.
- Cada configuração concluída é gravada em `dev_checkpoints/` (abertura exclusiva); se a execução cair, `python avaliar_fluxo.py dev` retoma pelas que faltam.
- No teste não há poda: se a latência passar do teto, relata-se. A latência de cada consulta é a menor de 2 repetições, como no desenvolvimento; relatam-se a mediana e o máximo sobre as 20 consultas.

## Resultados

### Testes sem modelo

`41/41 testes passaram; 0 falharam; 0 pulados`, no computador de quem entrega (Windows) em 09/11/2026, inclusive o de integração com os índices e os conjuntos de consultas reais (com embedding e reranker falsos). Os mesmos 41 também passaram numa cópia da pasta em Linux (Python 3.10) em 08/11/2026.

### Pré-registro

- `regra_escolha_fluxo.md` (sha256 `fa77637b72388657f92807e0d33007f8a42b1783fd1a114cef3c898623128b68`) foi commitada em `279a9a4`, em 08/11/2026 às 18:59:38 (−03:00), antes de qualquer execução com embedding ou reranker. O `dev` confere o sha256 e o commit antes de rodar e grava os dois no resultado.
- O código foi commitado em `4d5c1a7`, em 09/11/2026 às 06:27:38, antes da 1ª execução do desenvolvimento (06:37:36).
- Insumos: os 13 sha256 da seção 11 conferem (registrado em `resultados_fluxo_dev.json`).
- Os commits seguintes, todos em 09/11/2026:
  - `744432e`, às 21:19:00: desenvolvimento, escolha e a 1ª execução arquivada;
  - `8d9d30f`, às 21:30:39: teste;
  - um último com este README.

### Desenvolvimento (14 consultas nas regras, 15 no manual)

Execução válida: 09/11/2026, das 20:18:37 às 21:12:18 (53,7 min), as 28 configurações do zero, embedding e reranker em CPU. Carregamento, fora do teto: embedding 24,0 s, reranker de 512 10,1 s, reranker de 2048 8,9 s. Houve uma execução anterior, descartada (ver "Desvios").

**Regras (Entrega 2, `com_pontos`)**

| configuração | situação | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência máx. (s) |
|---|---|---|---|---|---|---|---|
| vetor, sem reranker | medida | 0,29 | 0,50 | 0,50 | 0,50 | 0,390 | 0,98 |
| **híbrido, sem reranker** | medida | 0,43 | 0,71 | 0,86 | 0,93 | 0,606 | 0,61 |
| vetor, N = 5, 512 | medida | 0,50 | 0,50 | 0,50 | 0,50 | 0,521 | 15,14 |
| vetor, N = 5, 2048 | medida | 0,50 | 0,50 | 0,50 | 0,50 | 0,521 | 17,64 |
| híbrido, N = 5, 512 | excluída (`sint_regra_grande_regioes`, 14ª consulta: 22,8 s) | – | – | – | – | – | – |
| híbrido, N = 5, 2048 | excluída (`sint_televendas_x_campo`, 10ª: 22,2 s) | – | – | – | – | – | – |
| vetor, N = 10, 2048 | excluída (`sint_ramos_12_19`, 4ª: 24,8 s) | – | – | – | – | – | – |
| híbrido, N = 10, 2048 | excluída (`img_infinitto`, 1ª: 25,1 s) | – | – | – | – | – | – |
| vetor / híbrido, N = 10, 512 | excluídas (`img_infinitto`, 1ª: 34,7 s / 43,2 s) | – | – | – | – | – | – |
| vetor / híbrido, N = 20, 2048 | excluídas (`img_infinitto`, 1ª: 35,2 s / 42,3 s) | – | – | – | – | – | – |
| vetor / híbrido, N = 20, 512 | excluídas (`img_infinitto`, 1ª: 66,6 s / 68,4 s) | – | – | – | – | – | – |
| vetor / híbrido, N = 50, 2048 | excluídas (`img_infinitto`, 1ª: 96,0 s / 94,3 s) | – | – | – | – | – | – |
| vetor / híbrido, N = 50, 512 | excluídas (`img_infinitto`, 1ª: 111,7 s / 115,3 s) | – | – | – | – | – | – |

**Manual (Entrega 3, estratégia C; reranker só com `max_length` 2048)**

| configuração | situação | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência máx. (s) |
|---|---|---|---|---|---|---|---|
| vetor, sem reranker | medida | 0,53 | 0,80 | 0,93 | 1,00 | 0,693 | 0,32 |
| híbrido, sem reranker | medida | 0,40 | 0,87 | 0,93 | 1,00 | 0,637 | 0,35 |
| **vetor, N = 5** | medida | 0,73 | 0,93 | 0,93 | 1,00 | 0,833 | 9,79 |
| híbrido, N = 5 | medida | 0,73 | 0,87 | 0,93 | 1,00 | 0,804 | 12,40 |
| vetor, N = 10 | excluída (`mdev_08`: 23,8 s) | – | – | – | – | – | – |
| híbrido, N = 10 | excluída (`mdev_02`: 20,0 s, acima do teto por fração de segundo) | – | – | – | – | – | – |
| vetor / híbrido, N = 20 | excluídas (`mdev_01`: 31,2 s / 29,7 s) | – | – | – | – | – | – |
| vetor / híbrido, N = 50 | excluídas (`mdev_01`: 63,3 s / 61,8 s) | – | – | – | – | – | – |

O que a tabela mostra:
- **Medidas:** 8 de 28 configurações; 20 foram excluídas por latência. Toda configuração com N ≥ 10 foi excluída. Com N = 5, só caíram as de fase 1 híbrida nas regras.
- **Sem reranker, reprodução exata:** os números repetem as Entregas 2 e 3 (posições até 10 idênticas).
- **Regras, vetor com N = 5:** o reranker sobe o hit@1 de 0,29 para 0,50, mas não o hit@3 (0,50). Com 5 candidatos ele só reordena o top-5 do vetor, cujo hit@5 é 0,50.
- **Manual, vetor com N = 5:** o reranker sobe o hit@1 de 0,53 para 0,73 e o MRR de 0,693 para 0,833.

### Dupla escolhida

Aplicada a seção 6 (`python avaliar_fluxo.py escolher`, 09/11/2026 21:16:07): **regras `híbrido, sem reranker` + manual `vetor + reranker, N = 5, max_length 2048`**. 12 das 180 duplas cabem no teto. **Decidida por: soma dos hit@3** (a 2ª colocada perde já no 1º critério). Conferida por um cálculo independente da mesma regra, feito do zero a partir dos checkpoints: mesma dupla, mesmas 5 melhores, mesmo critério.

| # | regras | manual | soma hit@3 | soma MRR | latência da dupla (s) |
|---|---|---|---|---|---|
| **1** | **híbrido, sem reranker** | **vetor, N = 5** | **1,648** (173/105) | **1,439** | **10,40** (0,61 + 9,79) |
| 2 | híbrido, sem reranker | híbrido, N = 5 | 1,581 | 1,410 | 13,01 |
| 3 | híbrido, sem reranker | híbrido, sem reranker | 1,581 | 1,243 | 0,96 |
| 4 | híbrido, sem reranker | vetor, sem reranker | 1,514 | 1,299 | 0,93 |
| 5 | vetor, sem reranker | vetor, N = 5 | 1,433 | 1,223 | 10,77 |

### Teste (20 consultas em cada índice; rodou uma vez; só relata)

| índice | configuração | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência mediana / máx. (s) |
|---|---|---|---|---|---|---|---|
| regras | híbrido, sem reranker | 0,50 | 0,75 | 0,80 | 0,90 | 0,640 | 0,32 / 0,38 |
| manual | vetor, N = 5, 2048 | 0,70 | 0,80 | 0,85 | 0,90 | 0,771 | 7,14 / 10,86 |

- **Latência:** o pior caso de cada índice somado dá 11,24 s, abaixo do teto de 20 s. As consultas dos dois índices são diferentes, e o teto vale para a soma na mesma pergunta.
- **Regras, reprodução:** a linha é idêntica à de `com_pontos` + híbrido no teste da Entrega 2 (README da Entrega 2).
- **Comparação com os padrões anteriores (herdados; não decidem nada):**
  - regras: o padrão da Entrega 2, `com_pontos` + híbrido + rerank (50), teve no teste hit@3 0,85 e MRR 0,827;
  - manual: o padrão da Entrega 3, C + vetor + rerank (50), teve hit@3 0,75 e MRR 0,785.

  Os dois foram excluídos aqui pela latência.
- **Ordem escolha → teste:** `config_escolhida.json` foi gravado às 21:16:07 e commitado às 21:19:00 (`744432e`); o teste gravou o resultado às 21:21:48. O teste grava o sha256 da configuração que usou (`b6cf2f6c…`), que confere com o arquivo commitado.
- **Carregamento no teste, fora do teto:** embedding 43,3 s, reranker 5,5 s.

### Demonstração do fluxo

`python fluxo.py --sessao --responder --so-fontes`, em 09/11/2026: modelos e índices carregados em 23 s, uma vez para a sessão inteira.

| pergunta | busca: regras + manual | contexto | regras (nota do RRF) | manual (nota do reranker) | Gemini (`gemini-3.8-flash`) |
|---|---|---|---|---|---|
| como bloquear vendas para clientes com títulos vencidos há mais de 30 dias? | 0,22 + 6,88 = 7,10 s | 3.308 tokens | 143, 162, 175 (0,029 a 0,026) | seção 4.3.1, p. 9; seção 4.3.4, p. 12; seção 9.1.1, p. 56 (0,007 a 0,004) | "Não encontrei nos documentos." 4.503 tokens (entrada 3.860, saída 6, raciocínio 637); 29,1 s |
| como escrever uma condição com E e OU em GOBR? | 0,18 + 6,57 = 6,75 s | 3.697 tokens | 206, 229, 153 (0,032 a 0,031) | capítulo 10 (abertura), p. 57–58 (0,132); seção 1.3, p. 2 (0,073); capítulo 7 (abertura), p. 38 (0,008) | resposta não registrada |
| como agendar ligações a cada 14 dias para clientes ativos e não agendar os inadimplentes? | 0,26 + 8,45 = 8,71 s | 2.190 tokens | 138, regra_050, 129 (0,031 a 0,029) | seção 7.3.4, p. 40 (0,216); seção 8.2, p. 48–49 (0,062); seção 6.4, p. 25–26 (0,025) | resposta abaixo; 3.523 tokens (entrada 2.561, saída 258, raciocínio 704); 133,3 s |

Resposta à 3ª pergunta, como saiu na tela:

````text
Com base nas regras de exemplo e no manual, os blocos de parametrização são avaliados em ordem. Para atender a essa necessidade, define-se primeiro o bloqueio dos clientes inadimplentes e, em seguida, a frequência para os clientes ativos:

1. **Bloquear inadimplentes:** utiliza-se o filtro `quando inadimplentes` com a ação `nao agendar`.
2. **Definir frequência para ativos:** utiliza-se o filtro `quando ativos para o vendedor` com a instrução `frequencia de 14 dias`.

Exemplo de estrutura em GOBR:

```gobr
version 1.0

time "todos":
    vendedores todos ativados

parametros "Não agendar inadimplentes":
    do time("todos")
    quando inadimplentes
    nao agendar

parametros "Freq. de 14 dias para clientes ativos":
    do time("todos")
    quando ativos para o vendedor
    frequencia de 14 dias
```

*(Nota: O manual destaca que `nao agendar` é uma parametrização exclusiva, não podendo ser combinada com definição de frequência na mesma regra).*
````

O que a demonstração mostra:
- **Busca dentro do teto:** a busca ficou entre 6,8 e 8,7 s por pergunta. A chamada ao Gemini fica fora do teto, que vale só para a busca, e levou 29 s e 133 s.
- **1ª pergunta, fora do domínio:** as regras do Govendas tratam de agendar ligações e visitas, não de bloquear vendas por título vencido. A resposta "Não encontrei nos documentos." é a que o prompt manda dar quando o contexto não traz a resposta.
- **3ª pergunta, do domínio:** a resposta propõe uma regra GOBR completa. Ela não foi validada (não passou pelo parser da Entrega 1 nem por um especialista): gerar e validar a parametrização é o escopo da Entrega 5.
- **Aviso do SDK:** `Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.` aparece porque as duas variáveis estavam definidas. A chamada usou `GOOGLE_API_KEY`.

## Ajustes feitos olhando resultado

1. **O desenvolvimento foi refeito do zero depois de ver os tempos da 1ª execução.** Não mudou código, regra, grade, consulta nem teto. O motivo, o critério e o efeito estão em "Desvios". A repetição mudou a escolha do manual.
2. **Depois do teste, nada foi ajustado.** O defeito de exibição visto na demonstração não foi corrigido (ver "Desvios").

## Desvios e extras declarados

- **Ordem de execução (seção 5 da regra):** a regra manda executar "por índice"; o código executa por fase de `max_length` (sem reranker, depois 512, depois 2048), regras e manual dentro de cada fase. Motivo: manter um só reranker na memória e carregar cada um uma vez. A própria seção 5 diz que a ordem só afeta o tempo de execução; as configurações, as consultas e as medidas são as mesmas.
- **1ª execução do desenvolvimento descartada** (09/11/2026, 06:37:36 a 19:00:53; guardada inteira em `dev_1a_execucao/`, 31 arquivos conferidos por sha256 ao mover):
  - O computador foi suspenso (tampa fechada) de ≈ 07:03 a ≈ 18:43, no meio da configuração `regras_vetor_N10_L2048`. A execução ativa somou ≈ 42 min de 12 h 23 min de relógio; o instante exato da suspensão não ficou registrado. A seção 5 pede o computador acordado e sem outras tarefas, e a poda exclui uma configuração com uma única medição.
  - Resultado: 5 de 28 medidas e 23 excluídas, várias com tempos incoerentes. Exemplo: `manual_vetor_N5_L2048` foi excluída com 20,4 s na 1ª consulta, medidos depois de o computador acordar, e na execução válida o máximo dela foi 9,8 s.
  - Um teste auxiliar, sem modelo, rodou numa máquina virtual no mesmo computador das 06:40:24 às 06:40:42, nos primeiros segundos da fase de 512.
  - **Decisão** (≈ 19:20): repetir as 28 configurações do zero, em condições controladas: na tomada, sem suspensão, sem outros programas, OneDrive pausado.
    - O critério foi repetir tudo, sem escolha caso a caso.
    - A decisão foi tomada pelos tempos, antes de aplicar a regra de escolha à 1ª execução.
    - Ruído de máquina só aumenta tempo, então ele só consegue excluir uma configuração indevidamente, nunca incluir (raciocínio próprio; **não encontrei no material**).
  - **Determinismo:** as 5 configurações medidas nas duas execuções têm as mesmas posições em todas as consultas.
  - **Efeito, calculado depois do teste, só para registro:** na 1ª execução a regra teria escolhido regras `híbrido, sem reranker` + manual `híbrido, sem reranker` (6 duplas viáveis). A repetição trocou o manual por `vetor + reranker, N = 5`, que na 1ª execução tinha sido excluída com 20,4 s, medidos depois de o computador acordar.
  - A seção 8 da regra manda declarar aqui qualquer mudança; a regra não foi reescrita.
- **Commit da escolha com o teste já rodando:**
  - O procedimento combinado (não a regra) era commitar `config_escolhida.json` antes de começar o teste.
  - O teste começou logo depois do `escolher` (21:16). O commit do desenvolvimento e da escolha (`744432e`) saiu às 21:19:00, com o teste em andamento e antes de ele gravar o resultado (21:21:48). O resultado do teste foi commitado em `8d9d30f`, às 21:30:39.
  - A ordem fica provada pelo commit, pelo sha256 da configuração gravado no resultado do teste (igual ao do arquivo commitado) e pelos horários.
  - A seção 7 (teste só depois de `config_escolhida.json` existir, só com a dupla escolhida, uma vez) foi cumprida, e o código a impõe.
  - Os comandos do git rodaram durante a medição do teste; a latência do teste só é relatada.
- **`--sem-git` e `--aceitar-insumos`** (em `dev` e `tudo`): não estão na regra e não foram usados. O JSON do desenvolvimento traz o commit da regra e todos os insumos conferindo. Existem para o caso de o git não poder ser lido ou de um insumo divergir; sem elas o `dev` não roda com a regra fora de commit ou com insumo diferente do registrado.
- **"Decidida por":** o relatório da escolha diz o primeiro critério em que a dupla escolhida difere da segunda colocada. É só relato; a escolha segue a seção 6.
- **Defeito de exibição:** com `--responder`, a linha `Contexto:` diz `tokens de LLM: 0 (sem --responder)`, porque é impressa antes da chamada ao Gemini. Os tokens reais estão na linha `Tokens da API`, logo abaixo da resposta. Não corrigido, para não mexer no código depois do teste.

## Lacunas e limites

- **O que ficou de fora:** entrada por imagem (o fluxo recebe texto), agente e grafo, escolha de em qual índice buscar (a mesma pergunta vai aos dois), geração da regra GOBR, memória de contexto e avaliação da resposta do Gemini. O pré-registro (seção 2) deixa o agente, o grafo e o roteamento para a Entrega 5; a geração da regra e a memória correspondem aos títulos das Entregas 5 ("Fluxo agêntico para gerar uma parametrização") e 6 ("Agente com memória de contexto").
- **A latência pesou mais que o acerto nas regras:**
  - Com o teto de 20 s neste computador (CPU), o reranker só coube com N = 5, e nas regras nenhuma configuração com reranker ficou à frente do híbrido sem reranker.
  - O padrão da Entrega 2 (híbrido + rerank com 50 candidatos) acerta mais no teste (hit@3 0,85 contra 0,75), mas não cabe no teto aqui.
  - Em GPU, ou com um reranker menor, o resultado pode mudar. Não testado.
- **`max_length` 512 mais lento que 2048 com N ≥ 10, nas duas execuções:**
  - Exemplo: vetor, N = 20, na `img_infinitto`: 66,6 s com 512 contra 35,2 s com 2048. Com N = 5 a ordem é a esperada (15,1 s contra 17,6 s).
  - O código é o mesmo `CrossEncoder` da Entrega 2; só muda o `max_length`.
  - Durante a 1ª execução isso foi atribuído a contaminação do ambiente. A execução controlada repetiu o padrão, então essa atribuição estava errada. A causa não foi investigada.
- **Ruído de latência e poda por uma medição:**
  - A mesma configuração (`regras_vetor_N5_L2048`) teve máximo de 14,3 s numa execução e 17,6 s na outra.
  - Configurações perto do teto, como `manual_hibrido_N10_L2048` (excluída com 20,0 s), podem cair de um lado ou do outro. A poda da seção 5 decide com uma única medição.
- **Qualidade da resposta do Gemini não é medida:** não há gabarito para ela. Com `--responder` só se relatam os tokens e o tempo da chamada.
- **Conjuntos pequenos:** 14 e 15 consultas no desenvolvimento (uma consulta vale 7,1 e 6,7 pontos percentuais de hit@3), 20 no teste. Empates são prováveis e a margem entre configurações é fina. **Não encontrei no material** critério de significância.
- **Conjuntos já usados:** os de desenvolvimento escolheram os padrões das Entregas 2 e 3, e os de teste já foram vistos com 50 candidatos; o relatório de teste desta entrega não é virgem. A regra não usa nenhum número de teste.
- **Consultas escritas pela mesma autoria dos índices:** favorecem a busca por palavras (declarado nas Entregas 2 e 3).
- **Pergunta única para os dois índices:** cada índice foi avaliado com perguntas do tipo dele; o fluxo manda a mesma pergunta aos dois e a qualidade com a pergunta "do tipo errado" não foi medida. Na 1ª pergunta da demonstração, as notas baixas do reranker no manual (0,004 a 0,007) mostram esse caso.
- **Latência é local:** vale para o computador e as condições do dia; o pior caso do desenvolvimento não é garantia para perguntas novas.
- **Carregamento fora do teto:** o teto vale por pergunta com modelos e índices já carregados. `python fluxo.py "pergunta"` (execução única) carrega tudo a cada chamada (23 a 45 s neste computador), e a espera real é maior que 20 s; o modo `--sessao` é o que o teto descreve.
- **Contexto sem corte:** a regra entra inteira (decisão herdada das Entregas 1 e 2). O GOBR de uma regra chega a 22.311 caracteres (medido em 05/11/2026), então o contexto de um top-3 com regra grande pode ser bem maior que o típico. Sem teto de tamanho nesta entrega.
- **Tokens do contexto são aproximados:** no modo padrão são contados com o tokenizer do bge-m3. Só o `--responder` traz a contagem real da API.
- **Variante e estratégia:** `com_pontos` e a estratégia C foram escolhidas com 50 candidatos e não foram reavaliadas com N pequeno.
- **Pesos iguais na dupla:** uma pergunta pode precisar só de um dos índices.
- **Testes sem modelo não medem qualidade de busca:** conferem o encanamento (grade, cronômetro, poda, escolha, contexto, chamada ao Gemini com cliente falso).

## Reaproveitamento das Entregas 1, 2 e 3 (sem alteração)

Nenhum arquivo de `entrega1\`, `entrega2\` ou `entrega3\` foi alterado: o reuso é só por `import`. O `git status` dessas pastas está limpo, e os `__pycache__` que existem nelas são de antes desta entrega (o mais recente é de 03/11/2026).

- **Entrega 2** (`comum.py`, `avaliar.py`): `Reranker`, `buscar_regras`, `carregar_indice`, `criar_embedding`, `criar_reranker`, `criar_contador_tokens`, `MODELO_RERANKER` e `RERANKER_MAX_LENGTH` (de `comum.py`); `metricas`, `posicao_da_primeira_relevante`, `carregar_consultas` e `CONJUNTOS` (de `avaliar.py`). O reranker de `max_length` 512 é um `CrossEncoder` do mesmo modelo, construído em `comum_fluxo.py` do mesmo jeito que o `criar_reranker` da Entrega 2 e embrulhado na classe `Reranker` dela. Os índices e os conjuntos de consultas são os da Entrega 2.
- **Entrega 3** (`comum_manual.py`): `buscar`, `acerta`, `carregar_indice` e `carregar_consultas`; os testes também leem `ESTRATEGIA_PADRAO`, `RERANK_PADRAO` e `HIBRIDO_PADRAO` para provar que não mudaram.
- **Entrega 1:** só o nome do modelo padrão do Gemini (`gemini-3.8-flash`, de `gerar_explicacoes.py`) e o modo de criar o cliente (`google-genai`, chave em `GEMINI_API_KEY` ou `GOOGLE_API_KEY`); nada é importado.
- **Insumos:** a seção 11 de `regra_escolha_fluxo.md` registra o sha256 dos índices, dos 4 conjuntos de consultas e de `comum.py`, `avaliar.py` e `comum_manual.py`; `python avaliar_fluxo.py insumos` confere, e o `dev` não roda se algum diferir.
