# Desenvolvimento do fluxo (Entrega 4) - regras: 14 consultas; manual: 15 consultas

Gerado em 2026-11-09T21:12:18-03:00. Teto 20 s por pergunta (regras + manual somados); 2 repetições por consulta, vale a menor; a latência da configuração é a maior entre as consultas. Acerto e MRR vêm da 1ª repetição, sobre o ranking completo.

Regra: sha256 `fa77637b72388657f92807e0d33007f8a42b1783fd1a114cef3c898623128b68`. Commit da regra: 279a9a4160ab em 2026-11-08T18:59:38-03:00.

## Regras (Entrega 2, com_pontos)

| configuração | situação | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência máx. (s) |
|---|---|---|---|---|---|---|---|
| regras_vetor_sem-rerank | medida | 0.29 | 0.50 | 0.50 | 0.50 | 0.390 | 0.98 |
| regras_hibrido_sem-rerank | medida | 0.43 | 0.71 | 0.86 | 0.93 | 0.606 | 0.61 |
| regras_vetor_N5_L512 | medida | 0.50 | 0.50 | 0.50 | 0.50 | 0.521 | 15.14 |
| regras_hibrido_N5_L512 | excluída por latência (sint_regra_grande_regioes: 22.8 s) | - | - | - | - | - | - |
| regras_vetor_N5_L2048 | medida | 0.50 | 0.50 | 0.50 | 0.50 | 0.521 | 17.64 |
| regras_hibrido_N5_L2048 | excluída por latência (sint_televendas_x_campo: 22.2 s) | - | - | - | - | - | - |
| regras_vetor_N10_L512 | excluída por latência (img_infinitto: 34.7 s) | - | - | - | - | - | - |
| regras_hibrido_N10_L512 | excluída por latência (img_infinitto: 43.2 s) | - | - | - | - | - | - |
| regras_vetor_N10_L2048 | excluída por latência (sint_ramos_12_19: 24.8 s) | - | - | - | - | - | - |
| regras_hibrido_N10_L2048 | excluída por latência (img_infinitto: 25.1 s) | - | - | - | - | - | - |
| regras_vetor_N20_L512 | excluída por latência (img_infinitto: 66.6 s) | - | - | - | - | - | - |
| regras_hibrido_N20_L512 | excluída por latência (img_infinitto: 68.4 s) | - | - | - | - | - | - |
| regras_vetor_N20_L2048 | excluída por latência (img_infinitto: 35.2 s) | - | - | - | - | - | - |
| regras_hibrido_N20_L2048 | excluída por latência (img_infinitto: 42.3 s) | - | - | - | - | - | - |
| regras_vetor_N50_L512 | excluída por latência (img_infinitto: 111.7 s) | - | - | - | - | - | - |
| regras_hibrido_N50_L512 | excluída por latência (img_infinitto: 115.3 s) | - | - | - | - | - | - |
| regras_vetor_N50_L2048 | excluída por latência (img_infinitto: 96.0 s) | - | - | - | - | - | - |
| regras_hibrido_N50_L2048 | excluída por latência (img_infinitto: 94.3 s) | - | - | - | - | - | - |

## Manual (Entrega 3, estratégia C)

| configuração | situação | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência máx. (s) |
|---|---|---|---|---|---|---|---|
| manual_vetor_sem-rerank | medida | 0.53 | 0.80 | 0.93 | 1.00 | 0.693 | 0.32 |
| manual_hibrido_sem-rerank | medida | 0.40 | 0.87 | 0.93 | 1.00 | 0.637 | 0.35 |
| manual_vetor_N5_L2048 | medida | 0.73 | 0.93 | 0.93 | 1.00 | 0.833 | 9.79 |
| manual_hibrido_N5_L2048 | medida | 0.73 | 0.87 | 0.93 | 1.00 | 0.804 | 12.40 |
| manual_vetor_N10_L2048 | excluída por latência (mdev_08: 23.8 s) | - | - | - | - | - | - |
| manual_hibrido_N10_L2048 | excluída por latência (mdev_02: 20.0 s) | - | - | - | - | - | - |
| manual_vetor_N20_L2048 | excluída por latência (mdev_01: 31.2 s) | - | - | - | - | - | - |
| manual_hibrido_N20_L2048 | excluída por latência (mdev_01: 29.7 s) | - | - | - | - | - | - |
| manual_vetor_N50_L2048 | excluída por latência (mdev_01: 63.3 s) | - | - | - | - | - | - |
| manual_hibrido_N50_L2048 | excluída por latência (mdev_01: 61.8 s) | - | - | - | - | - | - |

## Carregamento e aquecimento (fora do teto; segundos, por execução)

- Execução 1 (2026-11-09T20:18:37-03:00 a 2026-11-09T21:12:18-03:00; dispositivo: {'embedding': 'cpu', 'reranker_2048': 'cpu'}): embedding 24.03, indice_regras 1.39, aquecimento_regras_0 25.9, indice_manual 1.32, aquecimento_manual_0 1.66, reranker_512 10.11, aquecimento_regras_512 14.53, reranker_2048 8.87, aquecimento_regras_2048 16.41, aquecimento_manual_2048 4.19

## Insumos (sha256 da seção 11 da regra)

Todos conferem.
