# Desenvolvimento do fluxo (Entrega 4) - regras: 14 consultas; manual: 15 consultas

Gerado em 2026-11-09T19:00:53-03:00. Teto 20 s por pergunta (regras + manual somados); 2 repetições por consulta, vale a menor; a latência da configuração é a maior entre as consultas. Acerto e MRR vêm da 1ª repetição, sobre o ranking completo.

Regra: sha256 `fa77637b72388657f92807e0d33007f8a42b1783fd1a114cef3c898623128b68`. Commit da regra: 279a9a4160ab em 2026-11-08T18:59:38-03:00.

## Regras (Entrega 2, com_pontos)

| configuração | situação | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência máx. (s) |
|---|---|---|---|---|---|---|---|
| regras_vetor_sem-rerank | medida | 0.29 | 0.50 | 0.50 | 0.50 | 0.390 | 1.15 |
| regras_hibrido_sem-rerank | medida | 0.43 | 0.71 | 0.86 | 0.93 | 0.606 | 1.18 |
| regras_vetor_N5_L512 | excluída por latência (sint_quinzenal_mensal: 24.1 s) | - | - | - | - | - | - |
| regras_hibrido_N5_L512 | excluída por latência (img_infinitto: 38.0 s) | - | - | - | - | - | - |
| regras_vetor_N5_L2048 | medida | 0.50 | 0.50 | 0.50 | 0.50 | 0.521 | 14.32 |
| regras_hibrido_N5_L2048 | excluída por latência (sint_regra_grande_regioes: 45.6 s) | - | - | - | - | - | - |
| regras_vetor_N10_L512 | excluída por latência (img_infinitto: 49.0 s) | - | - | - | - | - | - |
| regras_hibrido_N10_L512 | excluída por latência (img_infinitto: 50.8 s) | - | - | - | - | - | - |
| regras_vetor_N10_L2048 | excluída por latência (img_maxlub: 27.0 s) | - | - | - | - | - | - |
| regras_hibrido_N10_L2048 | excluída por latência (img_infinitto: 21.6 s) | - | - | - | - | - | - |
| regras_vetor_N20_L512 | excluída por latência (img_infinitto: 55.9 s) | - | - | - | - | - | - |
| regras_hibrido_N20_L512 | excluída por latência (img_infinitto: 41.6 s) | - | - | - | - | - | - |
| regras_vetor_N20_L2048 | excluída por latência (img_infinitto: 32.8 s) | - | - | - | - | - | - |
| regras_hibrido_N20_L2048 | excluída por latência (img_infinitto: 83.8 s) | - | - | - | - | - | - |
| regras_vetor_N50_L512 | excluída por latência (img_infinitto: 81.6 s) | - | - | - | - | - | - |
| regras_hibrido_N50_L512 | excluída por latência (img_infinitto: 88.9 s) | - | - | - | - | - | - |
| regras_vetor_N50_L2048 | excluída por latência (img_infinitto: 181.5 s) | - | - | - | - | - | - |
| regras_hibrido_N50_L2048 | excluída por latência (img_infinitto: 204.4 s) | - | - | - | - | - | - |

## Manual (Entrega 3, estratégia C)

| configuração | situação | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência máx. (s) |
|---|---|---|---|---|---|---|---|
| manual_vetor_sem-rerank | medida | 0.53 | 0.80 | 0.93 | 1.00 | 0.693 | 0.59 |
| manual_hibrido_sem-rerank | medida | 0.40 | 0.87 | 0.93 | 1.00 | 0.637 | 0.65 |
| manual_vetor_N5_L2048 | excluída por latência (mdev_01: 20.4 s) | - | - | - | - | - | - |
| manual_hibrido_N5_L2048 | excluída por latência (mdev_01: 20.0 s) | - | - | - | - | - | - |
| manual_vetor_N10_L2048 | excluída por latência (mdev_01: 28.0 s) | - | - | - | - | - | - |
| manual_hibrido_N10_L2048 | excluída por latência (mdev_01: 28.4 s) | - | - | - | - | - | - |
| manual_vetor_N20_L2048 | excluída por latência (mdev_01: 49.2 s) | - | - | - | - | - | - |
| manual_hibrido_N20_L2048 | excluída por latência (mdev_01: 58.0 s) | - | - | - | - | - | - |
| manual_vetor_N50_L2048 | excluída por latência (mdev_01: 120.5 s) | - | - | - | - | - | - |
| manual_hibrido_N50_L2048 | excluída por latência (mdev_01: 131.2 s) | - | - | - | - | - | - |

## Carregamento e aquecimento (fora do teto; segundos, por execução)

- Execução 1 (2026-11-09T06:37:36-03:00 a 2026-11-09T19:00:53-03:00; dispositivo: {'embedding': 'cpu', 'reranker_2048': 'cpu'}): embedding 68.05, indice_regras 3.83, aquecimento_regras_0 74.63, indice_manual 1.57, aquecimento_manual_0 1.93, reranker_512 10.8, aquecimento_regras_512 19.18, reranker_2048 6.26, aquecimento_regras_2048 9.93, aquecimento_manual_2048 2.13

## Insumos (sha256 da seção 11 da regra)

Todos conferem.
