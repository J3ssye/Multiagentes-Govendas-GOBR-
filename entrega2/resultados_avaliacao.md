# Avaliação da recuperação (Entrega 2)

## Variante: sem_pontos

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
| sint_quinzenal_mensal | sintetica | 80 | Regra 238 (0.7483)<br>Regra 240 (0.7357)<br>Regra 150 (0.7355) |
| sint_bloqueios_rota_hoje | sintetica | 24 | Regra 156 (0.8274)<br>Regra 129 (0.7962)<br>Regra regra_029 (0.7895) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.7757)<br>Regra 156 (0.754)<br>Regra 138 (0.7496) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.8448)<br>Regra 087 (0.8386)<br>Regra 106 (0.8298) |
| sint_ramo_e_ciclo_de_vida | sintetica | 2 | Regra 079 (0.7565)<br>Regra Hospidrogas (0.6922)<br>Regra 161 (0.6917) |
| sint_campo_pf_ramo17 | sintetica | 16 | Regra 075 (0.8104)<br>Regra 106 (0.809)<br>Regra 119 (0.8051) |
| sint_30_dias_sem_choque | sintetica | 1 | Regra 063 (0.768)<br>Regra 124 (0.7532)<br>Regra 102 (0.7502) |
| sint_regra_grande_regioes | sintetica | 12 | Regra 180 (0.6857)<br>Regra 201 (0.6644)<br>Regra 168 (0.66) |

## Variante: com_pontos

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 14 | 0.29 | 0.50 | 0.50 | 0.50 | 0.390 |
| imagem | 3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.048 |
| sintetica | 11 | 0.36 | 0.64 | 0.64 | 0.64 | 0.484 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| img_infinitto | imagem | 47 | Regra 156 (0.7516)<br>Regra 141 (0.7444)<br>Regra 211 (0.732) |
| img_maxlub | imagem | 18 | Regra 156 (0.7947)<br>Regra 129 (0.7767)<br>Regra 150 (0.7639) |
| img_v1vidros | imagem | 15 | Regra 156 (0.8042)<br>Regra regra_029 (0.803)<br>Regra 129 (0.7995) |
| sint_ramos_12_19 | sintetica | 1 | Regra 079 (0.8157)<br>Regra 136 (0.7075)<br>Regra 241 (0.7007) |
| sint_vendedora_sandra | sintetica | 1 | Regra Milenium (0.8047)<br>Regra 086 (0.7656)<br>Regra 105 (0.7651) |
| sint_prospeccao_50_53 | sintetica | 3 | Regra 075 (0.7896)<br>Regra 156 (0.7839)<br>Regra 056 (0.7773) |
| sint_quinzenal_mensal | sintetica | 68 | Regra 238 (0.7425)<br>Regra 240 (0.7357)<br>Regra 150 (0.7355) |
| sint_bloqueios_rota_hoje | sintetica | 18 | Regra 156 (0.8274)<br>Regra 129 (0.7962)<br>Regra regra_029 (0.7895) |
| sint_bloqueio_30d_prospect_14_ativo_7 | sintetica | 1 | Regra 077 (0.7757)<br>Regra 156 (0.754)<br>Regra 138 (0.7496) |
| sint_televendas_x_campo | sintetica | 1 | Regra 091 (0.8206)<br>Regra 106 (0.8164)<br>Regra 087 (0.815) |
| sint_ramo_e_ciclo_de_vida | sintetica | 3 | Regra 079 (0.7565)<br>Regra 161 (0.6917)<br>Regra Hospidrogas (0.6875) |
| sint_campo_pf_ramo17 | sintetica | 23 | Regra 172 (0.8041)<br>Regra 133 (0.7993)<br>Regra 075 (0.7989) |
| sint_30_dias_sem_choque | sintetica | 2 | Regra 102 (0.7502)<br>Regra 063 (0.7361)<br>Regra 133 (0.7321) |
| sint_regra_grande_regioes | sintetica | 25 | Regra 180 (0.6857)<br>Regra 201 (0.6644)<br>Regra 192 (0.6546) |
