# Avaliação da recuperação (Entrega 2) - conjunto: dev (14 consultas)

## Variante: sem_pontos

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| vetor | 14 | 0.36 | 0.50 | 0.50 | 0.50 | 0.452 |
| vetor + rerank(50) | 14 | 0.50 | 0.71 | 0.71 | 0.86 | 0.633 |
| híbrido (vetor+BM25) | 14 | 0.36 | 0.86 | 0.86 | 0.93 | 0.589 |
| híbrido + rerank(50) | 14 | 0.57 | 0.79 | 0.79 | 0.93 | 0.699 |

## sem_pontos - vetor

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.36 | 0.50 | 0.50 | 0.50 | 0.452 |
| imagem | 3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.044 |
| sintetica | 11 | 0.45 | 0.64 | 0.64 | 0.64 | 0.564 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 40 | Regra 156 (0.7516)<br>Regra 141 (0.7444)<br>Regra 086 (0.7436) |
| img_maxlub | imagem | 29 | Regra 156 (0.7947)<br>Regra 129 (0.7767)<br>Regra regra_050 (0.7679) |
| img_v1vidros | imagem | 14 | Regra regra_047 (0.8065)<br>Regra 156 (0.8042)<br>Regra regra_050 (0.8035) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.8157)<br>Regra 136 (0.7188)<br>Regra Hospidrogas (0.7077) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.8047)<br>Regra 105 (0.7809)<br>Regra regra_047 (0.7782) |
| sint_prospeccao_50_53 | sintetica | 2 | Regra 075 (0.7995)<br>Regra 056 (0.796)<br>Regra 105 (0.7875) |
| sint_quinzenal_mensal | sintetica | 89 | Regra 238 (0.7524)<br>Regra 240 (0.7394)<br>Regra 217 (0.7337) |
| sint_bloqueios_rota_hoje | sintetica | 24 | Regra 156 (0.8274)<br>Regra 129 (0.7962)<br>Regra regra_029 (0.7895) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.7757)<br>Regra 156 (0.754)<br>Regra 138 (0.7496) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.8448)<br>Regra 087 (0.8386)<br>Regra 106 (0.8298) |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | Regra 079 (0.7565)<br>Regra Hospidrogas (0.6922)<br>Regra 161 (0.6917) |
| sint_campo_pf_ramo17 | sintetica | 16 | Regra 075 (0.8104)<br>Regra 106 (0.809)<br>Regra 119 (0.8051) |
| sint_30_dias_sem_choque | sintetica | 1 | Regra 063 (0.768)<br>Regra 124 (0.7532)<br>Regra 102 (0.7502) |
| sint_regra_grande_regioes | sintetica | 12 | Regra 180 (0.6857)<br>Regra 201 (0.6644)<br>Regra 168 (0.66) |

## sem_pontos - vetor + rerank(50)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.50 | 0.71 | 0.71 | 0.86 | 0.633 |
| imagem | 3 | 0.00 | 0.00 | 0.00 | 0.67 | 0.115 |
| sintetica | 11 | 0.64 | 0.91 | 0.91 | 0.91 | 0.774 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 15 | Regra Maxlub (0.9112)<br>Regra regra_049 (0.9085)<br>Regra 224 (0.9041) |
| img_maxlub | imagem | 6 | Regra 156 (0.8613)<br>Regra 244 (0.8213)<br>Regra 230 (0.7884) |
| img_v1vidros | imagem | 9 | Regra regra_049 (0.9642)<br>Regra Maxlub (0.8835)<br>Regra 230 (0.8752) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.9951)<br>Regra 136 (0.9885)<br>Regra 241 (0.9691) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.9982)<br>Regra 085 (0.9027)<br>Regra regra_050 (0.8363) |
| sint_prospeccao_50_53 | sintetica | 1 | Regra 056 (0.995)<br>Regra 122 (0.981)<br>Regra 075 (0.9777) |
| sint_quinzenal_mensal | sintetica | 89 | Regra 221 (0.9666)<br>Regra Goiás Clean (0.9664)<br>Regra 217 (0.9564) |
| sint_bloqueios_rota_hoje | sintetica | 1 | Regra 076 (0.9986)<br>Regra 244 (0.99)<br>Regra 171 (0.9892) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.9994)<br>Regra 201 (0.9951)<br>Regra 208 (0.9942) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.9956)<br>Regra 087 (0.9912)<br>Regra 058 (0.99) |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | Regra 136 (0.9465)<br>Regra Hospidrogas (0.9423)<br>Regra 246 (0.914) |
| sint_campo_pf_ramo17 | sintetica | 1 | Regra 068 Playpet (0.9938)<br>Regra 122 (0.9875)<br>Regra 101 (0.978) |
| sint_30_dias_sem_choque | sintetica | 2 | Regra 124 (0.9979)<br>Regra 063 (0.9959)<br>Regra 102 (0.9945) |
| sint_regra_grande_regioes | sintetica | 2 | Regra 246 (0.9953)<br>Regra 032 (0.988)<br>Regra 180 (0.9867) |

## sem_pontos - híbrido (vetor+BM25)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.36 | 0.86 | 0.86 | 0.93 | 0.589 |
| imagem | 3 | 0.00 | 0.67 | 0.67 | 1.00 | 0.389 |
| sintetica | 11 | 0.45 | 0.91 | 0.91 | 0.91 | 0.643 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 6 | Regra regra_049 (0.0276)<br>Regra 229 (0.0274)<br>Regra 150 (0.0272) |
| img_maxlub | imagem | 2 | Regra 224 (0.0271)<br>Regra Maxlub (0.0271)<br>Regra 173 (0.0265) |
| img_v1vidros | imagem | 2 | Regra regra_049 (0.0315)<br>Regra V1 Vidros (0.0294)<br>Regra 191 (0.0289) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.0328)<br>Regra Hospidrogas (0.032)<br>Regra 136 (0.0318) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.0328)<br>Regra 113 (0.0315)<br>Regra regra_047 (0.0313) |
| sint_prospeccao_50_53 | sintetica | 1 | Regra 056 (0.0325)<br>Regra 113 (0.0312)<br>Regra regra_047 (0.0308) |
| sint_quinzenal_mensal | sintetica | 13 | Regra Goiás Clean (0.0284)<br>Regra 212 (0.028)<br>Regra 226 (0.0271) |
| sint_bloqueios_rota_hoje | sintetica | 3 | Regra 244 (0.0312)<br>Regra 171 (0.0289)<br>Regra 076 (0.0283) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.0323)<br>Regra 138 (0.0292)<br>Regra 076 (0.0288) |
| sint_televendas_x_campo | sintetica | 2 | Regra 087 (0.0323)<br>Regra 091 (0.0315)<br>Regra 048 (0.0313) |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | Regra 079 (0.0325)<br>Regra Hospidrogas (0.0325)<br>Regra 136 (0.0315) |
| sint_campo_pf_ramo17 | sintetica | 3 | Regra 106 (0.0323)<br>Regra 119 (0.0315)<br>Regra 068 Playpet (0.0296) |
| sint_30_dias_sem_choque | sintetica | 1 | Regra 063 (0.0323)<br>Regra 124 (0.0323)<br>Regra VetVida (0.0303) |
| sint_regra_grande_regioes | sintetica | 3 | Regra 180 (0.0311)<br>Regra 241 (0.0303)<br>Regra 032 (0.0303) |

## sem_pontos - híbrido + rerank(50)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.57 | 0.79 | 0.79 | 0.93 | 0.699 |
| imagem | 3 | 0.00 | 0.00 | 0.00 | 0.67 | 0.094 |
| sintetica | 11 | 0.73 | 1.00 | 1.00 | 1.00 | 0.864 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 22 | Regra Maxlub (0.9112)<br>Regra regra_049 (0.9085)<br>Regra 224 (0.9041) |
| img_maxlub | imagem | 8 | Regra 156 (0.8613)<br>Regra 244 (0.8213)<br>Regra 230 (0.7884) |
| img_v1vidros | imagem | 9 | Regra regra_049 (0.9642)<br>Regra Maxlub (0.8835)<br>Regra 230 (0.8752) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.9951)<br>Regra 136 (0.9885)<br>Regra 241 (0.9691) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.9982)<br>Regra 085 (0.9027)<br>Regra regra_050 (0.8363) |
| sint_prospeccao_50_53 | sintetica | 1 | Regra 056 (0.995)<br>Regra 122 (0.981)<br>Regra 075 (0.9777) |
| sint_quinzenal_mensal | sintetica | 1 | Regra 065 (0.9956)<br>Regra 221 (0.9666)<br>Regra Goiás Clean (0.9664) |
| sint_bloqueios_rota_hoje | sintetica | 1 | Regra 076 (0.9986)<br>Regra 244 (0.99)<br>Regra 171 (0.9892) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.9994)<br>Regra 155 (0.996)<br>Regra 201 (0.9951) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.9956)<br>Regra 087 (0.9912)<br>Regra 058 (0.99) |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | Regra 136 (0.9465)<br>Regra Hospidrogas (0.9423)<br>Regra 246 (0.914) |
| sint_campo_pf_ramo17 | sintetica | 1 | Regra 068 Playpet (0.9938)<br>Regra 122 (0.9875)<br>Regra 101 (0.978) |
| sint_30_dias_sem_choque | sintetica | 2 | Regra 124 (0.9979)<br>Regra 063 (0.9959)<br>Regra 102 (0.9945) |
| sint_regra_grande_regioes | sintetica | 2 | Regra 246 (0.9953)<br>Regra 032 (0.988)<br>Regra 180 (0.9867) |

### vetor x vetor + rerank(50)

Teto do re-ranking: em **13/14** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| img_infinitto | imagem | 40 | 15 | melhorou |
| img_maxlub | imagem | 29 | 6 | melhorou |
| img_v1vidros | imagem | 14 | 9 | melhorou |
| sint_ramos_12_19 | sintetica | 1 | 1 | igual |
| sint_vendedora_sandra | sintetica | 1 | 1 | igual |
| sint_prospeccao_50_53 | sintetica | 2 | 1 | melhorou |
| sint_quinzenal_mensal | sintetica | 89 | 89 | igual |
| sint_bloqueios_rota_hoje | sintetica | 24 | 1 | melhorou |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | 1 | igual |
| sint_televendas_x_campo | sintetica | 1 | 1 | igual |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | 2 | igual |
| sint_campo_pf_ramo17 | sintetica | 16 | 1 | melhorou |
| sint_30_dias_sem_choque | sintetica | 1 | 2 | piorou |
| sint_regra_grande_regioes | sintetica | 12 | 2 | melhorou |

### vetor x híbrido (vetor+BM25)

Teto do re-ranking: em **13/14** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| img_infinitto | imagem | 40 | 6 | melhorou |
| img_maxlub | imagem | 29 | 2 | melhorou |
| img_v1vidros | imagem | 14 | 2 | melhorou |
| sint_ramos_12_19 | sintetica | 1 | 1 | igual |
| sint_vendedora_sandra | sintetica | 1 | 1 | igual |
| sint_prospeccao_50_53 | sintetica | 2 | 1 | melhorou |
| sint_quinzenal_mensal | sintetica | 89 | 13 | melhorou |
| sint_bloqueios_rota_hoje | sintetica | 24 | 3 | melhorou |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | 1 | igual |
| sint_televendas_x_campo | sintetica | 1 | 2 | piorou |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | 2 | igual |
| sint_campo_pf_ramo17 | sintetica | 16 | 3 | melhorou |
| sint_30_dias_sem_choque | sintetica | 1 | 1 | igual |
| sint_regra_grande_regioes | sintetica | 12 | 3 | melhorou |

### vetor x híbrido + rerank(50)

Teto do re-ranking: em **13/14** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| img_infinitto | imagem | 40 | 22 | melhorou |
| img_maxlub | imagem | 29 | 8 | melhorou |
| img_v1vidros | imagem | 14 | 9 | melhorou |
| sint_ramos_12_19 | sintetica | 1 | 1 | igual |
| sint_vendedora_sandra | sintetica | 1 | 1 | igual |
| sint_prospeccao_50_53 | sintetica | 2 | 1 | melhorou |
| sint_quinzenal_mensal | sintetica | 89 | 1 | melhorou |
| sint_bloqueios_rota_hoje | sintetica | 24 | 1 | melhorou |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | 1 | igual |
| sint_televendas_x_campo | sintetica | 1 | 1 | igual |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | 2 | igual |
| sint_campo_pf_ramo17 | sintetica | 16 | 1 | melhorou |
| sint_30_dias_sem_choque | sintetica | 1 | 2 | piorou |
| sint_regra_grande_regioes | sintetica | 12 | 2 | melhorou |

## Variante: com_pontos

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| vetor | 14 | 0.29 | 0.50 | 0.50 | 0.50 | 0.390 |
| vetor + rerank(50) | 14 | 0.57 | 0.86 | 0.86 | 0.86 | 0.697 |
| híbrido (vetor+BM25) | 14 | 0.43 | 0.71 | 0.86 | 0.93 | 0.606 |
| híbrido + rerank(50) | 14 | 0.64 | 0.93 | 0.93 | 0.93 | 0.766 |

## com_pontos - vetor

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.29 | 0.50 | 0.50 | 0.50 | 0.390 |
| imagem | 3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.048 |
| sintetica | 11 | 0.36 | 0.64 | 0.64 | 0.64 | 0.483 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 47 | Regra 156 (0.7516)<br>Regra 141 (0.7444)<br>Regra 211 (0.732) |
| img_maxlub | imagem | 18 | Regra 156 (0.7947)<br>Regra 129 (0.7767)<br>Regra 150 (0.7639) |
| img_v1vidros | imagem | 15 | Regra 156 (0.8042)<br>Regra regra_029 (0.803)<br>Regra 129 (0.7995) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.8157)<br>Regra 136 (0.7075)<br>Regra 241 (0.7007) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.8047)<br>Regra 086 (0.7656)<br>Regra 105 (0.7651) |
| sint_prospeccao_50_53 | sintetica | 3 | Regra 075 (0.7896)<br>Regra 156 (0.7839)<br>Regra 056 (0.7773) |
| sint_quinzenal_mensal | sintetica | 81 | Regra 238 (0.747)<br>Regra 240 (0.7394)<br>Regra 150 (0.7289) |
| sint_bloqueios_rota_hoje | sintetica | 18 | Regra 156 (0.8274)<br>Regra 129 (0.7962)<br>Regra regra_029 (0.7895) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.7757)<br>Regra 156 (0.754)<br>Regra 138 (0.7496) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.8206)<br>Regra 106 (0.8164)<br>Regra 087 (0.815) |
| sint_ramo_e_ciclo_de_vida | sintetica | 3 | Regra 079 (0.7565)<br>Regra 161 (0.6917)<br>Regra Hospidrogas (0.6875) |
| sint_campo_pf_ramo17 | sintetica | 23 | Regra 172 (0.8041)<br>Regra 133 (0.7993)<br>Regra 075 (0.7989) |
| sint_30_dias_sem_choque | sintetica | 2 | Regra 102 (0.7502)<br>Regra 063 (0.7361)<br>Regra 133 (0.7321) |
| sint_regra_grande_regioes | sintetica | 25 | Regra 180 (0.6857)<br>Regra 201 (0.6644)<br>Regra 192 (0.6546) |

## com_pontos - vetor + rerank(50)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.57 | 0.86 | 0.86 | 0.86 | 0.697 |
| imagem | 3 | 0.00 | 0.67 | 0.67 | 0.67 | 0.248 |
| sintetica | 11 | 0.73 | 0.91 | 0.91 | 0.91 | 0.819 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 13 | Regra 194 (0.9391)<br>Regra Maxlub (0.9172)<br>Regra regra_049 (0.9137) |
| img_maxlub | imagem | 3 | Regra 230 (0.8752)<br>Regra 156 (0.8613)<br>Regra Maxlub (0.7607) |
| img_v1vidros | imagem | 3 | Regra regra_049 (0.9647)<br>Regra Maxlub (0.8883)<br>Regra V1 Vidros (0.8874) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.9951)<br>Regra 136 (0.9871)<br>Regra 241 (0.9691) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.9982)<br>Regra 085 (0.9027)<br>Regra regra_029 (0.7457) |
| sint_prospeccao_50_53 | sintetica | 1 | Regra 056 (0.994)<br>Regra 122 (0.9846)<br>Regra 075 (0.9803) |
| sint_quinzenal_mensal | sintetica | 81 | Regra Goiás Clean (0.972)<br>Regra 221 (0.9621)<br>Regra Supergiro (0.9481) |
| sint_bloqueios_rota_hoje | sintetica | 1 | Regra 076 (0.9986)<br>Regra 244 (0.989)<br>Regra 196 (0.9834) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.9994)<br>Regra 201 (0.9951)<br>Regra 076 (0.9932) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.991)<br>Regra 058 (0.985)<br>Regra 087 (0.9755) |
| sint_ramo_e_ciclo_de_vida | sintetica | 1 | Regra Hospidrogas (0.942)<br>Regra 136 (0.9181)<br>Regra 246 (0.9051) |
| sint_campo_pf_ramo17 | sintetica | 1 | Regra 068 Playpet (0.9931)<br>Regra VetVida (0.9881)<br>Regra 122 (0.9837) |
| sint_30_dias_sem_choque | sintetica | 2 | Regra 124 (0.9978)<br>Regra 063 (0.9951)<br>Regra 102 (0.9945) |
| sint_regra_grande_regioes | sintetica | 2 | Regra 246 (0.9953)<br>Regra 032 (0.988)<br>Regra 182 (0.9869) |

## com_pontos - híbrido (vetor+BM25)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.43 | 0.71 | 0.86 | 0.93 | 0.606 |
| imagem | 3 | 0.33 | 0.67 | 0.67 | 1.00 | 0.537 |
| sintetica | 11 | 0.45 | 0.73 | 0.91 | 0.91 | 0.625 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 9 | Regra 194 (0.0291)<br>Regra Maxlub (0.029)<br>Regra 229 (0.0284) |
| img_maxlub | imagem | 1 | Regra Maxlub (0.0287)<br>Regra 173 (0.0275)<br>Regra 224 (0.0274) |
| img_v1vidros | imagem | 2 | Regra regra_049 (0.0315)<br>Regra V1 Vidros (0.0292)<br>Regra 194 (0.029) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.0328)<br>Regra 136 (0.0318)<br>Regra Hospidrogas (0.0318) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.0328)<br>Regra 086 (0.0313)<br>Regra 113 (0.0306) |
| sint_prospeccao_50_53 | sintetica | 1 | Regra 056 (0.0323)<br>Regra regra_047 (0.0315)<br>Regra 113 (0.0297) |
| sint_quinzenal_mensal | sintetica | 11 | Regra 212 (0.029)<br>Regra Goiás Clean (0.0269)<br>Regra 226 (0.0269) |
| sint_bloqueios_rota_hoje | sintetica | 2 | Regra 244 (0.0299)<br>Regra 076 (0.0292)<br>Regra 173 (0.0279) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.0323)<br>Regra 076 (0.0289)<br>Regra 138 (0.0287) |
| sint_televendas_x_campo | sintetica | 3 | Regra 048 (0.032)<br>Regra 087 (0.032)<br>Regra 091 (0.0318) |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | Regra 079 (0.0325)<br>Regra Hospidrogas (0.0323)<br>Regra 136 (0.0313) |
| sint_campo_pf_ramo17 | sintetica | 4 | Regra 106 (0.0318)<br>Regra 119 (0.0305)<br>Regra VetVida (0.0284) |
| sint_30_dias_sem_choque | sintetica | 1 | Regra 063 (0.032)<br>Regra 124 (0.0313)<br>Regra 102 (0.0303) |
| sint_regra_grande_regioes | sintetica | 5 | Regra 241 (0.0315)<br>Regra 180 (0.0313)<br>Regra 197 (0.0295) |

## com_pontos - híbrido + rerank(50)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.64 | 0.93 | 0.93 | 0.93 | 0.766 |
| imagem | 3 | 0.00 | 0.67 | 0.67 | 0.67 | 0.241 |
| sintetica | 11 | 0.82 | 1.00 | 1.00 | 1.00 | 0.909 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 18 | Regra 197 (0.9541)<br>Regra 194 (0.9391)<br>Regra Maxlub (0.9172) |
| img_maxlub | imagem | 3 | Regra 230 (0.8752)<br>Regra 156 (0.8613)<br>Regra Maxlub (0.7607) |
| img_v1vidros | imagem | 3 | Regra regra_049 (0.9647)<br>Regra Maxlub (0.8883)<br>Regra V1 Vidros (0.8874) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.9951)<br>Regra 136 (0.9871)<br>Regra 241 (0.9691) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.9982)<br>Regra 085 (0.9027)<br>Regra regra_029 (0.7457) |
| sint_prospeccao_50_53 | sintetica | 1 | Regra 056 (0.994)<br>Regra 122 (0.9846)<br>Regra 075 (0.9803) |
| sint_quinzenal_mensal | sintetica | 1 | Regra 065 (0.9956)<br>Regra Goiás Clean (0.972)<br>Regra 171 (0.9641) |
| sint_bloqueios_rota_hoje | sintetica | 1 | Regra 076 (0.9986)<br>Regra 244 (0.989)<br>Regra 171 (0.9881) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.9994)<br>Regra 155 (0.996)<br>Regra 201 (0.9951) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.991)<br>Regra 058 (0.985)<br>Regra 087 (0.9755) |
| sint_ramo_e_ciclo_de_vida | sintetica | 1 | Regra Hospidrogas (0.942)<br>Regra 136 (0.9181)<br>Regra 246 (0.9051) |
| sint_campo_pf_ramo17 | sintetica | 1 | Regra 068 Playpet (0.9931)<br>Regra VetVida (0.9881)<br>Regra 122 (0.9837) |
| sint_30_dias_sem_choque | sintetica | 2 | Regra 124 (0.9978)<br>Regra 063 (0.9951)<br>Regra 102 (0.9945) |
| sint_regra_grande_regioes | sintetica | 2 | Regra 246 (0.9953)<br>Regra 032 (0.988)<br>Regra 182 (0.9869) |

### vetor x vetor + rerank(50)

Teto do re-ranking: em **13/14** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| img_infinitto | imagem | 47 | 13 | melhorou |
| img_maxlub | imagem | 18 | 3 | melhorou |
| img_v1vidros | imagem | 15 | 3 | melhorou |
| sint_ramos_12_19 | sintetica | 1 | 1 | igual |
| sint_vendedora_sandra | sintetica | 1 | 1 | igual |
| sint_prospeccao_50_53 | sintetica | 3 | 1 | melhorou |
| sint_quinzenal_mensal | sintetica | 81 | 81 | igual |
| sint_bloqueios_rota_hoje | sintetica | 18 | 1 | melhorou |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | 1 | igual |
| sint_televendas_x_campo | sintetica | 1 | 1 | igual |
| sint_ramo_e_ciclo_de_vida | sintetica | 3 | 1 | melhorou |
| sint_campo_pf_ramo17 | sintetica | 23 | 1 | melhorou |
| sint_30_dias_sem_choque | sintetica | 2 | 2 | igual |
| sint_regra_grande_regioes | sintetica | 25 | 2 | melhorou |

### vetor x híbrido (vetor+BM25)

Teto do re-ranking: em **13/14** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| img_infinitto | imagem | 47 | 9 | melhorou |
| img_maxlub | imagem | 18 | 1 | melhorou |
| img_v1vidros | imagem | 15 | 2 | melhorou |
| sint_ramos_12_19 | sintetica | 1 | 1 | igual |
| sint_vendedora_sandra | sintetica | 1 | 1 | igual |
| sint_prospeccao_50_53 | sintetica | 3 | 1 | melhorou |
| sint_quinzenal_mensal | sintetica | 81 | 11 | melhorou |
| sint_bloqueios_rota_hoje | sintetica | 18 | 2 | melhorou |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | 1 | igual |
| sint_televendas_x_campo | sintetica | 1 | 3 | piorou |
| sint_ramo_e_ciclo_de_vida | sintetica | 3 | 2 | melhorou |
| sint_campo_pf_ramo17 | sintetica | 23 | 4 | melhorou |
| sint_30_dias_sem_choque | sintetica | 2 | 1 | melhorou |
| sint_regra_grande_regioes | sintetica | 25 | 5 | melhorou |

### vetor x híbrido + rerank(50)

Teto do re-ranking: em **13/14** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| img_infinitto | imagem | 47 | 18 | melhorou |
| img_maxlub | imagem | 18 | 3 | melhorou |
| img_v1vidros | imagem | 15 | 3 | melhorou |
| sint_ramos_12_19 | sintetica | 1 | 1 | igual |
| sint_vendedora_sandra | sintetica | 1 | 1 | igual |
| sint_prospeccao_50_53 | sintetica | 3 | 1 | melhorou |
| sint_quinzenal_mensal | sintetica | 81 | 1 | melhorou |
| sint_bloqueios_rota_hoje | sintetica | 18 | 1 | melhorou |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | 1 | igual |
| sint_televendas_x_campo | sintetica | 1 | 1 | igual |
| sint_ramo_e_ciclo_de_vida | sintetica | 3 | 1 | melhorou |
| sint_campo_pf_ramo17 | sintetica | 23 | 1 | melhorou |
| sint_30_dias_sem_choque | sintetica | 2 | 2 | igual |
| sint_regra_grande_regioes | sintetica | 25 | 2 | melhorou |
