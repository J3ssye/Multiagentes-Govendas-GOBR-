# Avaliação da recuperação no manual (Entrega 3) - conjunto: teste (20 consultas)

Gerado em 03/11/2026 14:16. Ranking de chunks, sem agrupar; candidatos do reranker: 50.

## Resumo - regra oficial (a folha principal do chunk está no gabarito)

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 20 | 0.50 | 0.80 | 0.85 | 0.90 | 0.654 |
| C · vetor + rerank | 20 | 0.75 | 0.75 | 0.85 | 0.90 | 0.785 |
| C · híbrido | 20 | 0.70 | 0.90 | 0.90 | 0.95 | 0.784 |
| C · híbrido + rerank | 20 | 0.75 | 0.75 | 0.85 | 0.90 | 0.783 |
| B · vetor | 20 | 0.25 | 0.40 | 0.45 | 0.55 | 0.353 |
| B · vetor + rerank | 20 | 0.40 | 0.55 | 0.55 | 0.65 | 0.491 |
| B · híbrido | 20 | 0.30 | 0.60 | 0.60 | 0.65 | 0.440 |
| B · híbrido + rerank | 20 | 0.40 | 0.55 | 0.55 | 0.65 | 0.491 |

## Sensibilidade - acerta também o chunk com pelo menos 50% de uma folha do gabarito (só relata; não decide)

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 20 | 0.50 | 0.80 | 0.85 | 0.90 | 0.654 |
| C · vetor + rerank | 20 | 0.75 | 0.75 | 0.85 | 0.90 | 0.785 |
| C · híbrido | 20 | 0.70 | 0.90 | 0.90 | 0.95 | 0.784 |
| C · híbrido + rerank | 20 | 0.75 | 0.75 | 0.85 | 0.90 | 0.783 |
| B · vetor | 20 | 0.35 | 0.70 | 0.75 | 0.80 | 0.536 |
| B · vetor + rerank | 20 | 0.60 | 0.80 | 0.80 | 0.90 | 0.709 |
| B · híbrido | 20 | 0.50 | 0.85 | 0.85 | 0.85 | 0.659 |
| B · híbrido + rerank | 20 | 0.60 | 0.80 | 0.80 | 0.90 | 0.709 |

## Estratégia C

### MRR por tipo de consulta (regra oficial)

| configuração | MRR conceito | MRR opcoes | MRR sintaxe |
|---|---|---|---|
| vetor | 0.854 (n=8) | 0.576 (n=8) | 0.408 (n=4) |
| vetor + rerank | 0.883 (n=8) | 0.793 (n=8) | 0.573 (n=4) |
| híbrido | 0.833 (n=8) | 0.833 (n=8) | 0.587 (n=4) |
| híbrido + rerank | 0.882 (n=8) | 0.793 (n=8) | 0.566 (n=4) |

### Posição do primeiro acerto, por consulta (regra oficial)

| consulta | tipo | gabarito | vetor | vetor + rerank | híbrido | híbrido + rerank |
|---|---|---|---|---|---|---|
| mteste_01 | conceito | 1.2 | 1 | 1 | 1 | 1 |
| mteste_02 | conceito | 2.0 | 2 | 1 | 3 | 1 |
| mteste_03 | conceito | 3.2 | 1 | 1 | 1 | 1 |
| mteste_04 | conceito | 4.1, 4.1.1, 4.1.2 | 1 | 16 | 3 | 17 |
| mteste_05 | conceito | 4.1.1 | 3 | 1 | 1 | 1 |
| mteste_06 | conceito | 4.1.2 | 1 | 1 | 1 | 1 |
| mteste_07 | opcoes | 6.4 | 1 | 1 | 1 | 1 |
| mteste_08 | opcoes | 6.5 | 2 | 1 | 1 | 1 |
| mteste_09 | opcoes | 6.6 | 5 | 5 | 1 | 5 |
| mteste_10 | sintaxe | 6.9 | 44 | 24 | 72 | 72 |
| mteste_11 | conceito | 7.0 | 1 | 1 | 1 | 1 |
| mteste_12 | sintaxe | 7.3.1 | 9 | 4 | 3 | 4 |
| mteste_13 | sintaxe | 7.2, 7.3.3 | 1 | 1 | 1 | 1 |
| mteste_14 | opcoes | 7.3.5 | 1 | 1 | 1 | 1 |
| mteste_15 | sintaxe | 7.3.6 | 2 | 1 | 1 | 1 |
| mteste_16 | opcoes | 7.3.7 | 1 | 1 | 1 | 1 |
| mteste_17 | opcoes | 8.3 | 3 | 1 | 1 | 1 |
| mteste_18 | opcoes | 8.4.1, 9.1.1 | 2 | 7 | 2 | 7 |
| mteste_19 | opcoes | 6.8, 8.4.2 | 13 | 1 | 6 | 1 |
| mteste_20 | conceito | 8.7 | 1 | 1 | 1 | 1 |

### Consultas fora do 1º lugar: top-3 devolvido (folha e nota)

**vetor**

- mteste_02 (posição 2; gabarito 2.0): 10.0 (0.5672); 2.0 (0.5454); 1.2 (0.5413)
- mteste_05 (posição 3; gabarito 4.1.1): 1.0 (0.6529); 7.0 (0.6457); 4.1.1 (0.6441)
- mteste_08 (posição 2; gabarito 6.5): 6.11 (0.5824); 6.5 (0.566); 7.3.4 (0.5388)
- mteste_09 (posição 5; gabarito 6.6): 4.6 (0.6622); 6.7 (0.6227); 4.6.1 (0.5954)
- mteste_10 (posição 44; gabarito 6.9): 4.7 (0.5906); 4.5 (0.5801); 4.3.3 (0.5493)
- mteste_12 (posição 9; gabarito 7.3.1): 7.2 (0.6523); 7.3.2 (0.6365); 7.3.3 (0.6322)
- mteste_15 (posição 2; gabarito 7.3.6): 7.2 (0.6858); 7.3.6 (0.6731); 7.3.5 (0.673)
- mteste_17 (posição 3; gabarito 8.3): 8.0 (0.6494); 8.7 (0.6445); 8.3 (0.632)
- mteste_18 (posição 2; gabarito 8.4.1, 9.1.1): 6.10 (0.6251); 8.4.1 (0.6135); 6.11 (0.6126)
- mteste_19 (posição 13; gabarito 6.8, 8.4.2): 8.0 (0.6481); 8.1 (0.6163); 8.2 (0.5947)

**vetor + rerank**

- mteste_04 (posição 16; gabarito 4.1, 4.1.1, 4.1.2): 1.0 (0.0371); 3.3.1 (0.02); 6.4 (0.0075)
- mteste_09 (posição 5; gabarito 6.6): 3.3.1 (0.0548); 4.6 (0.0523); 9.1 (0.0225)
- mteste_10 (posição 24; gabarito 6.9): 4.7 (0.2987); 4.1.2 (0.1694); 4.5 (0.1638)
- mteste_12 (posição 4; gabarito 7.3.1): 7.3.2 (0.4666); 7.3.7 (0.2886); 7.2 (0.1774)
- mteste_18 (posição 7; gabarito 8.4.1, 9.1.1): 6.10 (0.4711); 4.6.1 (0.344); 8.2 (0.2235)

**híbrido**

- mteste_02 (posição 3; gabarito 2.0): 10.0 (0.0323); 1.2 (0.0323); 2.0 (0.0323)
- mteste_04 (posição 3; gabarito 4.1, 4.1.1, 4.1.2): 4.3.4 (0.0317); 4.7 (0.0303); 4.1.1 (0.0295)
- mteste_10 (posição 72; gabarito 6.9): 4.1.2 (0.032); 8.8 (0.031); 4.7 (0.0307)
- mteste_12 (posição 3; gabarito 7.3.1): 7.3.2 (0.0323); 7.4.1 (0.031); 7.3.1 (0.0309)
- mteste_18 (posição 2; gabarito 8.4.1, 9.1.1): 6.10 (0.0303); 9.1.1 (0.03); 8.0 (0.0295)
- mteste_19 (posição 6; gabarito 6.8, 8.4.2): 8.0 (0.0309); 6.11 (0.0309); 8.7 (0.0303)

**híbrido + rerank**

- mteste_04 (posição 17; gabarito 4.1, 4.1.1, 4.1.2): 1.0 (0.0371); 3.3.1 (0.02); 6.4 (0.0075)
- mteste_09 (posição 5; gabarito 6.6): 3.3.1 (0.0548); 4.6 (0.0523); 9.1 (0.0225)
- mteste_10 (posição 72; gabarito 6.9): 4.7 (0.2987); 4.1.2 (0.1694); 4.5 (0.1638)
- mteste_12 (posição 4; gabarito 7.3.1): 7.3.2 (0.4666); 7.3.7 (0.2886); 7.2 (0.1774)
- mteste_18 (posição 7; gabarito 8.4.1, 9.1.1): 6.10 (0.4711); 4.6.1 (0.344); 8.2 (0.2235)


## Estratégia B

### MRR por tipo de consulta (regra oficial)

| configuração | MRR conceito | MRR opcoes | MRR sintaxe |
|---|---|---|---|
| vetor | 0.344 (n=8) | 0.245 (n=8) | 0.583 (n=4) |
| vetor + rerank | 0.443 (n=8) | 0.535 (n=8) | 0.500 (n=4) |
| híbrido | 0.393 (n=8) | 0.394 (n=8) | 0.625 (n=4) |
| híbrido + rerank | 0.443 (n=8) | 0.535 (n=8) | 0.500 (n=4) |

### Posição do primeiro acerto, por consulta (regra oficial)

| consulta | tipo | gabarito | vetor | vetor + rerank | híbrido | híbrido + rerank |
|---|---|---|---|---|---|---|
| mteste_01 | conceito | 1.2 | fora | fora | fora | fora |
| mteste_02 | conceito | 2.0 | fora | fora | fora | fora |
| mteste_03 | conceito | 3.2 | 1 | 2 | 1 | 2 |
| mteste_04 | conceito | 4.1, 4.1.1, 4.1.2 | 18 | 25 | 7 | 25 |
| mteste_05 | conceito | 4.1.1 | fora | fora | fora | fora |
| mteste_06 | conceito | 4.1.2 | 1 | 1 | 1 | 1 |
| mteste_07 | opcoes | 6.4 | 2 | 1 | 1 | 1 |
| mteste_08 | opcoes | 6.5 | 1 | 1 | 1 | 1 |
| mteste_09 | opcoes | 6.6 | 9 | 8 | 3 | 8 |
| mteste_10 | sintaxe | 6.9 | fora | fora | fora | fora |
| mteste_11 | conceito | 7.0 | 2 | 1 | 2 | 1 |
| mteste_12 | sintaxe | 7.3.1 | 3 | 2 | 2 | 2 |
| mteste_13 | sintaxe | 7.2, 7.3.3 | 1 | 1 | 1 | 1 |
| mteste_14 | opcoes | 7.3.5 | 13 | 1 | 3 | 1 |
| mteste_15 | sintaxe | 7.3.6 | 1 | 2 | 1 | 2 |
| mteste_16 | opcoes | 7.3.7 | fora | fora | fora | fora |
| mteste_17 | opcoes | 8.3 | 6 | 10 | 3 | 10 |
| mteste_18 | opcoes | 8.4.1, 9.1.1 | 20 | 17 | 17 | 18 |
| mteste_19 | opcoes | 6.8, 8.4.2 | 17 | 1 | 11 | 1 |
| mteste_20 | conceito | 8.7 | 5 | 1 | 2 | 1 |

### Consultas fora do 1º lugar: top-3 devolvido (folha e nota)

**vetor**

- mteste_01 (posição fora; gabarito 1.2): 1.3 (0.613); 1.1 (0.5974); 2.1 (0.587)
- mteste_02 (posição fora; gabarito 2.0): 1.3 (0.5719); 10.0 (0.5599); 2.1 (0.5568)
- mteste_04 (posição 18; gabarito 4.1, 4.1.1, 4.1.2): 4.5 (0.5989); 3.5 (0.5897); 4.6 (0.5725)
- mteste_05 (posição fora; gabarito 4.1.1): 4.1.2 (0.6969); 1.0 (0.6567); 7.0 (0.6192)
- mteste_07 (posição 2; gabarito 6.4): 6.11 (0.5878); 6.4 (0.5821); 4.3.4 (0.5811)
- mteste_09 (posição 9; gabarito 6.6): 4.6 (0.6573); 4.5 (0.6459); 6.7 (0.6257)
- mteste_10 (posição fora; gabarito 6.9): 4.7 (0.5699); 4.5 (0.5651); 4.1.2 (0.5458)
- mteste_11 (posição 2; gabarito 7.0): 7.1 (0.5189); 7.0 (0.5021); 4.7 (0.5017)
- mteste_12 (posição 3; gabarito 7.3.1): 7.3.3 (0.6648); 7.3.6 (0.6525); 7.3.1 (0.6332)
- mteste_14 (posição 13; gabarito 7.3.5): 7.3.6 (0.5936); 7.4.3 (0.5898); 6.8 (0.5865)
- mteste_16 (posição fora; gabarito 7.3.7): 7.3.8 (0.6762); 7.3.3 (0.6098); 7.1 (0.5975)
- mteste_17 (posição 6; gabarito 8.3): 8.0 (0.6426); 8.2 (0.6087); 8.8 (0.5914)
- mteste_18 (posição 20; gabarito 8.4.1, 9.1.1): 6.1 (0.6156); 8.2 (0.6079); 6.11 (0.5825)
- mteste_19 (posição 17; gabarito 6.8, 8.4.2): 8.0 (0.6394); 8.2 (0.6252); 8.8 (0.5967)
- mteste_20 (posição 5; gabarito 8.7): 8.8 (0.5985); 8.2 (0.5925); 8.0 (0.574)

**vetor + rerank**

- mteste_01 (posição fora; gabarito 1.2): 1.1 (0.2227); 1.3 (0.0321); 2.1 (0.0142)
- mteste_02 (posição fora; gabarito 2.0): 1.3 (0.3273); 10.0 (0.2687); 2.1 (0.177)
- mteste_03 (posição 2; gabarito 3.2): 3.1 (0.9554); 3.2 (0.7942); 3.5 (0.2397)
- mteste_04 (posição 25; gabarito 4.1, 4.1.1, 4.1.2): 1.0 (0.0456); 6.4 (0.031); 2.1 (0.0177)
- mteste_05 (posição fora; gabarito 4.1.1): 4.1.2 (0.9359); 1.0 (0.8621); 1.1 (0.4569)
- mteste_09 (posição 8; gabarito 6.6): 4.6 (0.054); 9.1 (0.0214); 3.3.1 (0.0175)
- mteste_10 (posição fora; gabarito 6.9): 4.1.2 (0.2665); 4.7 (0.2365); 4.4 (0.0599)
- mteste_12 (posição 2; gabarito 7.3.1): 7.3.3 (0.8398); 7.3.1 (0.5649); 7.3.8 (0.257)
- mteste_15 (posição 2; gabarito 7.3.6): 7.3.8 (0.8642); 7.3.6 (0.858); 6.8 (0.2741)
- mteste_16 (posição fora; gabarito 7.3.7): 7.3.8 (0.8781); 7.3.3 (0.0969); 7.3.1 (0.0716)
- mteste_17 (posição 10; gabarito 8.3): 8.2 (0.0814); 8.0 (0.0415); 8.8 (0.0182)
- mteste_18 (posição 17; gabarito 8.4.1, 9.1.1): 6.1 (0.5026); 6.1 (0.412); 8.2 (0.4082)

**híbrido**

- mteste_01 (posição fora; gabarito 1.2): 1.0 (0.032); 1.1 (0.032); 2.1 (0.032)
- mteste_02 (posição fora; gabarito 2.0): 2.1 (0.0323); 10.0 (0.0323); 1.3 (0.032)
- mteste_04 (posição 7; gabarito 4.1, 4.1.1, 4.1.2): 4.3.4 (0.0318); 4.7 (0.0308); 3.5 (0.0302)
- mteste_05 (posição fora; gabarito 4.1.1): 4.1.2 (0.0323); 1.0 (0.0311); 1.1 (0.0297)
- mteste_09 (posição 3; gabarito 6.6): 4.6 (0.0313); 4.7 (0.031); 6.6 (0.0309)
- mteste_10 (posição fora; gabarito 6.9): 4.1.2 (0.032); 4.4 (0.0305); 8.0 (0.0303)
- mteste_11 (posição 2; gabarito 7.0): 7.1 (0.0315); 7.0 (0.0289); 6.4 (0.0287)
- mteste_12 (posição 2; gabarito 7.3.1): 7.3.3 (0.0325); 7.3.1 (0.0323); 7.3.8 (0.0313)
- mteste_14 (posição 3; gabarito 7.3.5): 7.3.6 (0.0325); 4.7 (0.0313); 7.3.5 (0.0301)
- mteste_16 (posição fora; gabarito 7.3.7): 7.3.8 (0.0328); 7.3.10 (0.0311); 7.3.1 (0.0308)
- mteste_17 (posição 3; gabarito 8.3): 8.2 (0.0325); 8.5.2 (0.0308); 8.3 (0.0308)
- mteste_18 (posição 17; gabarito 8.4.1, 9.1.1): 8.0 (0.0308); 8.8 (0.0286); 4.6.1 (0.0283)
- mteste_19 (posição 11; gabarito 6.8, 8.4.2): 8.0 (0.0315); 3.4 (0.0295); 4.1.2 (0.0292)
- mteste_20 (posição 2; gabarito 8.7): 8.8 (0.0325); 8.7 (0.0318); 8.0 (0.0302)

**híbrido + rerank**

- mteste_01 (posição fora; gabarito 1.2): 1.1 (0.2227); 1.3 (0.0321); 2.1 (0.0142)
- mteste_02 (posição fora; gabarito 2.0): 1.3 (0.3273); 10.0 (0.2687); 2.1 (0.177)
- mteste_03 (posição 2; gabarito 3.2): 3.1 (0.9554); 3.2 (0.7942); 3.5 (0.2397)
- mteste_04 (posição 25; gabarito 4.1, 4.1.1, 4.1.2): 1.0 (0.0456); 6.4 (0.031); 2.1 (0.0177)
- mteste_05 (posição fora; gabarito 4.1.1): 4.1.2 (0.9359); 1.0 (0.8621); 1.1 (0.4569)
- mteste_09 (posição 8; gabarito 6.6): 4.6 (0.054); 9.1 (0.0214); 3.3.1 (0.0175)
- mteste_10 (posição fora; gabarito 6.9): 4.1.2 (0.2665); 4.7 (0.2365); 4.4 (0.0599)
- mteste_12 (posição 2; gabarito 7.3.1): 7.3.3 (0.8398); 7.3.1 (0.5649); 7.3.8 (0.257)
- mteste_15 (posição 2; gabarito 7.3.6): 7.3.8 (0.8642); 7.3.6 (0.858); 6.8 (0.2741)
- mteste_16 (posição fora; gabarito 7.3.7): 7.3.8 (0.8781); 7.3.3 (0.0969); 7.3.1 (0.0716)
- mteste_17 (posição 10; gabarito 8.3): 8.2 (0.0814); 8.0 (0.0415); 8.8 (0.0182)
- mteste_18 (posição 18; gabarito 8.4.1, 9.1.1): 6.1 (0.5026); 6.1 (0.412); 8.2 (0.4082)


## Teste

O teste só relata; o padrão foi escolhido no desenvolvimento.
