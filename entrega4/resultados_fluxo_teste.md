# Teste do fluxo (Entrega 4) - dupla escolhida no desenvolvimento

Gerado em 2026-11-09T21:21:48-03:00. Rodou uma vez. Só relata: nada foi ajustado depois de ver estes números.
Regra: sha256 `fa77637b72388657f92807e0d33007f8a42b1783fd1a114cef3c898623128b68`. config_escolhida.json: sha256 `b6cf2f6c0baafb855386ccaaa14c4ebfc54ba1bed7ae5ebb92950a45c4f67d28`.
Dispositivo: {'embedding': 'cpu', 'reranker_2048': 'cpu'}.

| índice | configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR | latência mediana (s) | latência máx. (s) |
|---|---|---|---|---|---|---|---|---|---|
| regras | regras_hibrido_sem-rerank | 20 | 0.50 | 0.75 | 0.80 | 0.90 | 0.640 | 0.32 | 0.38 |
| manual | manual_vetor_N5_L2048 | 20 | 0.70 | 0.80 | 0.85 | 0.90 | 0.771 | 7.14 | 10.86 |

Teto: 20 s por pergunta. Pior caso de cada índice somado: 11.24 s (as consultas dos dois índices são diferentes; o teto vale para a soma na mesma pergunta).

## Posição do primeiro acerto, por consulta

**regras**: teste_022 1 (0.3 s); teste_023 1 (0.4 s); teste_038 16 (0.3 s); teste_043 9 (0.2 s); teste_054 21 (0.3 s); teste_061 2 (0.4 s); teste_074 1 (0.3 s); teste_083 2 (0.3 s); teste_099 3 (0.3 s); teste_107 1 (0.3 s); teste_116 4 (0.4 s); teste_119 1 (0.3 s); teste_125 6 (0.3 s); teste_165 3 (0.3 s); teste_168 1 (0.3 s); teste_171 1 (0.3 s); teste_187 2 (0.3 s); teste_202 1 (0.4 s); teste_214 1 (0.3 s); teste_242 1 (0.3 s)

**manual**: mteste_01 1 (4.4 s); mteste_02 1 (8.1 s); mteste_03 1 (5.4 s); mteste_04 5 (7.6 s); mteste_05 1 (4.0 s); mteste_06 1 (7.7 s); mteste_07 1 (10.9 s); mteste_08 1 (9.1 s); mteste_09 2 (5.8 s); mteste_10 44 (7.4 s); mteste_11 1 (7.7 s); mteste_12 9 (3.6 s); mteste_13 1 (2.7 s); mteste_14 1 (6.7 s); mteste_15 1 (6.9 s); mteste_16 1 (3.2 s); mteste_17 1 (3.4 s); mteste_18 2 (8.5 s); mteste_19 13 (7.7 s); mteste_20 1 (9.1 s)

## Carregamento e aquecimento (fora do teto; segundos)

embedding 43.32, indice_regras 1.22, aquecimento_regras_0 44.92, indice_manual 0.52, reranker_2048 5.48, aquecimento_manual_2048 8.2
