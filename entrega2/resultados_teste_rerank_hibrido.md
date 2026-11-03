# Avaliação da recuperação (Entrega 2) - conjunto: teste (20 consultas)

## Variante: sem_pontos

| configuração | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| vetor | 20 | 0.25 | 0.50 | 0.55 | 0.60 | 0.399 |
| vetor + rerank(50) | 20 | 0.75 | 0.95 | 0.95 | 0.95 | 0.844 |
| híbrido (vetor+BM25) | 20 | 0.45 | 0.75 | 0.80 | 0.90 | 0.615 |
| híbrido + rerank(50) | 20 | 0.75 | 0.95 | 0.95 | 0.95 | 0.844 |

## sem_pontos - vetor

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 20 | 0.25 | 0.50 | 0.55 | 0.60 | 0.399 |
| imagem | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.000 |
| sintetica | 20 | 0.25 | 0.50 | 0.55 | 0.60 | 0.399 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| teste_022 | sintetica | 2 | Regra 207 (0.7345)<br>Regra Supergiro (0.7344)<br>Regra 219 (0.7287) |
| teste_023 | sintetica | 8 | Regra 087 (0.7684)<br>Regra 070 (0.7549)<br>Regra 075 (0.7545) |
| teste_038 | sintetica | 11 | Regra 086 (0.815)<br>Regra regra_047 (0.8069)<br>Regra regra_050 (0.8016) |
| teste_043 | sintetica | 1 | Regra regra_043 (0.6786)<br>Regra regra_029 (0.6723)<br>Regra NB PI (0.6471) |
| teste_054 | sintetica | 24 | Regra 156 (0.7958)<br>Regra 075 (0.7941)<br>Regra 113 (0.7857) |
| teste_061 | sintetica | 18 | Regra VetVida (0.8333)<br>Regra 091 (0.8232)<br>Regra 230 (0.82) |
| teste_074 | sintetica | 17 | Regra 105 (0.7808)<br>Regra regra_047 (0.7569)<br>Regra 141 (0.7568) |
| teste_083 | sintetica | 3 | Regra 073 (0.7791)<br>Regra Mais Descartaveis (0.7478)<br>Regra 083 Brida (0.7232) |
| teste_099 | sintetica | 5 | Regra 075 (0.8049)<br>Regra 230 (0.8022)<br>Regra 119 (0.7981) |
| teste_107 | sintetica | 2 | Regra 105 (0.7573)<br>Regra 107 (0.7495)<br>Regra 157 (0.7424) |
| teste_116 | sintetica | 12 | Regra 087 (0.7768)<br>Regra 070 (0.7719)<br>Regra 075 (0.7701) |
| teste_119 | sintetica | 2 | Regra 075 (0.8202)<br>Regra 119 (0.8145)<br>Regra 122 (0.8004) |
| teste_125 | sintetica | 31 | Regra regra_050 (0.8172)<br>Regra 086 (0.8138)<br>Regra regra_047 (0.81) |
| teste_165 | sintetica | 21 | Regra 122 (0.8279)<br>Regra 075 (0.8236)<br>Regra 230 (0.822) |
| teste_168 | sintetica | 3 | Regra 231 (0.7492)<br>Regra 236 (0.7451)<br>Regra 168 (0.744) |
| teste_171 | sintetica | 1 | Regra 171 (0.8097)<br>Regra 185 (0.8082)<br>Regra 192 (0.7877) |
| teste_187 | sintetica | 12 | Regra 219 (0.8001)<br>Regra 185 (0.7935)<br>Regra 224 (0.7928) |
| teste_202 | sintetica | 1 | Regra 202 (0.7676)<br>Regra 217 (0.7616)<br>Regra 152 (0.7587) |
| teste_214 | sintetica | 1 | Regra 214 (0.7655)<br>Regra 237 (0.7528)<br>Regra 199 (0.7527) |
| teste_242 | sintetica | 1 | Regra 242 (0.7737)<br>Regra 202 (0.7528)<br>Regra 217 (0.7508) |

## sem_pontos - vetor + rerank(50)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 20 | 0.75 | 0.95 | 0.95 | 0.95 | 0.844 |
| imagem | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.000 |
| sintetica | 20 | 0.75 | 0.95 | 0.95 | 0.95 | 0.844 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| teste_022 | sintetica | 1 | Regra Supergiro (0.9973)<br>Regra VetVida (0.9925)<br>Regra Goiás Clean (0.9923) |
| teste_023 | sintetica | 1 | Regra BSB Vet (0.9851)<br>Regra 108 (0.9033)<br>Regra 230 (0.9003) |
| teste_038 | sintetica | 19 | Regra 105 (0.9852)<br>Regra Armazém Santa Maria (0.9784)<br>Regra 101 (0.9771) |
| teste_043 | sintetica | 3 | Regra regra_029 (0.9713)<br>Regra 105 (0.962)<br>Regra regra_043 (0.9618) |
| teste_054 | sintetica | 1 | Regra 054 (0.9971)<br>Regra NB PI (0.9965)<br>Regra 122 (0.9954) |
| teste_061 | sintetica | 1 | Regra 061 (0.9962)<br>Regra 122 (0.9877)<br>Regra 101 (0.9868) |
| teste_074 | sintetica | 1 | Regra 074 Bela Forma (0.9904)<br>Regra Makro Services (0.9615)<br>Regra Armazém Santa Maria (0.9264) |
| teste_083 | sintetica | 2 | Regra Padrão goVendas Customizável (0.9808)<br>Regra 083 Brida (0.9697)<br>Regra 073 (0.9544) |
| teste_099 | sintetica | 1 | Regra 099 (0.996)<br>Regra 101 (0.9948)<br>Regra 075 (0.991) |
| teste_107 | sintetica | 1 | Regra 107 (0.9996)<br>Regra Makro Services (0.9916)<br>Regra 074 Bela Forma (0.981) |
| teste_116 | sintetica | 1 | Regra 116 (0.9863)<br>Regra 172 (0.9594)<br>Regra 181 (0.9484) |
| teste_119 | sintetica | 1 | Regra 119 (0.9973)<br>Regra 058 (0.9929)<br>Regra 075 (0.9908) |
| teste_125 | sintetica | 2 | Regra 156 (0.9883)<br>Regra 125 (0.9853)<br>Regra regra_050 (0.983) |
| teste_165 | sintetica | 1 | Regra Chegatto (0.9974)<br>Regra 209 (0.9936)<br>Regra 171 (0.993) |
| teste_168 | sintetica | 1 | Regra 168 (0.9995)<br>Regra 236 (0.9993)<br>Regra 245 (0.9951) |
| teste_171 | sintetica | 1 | Regra 171 (0.9988)<br>Regra 201 (0.998)<br>Regra 158 (0.9976) |
| teste_187 | sintetica | 2 | Regra 203 (0.9989)<br>Regra 187 (0.9988)<br>Regra 173 (0.9975) |
| teste_202 | sintetica | 1 | Regra 202 (0.9871)<br>Regra 237 (0.9767)<br>Regra 152 (0.9725) |
| teste_214 | sintetica | 1 | Regra 214 (0.9974)<br>Regra 174 (0.9898)<br>Regra 171 (0.9849) |
| teste_242 | sintetica | 1 | Regra 242 (0.9921)<br>Regra 190 (0.9322)<br>Regra 184 (0.9284) |

## sem_pontos - híbrido (vetor+BM25)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 20 | 0.45 | 0.75 | 0.80 | 0.90 | 0.615 |
| imagem | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.000 |
| sintetica | 20 | 0.45 | 0.75 | 0.80 | 0.90 | 0.615 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| teste_022 | sintetica | 1 | Regra Supergiro (0.0325)<br>Regra 124 (0.0301)<br>Regra 066 (0.0284) |
| teste_023 | sintetica | 1 | Regra BSB Vet (0.0311)<br>Regra 087 (0.0303)<br>Regra 058 (0.0289) |
| teste_038 | sintetica | 23 | Regra regra_050 (0.0313)<br>Regra 113 (0.029)<br>Regra 048 (0.027) |
| teste_043 | sintetica | 9 | Regra NB PI (0.031)<br>Regra regra_050 (0.0303)<br>Regra 220 (0.0274) |
| teste_054 | sintetica | 18 | Regra 113 (0.0317)<br>Regra 122 (0.0293)<br>Regra regra_050 (0.0289) |
| teste_061 | sintetica | 3 | Regra VetVida (0.0305)<br>Regra 087 (0.0294)<br>Regra 061 (0.0292) |
| teste_074 | sintetica | 2 | Regra 113 (0.0308)<br>Regra 074 Bela Forma (0.0294)<br>Regra 162 (0.0257) |
| teste_083 | sintetica | 2 | Regra MGR (0.032)<br>Regra 083 Brida (0.0315)<br>Regra Mais Descartaveis (0.0311) |
| teste_099 | sintetica | 2 | Regra 106 (0.031)<br>Regra 099 (0.0299)<br>Regra 048 (0.0283) |
| teste_107 | sintetica | 1 | Regra 107 (0.0325)<br>Regra 078 (0.0299)<br>Regra 074 Bela Forma (0.029) |
| teste_116 | sintetica | 4 | Regra 087 (0.0323)<br>Regra 066 (0.0308)<br>Regra 070 (0.0306) |
| teste_119 | sintetica | 1 | Regra 119 (0.0325)<br>Regra 087 (0.0298)<br>Regra 122 (0.0294) |
| teste_125 | sintetica | 6 | Regra regra_050 (0.0305)<br>Regra 138 (0.0298)<br>Regra 119 (0.0292) |
| teste_165 | sintetica | 3 | Regra 171 (0.0304)<br>Regra 230 (0.029)<br>Regra Chegatto (0.0287) |
| teste_168 | sintetica | 1 | Regra 168 (0.0323)<br>Regra 236 (0.0323)<br>Regra 213 (0.0303) |
| teste_171 | sintetica | 1 | Regra 171 (0.0328)<br>Regra 158 (0.031)<br>Regra 174 (0.0305) |
| teste_187 | sintetica | 2 | Regra 171 (0.0303)<br>Regra 187 (0.0303)<br>Regra Maxlub (0.0302) |
| teste_202 | sintetica | 1 | Regra 202 (0.032)<br>Regra 226 (0.0306)<br>Regra 152 (0.0294) |
| teste_214 | sintetica | 1 | Regra 214 (0.0328)<br>Regra 146 (0.0303)<br>Regra 174 (0.0289) |
| teste_242 | sintetica | 1 | Regra 242 (0.0328)<br>Regra 200 (0.029)<br>Regra 152 (0.029) |

## sem_pontos - híbrido + rerank(50)

| conjunto | n | hit@1 | hit@3 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|---|
| todas | 20 | 0.75 | 0.95 | 0.95 | 0.95 | 0.844 |
| imagem | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.000 |
| sintetica | 20 | 0.75 | 0.95 | 0.95 | 0.95 | 0.844 |

| consulta | tipo | posição da regra certa | top-3 devolvido |
|---|---|---|---|
| teste_022 | sintetica | 1 | Regra Supergiro (0.9973)<br>Regra 087 (0.9936)<br>Regra VetVida (0.9925) |
| teste_023 | sintetica | 1 | Regra BSB Vet (0.9851)<br>Regra 230 (0.9003)<br>Regra 075 (0.8726) |
| teste_038 | sintetica | 19 | Regra 105 (0.9852)<br>Regra Armazém Santa Maria (0.9784)<br>Regra 101 (0.9771) |
| teste_043 | sintetica | 3 | Regra regra_029 (0.9713)<br>Regra 105 (0.962)<br>Regra regra_043 (0.9618) |
| teste_054 | sintetica | 1 | Regra 054 (0.9971)<br>Regra NB PI (0.9965)<br>Regra 122 (0.9954) |
| teste_061 | sintetica | 1 | Regra 061 (0.9962)<br>Regra 122 (0.9877)<br>Regra 101 (0.9868) |
| teste_074 | sintetica | 1 | Regra 074 Bela Forma (0.9904)<br>Regra 135 (0.9577)<br>Regra Armazém Santa Maria (0.9264) |
| teste_083 | sintetica | 2 | Regra Padrão goVendas Customizável (0.9808)<br>Regra 083 Brida (0.9697)<br>Regra 073 (0.9544) |
| teste_099 | sintetica | 1 | Regra 099 (0.996)<br>Regra 101 (0.9948)<br>Regra 116 (0.9936) |
| teste_107 | sintetica | 1 | Regra 107 (0.9996)<br>Regra Makro Services (0.9916)<br>Regra 074 Bela Forma (0.981) |
| teste_116 | sintetica | 1 | Regra 116 (0.9863)<br>Regra 172 (0.9594)<br>Regra 181 (0.9484) |
| teste_119 | sintetica | 1 | Regra 119 (0.9973)<br>Regra 058 (0.9929)<br>Regra 075 (0.9908) |
| teste_125 | sintetica | 2 | Regra 156 (0.9883)<br>Regra 125 (0.9853)<br>Regra regra_050 (0.983) |
| teste_165 | sintetica | 1 | Regra Chegatto (0.9974)<br>Regra 209 (0.9936)<br>Regra 171 (0.993) |
| teste_168 | sintetica | 1 | Regra 168 (0.9995)<br>Regra 236 (0.9993)<br>Regra 245 (0.9951) |
| teste_171 | sintetica | 1 | Regra 171 (0.9988)<br>Regra 201 (0.998)<br>Regra 208 (0.9979) |
| teste_187 | sintetica | 2 | Regra 203 (0.9989)<br>Regra 187 (0.9988)<br>Regra 173 (0.9975) |
| teste_202 | sintetica | 1 | Regra 202 (0.9871)<br>Regra 237 (0.9767)<br>Regra 152 (0.9725) |
| teste_214 | sintetica | 1 | Regra 214 (0.9974)<br>Regra 174 (0.9898)<br>Regra 203 (0.9879) |
| teste_242 | sintetica | 1 | Regra 242 (0.9921)<br>Regra 174 (0.937)<br>Regra 190 (0.9322) |

### vetor x vetor + rerank(50)

Teto do re-ranking: em **20/20** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| teste_022 | sintetica | 2 | 1 | melhorou |
| teste_023 | sintetica | 8 | 1 | melhorou |
| teste_038 | sintetica | 11 | 19 | piorou |
| teste_043 | sintetica | 1 | 3 | piorou |
| teste_054 | sintetica | 24 | 1 | melhorou |
| teste_061 | sintetica | 18 | 1 | melhorou |
| teste_074 | sintetica | 17 | 1 | melhorou |
| teste_083 | sintetica | 3 | 2 | melhorou |
| teste_099 | sintetica | 5 | 1 | melhorou |
| teste_107 | sintetica | 2 | 1 | melhorou |
| teste_116 | sintetica | 12 | 1 | melhorou |
| teste_119 | sintetica | 2 | 1 | melhorou |
| teste_125 | sintetica | 31 | 2 | melhorou |
| teste_165 | sintetica | 21 | 1 | melhorou |
| teste_168 | sintetica | 3 | 1 | melhorou |
| teste_171 | sintetica | 1 | 1 | igual |
| teste_187 | sintetica | 12 | 2 | melhorou |
| teste_202 | sintetica | 1 | 1 | igual |
| teste_214 | sintetica | 1 | 1 | igual |
| teste_242 | sintetica | 1 | 1 | igual |

### vetor x híbrido (vetor+BM25)

Teto do re-ranking: em **20/20** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| teste_022 | sintetica | 2 | 1 | melhorou |
| teste_023 | sintetica | 8 | 1 | melhorou |
| teste_038 | sintetica | 11 | 23 | piorou |
| teste_043 | sintetica | 1 | 9 | piorou |
| teste_054 | sintetica | 24 | 18 | melhorou |
| teste_061 | sintetica | 18 | 3 | melhorou |
| teste_074 | sintetica | 17 | 2 | melhorou |
| teste_083 | sintetica | 3 | 2 | melhorou |
| teste_099 | sintetica | 5 | 2 | melhorou |
| teste_107 | sintetica | 2 | 1 | melhorou |
| teste_116 | sintetica | 12 | 4 | melhorou |
| teste_119 | sintetica | 2 | 1 | melhorou |
| teste_125 | sintetica | 31 | 6 | melhorou |
| teste_165 | sintetica | 21 | 3 | melhorou |
| teste_168 | sintetica | 3 | 1 | melhorou |
| teste_171 | sintetica | 1 | 1 | igual |
| teste_187 | sintetica | 12 | 2 | melhorou |
| teste_202 | sintetica | 1 | 1 | igual |
| teste_214 | sintetica | 1 | 1 | igual |
| teste_242 | sintetica | 1 | 1 | igual |

### vetor x híbrido + rerank(50)

Teto do re-ranking: em **20/20** consultas a regra certa está entre os 50 candidatos da busca vetorial (as outras o reranker não consegue resgatar).

| consulta | tipo | só vetor | vetor + rerank | variação |
|---|---|---|---|---|
| teste_022 | sintetica | 2 | 1 | melhorou |
| teste_023 | sintetica | 8 | 1 | melhorou |
| teste_038 | sintetica | 11 | 19 | piorou |
| teste_043 | sintetica | 1 | 3 | piorou |
| teste_054 | sintetica | 24 | 1 | melhorou |
| teste_061 | sintetica | 18 | 1 | melhorou |
| teste_074 | sintetica | 17 | 1 | melhorou |
| teste_083 | sintetica | 3 | 2 | melhorou |
| teste_099 | sintetica | 5 | 1 | melhorou |
| teste_107 | sintetica | 2 | 1 | melhorou |
| teste_116 | sintetica | 12 | 1 | melhorou |
| teste_119 | sintetica | 2 | 1 | melhorou |
| teste_125 | sintetica | 31 | 2 | melhorou |
| teste_165 | sintetica | 21 | 1 | melhorou |
| teste_168 | sintetica | 3 | 1 | melhorou |
| teste_171 | sintetica | 1 | 1 | igual |
| teste_187 | sintetica | 12 | 2 | melhorou |
| teste_202 | sintetica | 1 | 1 | igual |
| teste_214 | sintetica | 1 | 1 | igual |
| teste_242 | sintetica | 1 | 1 | igual |
