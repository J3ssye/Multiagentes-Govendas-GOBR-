# Relatório — Entrega 1: Geração de explicações

Gerado em 20/10/2026 10:53 · modelo: gemini-3.5-flash-lite, gemini-3.6-flash, gemini-3.8-flash

## Corpus

- Arquivos .gobr lidos: **249** (exemplos + referências)
- Regras únicas (após remover cópias idênticas): **199**
- Blocos `parametros` interpretados: **1548**
- Linhas não classificadas pelo parser: **0**
- Filtros de cliente: **1887**; com tradução no glossário: **1887** (100.0%); marcados como aproximação do manual: 115

## Verificação automática das explicações

- Explicações geradas: **199** (origem: {'llm': 199})
- Passaram na verificação: **199/199** (100.0%)
- Tentativas necessárias (entre as aprovadas): {1: 199}

## Pontos de atenção detectados automaticamente (regras únicas)

- sem bloco final (clientes não cobertos mantêm a configuração anterior) — §7.6: **159**
- usa time/carteira não definido no arquivo: **43**
- nome do bloco cita número que não está no código: **35**
- bloco inalcançável (depois de um bloco sem filtro) — §7.6: **1**

## Avaliação contra as imagens (regra de negócio original)

Para os 3 exemplos, cada item da imagem é procurado na explicação gerada **a partir do .gobr** (mesma ação e pelo menos uma palavra em comum no nome/critério).

### exemplos/RegraInfinittoDesign.gobr

| Item da imagem | Ação na imagem | Segmento gerado (a partir do .gobr) | Resultado |
|---|---|---|---|
| Ativo | 14 dias | [3] Ativos -> 14 dias | coberto |
| Risco de inatividade | 7 dias | [4] Risco de inatividade -> 7 dias | coberto |
| Inativo | 28 dias | [5] Inativos -> 28 dias | coberto |
| Prospect | 7 dias | [2] Prospects -> 7 dias | coberto |

Cobertura dos itens da imagem que têm ação: **4/4**.

Blocos do .gobr que a imagem não mostra: [1] Baixados na Receita Federal -> Não agendar

### exemplos/RegraMaxlub.gobr

| Item da imagem | Ação na imagem | Segmento gerado (a partir do .gobr) | Resultado |
|---|---|---|---|
| Clientes Ativos | 14 dias | [5] Clientes ativos -> 14 dias | coberto |
| Risco de Inatividade | 7 dias | [6] Risco de inatividade -> 7 dias | coberto |
| Inativos (90 dias) | 14 dias | [7] Inativos (90 a 120 dias) -> 14 dias | coberto |
| Inativos (120 dias) | 21 dias | [8] Inativos (120 a 150 dias) -> 21 dias | coberto |
| Inativos (150 dias) | 28 dias | [9] Inativos (150 a 180 dias) -> 28 dias | coberto |
| Prospects | 14 dias | [4] Clientes prospects -> 14 dias | coberto |
| Não agendar inadimplentes | Não agendar | [2] Não agendar inadimplentes -> Não agendar | coberto |
| Não agendar clientes em rota | Não agendar | [3] Não agendar clientes com rota na semana -> Não agendar | coberto |
| Capacidade de atendimento: 35 clientes (Dia) | - | - | não existe no .gobr (requisito sem bloco correspondente) |

Cobertura dos itens da imagem que têm ação: **8/8**.

Blocos do .gobr que a imagem não mostra: [1] Não agendar baixados na Receita -> Não agendar; [10] Clientes fora das regras padrão -> Não agendar

### exemplos/V1Vidros-RegraComercial.gobr

| Item da imagem | Ação na imagem | Segmento gerado (a partir do .gobr) | Resultado |
|---|---|---|---|
| Regra 01: Clientes Ativos | 14 dias | [2] Clientes Ativos -> 14 dias | coberto |
| Regra 02: Risco de Inatividade | 7 dias | [3] Risco de Inatividade -> 7 dias | coberto |
| Regra 03: Inativos | 14 dias | [4] Inativos -> 14 dias | coberto |
| Regra 04: Clientes Prospects | 7 dias | [5] Clientes Prospects -> 7 dias | coberto |
| Agendar Inadiplentes | - | - | não existe no .gobr (requisito sem bloco correspondente) |
| Não agendar | Não agendar | [1] Baixados na Receita -> Não agendar | coberto |

Cobertura dos itens da imagem que têm ação: **5/5**.
