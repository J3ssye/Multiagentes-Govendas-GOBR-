# Avaliação da recuperação no manual (Entrega 3) - conjunto: dev (15 consultas)

Gerado em 03/11/2026 13:36. Ranking de chunks, sem agrupar; candidatos do reranker: 50.

## Resumo - regra oficial (a folha principal do chunk está no gabarito)

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 15 | 0.53 | 0.80 | 0.93 | 1.00 | 0.693 |
| C · vetor + rerank | 15 | 0.60 | 0.93 | 1.00 | 1.00 | 0.772 |
| C · híbrido | 15 | 0.40 | 0.87 | 0.93 | 1.00 | 0.637 |
| C · híbrido + rerank | 15 | 0.60 | 0.93 | 1.00 | 1.00 | 0.772 |
| B · vetor | 15 | 0.33 | 0.67 | 0.73 | 0.80 | 0.518 |
| B · vetor + rerank | 15 | 0.47 | 0.80 | 0.87 | 0.87 | 0.630 |
| B · híbrido | 15 | 0.27 | 0.73 | 0.80 | 0.87 | 0.503 |
| B · híbrido + rerank | 15 | 0.47 | 0.80 | 0.87 | 0.87 | 0.625 |

## Sensibilidade - acerta também o chunk com pelo menos 50% de uma folha do gabarito (só relata; não decide)

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| C · vetor | 15 | 0.53 | 0.80 | 0.93 | 1.00 | 0.693 |
| C · vetor + rerank | 15 | 0.60 | 0.93 | 1.00 | 1.00 | 0.772 |
| C · híbrido | 15 | 0.40 | 0.87 | 0.93 | 1.00 | 0.637 |
| C · híbrido + rerank | 15 | 0.60 | 0.93 | 1.00 | 1.00 | 0.772 |
| B · vetor | 15 | 0.47 | 0.80 | 0.87 | 1.00 | 0.663 |
| B · vetor + rerank | 15 | 0.67 | 0.93 | 1.00 | 1.00 | 0.791 |
| B · híbrido | 15 | 0.40 | 0.93 | 0.93 | 1.00 | 0.633 |
| B · híbrido + rerank | 15 | 0.67 | 0.93 | 1.00 | 1.00 | 0.791 |

## Estratégia C

### MRR por tipo de consulta (regra oficial)

| configuração | MRR conceito | MRR opcoes | MRR sintaxe |
|---|---|---|---|
| vetor | 0.778 (n=3) | 0.508 (n=8) | 1.000 (n=4) |
| vetor + rerank | 0.833 (n=3) | 0.635 (n=8) | 1.000 (n=4) |
| híbrido | 0.583 (n=3) | 0.539 (n=8) | 0.875 (n=4) |
| híbrido + rerank | 0.833 (n=3) | 0.635 (n=8) | 1.000 (n=4) |

### Posição do primeiro acerto, por consulta (regra oficial)

| consulta | tipo | gabarito | vetor | vetor + rerank | híbrido | híbrido + rerank |
|---|---|---|---|---|---|---|
| mdev_01 | conceito | 2.2, 10.0 | 3 | 2 | 4 | 2 |
| mdev_02 | sintaxe | 3.1 | 1 | 1 | 1 | 1 |
| mdev_03 | opcoes | 3.3.1, 3.4 | 1 | 1 | 2 | 1 |
| mdev_04 | conceito | 4.2, 4.4, 4.5, 4.7 | 1 | 1 | 1 | 1 |
| mdev_05 | opcoes | 4.3.4, 4.5, 4.6.1 | 1 | 1 | 1 | 1 |
| mdev_06 | opcoes | 5.1, 5.3, 7.3.8, 7.3.9, 7.3.10, 8.2 | 2 | 4 | 2 | 4 |
| mdev_07 | opcoes | 6.2 | 5 | 2 | 7 | 2 |
| mdev_08 | opcoes | 6.3 | 6 | 2 | 1 | 2 |
| mdev_09 | opcoes | 6.11.1, 6.12, 6.13 | 5 | 2 | 2 | 2 |
| mdev_10 | sintaxe | 7.3.4 | 1 | 1 | 1 | 1 |
| mdev_11 | opcoes | 7.4.3 | 2 | 1 | 3 | 1 |
| mdev_12 | opcoes | 8.2, 8.5.1 | 2 | 3 | 3 | 3 |
| mdev_13 | sintaxe | 8.2, 8.6 | 1 | 1 | 1 | 1 |
| mdev_14 | conceito | 9.0 | 1 | 1 | 2 | 1 |
| mdev_15 | sintaxe | 6.13, 7.4.1, 10.0 | 1 | 1 | 2 | 1 |

### Consultas fora do 1º lugar: top-3 devolvido (folha e nota)

**vetor**

- mdev_01 (posição 3; gabarito 2.2, 10.0): 1.3 (0.5982); 1.0 (0.5447); 10.0 (0.5379)
- mdev_06 (posição 2; gabarito 5.1, 5.3, 7.3.8, 7.3.9, 7.3.10, 8.2): 7.3.7 (0.6235); 5.3 (0.594); 7.3.1 (0.5669)
- mdev_07 (posição 5; gabarito 6.2): 6.10 (0.5808); 6.11 (0.5777); 6.1 (0.5776)
- mdev_08 (posição 6; gabarito 6.3): 4.3.3 (0.6476); 4.4 (0.6004); 4.3.1 (0.5918)
- mdev_09 (posição 5; gabarito 6.11.1, 6.12, 6.13): 5.5 (0.6767); 5.4 (0.6705); 5.2 (0.6514)
- mdev_11 (posição 2; gabarito 7.4.3): 7.3.6 (0.6671); 7.4.3 (0.65); 7.4.2 (0.6367)
- mdev_12 (posição 2; gabarito 8.2, 8.5.1): 5.6 (0.5984); 8.5.1 (0.5919); 8.7 (0.5876)

**vetor + rerank**

- mdev_01 (posição 2; gabarito 2.2, 10.0): 1.3 (0.5865); 10.0 (0.4864); 1.0 (0.2208)
- mdev_06 (posição 4; gabarito 5.1, 5.3, 7.3.8, 7.3.9, 7.3.10, 8.2): 7.3.7 (0.4416); 7.3.1 (0.1887); 7.3.3 (0.1424)
- mdev_07 (posição 2; gabarito 6.2): 4.3.2 (0.5166); 6.2 (0.4319); 6.11 (0.3956)
- mdev_08 (posição 2; gabarito 6.3): 4.3.3 (0.0568); 6.3 (0.0398); 6.5 (0.0077)
- mdev_09 (posição 2; gabarito 6.11.1, 6.12, 6.13): 5.4 (0.6531); 6.13 (0.6194); 6.11.1 (0.4497)
- mdev_12 (posição 3; gabarito 8.2, 8.5.1): 5.1 (0.0634); 8.1 (0.0631); 8.5.1 (0.0577)

**híbrido**

- mdev_01 (posição 4; gabarito 2.2, 10.0): 3.1 (0.0309); 7.0 (0.0305); 4.1.1 (0.0299)
- mdev_03 (posição 2; gabarito 3.3.1, 3.4): 3.5 (0.0325); 3.3.1 (0.0315); 3.4 (0.0311)
- mdev_06 (posição 2; gabarito 5.1, 5.3, 7.3.8, 7.3.9, 7.3.10, 8.2): 7.3.7 (0.0325); 5.3 (0.032); 5.1 (0.0315)
- mdev_07 (posição 7; gabarito 6.2): 6.10 (0.032); 6.1 (0.0317); 6.11 (0.0308)
- mdev_09 (posição 2; gabarito 6.11.1, 6.12, 6.13): 5.5 (0.0318); 6.11.1 (0.0315); 6.13 (0.0313)
- mdev_11 (posição 3; gabarito 7.4.3): 6.8 (0.0315); 8.4.2 (0.0313); 7.4.3 (0.0313)
- mdev_12 (posição 3; gabarito 8.2, 8.5.1): 5.6 (0.0325); 8.7 (0.0315); 8.2 (0.0315)
- mdev_14 (posição 2; gabarito 9.0): 2.1 (0.0318); 9.0 (0.0307); 2.0 (0.0306)
- mdev_15 (posição 2; gabarito 6.13, 7.4.1, 10.0): 5.5 (0.0317); 7.4.1 (0.0303); 6.12 (0.0295)

**híbrido + rerank**

- mdev_01 (posição 2; gabarito 2.2, 10.0): 1.3 (0.5865); 10.0 (0.4864); 1.0 (0.2208)
- mdev_06 (posição 4; gabarito 5.1, 5.3, 7.3.8, 7.3.9, 7.3.10, 8.2): 7.3.7 (0.4416); 7.3.1 (0.1887); 7.3.3 (0.1424)
- mdev_07 (posição 2; gabarito 6.2): 4.3.2 (0.5166); 6.2 (0.4319); 6.11 (0.3956)
- mdev_08 (posição 2; gabarito 6.3): 4.3.3 (0.0568); 6.3 (0.0398); 6.5 (0.0077)
- mdev_09 (posição 2; gabarito 6.11.1, 6.12, 6.13): 5.4 (0.6531); 6.13 (0.6194); 6.11.1 (0.4497)
- mdev_12 (posição 3; gabarito 8.2, 8.5.1): 5.1 (0.0634); 8.1 (0.0631); 8.5.1 (0.0577)


## Estratégia B

### MRR por tipo de consulta (regra oficial)

| configuração | MRR conceito | MRR opcoes | MRR sintaxe |
|---|---|---|---|
| vetor | 0.507 (n=3) | 0.490 (n=8) | 0.583 (n=4) |
| vetor + rerank | 0.528 (n=3) | 0.754 (n=8) | 0.458 (n=4) |
| híbrido | 0.505 (n=3) | 0.525 (n=8) | 0.458 (n=4) |
| híbrido + rerank | 0.505 (n=3) | 0.754 (n=8) | 0.458 (n=4) |

### Posição do primeiro acerto, por consulta (regra oficial)

| consulta | tipo | gabarito | vetor | vetor + rerank | híbrido | híbrido + rerank |
|---|---|---|---|---|---|---|
| mdev_01 | conceito | 2.2, 10.0 | 2 | 1 | 2 | 1 |
| mdev_02 | sintaxe | 3.1 | 1 | 1 | 1 | 1 |
| mdev_03 | opcoes | 3.3.1, 3.4 | 1 | 1 | 2 | 1 |
| mdev_04 | conceito | 4.2, 4.4, 4.5, 4.7 | 1 | 2 | 1 | 2 |
| mdev_05 | opcoes | 4.3.4, 4.5, 4.6.1 | 1 | 1 | 2 | 1 |
| mdev_06 | opcoes | 5.1, 5.3, 7.3.8, 7.3.9, 7.3.10, 8.2 | 2 | 1 | 1 | 1 |
| mdev_07 | opcoes | 6.2 | 4 | 3 | 6 | 3 |
| mdev_08 | opcoes | 6.3 | 10 | 2 | 1 | 2 |
| mdev_09 | opcoes | 6.11.1, 6.12, 6.13 | 14 | 5 | 5 | 5 |
| mdev_10 | sintaxe | 7.3.4 | fora | fora | fora | fora |
| mdev_11 | opcoes | 7.4.3 | 2 | 1 | 2 | 1 |
| mdev_12 | opcoes | 8.2, 8.5.1 | 2 | 1 | 3 | 1 |
| mdev_13 | sintaxe | 8.2, 8.6 | 3 | 2 | 2 | 2 |
| mdev_14 | conceito | 9.0 | 49 | 12 | 65 | 65 |
| mdev_15 | sintaxe | 6.13, 7.4.1, 10.0 | 1 | 3 | 3 | 3 |

### Consultas fora do 1º lugar: top-3 devolvido (folha e nota)

**vetor**

- mdev_01 (posição 2; gabarito 2.2, 10.0): 1.0 (0.5575); 10.0 (0.5557); 7.0 (0.5469)
- mdev_06 (posição 2; gabarito 5.1, 5.3, 7.3.8, 7.3.9, 7.3.10, 8.2): 1.3 (0.5825); 7.3.8 (0.5709); 7.3.3 (0.5707)
- mdev_07 (posição 4; gabarito 6.2): 6.1 (0.5866); 6.10 (0.575); 6.11 (0.5649)
- mdev_08 (posição 10; gabarito 6.3): 4.3.3 (0.6316); 4.3.2 (0.6162); 4.4 (0.5971)
- mdev_09 (posição 14; gabarito 6.11.1, 6.12, 6.13): 5.3 (0.6828); 5.5 (0.6585); 6.4 (0.6134)
- mdev_10 (posição fora; gabarito 7.3.4): 7.3.5 (0.6176); 6.4 (0.5842); 7.3.10 (0.5833)
- mdev_11 (posição 2; gabarito 7.4.3): 7.3.6 (0.6608); 7.4.3 (0.6511); 7.4.1 (0.6073)
- mdev_12 (posição 2; gabarito 8.2, 8.5.1): 5.1 (0.6231); 8.2 (0.6112); 5.6 (0.6064)
- mdev_13 (posição 3; gabarito 8.2, 8.6): 8.7 (0.6482); 8.1 (0.6098); 8.2 (0.5801)
- mdev_14 (posição 49; gabarito 9.0): 2.1 (0.559); 8.8 (0.5543); 4.7 (0.5422)

**vetor + rerank**

- mdev_04 (posição 2; gabarito 4.2, 4.4, 4.5, 4.7): 4.3.1 (0.4017); 4.7 (0.3953); 4.3.4 (0.194)
- mdev_07 (posição 3; gabarito 6.2): 6.1 (0.5669); 4.3.2 (0.4816); 6.2 (0.4288)
- mdev_08 (posição 2; gabarito 6.3): 4.3.3 (0.0541); 6.3 (0.0536); 4.3.2 (0.0054)
- mdev_09 (posição 5; gabarito 6.11.1, 6.12, 6.13): 5.3 (0.6853); 5.1 (0.4901); 5.5 (0.3904)
- mdev_10 (posição fora; gabarito 7.3.4): 7.3.5 (0.2648); 7.3.9 (0.0655); 7.3.10 (0.0331)
- mdev_13 (posição 2; gabarito 8.2, 8.6): 8.7 (0.1096); 8.2 (0.0085); 8.1 (0.008)
- mdev_14 (posição 12; gabarito 9.0): 10.0 (0.0924); 8.8 (0.0705); 6.5 (0.0376)
- mdev_15 (posição 3; gabarito 6.13, 7.4.1, 10.0): 5.1 (0.1453); 7.0 (0.0793); 10.0 (0.0516)

**híbrido**

- mdev_01 (posição 2; gabarito 2.2, 10.0): 7.0 (0.0313); 10.0 (0.0311); 4.1.2 (0.0308)
- mdev_03 (posição 2; gabarito 3.3.1, 3.4): 3.5 (0.0315); 3.3.1 (0.0307); 3.4 (0.0306)
- mdev_05 (posição 2; gabarito 4.3.4, 4.5, 4.6.1): 4.6 (0.0323); 4.6.1 (0.0318); 6.10 (0.0318)
- mdev_07 (posição 6; gabarito 6.2): 6.10 (0.0318); 6.11 (0.0308); 6.1 (0.0306)
- mdev_09 (posição 5; gabarito 6.11.1, 6.12, 6.13): 5.5 (0.0311); 5.3 (0.0307); 6.11.2 (0.0302)
- mdev_10 (posição fora; gabarito 7.3.4): 7.3.5 (0.0323); 6.4 (0.0315); 6.4 (0.0306)
- mdev_11 (posição 2; gabarito 7.4.3): 7.3.6 (0.032); 7.4.3 (0.0311); 6.8 (0.0308)
- mdev_12 (posição 3; gabarito 8.2, 8.5.1): 5.1 (0.0328); 5.6 (0.032); 8.2 (0.0308)
- mdev_13 (posição 2; gabarito 8.2, 8.6): 8.7 (0.0328); 8.2 (0.032); 5.6 (0.0301)
- mdev_14 (posição 65; gabarito 9.0): 2.1 (0.0325); 4.7 (0.0315); 8.8 (0.0311)
- mdev_15 (posição 3; gabarito 6.13, 7.4.1, 10.0): 7.0 (0.0313); 5.5 (0.031); 10.0 (0.0294)

**híbrido + rerank**

- mdev_04 (posição 2; gabarito 4.2, 4.4, 4.5, 4.7): 4.3.1 (0.4017); 4.7 (0.3953); 4.3.4 (0.194)
- mdev_07 (posição 3; gabarito 6.2): 6.1 (0.5669); 4.3.2 (0.4816); 6.2 (0.4288)
- mdev_08 (posição 2; gabarito 6.3): 4.3.3 (0.0541); 6.3 (0.0536); 4.3.2 (0.0054)
- mdev_09 (posição 5; gabarito 6.11.1, 6.12, 6.13): 5.3 (0.6853); 5.1 (0.4901); 5.5 (0.3904)
- mdev_10 (posição fora; gabarito 7.3.4): 7.3.5 (0.2648); 7.3.9 (0.0655); 7.3.10 (0.0331)
- mdev_13 (posição 2; gabarito 8.2, 8.6): 8.7 (0.1096); 8.2 (0.0085); 8.1 (0.008)
- mdev_14 (posição 65; gabarito 9.0): 10.0 (0.0924); 8.8 (0.0705); 6.5 (0.0376)
- mdev_15 (posição 3; gabarito 6.13, 7.4.1, 10.0): 5.1 (0.1453); 7.0 (0.0793); 10.0 (0.0516)


## Padrão pela regra fixada

**C · vetor + rerank**: MRR 0.772, hit@1 0.60 (maior MRR no dev; desempates: hit@1, configuração mais simples, estratégia C).
