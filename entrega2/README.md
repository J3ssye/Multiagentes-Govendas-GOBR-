# Entrega 2 — Indexação das explicações

Pega as 199 explicações geradas na Entrega 1, transforma cada regra em um nó (texto + metadados), calcula os embeddings com o **bge-m3 local** e grava o índice em disco. A busca devolve as regras mais parecidas com um pedido em linguagem natural, **com o código GOBR delas**, para servir de exemplo ao agente (Entregas 4 e 5).

## Como rodar (PowerShell, na pasta `trabalho\entrega2`)

```powershell
pip install -r requirements.txt

python teste_plumbing.py                  # opcional; não usa o bge-m3, roda em segundos
python indexar.py --variante ambas        # 1ª vez baixa o bge-m3 (~2 GB)
python avaliar.py --rerank --hibrido      # conjunto de DESENVOLVIMENTO: vetor, +rerank, híbrido, híbrido+rerank
python avaliar.py --conjunto teste --rerank --hibrido   # conjunto de TESTE (rodar uma vez, sem ajustar nada depois)
python buscar.py "ativos 14 dias, inativos 28 dias, prospects 7 dias" --mostrar-gobr [--hibrido] [--rerank]
```

Sem GPU funciona, só demora mais (o `indexar.py` imprime o dispositivo e o tempo de embedding).

## Arquivos

| Arquivo | Papel |
|---|---|
| `comum.py` | Carrega as regras, monta o texto, divide se preciso, cria os nós, agrupa a busca |
| `indexar.py` | Gera e grava o índice (`indices/indice_<variante>/`) |
| `buscar.py` | Consulta o índice |
| `avaliar.py` | Mede se a regra certa volta entre as primeiras; compara vetor, re-ranking e híbrido |
| `consultas_avaliacao.json` | 14 consultas de **desenvolvimento** (usadas para tomar decisões) |
| `consultas_teste.json` | 20 consultas de **teste** (regras sorteadas, não usadas para decidir nada) |
| `teste_plumbing.py` | Testa o código sem o modelo (embedding de hash de palavras: **não mede qualidade**) |

## O que o índice guarda (DMAS §4.7.2, Listing 4.21: vetor + texto + metadados)

- **Texto embedado:** título + resumo + um segmento por linha (`- nome: critério -> ação`).
- **Metadados (não entram no vetor):** `regra_id`, `arquivo`, `titulo`, `parte`, `n_partes`, `tokens`, `n_blocos`, `origem`, `modelo`, `duplicatas`, `pontos_de_atencao`, `achados_automaticos`, **`gobr`**.

## Decisões

| Decisão | Alternativa descartada | Fonte / lacuna |
|---|---|---|
| **Um nó por regra.** Só divide se o texto passar do limite do modelo, e então **por segmento**, repetindo título e resumo em cada parte. A busca agrupa as partes e devolve a regra inteira. | `SentenceSplitter` com tamanho fixo e sobreposição | Enunciado, dica 4 (atenção à quebra dos chunks). **Não encontrei no AIMA nem no DMAS** discussão sobre tamanho ou sobreposição de chunk (a atividade de RAG da disciplina usa valores fixos, sem discuti-los: `SentenceSplitter` 512/64 na aula e 256/32 para manuais, Célula 7); "nunca devolver meia regra" é decisão de projeto. |
| **Indexar só as 199 regras únicas**; as cópias ficam em `duplicatas`. | Indexar os 249 arquivos | DMAS §4.7.3: indexar demais traz ruído. Na prática: `regra_001` absorveu 48 cópias; sem a deduplicação seriam 49 vetores idênticos dominando o top-k. |
| **O `gobr` vai como metadado** do nó. | Arquivo separado ligado por id | DMAS §4.7.2, Listing 4.21 (vetor, texto e metadados guardados juntos). |
| **Todo metadado fica fora do embedding** (`excluded_embed_metadata_keys`). | Padrão da biblioteca | Comportamento do LlamaIndex, **não está no material**. Sem isso o código GOBR inteiro viraria vetor. |
| **bge-m3 local**, o mesmo na indexação e na consulta; sem prefixo de instrução. | Embeddings do Gemini | Listing 4.21 usa um único encoder nas duas fases. O Gemini consumiria cota a cada consulta nas Entregas 4–6. |
| **Limite lido do modelo** (`embed_model.max_length`) e tokens contados com o tokenizer do bge-m3. | Número fixo no código | O `indexar.py` imprime quantas regras (se alguma) precisaram ser divididas. |
| **Sem checkpoint** por regra. | Checkpoint como na Entrega 1 | DMAS cap. 14 justifica checkpoint por limite de taxa e custo de API; aqui o modelo é local (sem cota, sem custo) e a gravação é atômica (pasta `.tmp` trocada no fim). |
| **Duas variantes:** `sem_pontos` e `com_pontos`. Padrão para as Entregas 4–6: `com_pontos` (ver "Ajustes feitos olhando resultado"); os scripts ainda usam `sem_pontos` como valor padrão de `--variante`. | Decidir no escuro | DMAS §4.7.3 alerta para ruído; se os pontos de atenção atrapalham é empírico, e o `avaliar.py` compara as duas. |
| **Re-ranking opcional** (`--rerank`): a busca vetorial traz 50 candidatos e o `bge-reranker-v2-m3` (cross-encoder) relê consulta + regra juntas e reordena. | Reindexar por segmento (adiado) | Atividade de RAG da disciplina, Células 8 e 10 (busca larga, depois cross-encoder reordena). **Não encontrei re-ranking no AIMA nem no DMAS.** Usamos o `CrossEncoder` direto, com `max_length=2048`, porque o `SentenceTransformerRerank` do LlamaIndex fixa 512 tokens e cortaria as regras maiores. |
| **Busca híbrida opcional** (`--hibrido`): ranking vetorial e ranking BM25 (palavras e números exatos) fundidos por RRF; pode vir antes do re-ranking. | Só vetor | Motivo: números como "14" x "28" pesam pouco no embedding. BM25, RRF (k=60) e os parâmetros k1=1,5/b=0,75 são valores usuais da literatura; **não encontrei no material**. Implementação própria em `comum.py`. |
| **Métricas hit@k e MRR** sobre o ranking de regras. | NDCG | DMAS §10.4.4: preferir métrica determinística quando há gabarito. O §10.4.1 cita o NDCG sem defini-lo (**lacuna**). hit@k e MRR são definição própria (abaixo). |

**Métricas.** `hit@k` = fração das consultas cuja regra certa está entre as k primeiras. `MRR` = média de 1/posição da regra certa.

## Como a avaliação é organizada

Dois conjuntos de consultas, com papéis diferentes:

- **Desenvolvimento** (`consultas_avaliacao.json`, 14 consultas: 3 descritas a partir das imagens de exemplo e 11 escritas por mim a partir de regras escolhidas). Serve para tomar decisões: variante, nº de candidatos (50), uso de re-ranking e de busca híbrida. A consulta `sint_quinzenal_mensal` foi corrigida de "15" para "14 dias" por inconsistência com o gabarito, após a primeira rodada.
- **Teste** (`consultas_teste.json`, 20 consultas): regras **sorteadas** (`random.seed(20261027)`) entre as 185 de `referencias/` que não estão no desenvolvimento; consultas escritas a partir da explicação de cada regra **antes de rodar qualquer busca**. Nada foi ajustado olhando esse conjunto. Configurações avaliadas (fixadas antes): vetor; vetor + rerank (50); híbrido; híbrido + rerank (50), sempre `sem_pontos`, bge-m3 e bge-reranker-v2-m3. **Desvio declarado (ver "Ajustes feitos olhando resultado"):** o teste passou a rodar as duas variantes, não só `sem_pontos`.

**Regra de escolha do padrão:** vale a configuração de maior MRR no **desenvolvimento**. O teste só relata; não escolhe. (Desvio declarado: a regra passou a valer para as 8 combinações de variante e configuração, não só para as 4 configurações de `sem_pontos`; ver "Ajustes feitos olhando resultado".)

## Resultados

Indexação: 199 regras -> 199 nós; nenhuma dividida (maior: 3.918 tokens, limite 8.192).

### Desenvolvimento (14 consultas)

Resultados completos, rodada de 28/10 (`python avaliar.py --rerank --hibrido`); saída por consulta, top-3 e comparações em `resultados_avaliacao_rerank_hibrido.md`:

| variante | configuração | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| `sem_pontos` | vetor | 0,36 | 0,50 | 0,50 | 0,50 | 0,452 |
| `sem_pontos` | vetor + rerank(50) | 0,50 | 0,71 | 0,71 | 0,86 | 0,633 |
| `sem_pontos` | híbrido (vetor+BM25) | 0,36 | 0,86 | 0,86 | 0,93 | 0,589 |
| `sem_pontos` | híbrido + rerank(50) | 0,57 | 0,79 | 0,79 | 0,93 | 0,699 |
| `com_pontos` | vetor | 0,29 | 0,50 | 0,50 | 0,50 | 0,390 |
| `com_pontos` | vetor + rerank(50) | 0,57 | 0,86 | 0,86 | 0,86 | 0,697 |
| `com_pontos` | híbrido (vetor+BM25) | 0,43 | 0,71 | 0,86 | 0,93 | 0,606 |
| `com_pontos` | híbrido + rerank(50) | 0,64 | 0,93 | 0,93 | 0,93 | **0,766** |

Maior MRR entre as 8 combinações: `com_pontos` + híbrido + rerank (50). Dentro de `sem_pontos`: híbrido + rerank (50). O padrão adotado e o desvio que isso representa estão em "Ajustes feitos olhando resultado".

Variantes do texto indexado: só com o vetor, `com_pontos` fica abaixo de `sem_pontos` (MRR 0,390 contra 0,452), e foi essa comparação isolada que fixou `sem_pontos` no README original. Com re-ranking ou híbrido a ordem se inverte.

Consultas de imagem, só vetor: posições 40, 29 e 14; com re-ranking: 15, 6 e 9.

### Teste (20 consultas)

Rodada de 02/11 (`python avaliar.py --conjunto teste --rerank --hibrido`, as duas variantes; terminou às 22:59). Saída por consulta, top-3 e comparações em `resultados_teste_rerank_hibrido.md`:

| variante | configuração | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| `sem_pontos` | vetor | 0,25 | 0,50 | 0,55 | 0,60 | 0,399 |
| `sem_pontos` | vetor + rerank(50) | 0,75 | 0,95 | 0,95 | 0,95 | 0,844 |
| `sem_pontos` | híbrido (vetor+BM25) | 0,45 | 0,75 | 0,80 | 0,90 | 0,615 |
| `sem_pontos` | híbrido + rerank(50) | 0,75 | 0,95 | 0,95 | 0,95 | 0,844 |
| `com_pontos` | vetor | 0,20 | 0,40 | 0,50 | 0,60 | 0,348 |
| `com_pontos` | vetor + rerank(50) | 0,75 | 0,85 | 0,95 | 0,95 | 0,829 |
| `com_pontos` | híbrido (vetor+BM25) | 0,50 | 0,75 | 0,80 | 0,90 | 0,640 |
| `com_pontos` | híbrido + rerank(50) | 0,75 | 0,85 | 0,95 | 0,95 | 0,827 |

O teste só relata. O padrão escolhido no desenvolvimento, `com_pontos` + híbrido + rerank (50), teve MRR 0,827 no teste. As melhores linhas do teste (`sem_pontos` + vetor + rerank(50) e `sem_pontos` + híbrido + rerank(50), MRR 0,844) ficam 0,017 acima: com 20 consultas, isso é cerca de 0,34 de soma de rank recíproco, menos do que uma única consulta caindo do 1º para o 2º lugar (0,5). O padrão não muda: a regra fixada decide no desenvolvimento.

### Ajustes feitos olhando resultado

1. **Variante padrão trocada de `sem_pontos` para `com_pontos` (desvio do protocolo).** O README original fixava `sem_pontos` comparando as variantes só no vetor (MRR 0,452 contra 0,390). A tabela completa do desenvolvimento inverte essa ordem nas outras três configurações: `com_pontos` fica à frente por +0,064 (vetor + rerank), +0,017 (híbrido) e +0,067 (híbrido + rerank) de MRR. A variante é um hiperparâmetro do índice e deve ser escolhida junto com a recuperação, não isolada numa configuração. Origem: AIMA cap. 19, parágrafos que antecedem o §19.4.1 (o conjunto de validação/desenvolvimento serve para avaliar os candidatos e escolher o melhor; o teste fica trancado até o fim dos experimentos). Aplicada a regra de escolha ("maior MRR no desenvolvimento") às 8 combinações, o padrão passa a ser **`com_pontos` + híbrido + rerank (50)** (tabela acima). A decisão se apoia só nos números do desenvolvimento.
   - *Ressalva de tamanho:* com 14 consultas, 0,067 de MRR equivale a cerca de 0,94 de soma de rank recíproco, o que duas consultas passando do 2º para o 1º lugar já produzem. A diferença é pequena; a troca segue a regra fixada e não prova que `com_pontos` seja melhor. **Não encontrei no material** critério de tamanho de amostra ou de significância para MRR (busca no projeto; a Tabela 10.1 do DMAS, §10.2.1, apenas formula a pergunta "quantos casos dão sinal confiável?").
2. **Teste nas duas variantes.** `consultas_teste.json` (sha256 `a91c9ff3…`, igual ao do commit `e090c52`) passa a ser rodado sem `--variante`, isto é, nas duas variantes, e só relata; a escolha do padrão não usa o teste.
3. **Código não alterado.** `buscar.py` e `indexar.py` continuam com `sem_pontos` como valor padrão de `--variante`. Para usar o novo padrão: `--variante com_pontos --hibrido --rerank`. As Entregas 4–6 devem passar a variante explicitamente.

## Limites conhecidos

- Todas as consultas (desenvolvimento e teste) foram escritas por mim a partir do texto das regras, então repetem o vocabulário delas. Isso **favorece a busca por palavras (BM25)** frente ao que um usuário real digitaria. O resultado vale como comparação entre configurações, não como estimativa de desempenho com usuários reais.
- O gabarito é o id exato da regra. O corpus tem regras quase iguais (ex.: `regra_043` é só "todos a cada 14 dias"); nesses casos o id exato pode ser inatingível, e isso entra na conta.
- 14 e 20 consultas são poucas: cada uma vale 7 e 5 pontos percentuais.
- O corpus tem muitas regras parecidas. Quando a regra "errada" que volta em 1º é da mesma família, isso pode ser aceitável; por isso o `avaliar.py` mostra o top-3 de cada consulta para leitura qualitativa.
- Dois blocos que as imagens mostram e o `.gobr` não têm (capacidade de 35 clientes/dia da Maxlub; "Agendar inadimplentes" da V1 Vidros) continuam sem bloco correspondente; vêm da Entrega 1.
- O índice guarda o texto da Entrega 1 como está (3 modelos Gemini diferentes; 115 filtros com tradução "(aprox.)").
- No `avaliar.py`, as tabelas de comparação "vetor x híbrido" e "vetor x híbrido + rerank" usam o cabeçalho fixo "vetor + rerank" e a nota "Teto do re-ranking" (função `comparar`); a coluna mostra a configuração do título da seção. É só rótulo: o resumo com hit@k e MRR sai de `resumo_configs`, não de `comparar`.
