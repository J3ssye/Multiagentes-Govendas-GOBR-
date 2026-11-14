# Regra de pré-registro do agente — Entrega 5

**Status:** pré-registro. Escrita em 10/11/2026 e revisada em 11/11 e 14/11/2026, antes do commit e antes de qualquer execução de embedding, reranker ou Gemini no desenvolvimento desta entrega. A prova da data é o commit deste arquivo e dos dois arquivos de mensagens da seção 8, feito pela aluna. O código do desenvolvimento e o do teste recusam rodar sem esse commit, e não existe atalho: nem `--sem-git`, nem variável de ambiente.

**Origem dos números.** Os da Entrega 4 estão marcados "herdado do handoff de 10/11" e foram conferidos no disco contra `entrega4/config_escolhida.json` e `entrega4/resultados_fluxo_dev.md`. Os marcados "medido em 10/11" saíram de código determinístico (parser e expressões regulares) rodado em 10/11, sem embedding, reranker nem Gemini. As passagens do DMAS (Dibia, *Designing Multi-Agent Systems*) foram lidas no Project em 10/11. A citação do AIMA é herdada da Entrega 4 e não foi relida.

**Revisão antes do commit (11/11 e 14/11/2026).** Feita sem nenhuma execução de embedding, reranker ou Gemini. Foram corrigidos seis erros de texto e de número (Enunciado e seções 6, 7.2, 7.4 e 12). Três mudanças de critério foram decididas pela aluna em 14/11: o roteador passa a tratar o pedido de regra em forma de pergunta (seção 5, com 6 mensagens novas no desenvolvimento e 5 no teste); a recusa `cabecalho_parametros_invalido` (seção 6); a métrica descritiva G9 (seção 8). Os números marcados "medido em 14/11" saíram do mesmo tipo de código determinístico dos de 10/11.

## Enunciado

A Entrega 5 é "Fluxo agêntico para gerar uma parametrização" (vence em 17/11/2026), título informado pela aluna em 10/11/2026. A Entrega 6, "Agente com memória de contexto", fica de fora. O Project não tem enunciado por entrega. O enunciado geral é `Trabalho da Disciplina de Multiagentes.pdf` (raiz do repositório), que diz:

- Objetivo: "Criar um agente de conversação que auxilie um usuário a escrever uma regra de parametrização do sistema Govendas utilizando uma DSL (Domain-Specific Language) que se chama GOBR".
- "O usuário irá entrar com uma imagem ou uma descrição das regras de negócio."
- "O agente deve ser proativo e auxiliar o usuário a identificar pontos falhos na modelagem comercial das regras de negócio."
- "Ao final o agente deve devolver a resposta para o usuário, gerando o conjunto de regras na linguagem GOBR."
- Dicas: indexar as descrições geradas e usá-las num RAG (Entrega 2); indexar o manual "para que possa servir de apoio para escrever a saída" (Entrega 3); atenção à quebra dos chunks; "Crie um fluxo com o langgraph para orientar o agente que irá descobrir os dados e formular a resposta."

O que nem o título nem o enunciado fixam (grafo, roteamento, validação, teto de turno, métrica da regra gerada) é proposta desta regra. Onde é escolha de engenharia, vem marcado "não encontrei no material". Não há rubrica, gabarito nem peso de nota no material, e esta regra não inventa nenhum.

**Imagem.** O enunciado geral lista a imagem como forma de entrada, mas não a atribui a nenhuma entrega. Esta regra mantém o fluxo só com texto (decisão do handoff de 10/11/2026; se mudar, muda antes do commit desta regra). Fica de fora: ler uma imagem e convertê-la em descrição.

**Proatividade.** Num turno só, sem memória (Entrega 6), o agente não espera resposta do usuário. O "ser proativo" desta entrega é devolver, junto com o GOBR, pontos de atenção: os achados de `analisa()` da Entrega 1, os avisos do validador (seção 6) e as premissas e perguntas que o próprio Gemini declara. Perguntar e esperar a resposta fica para a Entrega 6.

## 1. O que a regra decide

Uma configuração: a de busca no índice de regras (seção 7). O desenvolvimento mede e escolhe; o teste só relata. Esse arranjo segue a Entrega 4 (AIMA cap. 19, parágrafos que antecedem o §19.4.1: o conjunto de desenvolvimento avalia os candidatos e escolhe o melhor; o teste é a avaliação final; é analogia, e **não encontrei no material** uma passagem sobre pipelines de busca ou de agentes).

Todo o resto (grafo, roteador, validador, tentativas, prompts) é fixo desde o commit. O desenvolvimento mede e relata. Uma mudança feita olhando o desenvolvimento entra no README em "Ajustes feitos olhando resultado", com o erro que a motivou, como na Entrega 4 (seção 10).

## 2. Já decidido (esta regra não reabre)

1. **Reuso só por import.** Da Entrega 4: `comum_fluxo` (`Recursos`, `buscar_cfg`, `descrever_regra`, `descrever_trecho`, `montar_contexto`, `medir_configuracao`, `carregar_consultas`, `metricas_exatas`, `gravar_exclusivo`, `estado_git_da_regra` como modelo). Da Entrega 1: `gobr_parser` (`parse_texto`, `analisa`). Das Entregas 2 e 3: os índices e os módulos que a Entrega 4 já importa. Nenhum arquivo de `entrega1/` a `entrega4/` é editado, inclusive o README e os resultados da Entrega 4.
2. **Padrão de orquestração: workflow condicional, não orquestração autônoma.** Arestas condicionais, uma delas voltando a um nó anterior: DMAS §2.2.2 (o exemplo clássico: o teste do código passa e vai adiante, ou falha e volta a escrever o código) e Tabela 11.1 ("Conditional routing" pede "Conditional/Supervisor": ramificação explícita, execução limitada). Nenhum nó decide o próximo passo por LLM: quem decide é o código (no DMAS §2.3, é isso que define o padrão autônomo, o que esta entrega não usa). Descartado: orquestrador plan-based ou conduzido por IA, por §11.3.6 ("Start with the simplest pattern that could work. Add complexity only when evaluation demonstrates clear benefits.") e porque o desenvolvimento não mostra gargalo que um orquestrador resolveria. "Agêntico", aqui, é um LLM dentro do fluxo com ferramentas (buscas, parser) e um ciclo de correção com orçamento, que é o agente do Cap. 2 (raciocina, age, comunica, adapta). O título **não** define "fluxo agêntico", e **não encontrei no material** uma definição além do DMAS.
3. **LangGraph** é pedido pelo enunciado geral. O DMAS só o cita no §9.4 (o repositório do livro tem implementações equivalentes em LangGraph). Sobre a API do LangGraph: **não encontrei no material**.
4. **Modelo e chave.** Gemini, o mesmo da Entrega 1 e da 4 (`MODELO_GEMINI_PADRAO`). Parâmetros de geração da Entrega 1: temperatura 0,2, resposta JSON com schema, `max_output_tokens` 32768. A chave vem de `GOOGLE_API_KEY` e, na falta dela, de `GEMINI_API_KEY`. O valor nunca é lido para fora do SDK, impresso, gravado nem registrado em log. Falha de autenticação: o código diz para definir a variável de novo no ambiente.
5. **O que o usuário recebe** (do enunciado: "gerando o conjunto de regras na linguagem GOBR" e ser "proativo"): o GOBR, o status (aceita ou não validada), os pontos de atenção e as fontes (regras e trechos do manual). O resumo mostra as contagens reais de tokens da API, impressas depois do fim do grafo. Isso corrige o defeito de exibição da Entrega 4 (a linha "tokens de LLM: 0 (sem --responder)" é impressa antes da chamada) sem editar `entrega4/`.
6. **k = 3** itens por busca (herdado da Entrega 4; o material não justifica o valor: **não encontrei no material**).
7. **Tentativas: no máximo 2** chamadas de geração por turno (a primeira e uma retentativa). O precedente é a Entrega 1 (`gera_uma`, `max_tentativas=2`: uma nova tentativa com a lista de problemas). O DMAS pede terminação por orçamento de iterações (§2.5.1) e prefere encerrar cedo com resultado parcial a gastar recurso (§11.3.5), mas não dá o número: **não encontrei no material**.
8. **Teto de latência.** 20 s para a soma das buscas de um turno, no computador dela (herdado da Entrega 4). O pior caso de um turno é regras + manual (rota `ambos`, ou retentativa com consulta ao manual). **Turno inteiro: esta regra não fixa teto.** Decisão nova, com o motivo: só há duas observações de latência do Gemini, 29 s e 133 s (herdadas do handoff de 10/11), com o prompt de resposta livre da Entrega 4, e nenhuma com a saída JSON do nó `gerar`. O desenvolvimento e o teste registram o tempo por nó e do turno e relatam mediana e máximo, sem critério de aprovação. Uma chamada ao Gemini passa a erro de infraestrutura depois de `TIMEOUT_GEMINI_S` (proteção contra travamento, não critério de desempenho).
9. **Sem memória entre turnos** e **sem imagem** (Entrega 6 e a nota da seção Enunciado).
10. **Git sem atalho.** Ver seções 7.4 e 9.

## 3. Constantes

Os testes sem modelo leem o bloco desta seção e comparam com o código.

```
K = 3
TETO_BUSCA_S = 20.0
REPETICOES = 2
FATOR_CONFIRMACAO = 1.25
MAX_TENTATIVAS = 2
TIMEOUT_GEMINI_S = 300
RETENTATIVAS_INFRA = 2
DIVERGENCIA_CHAMADA_S = 2
DIVERGENCIA_CHAMADA_FRACAO = 0.10
LACUNA_ENTRE_CHAMADAS_S = 60
CHARS_TEXTO_CURTO = 1000
MODELO_RERANKER_MENOR = cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
MAX_LENGTH_RERANKER_MENOR = 512
ROTAS = regras, manual, ambos, nenhum
STATUS = aceita, invalida, resposta_linguagem, fora_do_escopo, erro_infra
RECUSAS = saida_invalida, linha_nao_reconhecida, sem_bloco_parametros, bloco_sem_fonte, bloco_sem_acao, nao_agendar_com_frequencia, linha_de_corpo_nao_classificada, cabecalho_parametros_invalido
AVISOS = sem_version, cabecalho_nao_reconhecido, bloco_inalcancavel, sem_regra_final, nome_diverge_do_codigo, fonte_indefinida
GRADE_REGRAS = R0, R1, R2, R3, R4
DOMINIO = gobr, govendas, gorules, linguagem, regra, parametr, cliente, vendedor, carteira, equipe, time, segmentac, frequencia, agend, bloco, filtro, alerta, aviso, notifica, mensagem, whatsapp, ramo, prospect, inadimpl, inativo, ativo, roteiro, rota, visita, supervisor, televendas
DESC_1 = \ba cada \d+
DESC_2 = \b\d+\s*(?:dias?|semanas?|meses|mes|anos?)\b
DESC_3 = \b(?:toda|todo|todas|todos)\s+(?:a\s+|o\s+)?(?:semana|dia|mes|segunda|terca|quarta|quinta|sexta)\b
DESC_4 = \b(?:semanal|quinzenal|mensal|diari[ao]|bimestral|trimestral|semestral)\b
DESC_5 = \bnao\s+(?:agendar|agenda|sao agendad\w+)\b|\bbloque(?:ar|ando|ados?)\b
PEDIDO_1 = \b(?:cri|ger|escrev|mont|fac|faz|elabor)\w*\s+(?:uma|outra)\s+(?:nova\s+)?regra\b
INTERROGATIVA = ^\s*(?:e\s+)?(?:como|qual|quais|que|o que|onde|quando|quanto|quantos|quantas|por que|porque)\b
```

## 4. O grafo

**Entrada:** uma mensagem de texto. **Saída:** um dicionário serializável em JSON, com `mensagem`, `rota` e `motivo_rota`, `regras` e `manual` (as fontes, com os mesmos campos da Entrega 4), `contexto`, `tentativas` (cada uma com o GOBR, as recusas, os avisos, os tokens e os segundos), `gobr` (o da última tentativa), `status`, `pontos_de_atencao`, `tokens` (totais da API) e `tempos_s` (por nó e do turno).

**Estado** do grafo: os campos acima mais o contador de tentativas e as recusas da tentativa corrente.

**Nós:**

1. `rotear`: função pura, 0 token. Decide a rota pela seção 5.
2. `buscar_regras`: `buscar_cfg` da Entrega 4 no índice de regras, com a configuração da seção 7. Na avaliação, esconde a regra de referência (seção 8).
3. `buscar_manual`: `buscar_cfg` da Entrega 4 no índice do manual, com a configuração da Entrega 4 (vetor + reranker N = 5, `max_length` 2048), que não é reaberta. A consulta é a mensagem (rotas `manual` e `ambos`) ou a pergunta montada das recusas (retentativa, seção 6).
4. `montar_contexto`: `montar_contexto` da Entrega 4 com o que foi buscado.
5. `gerar`: uma chamada ao Gemini com o contexto e a mensagem (e, na retentativa, o GOBR anterior e as recusas). Responde JSON com `gobr`, `premissas` e `perguntas`. Conta a tentativa.
6. `validar`: parser da Entrega 1 e o critério da seção 6. Sem LLM.
7. `responder_linguagem`: rota `manual`. Uma chamada ao Gemini com o contexto do manual (o prompt da Entrega 4, sem exigir GOBR). Sem validação.
8. `encerrar`: monta a saída e o status.

**Arestas:**

- início → `rotear`.
- `rotear` → por rota: `regras` → `buscar_regras`; `manual` → `buscar_manual`; `ambos` → `buscar_regras`; `nenhum` → `encerrar` (status `fora_do_escopo`, resposta "Não encontrei nos documentos" com uma dica de como pedir, 0 token).
- `buscar_regras` → `buscar_manual` se a rota é `ambos`; senão → `montar_contexto`.
- `buscar_manual` → `montar_contexto`.
- `montar_contexto` → `responder_linguagem` se a rota é `manual`; senão → `gerar`.
- `gerar` → `validar`.
- `validar` → aceita: `encerrar` (status `aceita`). Recusada, com tentativas abaixo de `MAX_TENTATIVAS` e o manual ainda não consultado: `buscar_manual` (com a consulta das recusas) → `montar_contexto` → `gerar`. Recusada, com tentativas abaixo do máximo e o manual já consultado: `gerar`. Recusada, com as tentativas esgotadas: `encerrar` (status `invalida`).
- `responder_linguagem` → `encerrar`.

As arestas de rota são condições sobre o estado; a de validação é condição sobre a saída do nó anterior (DMAS cap. 6, resumo: condições baseadas em saída servem à validação e ao controle de qualidade, e as baseadas em estado, ao comportamento dirigido por configuração). O ciclo `gerar → validar → gerar` é deliberado e limitado por contador no estado (DMAS §2.5.1; §11.3.5). A validação como nó separado, com erro estruturado, segue o §11.3.4 ("Validation: Check tool outputs before returning to agents"; "Clear error handling: Tools should never crash agents—return structured errors").

**Como consome a Entrega 4.** O grafo não chama `fluxo.py` por subprocesso nem lê o `--json`: importa as mesmas funções e produz, no nó `montar_contexto`, os mesmos campos que o `--json` da Entrega 4 traz (`regras`, `manual`, `contexto`, `tokens_contexto`, `tempos_s`), com lista vazia e tempo nulo no índice que a rota não buscou. Quem consome o `--json` da Entrega 4 consome o contexto do agente sem mudança. Descartado: o subprocesso, porque recarrega embedding, índices e reranker a cada turno (a Entrega 4 mediu o carregamento fora do teto, "embedding 24,03 s" entre outros) e estouraria o teto de busca.

**O que ainda não entra:** imagem; memória entre turnos e perguntas ao usuário com espera de resposta (Entrega 6); LLM como roteador; orquestrador autônomo e vários agentes (DMAS §2.3, §11.3.6); busca paralela dos dois índices (DMAS §2.2.3; o computador tem dois núcleos de CPU e o custo é o reranker); decomposição da descrição em subperguntas ao manual; ablação "com × sem manual" na geração; execução da regra no Govendas real (**não encontrei no material** um validador oficial do GOBR).

## 5. Roteamento

Quatro características da mensagem normalizada (minúsculas, sem acento). Uma frase é um trecho terminado em `.`, `!`, `?` ou quebra de linha.

- `dominio`: a mensagem casa o início de alguma palavra da lista `DOMINIO` (seção 3).
- `pedido`: frase terminada em `?` que casa `PEDIDO_1` e não casa `INTERROGATIVA` (seção 3). Pede para criar uma regra; conta como frase declarativa.
- `pergunta`: alguma frase termina em `?` e não é `pedido`.
- `descricao`: alguma frase, terminada em `?` ou não, casa algum padrão `DESC_1` a `DESC_5` ou `PEDIDO_1` (seção 3).

| `dominio` | `pergunta` | `descricao` | rota |
|---|---|---|---|
| não | | | `nenhum` |
| sim | não | | `regras` |
| sim | sim | não | `manual` |
| sim | sim | sim | `ambos` |

**Regras e manual.** Uma mensagem declarativa com termos do domínio é um pedido de regra: busca só nas regras. A razão vem da Entrega 4: uma pergunta de negócio puxou trechos do manual com notas de 0,004 a 0,007 (herdado do handoff de 10/11), custando o reranker (9,79 s no dev, herdado) por contexto fraco. Uma pergunta sobre a linguagem vai ao manual. Uma mensagem com os dois traços (descrição e pergunta) vai aos dois. Na geração, o manual também entra na retentativa (seção 6).

**Pedido em forma de pergunta (revisão de 14/11).** Na versão de 10/11, `descricao` só valia em frase sem `?`. Uma mensagem como "Pode criar uma regra para visitar clientes novos toda segunda?" ia ao manual e o agente não gerava regra nenhuma. Agora a pergunta de sim ou não que pede para criar uma regra é pedido (rota `regras`), e a descrição vale em qualquer frase: uma pergunta com descrição concreta vai a `ambos`. Uma pergunta iniciada por palavra interrogativa ("Como faço uma regra para...?") continua pergunta e, com descrição, vai a `ambos`.

**Descartado.** LLM como roteador: uma chamada por turno para decidir o que a regra acima decide nas mensagens do desenvolvimento (DMAS §11.3.6); reabre-se só se o acerto no desenvolvimento for ruim. Roteamento por nota de busca: as notas do reranker só existem depois do custo que se quer evitar, e as do vetor não são comparáveis entre dois índices de textos diferentes; **não encontrei no material** critério para isso. Que o roteamento por regras seja o suficiente: **não encontrei no material**; é o que o desenvolvimento mede.

**Calibração (medido em 10/11 e refeito em 14/11, sem modelo).** O léxico foi escrito em 10/11 olhando 38 mensagens do desenvolvimento (14 das regras da Entrega 2, 15 do manual da Entrega 3, 9 novas) e acertou 37 de 38. O erro é `rdev_06` ("marcar uma reunião com um cliente no Google Agenda"), um quase-domínio proposto como negativo difícil: tem termos do domínio e vai ao manual. O léxico recebeu cinco termos (`linguagem`, `aviso`, `notifica`, `mensagem`, `whatsapp`) por causa de `mdev_13` ("aviso chegar por WhatsApp", que não tinha nenhum termo do domínio). Esse é um ajuste olhando o desenvolvimento, declarado aqui.

Em 14/11 o desenvolvimento recebeu 6 mensagens (`rdev_10` a `rdev_15`: pedidos em forma de pergunta e uma pergunta de linguagem com número) e passou a 44. Cinco variantes foram medidas nas 44, por acerto de rota e por acerto de desfecho (gera regra = `regras` ou `ambos`; responde = `manual`; recusa = `nenhum`):

| variante | rota | desfecho |
|---|---|---|
| A: a de 10/11 | 38 de 44 | 39 de 44 |
| B: descrição vale em qualquer frase | 38 de 44 | 41 de 44 |
| C: B + `PEDIDO_1` | 39 de 44 | 42 de 44 |
| D: C + `INTERROGATIVA` (**a desta regra**) | 40 de 44 | 42 de 44 |
| E: D + toda pergunta de sim ou não com descrição é pedido | 41 de 44 | 42 de 44 |

Erros de D: `rdev_06` (`nenhum` → `manual`); `rdev_12` e `rdev_13` (`regras` → `ambos`: a regra é gerada, mas paga a busca no manual); `rdev_15` (`manual` → `ambos`: pergunta de linguagem com número, gera regra em vez de responder). As 38 mensagens de 10/11 têm o mesmo resultado em A e em D. E foi descartada: ganha uma mensagem (`rdev_13`) e, em `rdev_15`, troca `ambos` por `regras`, gerando sem o manual no contexto; uma pergunta de sim ou não com descrição e sem pedir "uma regra" é ambígua, e `ambos` é a rota que consulta as duas fontes. A diferença é de uma mensagem em 44, de mesma autoria do roteador; critério para escolher entre D e E: **não encontrei no material**. Este também é um ajuste olhando o desenvolvimento.

As mensagens de teste das Entregas 2 e 3 não foram abertas (só o sha256 foi calculado). As 15 do teste desta entrega (10 de 10/11 e 5 de 14/11) foram escritas sem rodar nenhum roteador sobre elas; as 5 de 14/11, antes de medir as variantes acima.

## 6. Validação

O validador é `parse_texto` (Entrega 1) sobre o campo `gobr`, mais as checagens abaixo. O parser, sozinho, **nunca recusa**: devolve `avisos` e `analise.achados`, e anexa em silêncio ao fim da cláusula anterior uma linha que não sabe classificar (lido em `entrega1/gobr_parser.py`, `parse_texto`, `_monta_bloco` e `analisa`). Por isso "aceita" é um critério desta regra, não do parser.

**Recusas** (qualquer uma recusa a tentativa):

| código | quando |
|---|---|
| `saida_invalida` | a resposta do Gemini não é o JSON esperado, ou `gobr` vem vazio |
| `linha_nao_reconhecida` | `ir["avisos"]` não está vazio (linha fora de bloco ou não classificada) |
| `sem_bloco_parametros` | nenhum bloco `parametros` |
| `bloco_sem_fonte` | algum bloco `parametros` sem fonte (achado `sem_fonte`) |
| `bloco_sem_acao` | algum bloco `parametros` sem nenhuma ação |
| `nao_agendar_com_frequencia` | achado de `analisa()` (Manual §7.3.4) |
| `linha_de_corpo_nao_classificada` | linha de corpo de bloco que o parser anexou à cláusula anterior sem classificar (reproduz o ramo `elif clausulas:` de `_monta_bloco`); exclui linhas de cabeçalho, continuações iniciadas por `e`/`ou` e listas com parênteses abertos |
| `cabecalho_parametros_invalido` | linha sem indentação que começa com `parametros` ou `limpar parametros` e que o parser não reconhece como cabeçalho (`HEADER_RE`). O parser anexa essa linha e o corpo dela ao bloco anterior, juntando dois blocos sem avisar |

**Avisos** (não recusam; vão para os pontos de atenção): `sem_version`; `cabecalho_nao_reconhecido` (linha de cabeçalho que o parser não reconhece: `time`, `carteira`, `segmentacao`, `alertas`, `tags`; em `parametros` e `limpar parametros` é recusa); e os achados de `analisa()`: `bloco_inalcancavel`, `sem_regra_final`, `nome_diverge_do_codigo`, `fonte_indefinida`.

**Calibração no corpus (medido em 10/11 e refeito em 14/11, sem modelo).** 249 arquivos conhecidos como válidos (246 em `referencias/` e 3 em `exemplos/`):

- `linha_nao_reconhecida`, `sem_bloco_parametros`, `bloco_sem_fonte` e `nao_agendar_com_frequencia`: 0 recusas.
- `bloco_sem_acao`: 1 (`regra_032`, bloco 74, sem ação reconhecida).
- `linha_de_corpo_nao_classificada`: 1 (`regra_236`, linhas 89 e 90: "normal na segunda e", "normal na quarta e").
- `cabecalho_parametros_invalido`: 1 (`regra_080`, linha 11: nome do bloco com aspas internas). Acrescentada em 14/11: sem ela, um bloco `parametros` com cabeçalho malformado some dentro do anterior e a regra sai como "aceita".
- Total: 3 de 249 (1,2 %) são falsos positivos conhecidos do critério.
- `sem_version`: 1 arquivo, `V1Vidros-RegraComercial.gobr`, exemplo oficial; por isso a falta de `version` é aviso e não recusa.
- `cabecalho_nao_reconhecido`: 12 arquivos (45 linhas de cabeçalho `carteira`).
- Ocorrências dos achados de `analisa()` nos mesmos 249: `sem_regra_final` 215, `fonte_indefinida` 46, `nome_diverge_do_codigo` 35, `bloco_inalcancavel` 1.
- Em 3 arquivos, uma linha desconhecida logo depois da fonte vira filtro temporal por exclusão e passa sem aviso.

**Limite.** O critério é estrutural. "Aceita" não quer dizer que o Govendas aceita a regra, nem que ela faz o que o usuário pediu. **Não encontrei no material** um validador oficial do GOBR.

**Retentativa.** Recusada e com tentativa sobrando: nova chamada com o GOBR anterior e a lista das recusas, com a linha quando há (formato da Entrega 1). Se o manual ainda não foi consultado, antes da nova chamada o grafo busca no manual com uma consulta montada das duas primeiras recusas, por tabela fixa:

| recusa | consulta ao manual |
|---|---|
| `linha_nao_reconhecida`, `linha_de_corpo_nao_classificada` | "Como escrevo em GOBR a linha: {linha}?" |
| `sem_bloco_parametros` | "Como declaro um bloco parametros em GOBR?" |
| `cabecalho_parametros_invalido` | "Como escrevo o cabeçalho de um bloco parametros em GOBR?" |
| `bloco_sem_fonte` | "Como declaro a fonte de clientes (do time ou da carteira) de um bloco parametros?" |
| `bloco_sem_acao` | "Que ações posso usar dentro de um bloco parametros?" |
| `nao_agendar_com_frequencia` | "Posso combinar nao agendar com frequencia no mesmo bloco?" |
| `saida_invalida` | nenhuma (não busca) |

Motivo: consultar o manual só quando há evidência de necessidade e em forma de pergunta, o formato das consultas da Entrega 3 (manual dev: hit@3 0,93 com a configuração escolhida, herdado), e não pagar o reranker do manual (9,79 s, herdado) num contexto que a Entrega 4 mostrou fraco para pergunta de negócio. Se isso melhora a geração, **não foi medido** (sem ablação; seção 12).

**Fim sem aceite.** Status `invalida`: a saída traz o GOBR da última tentativa marcado "NÃO VALIDADO", com as recusas. O agente nunca devolve GOBR recusado sem a marca.

**Infraestrutura.** Rede, cota, autenticação e tempo esgotado não contam como tentativa: repete-se a chamada até `RETENTATIVAS_INFRA` vezes; se persistir, o turno termina com status `erro_infra`, que fica fora do denominador da aceitação e é contado à parte.

## 7. Busca

### 7.1 Linha de base (herdada da Entrega 4)

- Regras: híbrido sem reranker (dev: hit@3 0,71, MRR 0,606, 0,61 s; herdado do handoff de 10/11).
- Manual: vetor + reranker N = 5, `max_length` 2048 (dev: hit@3 0,93, MRR 0,833, 9,79 s; herdado).
- Dupla: 10,4 s (herdado).

### 7.2 Por que o reranker de regras continua aberto

O que `entrega4/resultados_fluxo_dev.md` mostra nas regras (dev, 14 consultas; lido em 10/11):

- Vetor com N = 5: hit@3 0,50 (L512: 15,14 s; L2048: 17,64 s), abaixo do híbrido sem reranker (0,71). Com N pequeno, o reranker só reordena os candidatos da fase 1, e o hit@5 do vetor é 0,50.
- Híbrido com N = 5: excluídas por latência a 22,8 s (L512) e 22,2 s (L2048), perto do teto.
- N ≥ 10: de 24,8 s a 115,3 s.
- A consulta do pior caso é `img_infinitto` em 11 das 14 exclusões das regras; nas outras três são `sint_televendas_x_campo`, `sint_regra_grande_regioes` e `sint_ramos_12_19`.

A pergunta de por que `max_length` 512 ficou mais lento que 2048 com N ≥ 10 **não é investigada** nesta entrega. Os números de teste das Entregas 2 e 4 não entram em nenhuma decisão desta seção.

### 7.3 Grade de regras (todas sobre o índice `com_pontos`, fase 1 híbrida)

| id | configuração | alavanca |
|---|---|---|
| R0 | híbrido, sem reranker | linha de base da Entrega 4 |
| R1 | híbrido + `BAAI/bge-reranker-v2-m3`, N = 5, texto curto | menos texto por par, mesmo modelo da Entrega 2 |
| R2 | híbrido + `BAAI/bge-reranker-v2-m3`, N = 10, texto curto | idem; N = 10 alcança o hit@10 de 0,93 do híbrido |
| R3 | híbrido + `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`, N = 10, `max_length` 512 | reranker menor |
| R4 | idem R3, N = 20 | reranker menor, mais candidatos |

**Texto curto** = os primeiros `CHARS_TEXTO_CURTO` (1000) caracteres do texto do nó (título, resumo e os primeiros segmentos). Os nós têm mediana de 336 tokens do bge-m3 e máximo de 4.136 (herdado da Entrega 4); a conversão de caracteres em tokens **não foi medida**, e 1000 é escolha de engenharia (**não encontrei no material**).

**Reranker menor.** Conferido em 10/11 pela ficha do modelo: existe, inclui português (`pt`), licença apache-2.0, base mMiniLMv2-L12-H384 (destilada do XLM-R Large). A ficha não informa o número de parâmetros nem o tamanho máximo de sequência; `max_length` 512 é escolha de engenharia. O modelo é baixado no computador dela na primeira execução (precisa de rede). Se o download falhar, R3 e R4 saem da grade e isso é relatado; o resto segue.

**Fora da grade, com o motivo:**

- Cache de notas (`RerankerComCache`, Entrega 3): o cross-encoder pontua o par (consulta, texto). Uma pergunta nova não reaproveita nenhuma nota, então o cache não reduz a latência de um turno novo, e escondia o custo na medição (Entrega 4, seção 5).
- GPU: o dispositivo medido é CPU (`resultados_fluxo_dev.md`); **não encontrei no material** nem no disco outra opção.
- Fase 1 vetor: dev da Entrega 4, vetor sem reranker hit@3 0,50 contra 0,71 do híbrido.
- N ≥ 20 com o modelo grande: 35 s ou mais no dev da Entrega 4.
- Mudar a configuração do manual ou reabrir a dupla: não.

### 7.4 Como medir

Reuso do `medir_configuracao` da Entrega 4, com os conjuntos de desenvolvimento: 14 consultas de regras (`entrega2/consultas_avaliacao.json`) e 15 do manual (`entrega3/consultas_manual_dev.json`).

- **Ordem:** primeiro a configuração do manual (M) e R0; depois R1 a R4.
- **Repetições:** `REPETICOES` por consulta, vale a menor medida; o acerto vem da 1ª repetição. Latência de uma configuração = a maior latência entre as consultas (pior caso). Aquecimento e sem cache, como na Entrega 4.
- **Viabilidade:** lat(R) + lat(M) ≤ `TETO_BUSCA_S`, com lat(M) **medida nesta execução** (não a herdada). O pior caso de um turno é regras + manual.
- **Poda e confirmação:** `limite_R` = `TETO_BUSCA_S` − lat(M). Se a 1ª medição de uma consulta passar de `limite_R`: acima de `FATOR_CONFIRMACAO` × `limite_R`, a configuração é encerrada de imediato; até esse valor, só é encerrada se a repetição seguinte também passar. Motivo: a mesma configuração deu 14,3 s numa execução e 17,6 s na outra, razão 1,23 (herdado do handoff de 10/11), e a Entrega 4 podava por uma medição só. O fator 1,25: **não encontrei no material**.
- **Condições:** na tomada, tampa aberta, sem suspensão, sem outros programas, OneDrive pausado. O código pede a confirmação ("sim") e a grava no resultado, registra o dispositivo (cpu ou gpu) e, se o `psutil` estiver instalado, se estava na tomada.
- **Carga dos modelos fora da medida:** o modelo de embedding e os rerankers são carregados (e o menor, baixado) antes da 1ª chamada medida de cada configuração, no aquecimento. Essa carga não entra em nenhuma medida nem na regra da lacuna abaixo, que só vale entre chamadas medidas consecutivas da mesma configuração. Motivo: carregar ou baixar um modelo pode passar de `LACUNA_ENTRE_CHAMADAS_S` e arquivaria a execução sem o relógio ter divergido.
- **Divergência de relógio:** em cada chamada medida, comparam-se `perf_counter` e o relógio de parede. Se parede − perf passar de max(`DIVERGENCIA_CHAMADA_S`, `DIVERGENCIA_CHAMADA_FRACAO` × perf), ou se o intervalo de parede entre o fim de uma chamada medida e o início da seguinte, na mesma configuração, passar de `LACUNA_ENTRE_CHAMADAS_S`, a execução inteira é arquivada por ela (pasta `dev_1a_execucao_agente/`) e repetida do zero, sem escolher configuração por configuração, e isso se decide pelos tempos, antes de aplicar a regra de escolha (critério da Entrega 4, README, "Ajustes feitos olhando resultado"). Os valores 2 s, 10 % e 60 s: **não encontrei no material**.
- **Checkpoint** por configuração; a retomada só mede configurações ainda não gravadas, com a mesma grade.

### 7.5 Regra de escolha

1. Entre as configurações viáveis, só uma candidata com hit@3 do dev **estritamente maior** que o de R0 substitui a linha de base (os hit@3 são múltiplos de 1/14; o MRR sozinho não decide).
2. Entre as que superam R0: maior hit@3; empate, maior MRR; empate, menor latência; empate, a mais simples (ordem R1, R2, R3, R4).
3. Nenhuma supera R0: fica R0. É um resultado válido e é relatado.

As comparações dos passos 1 e 2 são exatas (frações). A saída é `config_agente.json`, gravado com abertura exclusiva, com a configuração de regras escolhida, as métricas e latências de todas as medidas (inclusive lat(M)), as excluídas com a consulta e o tempo, e o sha256 desta regra. Mudar o teto ou a grade depois de ver o desenvolvimento seria desvio, não ajuste.

## 8. Medição e relato

**Roteamento.** A rota esperada de cada mensagem é o que ela pede: as consultas das regras da Entrega 2 descrevem regras (`regras`); as do manual da Entrega 3 perguntam sobre a linguagem (`manual`); as novas trazem `rota_esperada` no arquivo.

| conjunto | Entrega 2 (regras) | Entrega 3 (manual) | novas | total |
|---|---|---|---|---|
| desenvolvimento | 14 | 15 | 15 (`consultas_roteamento_dev.json`) | 44 |
| teste | 20 | 20 | 15 (`consultas_roteamento_teste.json`) | 55 |

As novas têm negativos difíceis (`quase_dominio`), positivos difíceis (`descricao_e_pergunta` sem os marcadores do léxico), pedidos em forma de pergunta (`pedido_em_pergunta`) e pergunta de linguagem com número (`pergunta_com_numero`). Métrica: acerto exato de rota (k de n) por origem, acerto de desfecho (gera regra = `regras` ou `ambos`; responde = `manual`; recusa = `nenhum`), matriz de confusão, e quantas mensagens foram ao manual sem precisar (custo do reranker). Mensagens `nenhum` gastam 0 token. O roteador e a rota esperada têm a mesma autoria: o acerto superestima o de usuários reais (seção 12).

**Geração.** As consultas de regras da Entrega 2 (dev 14, teste 20), uma execução do grafo completo por consulta, com a regra de referência escondida (leave-one-out): a regra de `relevantes` é removida do ranking de regras antes de montar o contexto (busca com k + 1 e corte em k), pelo critério de relevância da Entrega 2. Denominador: todas as consultas. Status diferente de `aceita` conta como não aceita, inclusive por roteamento errado; `erro_infra` fica fora do denominador e é contado à parte.

Métricas da geração, todas descritivas, e nenhuma decide configuração:

- **G1** aceita na 1ª tentativa (k de n); **G2** aceita ao fim (k de n); **G3** número de tentativas; **G4** retentativas que consultaram o manual.
- **G5** tokens da API por turno (entrada, saída, raciocínio; mediana, máximo, total): DMAS §10.5.1 lista tokens e chamadas de API como eficiência de recursos.
- **G6** tempo por nó e do turno (mediana e máximo), sem teto de turno; **G7** tempo da busca de regras contra `TETO_BUSCA_S`.
- **G8** comparação estrutural com a regra de referência, para as geradas com GOBR: mesmo número de blocos `parametros`? mesmo conjunto de tipos de ação? mesmo conjunto de números de frequência? (contagens, sem limiar). O DMAS §10.4.4 avisa que a similaridade de superfície engana quando há várias soluções válidas; não há juiz LLM (não calibrado, custo; **não encontrei no material** critério para calibrá-lo).
- **G9** pontos de atenção por resposta com GOBR: número de premissas e de perguntas declaradas pelo Gemini e de avisos do validador (mediana e máximo), e em quantas respostas há pelo menos uma premissa ou pergunta (k de n). É o que esta entrega mede do "ser proativo e auxiliar o usuário a identificar pontos falhos na modelagem comercial" do enunciado. Conta se o agente apontou algo, não se o ponto é uma falha real: sem limiar e sem rubrica de qualidade (**não encontrei no material**).

Origem: o DMAS §10.2.1 e a Tabela 10.1 mandam definir os critérios de sucesso antes de construir; o §10.4.4 prefere métrica determinística quando há gabarito. A linha de base do passo 4 da Tabela 10.1 é a **própria 1ª tentativa**: G1 contra G2 mede o que o ciclo de correção acrescenta (DMAS §11.3.6: só vale a complexidade que a avaliação mostra), sem chamada extra.

**Busca (relato).** hit@1, hit@3, hit@5, hit@10 e MRR da configuração de regras escolhida (dev 14, teste 20) e a latência por consulta, como na Entrega 4. No teste, só relato.

**Ordem do desenvolvimento.**

- D1: confere esta regra commitada e os sha256 da seção 13.
- D2: busca (M, R0, R1 a R4; seção 7.4).
- D3: aplica a seção 7.5 e grava `config_agente.json`.
- D4: roteamento e geração do desenvolvimento, com a configuração escolhida.
- D5: grava `resultados_agente_dev.json` e `.md`.

Prompts e schema ficam no código. Mudar prompt, léxico ou validador olhando o D4 é "ajuste olhando resultado": entra no README com o erro que o motivou e vale só se feito antes do commit da escolha. Antes disso (D2 e D3) nada se ajusta.

## 9. Uso do teste

Só depois do commit da escolha. O código recusa rodar se não valer **tudo**:

- (a) esta regra está commitada, sem mudanças, e o sha256 dela é o do código;
- (b) `config_agente.json` e `resultados_agente_dev.json` estão commitados, sem mudanças;
- (c) o commit de (b) é posterior ao desta regra;
- (d) `resultados_agente_teste.json` e `.md` não existem.

Não há flag, variável de ambiente nem outro atalho. O teste roda uma vez, com a configuração escolhida: roteamento (55 mensagens), busca (relato) e geração (20 turnos). Durante o teste o código não imprime rota, aceitação, tentativas nem GOBR de nenhum item, só o progresso (n de 20); checkpoint por item (retomar é continuar a mesma execução, não repetir). Depois de ver o teste não se ajusta nada (configuração, léxico, validador, prompts, `MAX_TENTATIVAS`) nem se roda o desenvolvimento de novo. Falha de infraestrutura em um item: seção 6.

## 10. O que fica congelado a partir do commit

Tudo das seções 2 a 9 e 13. Qualquer mudança vira "desvio" declarado no README, com o motivo, e nunca reescreve esta regra. A única exceção prevista são os ajustes do D4 (seção 8), cada um declarado.

## 11. Propostas que o material não cobre

| Escolha | Proposta | Origem |
|---|---|---|
| Padrão de orquestração | workflow condicional com um ciclo limitado | DMAS §2.2.2, Tabela 11.1, §11.3.6; escolha entre eles: **não encontrei no material** |
| Definição de "fluxo agêntico" | LLM + ferramentas + ciclo de correção com orçamento | **não encontrei no material** |
| Roteador | regras sobre quatro características da mensagem | **não encontrei no material** |
| Critério de aceite | seção 6, calibrado em 249 arquivos | **não encontrei no material** (não há validador oficial) |
| `MAX_TENTATIVAS` | 2 | precedente da Entrega 1; o DMAS não dá número |
| Teto de turno | nenhum; só relato | decisão desta regra |
| Consulta ao manual na retentativa | tabela fixa de perguntas | **não encontrei no material** |
| Grade R0 a R4, texto curto de 1000 caracteres, `max_length` 512 | seção 7.3 | **não encontrei no material** |
| `FATOR_CONFIRMACAO`, limites de divergência de relógio | 1,25; 2 s, 10 % e 60 s | **não encontrei no material** |
| Substituir R0 só com hit@3 estritamente maior | seção 7.5 | **não encontrei no material** |
| `TIMEOUT_GEMINI_S` | 300 s | proteção; **não encontrei no material** |
| Esconder a regra de referência (leave-one-out) | seção 8 | **não encontrei no material** |

## 12. Limitações deste pré-registro

- **"Aceita" é estrutural.** Um GOBR pode passar pelo parser e estar errado para o negócio. O critério foi calibrado em 249 arquivos conhecidos como válidos: 3 deles seriam recusados (1,2 %), e o parser deixa passar linha desconhecida logo depois da fonte (seção 6).
- **Conjuntos pequenos.** 14 consultas de desenvolvimento e 20 de teste na geração: uma consulta vale 7,1 e 5,0 pontos percentuais. Os empates são prováveis, **não encontrei no material** critério de significância, e a geração é uma amostra por item (temperatura 0,2, sem semente; a variação entre execuções não é medida).
- **Leave-one-out não elimina cópia.** Regras muito parecidas com a de referência continuam no índice (a Entrega 1 só reuniu as exatamente iguais: 249 arquivos viram 199 regras), então a geração pode copiar uma regra vizinha.
- **Conjuntos já usados.** As consultas de regras de teste (Entrega 2) já foram usadas no teste de busca das Entregas 2 e 4; na geração e no roteamento são um uso novo, mas o relato de busca do teste não é virgem.
- **Roteador e conjuntos com a mesma autoria.** O léxico foi calibrado no desenvolvimento e as mensagens de teste seguem o mesmo estilo (frase declarativa para regra, pergunta para linguagem). O acerto superestima o de usuários reais. Negativos com termos do domínio e pedidos sem os marcadores do léxico vão errar de propósito. Uma pergunta de sim ou não com descrição concreta e sem pedir "uma regra" é ambígua (pedido ou dúvida sobre a linguagem) e vai a `ambos`: no desenvolvimento isso erra `rdev_13` e `rdev_15` (seção 5).
- **O manual fora da 1ª tentativa.** A geração só consulta o manual na rota `ambos` e na retentativa. Não há ablação; o efeito sobre a qualidade não é medido.
- **Pontos de atenção sem métrica de qualidade.** As premissas e perguntas do Gemini e os avisos do validador são contados (G9) e relatados, sem rubrica (não há no material): a contagem não diz se o ponto apontado é uma falha real. `sem_regra_final` aparece na maior parte do corpus (158 de 249 arquivos, 215 ocorrências), então informa pouco.
- **Latência é local.** Vale para este computador e as condições do dia; a do Gemini depende da rede e do modelo, e o turno inteiro não tem teto.
- **Saída longa.** Um GOBR grande (até 22.311 caracteres numa regra do índice, medido em 05/11/2026 e herdado da Entrega 4) pode estourar `max_output_tokens`; JSON truncado vira `saida_invalida` e gasta uma tentativa.
- **Chave.** A chave do Gemini vem do ambiente (`GOOGLE_API_KEY` ou, na falta dela, `GEMINI_API_KEY`). O código não a lê para fora do SDK, não a imprime, não a grava e não a registra em log.

## 13. Insumos (sha256 calculado em 10/11/2026, com HEAD em `bb9b779`)

Os 13 primeiros são os da Entrega 4 (seção 11 da regra dela), que conferem. Os dois de `entrega5/` foram recalculados em 14/11/2026, depois das mensagens acrescentadas na revisão.

| Arquivo | sha256 |
|---|---|
| `entrega2/indices/indice_com_pontos/default__vector_store.json` | `bf072e8dea1984fe6fc7dba874001c8b0f38bef055347e189bbc17b1d412c403` |
| `entrega2/indices/indice_com_pontos/docstore.json` | `6a53eb1f6cbb58eb897559282be3befd07967973ca8dc3b2dba19328b201657c` |
| `entrega2/indices/indice_com_pontos/index_store.json` | `0ed4e2005953345281606c1183e98697d49f2b64d7a9c516532e218ff6da9b84` |
| `entrega3/indices/indice_manual_C/default__vector_store.json` | `17814d70da582ec128ce677ea0cce18821ba8fefcb956c6f3a09f0f4f7a95417` |
| `entrega3/indices/indice_manual_C/docstore.json` | `0be5fbc3f264aaad22ef4d62aa05f3b5a446bfc64709d22c3ccd44524ad3566e` |
| `entrega3/indices/indice_manual_C/index_store.json` | `8fe24fd2ddf27df7bcecedc836822b911f40aae8037ff159d918259bb1c5db03` |
| `entrega2/consultas_avaliacao.json` (dev, regras) | `abcc8ee18798e9af0c8729d954f54624710831d0e39140a21bcc0af76fe5396d` |
| `entrega2/consultas_teste.json` (teste, regras) | `a91c9ff3726844396b29988317d0089f1447104deb96cd057cdc98a92184f646` |
| `entrega3/consultas_manual_dev.json` (dev, manual) | `2195ccd9076c25cf30bb28e9b9537999a073dfd2880c154dac2811d42885ea1a` |
| `entrega3/consultas_manual_teste.json` (teste, manual) | `e0f2c12a29e14da28323eaca2e6627b3b50fed51372766bcc0ced751f67f3350` |
| `entrega2/comum.py` | `769230dc050a3c2979eb4bbf003a15d658f085148b153731c63b333f3d67af9b` |
| `entrega2/avaliar.py` | `e37a8141c596cdde823fc1e645e8ccfcd7e00e1733ed2f3d5191ce5a58611372` |
| `entrega3/comum_manual.py` | `7a5d1bcec5b632b7157e06914406e9184b2db454288f56cf260de31d87d37ea4` |
| `entrega1/gobr_parser.py` | `bd2d781ddc92b8558c318288ca017b561eb824dc0eea192fc788a7b080006048` |
| `entrega4/comum_fluxo.py` | `5f6be266e18bc6ea01caff93470833c673b8d92c91255a19e5ba3bedf71b184a` |
| `entrega4/config_escolhida.json` | `b6cf2f6c0baafb855386ccaaa14c4ebfc54ba1bed7ae5ebb92950a45c4f67d28` |
| `entrega4/resultados_fluxo_dev.json` | `82812350ad67d2c3e8972f6f89111b42fae539331d39a9c89f7c5055b6c3c42c` |
| `entrega5/consultas_roteamento_dev.json` | `42423d44347cc855f42194cc6447e0151f52baeac4d4b96957ad1c1a9c0405ca` |
| `entrega5/consultas_roteamento_teste.json` | `cd2f075d1e1ea541e0d679d80e6422b36d87506d8d401e7c76d9f0c0be7fa0eb` |

O corpus de calibração (246 arquivos em `referencias/` e 3 em `exemplos/`) não foi alterado desde a Entrega 1.

## 14. Arquivos novos desta entrega

| Arquivo | Papel | Quando |
|---|---|---|
| `regra_agente.md` | esta regra (pré-registro) | agora |
| `consultas_roteamento_dev.json`, `consultas_roteamento_teste.json` | mensagens novas de roteamento | agora |
| `comum_agente.py` | constantes desta regra, roteador, validador, tabela de consultas ao manual, chamada ao Gemini com JSON, grade de regras, medição, escolha e a trava do git | passo 5 |
| `agente.py` | o grafo em LangGraph e a linha de comando: `python agente.py "mensagem" [--json] [--sessao] [--sem-llm] [--config] [--modelo]` | passo 5 |
| `avaliar_agente.py` | `busca`, `escolher`, `roteamento`, `geracao`, `dev`, `teste` (uma vez, com a trava) e `relatorio` | passo 5 |
| `teste_plumbing_agente.py` | testes sem modelo e sem rede, no estilo da Entrega 4 | passo 5 |
| `requirements.txt` | as da Entrega 4 mais `langgraph` (versão registrada no README) | passo 5 |
| `dev_checkpoints_agente/`, `resultados_agente_dev.json` e `.md`, `config_agente.json` | desenvolvimento e escolha | passo 6 |
| `resultados_agente_teste.json` e `.md` | teste, uma vez | passo 6 |
| `README.md` | no padrão do README da Entrega 4 | passo 7 |
