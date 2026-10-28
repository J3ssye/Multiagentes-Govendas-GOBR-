# Avaliação da recuperação (Entrega 2)

## Variante: sem_pontos (só busca vetorial)

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

## Variante: sem_pontos + re-ranking (50 candidatos)

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
