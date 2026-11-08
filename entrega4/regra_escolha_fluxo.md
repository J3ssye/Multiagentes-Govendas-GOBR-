# Regra de escolha da configuração do fluxo — Entrega 4

**Status:** pré-registro. Gravada em 07/11/2026, antes de qualquer execução de embedding ou de reranker no desenvolvimento desta entrega. A prova da data é o commit deste arquivo, feito pela aluna.

**Enunciado.** A única definição da Entrega 4 é o título "Construção de um fluxo básico de busca - RAG", informado pela aluna em 07/11/2026. Ele não fixa saída, métrica, teto de latência nem desempate. Os itens 2 e 3 da seção 2 são decisões dela de 07/11/2026. O resto é proposta, marcada com "não encontrei no material", e passa a valer quando este arquivo for commitado.

## 1. O que a regra decide

Uma **dupla** de configurações de busca para o fluxo interativo: uma para o índice de regras (Entrega 2) e uma para o índice do manual (Entrega 3). O desenvolvimento escolhe. O teste só relata.

Uma configuração combina:

- **fase 1:** `vetor` ou `hibrido` (vetor + BM25 por RRF, como na Entrega 2);
- **N:** quantos candidatos o reranker relê (`0` = sem reranker);
- **`max_length`** do reranker (só no índice de regras; no manual fica o da Entrega 2, 2048).

Fase 1, N e `max_length` são botões do pipeline de busca (hiperparâmetros). Quem os escolhe é o desenvolvimento, e o teste fica trancado até o fim: AIMA cap. 19, parágrafos que antecedem o §19.4.1 (o conjunto de validação/desenvolvimento avalia os candidatos e escolhe o melhor; o teste é a avaliação final). O AIMA trata de modelos aprendidos; aplicar isso a um pipeline de busca é analogia, e **não encontrei no material** uma passagem sobre pipelines de busca.

## 2. Já decidido (esta regra não reabre)

1. **Fluxo** (proposta apresentada a ela em 07/11/2026): workflow determinístico em Python: busca nas regras, busca no manual, montagem do contexto, resposta opcional. Sem agente, sem LangGraph, sem imagem. Origem: DMAS §2.2.1 e cap. 11 (Tabela 11.1: passos fixos e conhecidos pedem workflow sequencial; o anti-padrão que antecede o §11.3.7 dá de 3 a 5 vezes mais custo à orquestração por IA numa tarefa linear). O agente e o grafo ficam para a Entrega 5.
2. **Saída** (decisão dela, 07/11/2026, opção "Os dois; Gemini opcional"): por padrão, o contexto, isto é, 3 regras com o GOBR completo e 3 trechos do manual com seção e páginas, sem chamada de LLM (0 token). Com `--responder`, uma chamada ao Gemini com esse contexto. A resposta do Gemini não entra nesta regra (não há gabarito para ela); os tokens dela são relatados (DMAS §10.5.1 lista tokens e chamadas de API como métrica de eficiência de recursos).
3. **Teto de latência** (decisão dela, 07/11/2026): 20 s por pergunta para a busca nas regras e no manual somadas, no computador dela. O número: **não encontrei no material** (o DMAS §3.5 só diz que o uso interativo exige baixa latência).
4. **Índices** (herdados): `entrega2/indices/indice_com_pontos` (variante da Entrega 2, cujo README manda as Entregas 4 a 6 passá-la explicitamente) e `entrega3/indices/indice_manual_C` (estratégia C). Embedding `BAAI/bge-m3` e reranker `BAAI/bge-reranker-v2-m3`, os da Entrega 2. As constantes `ESTRATEGIA_PADRAO`, `RERANK_PADRAO` e `HIBRIDO_PADRAO` da Entrega 3 não mudam: a configuração interativa é nova e fica registrada à parte, em `config_escolhida.json`.
5. **k = 3** itens por índice, fixo (é o tamanho da saída do fluxo; proposta). Valor dos exemplos do material: atividade de RAG, Célula 8 (`top_n=3`); aula, `similarity_top_k=3`; DMAS Listing 4.21 (`top_k=3`). O material não justifica o valor: **não encontrei no material**.
6. **Reuso só por import.** Nenhum arquivo de `entrega1/`, `entrega2/` ou `entrega3/` é alterado.

## 3. Constantes

Os testes sem modelo leem o bloco desta seção e comparam com o código.

```
K = 3
TETO_S = 20.0
REPETICOES = 2
FASE1 = vetor, hibrido
N_CANDIDATOS = 5, 10, 20, 50
MAX_LENGTH_REGRAS = 512, 2048
MAX_LENGTH_MANUAL = 2048
CONSULTA_AQUECIMENTO = teste de aquecimento
```

## 4. Espaço de configurações

- **Regras (Entrega 2, `com_pontos`):** 2 fases 1 × (sem reranker + 4 valores de N × 2 de `max_length`) = 18 configurações.
- **Manual (Entrega 3, estratégia C):** 2 fases 1 × (sem reranker + 4 valores de N) = 10 configurações.
- **Valores de N:** 10 é o da atividade de RAG da disciplina (Célula 8: `similarity_top_k=10`, `top_n=3`); 50 é o da Entrega 2 e da Entrega 3; 5 e 20 completam a grade (escolha de engenharia; **não encontrei no material**). N = 3 não entra: com k = 3 o reranker só reordenaria os mesmos 3 itens e o hit@3 não mudaria.
- **`max_length` do reranker nas regras:** 2048 é o da Entrega 2; 512 é uma alternativa mais barata (escolha de engenharia; **não encontrei no material**). Motivo da dimensão: o custo do reranker cresce com o tamanho do texto e os nós de regras variam muito. Tokens do bge-m3 por nó no índice `com_pontos`, medidos em 07/11/2026: mediana 336, p90 711, máximo 4.136; 50 dos 199 nós (25%) passam de 512 tokens, 8 (4%) de 1.024 e 2 (1%) de 2.048. Nos trechos do manual o teto de 512 tokens da estratégia C já limita o tamanho (máximo 511, em `entrega3/indices/relatorio_manual_C.json`), então só o valor 2048 entra.
- **Referências herdadas:** as configurações padrão da Entrega 2 (híbrido + N 50 + `max_length` 2048) e da Entrega 3 (vetor + N 50 + `max_length` 2048) fazem parte da grade. A expectativa de que a latência as exclua vem de um custo medido no teste da Entrega 3 (herdado do handoff de 03/11: cerca de 1 s por par), que não decide nada aqui: a exclusão é medida no desenvolvimento desta entrega.
- A grade foi escrita sem nenhum resultado de busca desta entrega (não existe nenhum). Os resultados das Entregas 2 e 3 já eram conhecidos (ver seção 10).

## 5. Como medir

**Conjuntos.** Desenvolvimento: `entrega2/consultas_avaliacao.json` (14 consultas, regras) e `entrega3/consultas_manual_dev.json` (15 consultas, manual). Teste: `entrega2/consultas_teste.json` (20) e `entrega3/consultas_manual_teste.json` (20).

**Acerto.** O mesmo das Entregas 2 e 3, com as funções delas importadas.
- Regras: a regra de `relevantes` (id exato) aparece no ranking de regras, com as partes agrupadas por regra (`posicao_da_primeira_relevante`, Entrega 2).
- Manual: regra oficial da Entrega 3 (a folha principal do chunk está no gabarito), ranking de chunks sem agrupar. A regra de cobertura de 50% (sensibilidade, só relatório na Entrega 3) não entra.
- Métricas: hit@1, hit@3, hit@5, hit@10 e MRR (`metricas`, Entrega 2) sobre o ranking completo de cada consulta (k = None).

**Latência.**
- **Relógio:** `time.perf_counter()` em volta da chamada de busca (`buscar_regras`, Entrega 2; `buscar`, Entrega 3), com índices e modelos já carregados. Entram: embedding da consulta, fase 1, fusão e reranker. Ficam fora: carregar modelos e índices (uma vez por sessão; será medido e relatado à parte), a montagem do contexto e o Gemini.
- **Sem cache:** o reranker da medição não usa `RerankerComCache` (Entrega 3), porque o cache esconderia o custo. O de 2048 é o `criar_reranker()` da Entrega 2; o de 512 é um `CrossEncoder` do mesmo modelo com `max_length=512`, construído em `comum_fluxo.py` e embrulhado na classe `Reranker` da Entrega 2.
- **Aquecimento:** antes da primeira medição, uma chamada descartada por modelo carregado (inclusive cada `max_length`) e por índice, com `CONSULTA_AQUECIMENTO`, `hibrido=True` e N = 2 (monta o BM25 e aquece o reranker).
- **Repetições:** cada consulta é cronometrada `REPETICOES` vezes e vale a **menor** medida (descarta interferência do sistema). O acerto vem da 1ª repetição.
- **Latência de uma configuração** = a **maior** latência entre as consultas do desenvolvimento dela (pior caso).
- **Latência da dupla** = latência da configuração de regras + latência da configuração do manual (busca em sequência: cota superior da soma dos piores casos).
- **Poda:** se a 1ª medição de uma consulta passar de `TETO_S`, a configuração é encerrada como "excluída por latência" (grava a consulta e o tempo) e não se mede mais nada dela.
- **Ordem:** por índice, primeiro as configurações sem reranker, depois N crescente e `max_length` 512 antes de 2048. A ordem só afeta o tempo de execução.
- **Condições:** uma configuração por vez, sem outras tarefas pesadas no computador; registrar o dispositivo (CPU ou GPU) e a data e hora no resultado.
- **Interrupção** (queda de ponte, falta de memória): retoma-se pelas configurações ainda não gravadas, com a mesma grade. Cada configuração concluída é gravada por checkpoint e não se repete.

## 6. Regra de escolha

Entre as duplas (R, M) em que nenhuma das duas configurações foi excluída e `lat(R) + lat(M) ≤ TETO_S`:

1. maior `hit@3(R) + hit@3(M)` (de 0 a 2);
2. empate: maior `MRR(R) + MRR(M)`;
3. empate: menor `lat(R) + lat(M)`;
4. empate: configuração mais simples, comparando primeiro a de regras e depois a do manual, nesta ordem: sem reranker antes de com reranker; vetor antes de híbrido; menor N; `max_length` 512 antes de 2048.

As comparações dos passos 1 e 2 são exatas (frações, sem arredondar): os hit@3 são múltiplos de 1/14 e de 1/15.

Se nenhuma dupla couber no teto, o desenvolvimento termina sem escolha e isso é relatado. Mudar o teto depois de ver o desenvolvimento seria desvio, não ajuste.

A saída é `config_escolhida.json`, gravado com abertura exclusiva, com: a dupla, as métricas e latências do desenvolvimento, as 5 melhores duplas e o sha256 deste arquivo.

## 7. Uso do teste

Só depois de `config_escolhida.json` existir. Roda uma vez, só com a dupla escolhida. Relata, para cada índice, hit@1, hit@3, hit@5, hit@10 e MRR, e as latências por consulta (mediana e máximo). Esses números só são relatados; nenhum entra em decisão. Se a latência no teste passar do teto, relata-se. Depois de ver o teste, não se ajusta nada (teto, k, grade, dupla). Se a execução cair antes de terminar e nenhum resultado tiver sido visto, repete-se igual; depois de ver resultados, não se repete.

## 8. O que fica congelado a partir do commit

Tudo das seções 2 a 7. Qualquer mudança vira "desvio" declarado no README, com o motivo, e nunca reescreve esta regra.

## 9. Propostas que o material não cobre

| Escolha | Proposta | Origem |
|---|---|---|
| Valor do teto | 20 s por pergunta | decisão dela em 07/11/2026; **não encontrei no material** |
| Leitura do teto | pior caso entre as consultas do desenvolvimento, não a mediana | **não encontrei no material** |
| Soma das duas buscas | em sequência, cada uma no seu pior caso | **não encontrei no material** |
| Métrica principal | hit@3: o item certo está entre os 3 devolvidos | métrica determinística quando há gabarito, DMAS §10.4.4; usar hit@3 como critério de escolha: **não encontrei no material** |
| Dupla | soma dos hit@3 das duas buscas, pesos iguais | **não encontrei no material** |
| Desempates | MRR; depois menor latência; depois mais simples | **não encontrei no material** |
| Grade, repetições, menor medida, aquecimento, poda | seções 4 e 5 | **não encontrei no material** |
| k = 3 | seção 2, item 5 | exemplos do material sem justificativa; **não encontrei no material** |

## 10. Limitações deste pré-registro

- **Conjuntos pequenos:** 14 consultas de desenvolvimento nas regras e 15 no manual. Uma consulta vale 7,1 e 6,7 pontos percentuais de hit@3, os empates são prováveis e a margem entre configurações é fina. **Não encontrei no material** critério de significância.
- **Conjuntos já usados:** os dois conjuntos de desenvolvimento já escolheram os padrões das Entregas 2 e 3, e os dois de teste já foram vistos para as configurações com 50 candidatos. Esta regra não usa nenhum número de teste, mas o relatório de teste desta entrega não é virgem.
- **Consultas escritas pela mesma autoria dos índices:** favorecem a busca por palavras (declarado nas Entregas 2 e 3).
- **Pergunta única para os dois índices:** cada índice é avaliado com perguntas do tipo dele (descrição de regra de negócio nas regras; pergunta sobre a linguagem no manual), mas o fluxo manda a mesma pergunta aos dois. A qualidade com a pergunta "do tipo errado" não foi medida. Decidir quando buscar em qual índice (roteamento) fica para a Entrega 5.
- **Latência é local:** vale para o computador e as condições do dia. O pior caso do desenvolvimento não é garantia para perguntas novas nem para o teste.
- **Carregamento fora do teto:** o teto vale por pergunta com modelos e índices já carregados. `python fluxo.py "pergunta"` (execução única) carrega tudo a cada chamada, e a espera real dessa forma de uso é maior que 20 s; o modo de sessão (várias perguntas, carregamento uma vez) é o que o teto descreve.
- **Variante e estratégia:** `com_pontos` e a estratégia C foram escolhidas com 50 candidatos e não foram reavaliadas com N pequeno.
- **Pesos iguais:** na prática uma pergunta pode precisar só de um dos índices.
- **Contexto sem corte:** a regra entra inteira (decisão herdada das Entregas 1 e 2). O GOBR de uma regra chega a 22.311 caracteres (medido em 05/11/2026), então o contexto de um top-3 com regra grande pode ficar bem maior que o típico. Sem teto de tamanho nesta entrega.
- **Tokens aproximados:** no modo padrão (sem LLM) os tokens do contexto são contados com o tokenizer do bge-m3, não com o do Gemini. Só o `--responder` traz a contagem real da API.

## 11. Insumos (sha256 calculado em 07/11/2026, com HEAD em `e08c64f`)

| Arquivo | sha256 |
|---|---|
| `entrega2/indices/indice_com_pontos/default__vector_store.json` | `bf072e8dea1984fe6fc7dba874001c8b0f38bef055347e189bbc17b1d412c403` |
| `entrega2/indices/indice_com_pontos/docstore.json` | `6a53eb1f6cbb58eb897559282be3befd07967973ca8dc3b2dba19328b201657c` |
| `entrega2/indices/indice_com_pontos/index_store.json` | `0ed4e2005953345281606c1183e98697d49f2b64d7a9c516532e218ff6da9b84` |
| `entrega3/indices/indice_manual_C/default__vector_store.json` | `17814d70da582ec128ce677ea0cce18821ba8fefcb956c6f3a09f0f4f7a95417` |
| `entrega3/indices/indice_manual_C/docstore.json` | `0be5fbc3f264aaad22ef4d62aa05f3b5a446bfc64709d22c3ccd44524ad3566e` |
| `entrega3/indices/indice_manual_C/index_store.json` | `8fe24fd2ddf27df7bcecedc836822b911f40aae8037ff159d918259bb1c5db03` |
| `entrega2/consultas_avaliacao.json` (dev, regras) | `abcc8ee18798e9af0c8729d954f54624710831d0e39140a21bcc0af76fe5396d` |
| `entrega2/consultas_teste.json` (teste, regras) | `a91c9ff3726844396b29988317d0089f1447104deb96cd057cdc98a92184f646` |
| `entrega3/consultas_manual_dev.json` (dev, manual) | `2195ccd9076c25cf30bb28e9b9537999a073dfd2880c154dac2811d42885ea1a` |
| `entrega3/consultas_manual_teste.json` (teste, manual) | `e0f2c12a29e14da28323eaca2e6627b3b50fed51372766bcc0ced751f67f3350` |
| `entrega2/comum.py` | `769230dc050a3c2979eb4bbf003a15d658f085148b153731c63b333f3d67af9b` |
| `entrega2/avaliar.py` | `e37a8141c596cdde823fc1e645e8ccfcd7e00e1733ed2f3d5191ce5a58611372` |
| `entrega3/comum_manual.py` | `7a5d1bcec5b632b7157e06914406e9184b2db454288f56cf260de31d87d37ea4` |

O sha256 de `entrega2/consultas_teste.json` (`a91c9ff3…`) é o que o README da Entrega 2 registra.

## 12. Arquivos novos desta entrega

| Arquivo | Papel | Quando |
|---|---|---|
| `regra_escolha_fluxo.md` | esta regra (pré-registro) | agora |
| `comum_fluxo.py` | constantes da regra, grade de configurações, busca configurável, cronômetro, montagem do contexto, prompt do `--responder` (Célula 8 da atividade de RAG, adaptado) e `escolher` (a regra em código) | passo 5 |
| `fluxo.py` | o fluxo: `python fluxo.py "pergunta" [--responder]` e modo de sessão (modelos carregados uma vez, várias perguntas); `--responder` usa `google-genai` e `GEMINI_API_KEY`, como na Entrega 1 | passo 5 |
| `avaliar_fluxo.py` | `dev` (grade, acerto e latência, com checkpoint por configuração), `escolher` (aplica a regra) e `teste` (uma vez, só a dupla escolhida) | passo 5 |
| `teste_plumbing_fluxo.py` | testes sem modelo e sem rede, no estilo de `teste_plumbing_manual.py` | passo 5 |
| `requirements.txt` | dependências (as da Entrega 3 mais `google-genai`) | passo 5 |
| `dev_checkpoints/`, `resultados_fluxo_dev.md` e `.json`, `config_escolhida.json` | desenvolvimento e escolha | passo 6 |
| `resultados_fluxo_teste.md` e `.json` | teste, uma vez | passo 6 |
| `README.md` | no padrão do README da Entrega 3 | passo 7 |
