# Entrega 1 — Geração de explicações (GOBR → regra de negócio)

Este código transforma cada regra `.gobr` em uma **explicação em linguagem de negócio**, no estilo das imagens da pasta `exemplos`. O enunciado pede isso na 1ª dica ("Traduza todas as regras .gobr em descrições parecidas com os exemplos que estão nas imagens"). A saída já sai no formato da próxima entrega (indexação, 27/10): **um documento por regra**.

## 1. Como rodar

A pasta `entrega1/` deve ficar dentro de `trabalho/`, ao lado de `exemplos/` e `referencias/`.

**Windows (PowerShell), dentro de `trabalho\entrega1`:**

```powershell
pip install -r requirements.txt
$env:GEMINI_API_KEY = "SUA_CHAVE"          # só vale para esta janela do PowerShell
python gerar_explicacoes.py --limite 3     # teste com 3 regras (~1 min)
python gerar_explicacoes.py                # todas; se parar no meio, rode de novo que ele continua
python gerar_explicacoes.py --refazer-falhas   # opcional: tenta de novo as que falharam na verificação
```

**Sem chave**, só a parte determinística (já vem pronta em `saida/`):

```powershell
python gerar_explicacoes.py --provedor nenhum
```

Opções:
- `--modelo` (padrão `gemini-3.8-flash`)
- `--paralelo` (regras processadas ao mesmo tempo, padrão 4)
- `--pensamento` (nível de raciocínio do Gemini 3.x, padrão `low`; quanto menor, mais rápido)
- `--intervalo` (segundos entre o início das primeiras chamadas, padrão 4)
- `--apenas regra_003` (filtra por nome do arquivo)
- `--dados` (pasta que contém `exemplos/` e `referencias/`)

Erros transitórios do Gemini (503 "high demand", 429 de cota) são tentados de novo automaticamente, com espera crescente.

## 2. Pipeline

```
 .gobr ──► [1] PARSER ──► representação ──► [2] GLOSSÁRIO ──► [3] FICHA ──► [4] GEMINI ──► JSON ──► [5] VERIFICAÇÃO ──► [6] saídas
          (determinístico)  estruturada      (manual §§)       (entrada       (redige,          ▲   falhou? 1 nova tentativa
                                                                do LLM)        few-shot)         └── com a lista de problemas
```

| Arquivo | Papel |
|---|---|
| `gobr_parser.py` | Lê o `.gobr` e devolve times, carteiras e blocos `parametros` (ordem, fonte, filtros, ações). Também faz a análise automática (pontos de atenção). |
| `glossario.py` | Traduz cada filtro/ação para português de negócio e anota a seção do Manual GoBR. |
| `explicacao.py` | Monta a ficha (entrada do LLM), a explicação sem LLM, o texto indexável e a verificação. |
| `gerar_explicacoes.py` | Orquestra tudo: lê os arquivos, elimina repetidos, chama o Gemini, verifica e grava as saídas. |
| `prompts/sistema.md` | Instruções do LLM. |
| `prompts/exemplos_fewshot.json` | Saídas-alvo dos 3 exemplos (few-shot). |
| `prompts/referencias_imagens.json` | Transcrição das 3 imagens, usada só para avaliar o resultado. |

## 3. Decisões e por quê

**D1 — Ler o `.gobr` por código antes de usar o LLM.**
A explicação precisa ser *fiel ao raciocínio do sistema* e *completa* (AIMA §28.3.4). O livro também avisa que um módulo de explicação separado precisa ser "construído, depurado, testado e mantido em sincronia" com o sistema original (§28.3.4; §19.9.4). Por isso o leitor lê 100% dos blocos sem IA, e o LLM só **redige** a partir do resultado.
*Descartado:* mandar o `.gobr` cru para o LLM, porque não haveria como provar que ele não pulou um bloco.

**D2 — Classificar cada linha pela palavra inicial, não pela indentação.**
Os arquivos misturam tab e espaço. Cada palavra-chave corresponde a um passo do **Manual §7.1**:
- `do time/da carteira` = fonte
- linhas antes do `quando` = filtro temporal (§5)
- `quando` = filtros de cliente (§6)
- `frequencia`/`preferencia`/`nao agendar`/`fixo`/`roteirizavel` = ações (§7.3–7.5)
- `sem choque` = conflito (§7.3.8)

Linhas que começam com `e`/`ou` e listas com parêntese aberto são continuação da linha anterior.

**D3 — Quebrar o `quando` em filtros individuais, protegendo `entre X e Y`.**
Assim cada filtro recebe sua tradução e seus números podem ser verificados. Aspas e parênteses também ficam protegidos (listas de cidades e de ids).

**D4 — Preservar a ordem dos blocos.**
Manual §7.6: *"clientes parametrizados em uma regra anterior não são reprocessados por regras subsequentes. A ordem importa."* É isso que permite explicar que `em 90 dias` depois de `em 60 dias` significa "entre 60 e 90 dias".

**D5 — Eliminar arquivos repetidos.**
Dos 249 arquivos, 199 são diferentes (uma regra aparece 28 vezes e outra 20). A comparação é feita por hash do texto, ignorando diferenças de espaço. Isso economiza chamadas ao LLM e evita que cópias dominem a busca na indexação. As cópias ficam listadas no campo `duplicatas`.

**D6 — Glossário com a seção do manual em cada tradução.**
Cada significado aponta de onde veio (ex.: `[§6.2]`). Quando o corpus usa uma forma que o manual não define exatamente (ex.: `sem venda`; `data da rota em N dias`), a tradução sai marcada **(aprox.)**. É uma lacuna declarada, não uma invenção. Resultado: 100% dos 1.887 filtros traduzidos, dos quais 115 marcados como aproximação.

**D7 — A ficha é a única entrada do LLM.**
O LLM recebe o significado de cada filtro já pronto (com o GOBR original ao lado). O trabalho dele é escrever bem, não interpretar a linguagem.

**D8 — Few-shot com o estilo da imagem e o conteúdo do `.gobr`.**
As imagens às vezes divergem do código:
- a Maxlub tem "Capacidade: 35 clientes/dia", que não existe no `.gobr`;
- a Infinitto não mostra o bloco "Baixados na Receita", que existe.

Os exemplos de saída seguem a imagem na forma (segmento → critério → frequência) e o `.gobr` no conteúdo. Assim o modelo aprende a ser fiel ao código.
Usei **leave-one-out**: ao gerar a explicação de um exemplo, ele nunca entra como few-shot de si mesmo, para a avaliação ser honesta.

**D9 — Saída em JSON com schema** (`titulo`, `resumo`, `segmentos[]`, `pontos_de_atencao[]`).
JSON pode ser verificado por código e indexado por segmento ou por regra. A temperatura é 0,2, para o texto variar pouco.

**D10 — Verificação automática + 1 nova tentativa com feedback.**
Para cada regra, o código confere:
- (a) há um segmento por bloco, sem faltar nem sobrar;
- (b) cada `nao agendar` aparece;
- (c) os números de cada frequência aparecem na ação;
- (d) os números de cada filtro aparecem no critério;
- (e) preferência de dias, `fixo` e `roteirizável` são mencionados.

Se algo falhar, o LLM recebe a lista de problemas e tenta de novo. No livro, isso equivale à **verificação** (o produto atende à especificação). A **validação** (a especificação atende o usuário) é a comparação com as imagens, na D13.

**D11 — Explicação sem LLM como alternativa.**
Se a chave ou a cota falharem, a regra fica com a explicação determinística, marcada como tal. Nenhuma regra fica sem explicação.

**D12 — Análise automática que aponta falhas (início do requisito "proativo").**
Todas as checagens vêm do manual:
- bloco nunca alcançado (§7.6);
- falta bloco final, então quem não se encaixa em nenhum bloco mantém a configuração anterior (§7.6);
- nome do bloco cita um número que não está no código (o nome é "história"; o filtro é a decisão, AIMA §28.3.4);
- `nao agendar` com frequência no mesmo bloco (§7.3.4);
- time/carteira não definido no arquivo.

**D13 — Avaliação contra as imagens.**
Nos 3 exemplos, cada item da imagem é procurado na explicação gerada a partir do `.gobr`. O relatório mostra o que bate, o que o `.gobr` tem a mais e o que a imagem pede mas o código não implementa.

**D14 — Um documento por regra, já pronto para indexar.**
O `texto_indexavel` reúne título, resumo, segmentos e pontos de atenção. Isso segue a dica "atente-se para a quebra dos chunks": uma regra cortada ao meio, se recuperada, geraria meia regra.

## 4. Saídas (`saida/`)

| Arquivo | Conteúdo |
|---|---|
| `explicacoes.jsonl` | **Entregável principal** (gerado com o Gemini). Uma linha por regra única, com `id`, `duplicatas`, `explicacao` (JSON), `texto_indexavel`, `verificacao` (ok, problemas, tentativas), `achados_automaticos`, `gobr`. |
| `explicacoes_deterministicas.jsonl` | Mesmo formato, gerado sem LLM (versão de segurança). |
| `regras_ir.jsonl` | A representação estruturada de cada regra, mais a ficha. |
| `explicacoes.md` | Todas as explicações em tabelas, para leitura humana. |
| `relatorio.md` | Números do corpus, taxa de verificação, pontos de atenção e avaliação contra as imagens. |

## 5. Limitações (declaradas)

- **A verificação confere estrutura, ações e números, não o sentido de cada frase.** Uma frase pode estar mal escrita sem mudar nenhum número. Recomendo ler uma amostra de cerca de 10 regras em `explicacoes.md`.
- **"Grupo" sem definição.** Sem a palavra `global`, a recência considera "algum vendedor do mesmo grupo" do dono da carteira (§6.2). O manual não define "grupo" com precisão.
- **Formas que o manual não define exatamente** (`sem venda`, `data da rota em N dias`, `preferencia do vendedor`) estão marcadas como **(aprox.)**.
- **Times e carteiras referenciados mas não definidos** (43 regras) podem estar em outro arquivo do mesmo cliente. Por isso são apontados como "confirmar", não como erro.
