# Explicações das regras GOBR

Gerado em 20/10/2026 10:53. Uma seção por regra única; cópias idênticas aparecem em 'Duplicatas'.

## Regra Infinitto Design

`exemplos/RegraInfinittoDesign.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes com CNPJ baixado na Receita não são agendados; para os demais, o sistema define frequências de contato específicas para prospects e por tempo decorrido desde o último pedido. Os blocos são avaliados em ordem: o cliente é parametrizado no primeiro bloco em que se enquadrar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Baixados na Receita Federal | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 7 dias |  |
| 3 | Ativos | Clientes com pedido nos últimos 60 dias com qualquer vendedor da empresa | 14 dias | Considera compras globais feitas com qualquer vendedor da empresa. |
| 4 | Risco de inatividade | Clientes com pedido nos últimos 90 dias com vendedores do mesmo grupo; na prática, entre 60 e 90 dias sem comprar | 7 dias | Considera compras com vendedores do mesmo grupo do dono da carteira. |
| 5 | Inativos | Todos os clientes do time que não se enquadraram nos blocos anteriores (na prática, sem pedido há mais de 90 dias) | 28 dias | Bloco sem filtro de cliente: funciona como regra final. |

**Pontos de atenção**

- O bloco 3 avalia a última compra global (com qualquer vendedor da empresa nos últimos 60 dias), enquanto o bloco 4 avalia apenas compras com vendedores do mesmo grupo nos últimos 90 dias.

## Regra Maxlub

`exemplos/RegraMaxlub.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes baixados, inadimplentes ou com visita presencial programada na semana não são agendados. Para os demais, a frequência de ligação varia conforme o histórico de compra e o ciclo de vida, deixando fora da agenda quem não compra há mais de 180 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar clientes com rota na semana | Clientes com visita presencial (data de rota) programada na semana atual | Não agendar |  |
| 4 | Clientes prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 5 | Clientes ativos | Clientes com pedido nos últimos 60 dias (com vendedores do mesmo grupo) | 14 dias |  |
| 6 | Risco de inatividade | Clientes com pedido nos últimos 90 dias que não entraram em Ativos; na prática, último pedido entre 60 e 90 dias atrás | 7 dias |  |
| 7 | Inativos (90 a 120 dias) | Clientes com pedido nos últimos 120 dias que não entraram nos blocos anteriores; na prática, último pedido entre 90 e 120 dias atrás | 14 dias |  |
| 8 | Inativos (120 a 150 dias) | Clientes com pedido nos últimos 150 dias que não entraram nos blocos anteriores; na prática, último pedido entre 120 e 150 dias atrás | 21 dias |  |
| 9 | Inativos (150 a 180 dias) | Clientes com pedido nos últimos 180 dias que não entraram nos blocos anteriores; na prática, último pedido entre 150 e 180 dias atrás | 28 dias |  |
| 10 | Clientes fora das regras padrão | Todos os clientes que sobraram dos blocos anteriores; na prática, sem pedido há mais de 180 dias | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Clientes inativos há mais de 180 dias caem no bloco final e deixam de ser agendados.
- Os títulos originais dos blocos 7, 8 e 9 citam 90, 120 e 150 dias, mas os filtros no código abrangem até 120, 150 e 180 dias, respectivamente (referindo-se ao início de cada faixa).

## Regra V1 Vidros

`exemplos/V1Vidros-RegraComercial.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização voltada para o time de televendas (vendedores ativos do tipo televendas). Clientes baixados na Receita Federal são retirados da agenda, enquanto os demais têm sua frequência de ligação definida pelo tempo desde a última compra ou fase de prospecção. Os blocos são avaliados em ordem: o cliente é fixado no primeiro bloco em que se enquadrar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Clientes Ativos | Clientes com compra realizada nos últimos 30 dias com vendedor do mesmo grupo | 14 dias |  |
| 3 | Risco de Inatividade | Clientes com compra nos últimos 45 dias, mas sem compras nos últimos 30 dias (na prática, entre 30 e 45 dias sem comprar) | 7 dias |  |
| 4 | Inativos | Clientes sem compras nos últimos 45 dias com vendedor do mesmo grupo | 14 dias |  |
| 5 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa (que nunca compraram) | 7 dias |  |

**Pontos de atenção**

- Falta de bloco de fechamento: não há uma regra final sem filtros para o time de televendas. Clientes que não se enquadrarem em nenhum dos critérios manterão o agendamento que já tinham anteriormente.
- Ordem de avaliação dos Prospects: o bloco de Prospects (quem nunca comprou) foi colocado depois do bloco de Inativos (sem compra há mais de 45 dias). Se a condição de inatividade considerar clientes sem histórico de compras, os prospects cairão no bloco 4 (14 dias) e nunca chegarão ao bloco 5 (7 dias).

## Regra Padrão goVendas Customizável

`referencias/regra_001.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK
Duplicatas: referencias/regra_002.gobr, referencias/regra_004.gobr, referencias/regra_005.gobr, referencias/regra_006.gobr, referencias/regra_009.gobr, referencias/regra_010.gobr, referencias/regra_012.gobr, referencias/regra_013.gobr, referencias/regra_014.gobr, referencias/regra_015.gobr, referencias/regra_016.gobr, referencias/regra_017.gobr, referencias/regra_018.gobr, referencias/regra_019.gobr, referencias/regra_021.gobr, referencias/regra_024.gobr, referencias/regra_025.gobr, referencias/regra_026.gobr, referencias/regra_027.gobr, referencias/regra_028.gobr, referencias/regra_030.gobr, referencias/regra_031.gobr, referencias/regra_033.gobr, referencias/regra_034.gobr, referencias/regra_035.gobr, referencias/regra_036.gobr, referencias/regra_039.gobr, referencias/regra_040.gobr, referencias/regra_042.gobr, referencias/regra_044.gobr, referencias/regra_052.gobr, referencias/regra_069.gobr, referencias/regra_084.gobr, referencias/regra_088.gobr, referencias/regra_092.gobr, referencias/regra_095.gobr, referencias/regra_096.gobr, referencias/regra_097.gobr, referencias/regra_100.gobr, referencias/regra_103.gobr, referencias/regra_104.gobr, referencias/regra_109.gobr, referencias/regra_110.gobr, referencias/regra_111.gobr, referencias/regra_112.gobr, referencias/regra_117.gobr, referencias/regra_118.gobr, referencias/regra_127.gobr

Parametrização aplicável à carteira fixa de todos os vendedores da empresa. A regra define frequências dinâmicas calculadas a partir das médias da empresa para inativos, ativos e clientes que nunca compraram. Os blocos são avaliados em ordem, e o cliente recebe a regra do primeiro bloco em que se enquadrar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Frequência de inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | Frequência média dos inativos da empresa |  |
| 2 | Frequência de ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | Frequência média dos ativos da empresa |  |
| 3 | Frequência de clientes sem vendas | Clientes sem nenhum pedido registrado (nunca compraram) | Frequência média dos inativos da empresa |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhuma das três condições mantêm a configuração que já tinham anteriormente.

## Regra regra_003

`referencias/regra_003.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização do time de televendas (vendedores ativados). A regra começa bloqueando filiais, clientes com visita recente ou rota próxima do representante externo e clientes que compraram nos últimos 7 dias. Em seguida, segmenta prospects e clientes conforme o intervalo da última compra com qualquer vendedor da empresa, finalizando com uma regra geral. Os blocos são avaliados em ordem: o cliente fica no primeiro em que se enquadrar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar filiais | Clientes cadastrados como filial | Não agendar |  |
| 2 | Não agendar com visita do externo recente | Clientes cuja última visita do representante externo no ERP ocorreu na semana anterior | Não agendar | Evita sobreposição com o atendimento de campo recente. |
| 3 | Não agendar com rota programada | Clientes com visita presencial (rota) agendada para os próximos 7 dias | Não agendar |  |
| 4 | Não agendar compra recente | Clientes com pedido nos últimos 7 dias com qualquer vendedor da empresa | Não agendar |  |
| 5 | Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 6 | Prospect ativado | Clientes cadastrados no ERP há pelo menos 60 dias que realizaram apenas uma compra com o vendedor da carteira | 14 dias |  |
| 7 | Ativos recentes | Clientes com última compra entre 7 e 30 dias atrás com qualquer vendedor da empresa | 14 dias |  |
| 8 | Risco de afastamento | Clientes com última compra entre 31 e 60 dias atrás com qualquer vendedor da empresa | 7 dias |  |
| 9 | Risco de inativação | Clientes com última compra entre 61 e 90 dias atrás com qualquer vendedor da empresa | 3 dias |  |
| 10 | Reativados | Clientes com compra nos últimos 14 dias e sem compra entre 15 e 90 dias atrás | 14 dias | Na prática, este bloco nunca é atingido porque clientes com compra em até 7 dias caem no bloco 4, e de 7 a 30 dias caem no bloco 7. |
| 11 | Inativos | Clientes sem compra nos últimos 90 dias com qualquer vendedor da empresa | 14 dias |  |
| 12 | Regra genérica | Todos os clientes do time que não entraram nos blocos anteriores | 21 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- O bloco 10 (Reativados) não recebe nenhum cliente: compras nos últimos 7 dias já foram bloqueadas no bloco 4, e compras de 7 a 14 dias já foram capturadas no bloco 7 (que cobre de 7 a 30 dias). Se o objetivo for tratar reativados de forma diferenciada, esse bloco precisaria vir antes do bloco 4 ou do bloco 7.

## Regra Nutri Distribuidora

`referencias/regra_007.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicada à carteira fixa dos vendedores de televendas. Os clientes recebem frequências de atendimento conforme sua situação de compra com o próprio vendedor (inativos, ativos ou clientes que nunca compraram). Os blocos são avaliados em ordem e cada cliente é parametrizado no primeiro critério em que se enquadrar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Inativos | Clientes considerados inativos segundo o histórico de compras com o próprio vendedor | 30 dias |  |
| 2 | Ativos | Clientes considerados ativos segundo o histórico de compras com o próprio vendedor | 14 dias |  |
| 3 | Sem vendas | Clientes sem nenhuma compra registrada (nunca compraram) | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadrarem como inativos, ativos ou sem vendas mantêm a parametrização que já tinham anteriormente.

## Regra NB PI

`referencias/regra_008.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicada às equipes de campo da Capital e do Interior (vendedores 34 e 35). Para a carteira da Capital, os clientes adimplentes ou que nunca compraram recebem atendimento quinzenal, enquanto os inadimplentes são atendidos a cada 30 dias. Já para a carteira do Interior, todos os clientes possuem frequência fixa de 30 dias. Os blocos são processados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Adimplentes (Capital) | Clientes da carteira Capital adimplentes (sem pendências financeiras) | 14 dias |  |
| 2 | Sem venda (Capital) | Clientes da carteira Capital sem nenhum pedido registrado | 14 dias |  |
| 3 | Inadimplentes (Capital) | Clientes da carteira Capital inadimplentes (com pendências financeiras em aberto) | 30 dias |  |
| 4 | Todos os clientes (Interior) | Todos os clientes da carteira Interior | 30 dias | Bloco sem filtro de clientes: atende toda a carteira fixa dos vendedores do Interior. |

**Pontos de atenção**

- A carteira da Capital não possui um bloco final sem filtro: clientes que não se enquadrem em adimplentes, sem venda ou inadimplentes mantêm a configuração anterior sem receber nova parametrização.

## Regra VetVida

`referencias/regra_011.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicada às carteiras fixas dos times de televendas e de campo. No televendas, clientes ativos não são agendados e os inativos ou sem venda recebem frequência quinzenal; no campo, clientes inativos inadimplentes são bloqueados e os demais atendidos a cada 14 dias em dias úteis. A avaliação ocorre bloco a bloco em ordem, dentro da carteira de cada vendedor.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes ativos (televendas) | Clientes da carteira fixa de televendas considerados ativos no histórico com o próprio vendedor | Não agendar |  |
| 2 | Clientes inativos (televendas) | Clientes da carteira fixa de televendas considerados inativos no histórico com o próprio vendedor | 14 dias, preferência em dias úteis (segunda a sexta) |  |
| 3 | Clientes sem venda (televendas) | Clientes da carteira fixa de televendas sem nenhuma compra registrada (nunca compraram) | 14 dias, preferência em dias úteis (segunda a sexta) |  |
| 4 | Inativos inadimplentes (campo) | Clientes da carteira fixa de campo considerados inativos para o próprio vendedor e que estão inadimplentes | Não agendar |  |
| 5 | Clientes ativos (campo) | Clientes da carteira fixa de campo considerados ativos no histórico com o próprio vendedor | 14 dias, preferência em dias úteis (segunda a sexta) |  |
| 6 | Inativos adimplentes (campo) | Clientes da carteira fixa de campo considerados inativos para o vendedor e que estão adimplentes (sem pendências financeiras) | 14 dias, preferência em dias úteis (segunda a sexta) |  |
| 7 | Clientes sem venda (campo) | Clientes da carteira fixa de campo sem nenhuma compra registrada (nunca compraram) | 14 dias, preferência em dias úteis (segunda a sexta) |  |

**Pontos de atenção**

- No televendas, clientes ativos são bloqueados de agendamento (não agendar), focando as ligações apenas em clientes inativos ou sem compras anteriores. Confirmar se a intenção da operação é realmente não contatar clientes ativos por televendas.
- Não há bloco final sem filtro para a carteira de televendas nem para a de campo: caso algum cliente não se enquadre nas definições de ativo, inativo ou sem venda para o vendedor, ele manterá a parametrização prévia sem atualização.

## Regra Trenas

`referencias/regra_020.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicada a todos os vendedores da empresa sobre suas carteiras fixas. Define uma frequência de atendimento única para toda a base de clientes cadastrados. Como possui apenas um bloco geral, todos os clientes da carteira recebem a mesma regra.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra padrão da Trenas | Todos os clientes da carteira fixa de cada vendedor da empresa | 7 dias | Bloco sem filtro: aplica-se a todos os clientes da carteira. |

## Regra Supergiro

`referencias/regra_022.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicada aos times de televendas e campo da Supergiro. Para o televendas, todos os clientes recebem atendimento quinzenal nos dias úteis. Para a equipe de campo, clientes sem vendas registradas não são agendados e os demais também recebem visitas a cada 14 dias de segunda a sexta. Os blocos são avaliados em ordem de acordo com a fonte de clientes.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 14 dias para todos os clientes (televendas) | Todos os clientes da carteira do time de televendas | 14 dias, preferência de segunda a sexta | Bloco sem filtro de clientes: funciona como regra geral para o televendas. |
| 2 | Não agendar clientes sem venda (campo) | Clientes da carteira fixa de campo sem nenhuma venda registrada (nunca compraram) | Não agendar |  |
| 3 | 14 dias para clientes ativos ou inativos (campo) | Todos os clientes da carteira de campo que sobraram dos blocos anteriores (clientes com histórico de compras) | 14 dias, preferência de segunda a sexta | Bloco sem filtro de clientes: funciona como regra final para a carteira de campo. |

## Regra BSB Vet

`referencias/regra_023.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização comercial dividida entre três equipes: televendas GYN (supervisores 5178), televendas DF e vendas de campo DF. As regras definem frequências e bloqueios de agendamento com base no histórico de compras com o vendedor, situação financeira (adimplência) e histórico de vendas. Dentro de cada equipe, os blocos são avaliados em ordem e o cliente permanece no primeiro em que se enquadrar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Televendas GYN - Sem venda | Clientes da carteira fixa do televendas GYN sem nenhuma venda registrada (nunca compraram) | 7 dias | Aplica-se ao time televendas GYN (supervisores 5178). |
| 2 | Televendas GYN - Demais clientes | Todos os clientes da carteira fixa do televendas GYN que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro para o televendas GYN: funciona como regra final da equipe. |
| 3 | Televendas DF - Adimplentes | Clientes da carteira fixa do televendas DF adimplentes (sem pendências financeiras) | 7 dias | Aplica-se ao time televendas DF. |
| 4 | Televendas DF - Ativos inadimplentes | Clientes da carteira fixa do televendas DF ativos para o próprio vendedor e inadimplentes | 14 dias |  |
| 5 | Televendas DF - Inativos inadimplentes | Clientes da carteira fixa do televendas DF inativos para o próprio vendedor e inadimplentes | Não agendar |  |
| 6 | Televendas DF - Sem venda | Clientes da carteira fixa do televendas DF sem nenhuma venda registrada (nunca compraram) | 7 dias | Clientes sem venda e adimplentes já foram capturados no bloco 3; este bloco alcança na prática quem não entrou nos blocos anteriores. |
| 7 | Campo DF - Ativos | Clientes do time de campo DF considerados ativos para o próprio vendedor | 7 dias, fixo | Aplica-se ao time de campo DF com restrição rígida de frequência na agenda. |
| 8 | Campo DF - Inativos e demais clientes | Todos os clientes do time de campo DF que sobraram dos blocos anteriores (na prática, inativos ou sem compras) | 15 dias, fixo | Bloco sem filtro para o time de campo DF: funciona como regra final da equipe, com restrição rígida de frequência. |

**Pontos de atenção**

- Não há bloco final sem filtro para a carteira televendas DF: clientes que não se enquadram em nenhum dos blocos da equipe mantêm a parametrização prévia.
- No televendas DF, o bloco 3 pega todos os adimplentes antes de avaliar se o cliente tem vendas. Clientes sem venda que sejam adimplentes já recebem 7 dias no bloco 3, fazendo com que o bloco 6 trate apenas eventuais inadimplentes sem vendas ou casos residuais.

## Regra regra_029

`referencias/regra_029.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicável a todos os vendedores da empresa sobre suas carteiras fixas. Clientes inativos para o próprio vendedor e simultaneamente inadimplentes são retirados da agenda, enquanto todos os demais clientes recebem uma frequência padrão de atendimento de 14 dias. Os blocos são avaliados em ordem de prioridade.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inativos inadimplentes | Clientes inativos no histórico com o próprio vendedor e inadimplentes | Não agendar |  |
| 2 | 14 dias para todos os clientes | Todos os clientes da carteira que sobraram do bloco anterior | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 032

`referencias/regra_032.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de televendas e carteiras das regiões Sul, Sudeste, Centro-Oeste, Norte e Nordeste. Os blocos dividem os clientes por situação na Receita Federal, fase prospect, ramos de atividade, faturamento e recência de compras, aplicando frequências de atendimento específicas. Os blocos são avaliados em ordem e cada cliente é parametrizado no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Prospects | Clientes em ciclo de vida prospect com a empresa | 14 dias |  |
| 3 | Ativos Curva A (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 4 | Ativos Curva B (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 10000 | 21 dias |  |
| 5 | Ativos Curva C (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 120 dias | 28 dias |  |
| 6 | Pré-inativos Curva A (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 7 | Pré-inativos Curva B (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 8 | Pré-inativos Curva C (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 150 dias considerando vendedores do mesmo grupo | 14 dias |  |
| 9 | Inativos Curva A (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 10 | Inativos Curva B (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 11 | Inativos Curva C (Sul, Sudeste e Centro-Oeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER | 14 dias |  |
| 12 | Ativos Curva A (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 13 | Ativos Curva B (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 10000 | 21 dias |  |
| 14 | Ativos Curva C (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 120 dias | 28 dias |  |
| 15 | Pré-inativos Curva A (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 16 | Pré-inativos Curva B (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 17 | Pré-inativos Curva C (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 150 dias | 14 dias |  |
| 18 | Inativos Curva A (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 19 | Inativos Curva B (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 20 | Inativos Curva C (Sul, Sudeste e Centro-Oeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO | 14 dias |  |
| 21 | Ativos Curva A (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 50000 | 10 dias |  |
| 22 | Ativos Curva B (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 23 | Ativos Curva C (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 120 dias | 21 dias |  |
| 24 | Pré-inativos Curva A (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 50000 | 7 dias |  |
| 25 | Pré-inativos Curva B (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 25000 | 10 dias |  |
| 26 | Pré-inativos Curva C (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 150 dias | 14 dias |  |
| 27 | Inativos Curva A (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com faturamento médio mensal acima de R$ 50000 | 10 dias |  |
| 28 | Inativos Curva B (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com faturamento médio mensal acima de R$ 25000 | 10 dias |  |
| 29 | Inativos Curva C (Sul, Sudeste e Centro-Oeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO | 21 dias |  |
| 30 | Ativos Curva A (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 15000 | 28 dias |  |
| 31 | Ativos Curva B (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 120 dias e faturamento médio mensal acima de R$ 10000 | 28 dias |  |
| 32 | Ativos Curva C (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 120 dias | 28 dias |  |
| 33 | Pré-inativos Curva A (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 15000 | 14 dias |  |
| 34 | Pré-inativos Curva B (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 35 | Pré-inativos Curva C (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 150 dias | 14 dias |  |
| 36 | Inativos Curva A (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com faturamento médio mensal acima de R$ 15000 | 28 dias |  |
| 37 | Inativos Curva B (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com faturamento médio mensal acima de R$ 10000 | 28 dias |  |
| 38 | Inativos Curva C (Sul, Sudeste e Centro-Oeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL | 28 dias |  |
| 39 | Ativos Curva A (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 40 | Ativos Curva B (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 10000 | 21 dias |  |
| 41 | Ativos Curva C (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 150 dias | 28 dias |  |
| 42 | Pré-inativos Curva A (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 43 | Pré-inativos Curva B (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 44 | Pré-inativos Curva C (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com compra nos últimos 180 dias | 14 dias |  |
| 45 | Inativos Curva A (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 46 | Inativos Curva B (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER com faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 47 | Inativos Curva C (Norte e Nordeste - Matcon, Ferragista, Agropecuária e Home Center) | Clientes dos ramos MATCON, FERRAGISTA, AGROPECUARIA ou HOME CENTER | 14 dias |  |
| 48 | Ativos Curva A (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 49 | Ativos Curva B (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 10000 | 21 dias |  |
| 50 | Ativos Curva C (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 150 dias | 28 dias |  |
| 51 | Pré-inativos Curva A (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 52 | Pré-inativos Curva B (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 53 | Pré-inativos Curva C (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com compra nos últimos 180 dias | 14 dias |  |
| 54 | Inativos Curva A (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 55 | Inativos Curva B (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO com faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 56 | Inativos Curva C (Norte e Nordeste - EPI e Licitação) | Clientes dos ramos EPI ou LICITACAO | 14 dias |  |
| 57 | Ativos Curva A (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 50000 | 10 dias |  |
| 58 | Ativos Curva B (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 25000 | 14 dias |  |
| 59 | Ativos Curva C (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 150 dias | 21 dias |  |
| 60 | Pré-inativos Curva A (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 50000 | 7 dias |  |
| 61 | Pré-inativos Curva B (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 25000 | 10 dias |  |
| 62 | Pré-inativos Curva C (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com compra nos últimos 180 dias | 14 dias |  |
| 63 | Inativos Curva A (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com faturamento médio mensal acima de R$ 50000 | 10 dias |  |
| 64 | Inativos Curva B (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO com faturamento médio mensal acima de R$ 25000 | 10 dias |  |
| 65 | Inativos Curva C (Norte e Nordeste - Atacado/ Distribuidores) | Clientes do ramo ATACADO | 21 dias |  |
| 66 | Ativos Curva A (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 15000 | 28 dias |  |
| 67 | Ativos Curva B (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 150 dias e faturamento médio mensal acima de R$ 10000 | 28 dias |  |
| 68 | Ativos Curva C (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 150 dias | 28 dias |  |
| 69 | Pré-inativos Curva A (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 15000 | 14 dias |  |
| 70 | Pré-inativos Curva B (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 180 dias e faturamento médio mensal acima de R$ 10000 | 14 dias |  |
| 71 | Pré-inativos Curva C (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com compra nos últimos 180 dias | 14 dias |  |
| 72 | Inativos Curva A (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com faturamento médio mensal acima de R$ 15000 | 28 dias |  |
| 73 | Inativos Curva B (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL com faturamento médio mensal acima de R$ 10000 | 28 dias |  |
| 74 | Inativos Curva C (Norte e Nordeste - Corporativo/ Consumidor) | Clientes do ramo CONS. FINAL |  | Nenhuma ação declarada no bloco. |
| 75 | Clientes que hoje não se enquadraram nas regras padrão | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira(sul_sudeste_centrooeste, norte_nordeste): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira(sul_sudeste_centrooeste): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira(norte_nordeste): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- carteira(sul_sudeste_centrooeste) é usado em diversos blocos, mas não é definido neste arquivo.
- carteira(norte_nordeste) é usado em diversos blocos, mas não é definido neste arquivo.
- O bloco 74 não possui nenhuma ação declarada.

## Regra Magnavet (Regra 037)

`referencias/regra_037.gobr` · origem: llm (gemini-3.6-flash) · verificação: OK

Parametrização aplicada à carteira fixa de todos os vendedores da empresa. Define uma regra única e padronizada para todos os clientes, sem diferenciação por tempo de compra ou perfil. A avaliação ocorre em um único bloco.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrão Magnavet | Todos os clientes da carteira | 30 dias, preferência de segunda a sexta | Bloco sem filtro: funciona como regra final. |

## Regra Padrão Gomes

`referencias/regra_038.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicada a todos os vendedores da empresa sobre suas carteiras fixas. Define a frequência de atendimento de acordo com o status de atividade para o vendedor e a situação financeira (adimplência), tratando clientes sem vendas na regra final. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 2 | Inativos adimplentes | Clientes inativos segundo o histórico com o vendedor e adimplentes (sem pendências financeiras) | 14 dias |  |
| 3 | Inativos inadimplentes | Clientes inativos segundo o histórico com o vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias |  |
| 4 | Sem vendas | Todos os clientes da carteira que sobraram dos blocos anteriores (por exemplo, clientes sem histórico de compras) | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra MGR

`referencias/regra_041.gobr` · origem: llm (gemini-3.8-flash) · verificação: OK

Parametrização aplicada à carteira fixa de todos os vendedores da empresa. Define a frequência de atendimento de forma dinâmica utilizando as médias gerais da empresa para clientes inativos, ativos e sem compras. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Frequência de inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | Frequência média dos inativos da empresa |  |
| 2 | Frequência de ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | Frequência média dos ativos da empresa |  |
| 3 | Frequência de clientes sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | Frequência média dos inativos da empresa |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a carteira fixa de toda a empresa: clientes que não se enquadrarem em nenhum dos critérios mantêm a configuração anterior.

## Regra regra_043

`referencias/regra_043.gobr` · origem: llm (gemini-3.6-flash) · verificação: OK

Parametrização aplicada a todos os vendedores da empresa para os clientes de suas carteiras fixas. Como há apenas um bloco sem filtros, todos os clientes cadastrados recebem uma frequência padrão de atendimento. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrão - Frequência de inativos | Todos os clientes da carteira fixa | 14 dias | Bloco sem filtro: funciona como regra única e final para toda a carteira. |

## Regra Milenium

`referencias/regra_045.gobr` · origem: llm (gemini-3.6-flash) · verificação: OK

Parametrização do time de vendas da empresa Milenium, dividida entre a vendedora Sandra (ID 945) e os demais vendedores. A vendedora Sandra atende seus clientes semanalmente, enquanto os demais vendedores possuem frequências ajustadas conforme o status de inatividade e inadimplência do cliente. Os blocos são avaliados em ordem por fonte de carteira.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Frequência semanal para clientes da Sandra | Todos os clientes da carteira fixa da vendedora Sandra (ID 945) | 7 dias (dias úteis) | Aplica-se apenas à carteira da vendedora Sandra (ID 945). Funciona como regra final para esta fonte. |
| 2 | Clientes inativos e inadimplentes | Clientes inativos no histórico de compras com o próprio vendedor e que estão inadimplentes | 30 dias (dias úteis) | Aplica-se à carteira dos demais vendedores da empresa (exceto Sandra). |
| 3 | Clientes inativos adimplentes | Clientes inativos no histórico de compras com o próprio vendedor que sobraram do bloco anterior (ou seja, adimplentes) | 7 dias (dias úteis) |  |
| 4 | Demais clientes | Todos os clientes da carteira dos demais vendedores que sobraram dos blocos anteriores (clientes ativos ou sem compras) | 14 dias (dias úteis) | Bloco sem filtro: funciona como regra final para a carteira da empresa (exceto Sandra). |

## Regra regra_046

`referencias/regra_046.gobr` · origem: llm (gemini-3.6-flash) · verificação: OK

Parametrização aplicável à carteira fixa de todos os vendedores da empresa. Define a frequência de atendimento com base na situação de atividade do cliente com o próprio vendedor e no status financeiro (adimplente ou inadimplente). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 2 | Inativos adimplentes | Clientes inativos com o vendedor e adimplentes (sem pendências financeiras) | 14 dias |  |
| 3 | Inativos inadimplentes | Clientes inativos com o vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias |  |
| 4 | Sem vendas (demais clientes) | Todos os clientes da carteira que não se enquadraram nos blocos anteriores (por exemplo, clientes sem histórico de compras) | 7 dias | Bloco sem filtro: funciona como regra final. |

## Regra regra_047

`referencias/regra_047.gobr` · origem: llm (gemini-3.6-flash) · verificação: OK

Parametrização aplicada à carteira fixa de todos os vendedores ativados da empresa. Define a frequência de atendimento combinando o status de atividade (ativo, inativo ou sem vendas) com a situação financeira (adimplente ou inadimplente). Os blocos são avaliados em ordem e um cliente só entra na primeira regra que se aplicar a ele.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes | Clientes ativos segundo o histórico do vendedor e adimplentes (sem pendências) | 7 dias |  |
| 2 | Ativos inadimplentes | Clientes ativos segundo o histórico do vendedor e inadimplentes | 14 dias |  |
| 3 | Inativos adimplentes | Clientes inativos segundo o histórico do vendedor e adimplentes | 14 dias |  |
| 4 | Inativos inadimplentes | Clientes inativos segundo o histórico do vendedor e inadimplentes | Não agendar |  |
| 5 | Clientes sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadrarem em nenhum dos critérios mantêm a configuração anterior.
- Existe uma parametrização de bloqueio para CPF descrita no cabeçalho da carteira, porém ela não consta como um bloco de não agendamento na lista.

## Regra 048

`referencias/regra_048.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para as carteiras fixa do time televendas e do time de campo. A regra define frequências de atendimento baseadas no status de atividade com o próprio vendedor e na adimplência dos clientes, avaliando os blocos em ordem sequencial para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes (televendas) | Clientes ativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 14 dias |  |
| 2 | Ativos inadimplentes (televendas) | Clientes ativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 7 dias |  |
| 3 | Inativos adimplentes (televendas) | Clientes inativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 30 dias |  |
| 4 | Inativos inadimplentes (televendas) | Clientes inativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 60 dias |  |
| 5 | Sem venda (televendas) | Clientes sem nenhuma venda registrada com o vendedor (nunca comprou) | 30 dias |  |
| 6 | Prospects (televendas) | Todos os clientes restantes da carteira televendas que não se enquadraram nos blocos anteriores | 30 dias | Bloco sem filtro: funciona como regra final para o televendas. |
| 7 | Ativos adimplentes (campo) | Clientes ativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 7 dias |  |
| 8 | Ativos inadimplentes (campo) | Clientes ativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias |  |
| 9 | Inativos adimplentes (campo) | Clientes inativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 14 dias |  |
| 10 | Inativos inadimplentes (campo) | Clientes inativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias |  |
| 11 | Sem venda (campo) | Clientes sem nenhuma venda registrada com o vendedor (nunca comprou) | 14 dias |  |
| 12 | Prospects (campo) | Todos os clientes restantes da carteira campo que não se enquadraram nos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final para o campo. |

## Regra regra_049

`referencias/regra_049.gobr` · origem: llm (gemini-3.6-flash) · verificação: OK

Parametrização para o time de televendas (vendedores do tipo televendas ativados). Clientes baixados na Receita Federal não são agendados. Para os demais, a frequência de ligação é definida pela recência de pedidos com vendedores do mesmo grupo, além de um bloco específico para prospects. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Clientes ativos | Clientes com pedido nos últimos 30 dias | 14 dias |  |
| 3 | Risco de inatividade | Clientes com pedido nos últimos 45 dias, mas sem pedido nos últimos 30 dias (na prática, entre 30 e 45 dias sem comprar) | 7 dias |  |
| 4 | Inativos | Clientes sem pedido nos últimos 45 dias | 14 dias |  |
| 5 | Clientes prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- O bloco de prospects está posicionado após o bloco de Inativos (sem pedido há mais de 45 dias). Dependendo da interpretação do sistema sobre o histórico de prospects, eles podem ser capturados em Inativos antes de chegar ao bloco de prospects. Recomenda-se mover o bloco de prospects para antes dos inativos.

## Regra regra_050

`referencias/regra_050.gobr` · origem: llm (gemini-3.6-flash) · verificação: OK

Parametrização aplicada à carteira fixa de todos os vendedores da empresa. Define atendimento a cada 7 dias para clientes adimplentes, reduz a frequência para 14 dias para inadimplentes ativos e bloqueia o agendamento de inadimplentes inativos. Os blocos são avaliados em ordem e de forma exclusiva.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 7 dias para adimplentes | Clientes adimplentes (sem pendências financeiras) | 7 dias |  |
| 2 | 14 dias para ativos inadimplentes | Clientes ativos no histórico de compras do próprio vendedor e inadimplentes | 14 dias |  |
| 3 | Não agendar inativos inadimplentes | Clientes inativos no histórico de compras do próprio vendedor e inadimplentes | Não agendar |  |
| 4 | 7 dias para clientes sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum dos 4 blocos mantêm a configuração que já tinham previamente.

## Regra Armazém Santa Maria

`referencias/regra_051.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira 'empresa toda' (todos os vendedores ativos). A frequência e a preferência de atendimento (dias úteis e sábado) variam conforme o status de atividade com o próprio vendedor e a adimplência. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos e adimplentes | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 7 dias, preferência para segunda a sexta e sábado |  |
| 2 | Ativos e inadimplentes | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias, preferência para segunda a sexta e sábado |  |
| 3 | Inativos e adimplentes | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 14 dias, preferência para segunda a sexta e sábado |  |
| 4 | Inativos e inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 5 | Sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias, preferência para segunda a sexta e sábado |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra Padrao 053

`referencias/regra_053.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para duas fontes de clientes: a carteira fixa do time de televendas e a carteira fixa dos vendedores de campo. No televendas, a frequência varia conforme o status de atividade com o próprio vendedor e a adimplência. No campo, a frequência é baseada na média da empresa para ativos, inativos e sem vendas, mantendo a preferência de dias do vendedor. Os blocos são avaliados em ordem separadamente para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 14 dias para ativos adimplentes (televendas) | Clientes da carteira de televendas ativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 14 dias |  |
| 2 | 30 dias para ativos inadimplentes (televendas) | Clientes da carteira de televendas ativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias |  |
| 3 | 7 dias para inativos adimplentes (televendas) | Clientes da carteira de televendas inativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 7 dias |  |
| 4 | Não agendar inativos inadimplentes (televendas) | Clientes da carteira de televendas inativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 5 | 7 dias para sem vendas (televendas) | Clientes da carteira de televendas sem nenhuma venda registrada (nunca compraram) | 7 dias |  |
| 6 | Configuração padrão de inativos (campo) | Clientes da carteira de campo inativos para o próprio vendedor | Frequência média dos clientes inativos da empresa, mantendo a preferência de dias do vendedor |  |
| 7 | Configuração padrão de ativos (campo) | Clientes da carteira de campo ativos para o próprio vendedor | Frequência média dos clientes ativos da empresa, mantendo a preferência de dias do vendedor |  |
| 8 | Configuração padrão de sem vendas (campo) | Clientes da carteira de campo sem nenhuma venda registrada (nunca compraram) | Frequência média dos clientes inativos da empresa, mantendo a preferência de dias do vendedor |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira televendas: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira regra padrão: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 054

`referencias/regra_054.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa. Define a frequência de atendimento para clientes sem nenhuma venda e para adimplentes, e remove da agenda os inadimplentes. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Empresa Customizavel: 14 dias para clientes sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |
| 2 | Regra Padrao da Empresa Customizavel: 30 dias para adimplentes | Clientes adimplentes (sem pendências financeiras) | 30 dias |  |
| 3 | Regra Padrao da Empresa Customizavel: Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 055

`referencias/regra_055.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira televendas, carteira capital e carteira interior. Define frequências de atendimento e regras de não agendamento baseadas em adimplência, histórico de vendas e tipo de carteira. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da NB Distribuidora Customizavel: 14 dias para adimplentes | Clientes adimplentes (sem pendências financeiras) | 14 dias | Aplica-se à carteira televendas. |
| 2 | Regra Padrao da NB Distribuidora: 30 dias para ativos inadimplentes | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias | Aplica-se à carteira televendas. |
| 3 | Regra Padrao da NB Distribuidora: 30 dias para clientes sem venda | Clientes sem nenhuma venda registrada (nunca compraram) | 30 dias | Aplica-se à carteira televendas. |
| 4 | Regra Padrao da NB Distribuidora: nao agendar inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se à carteira televendas. |
| 5 | Regra Padrao da NB Distribuidora Customizavel: 30 dias para clientes sem venda (capital) | Clientes sem nenhuma venda registrada (nunca compraram) | 30 dias | Aplica-se à carteira capital. |
| 6 | Regra Padrao da NB Distribuidora Customizavel: 30 dias para clientes inadimplentes (capital) | Clientes inadimplentes (com pendências financeiras em aberto) | 30 dias | Aplica-se à carteira capital. |
| 7 | Regra Padrao da NB Distribuidora Customizavel: 14 dias para clientes adimplentes (capital) | Todos os clientes da carteira capital que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final para a carteira capital. |
| 8 | Regra Padrao da NB Distribuidora Customizavel: 30 dias para todos os clientes (interior) | Todos os clientes da carteira interior | 30 dias | Bloco sem filtro: funciona como regra final para a carteira interior. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira televendas: clientes dessa carteira que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração anterior.

## Regra 056

`referencias/regra_056.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dividida entre a carteira de prospecção (vendedores IDs 50 e 53) e a regra padrão para o restante da empresa. A prospecção foca em clientes sem vendas e bloqueia quem já comprou. A regra padrão diferencia clientes ativos e inativos combinando adimplência e inadimplência, além de tratar novos clientes. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Prospects da prospecção | Clientes da carteira de prospecção (RCA 50 e 53) sem nenhuma venda registrada | 30 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 2 | Demais clientes da prospecção | Clientes da carteira de prospecção que já compraram; na prática, quem sobrou do bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final para a fonte de prospecção. |
| 3 | Adimplentes ativos | Clientes da regra padrão ativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 14 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 4 | Adimplentes inativos | Clientes da regra padrão inativos para o próprio vendedor e adimplentes | 30 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 5 | Ativos inadimplentes | Clientes da regra padrão ativos para o próprio vendedor e inadimplentes | 30 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 6 | Inativos inadimplentes | Clientes da regra padrão inativos para o próprio vendedor e inadimplentes | Não agendar |  |
| 7 | Clientes sem vendas da regra padrão | Clientes da regra padrão sem nenhuma venda registrada | 30 dias, mantendo a preferência de dias configurada pelo vendedor |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte da regra padrão: clientes que não se enquadram em nenhum dos blocos 3 ao 7 mantêm a parametrização que já tinham.

## Regra 057

`referencias/regra_057.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Primeiro define a frequência para prospects, depois para clientes ativos do vendedor, e por fim aplica uma frequência para os inativos restantes. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 30d para Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 30 dias |  |
| 2 | Freq. de 25d para Ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 25 dias |  |
| 3 | Freq. de 30d para Inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, inativos para o vendedor | 30 dias | Bloco sem filtro: funciona como regra final. |

## Regra 058

`referencias/regra_058.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização separada para a carteira de televendas e a carteira de campo. O televendas define 14 dias para inadimplentes e usa o histórico limitado a 14 dias para os demais. O campo prioriza adimplentes (7 dias), ativos inadimplentes (14 dias), inativos inadimplentes (60 dias) e quem nunca comprou (14 dias). Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 14 dias para clientes inadimplentes (televendas) | Clientes inadimplentes (com pendências financeiras em aberto) da carteira de televendas | 14 dias |  |
| 2 | Frequência baseada no histórico ou máximo de 14 dias (televendas) | Todos os clientes restantes da carteira de televendas que não se enquadraram no bloco anterior | Frequência do histórico de visitas, com limite máximo de 14 dias | Bloco sem filtro: funciona como regra final para a fonte televendas. |
| 3 | 7 dias para clientes adimplentes (campo) | Clientes adimplentes (sem pendências financeiras) da carteira de campo | 7 dias |  |
| 4 | 14 dias para clientes ativos inadimplentes (campo) | Clientes ativos para o próprio vendedor e inadimplentes, da carteira de campo | 14 dias |  |
| 5 | 60 dias para clientes inativos inadimplentes (campo) | Clientes inativos para o próprio vendedor e inadimplentes, da carteira de campo | 60 dias |  |
| 6 | 14 dias para clientes sem venda (campo) | Clientes sem nenhuma venda registrada (nunca comprou) da carteira de campo | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira de campo: clientes que não se enquadram em nenhum bloco desta fonte mantêm a parametrização que já tinham.

## Regra Hospidrogas

`referencias/regra_059.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas com base no ciclo de vida do cliente (prospect, ativo ou inativo) e em seu ramo de atividade. O primeiro bloco bloqueia ramos específicos, e os seguintes definem frequências variadas de atendimento. Os blocos são avaliados em ordem e o cliente fica no primeiro em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar ramos específicos | Clientes cuja atividade é diferente dos 15 ramos permitidos (ramos 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 17, 18 e 19) | Não agendar | Bloqueia grande parte dos ramos de atividade logo no início. |
| 2 | Prospects com ramos específicos | Clientes em ciclo de vida prospect e ramos de atividade iguais a 2, 7, 11, 12, 14 ou 19 | 30 dias |  |
| 3 | Ativos com ramos específicos (30 dias) | Clientes ativos para o vendedor e ramos de atividade iguais a 3, 4, 6, 8, 15 ou 18 | 30 dias |  |
| 4 | Ativos com ramos específicos (15 dias) | Clientes ativos para o vendedor e ramos de atividade iguais a 7 ou 17 | 15 dias |  |
| 5 | Ativos com ramos específicos (7 dias) | Clientes ativos para o vendedor e ramos de atividade iguais a 10, 11, 14 ou 19 | 7 dias |  |
| 6 | Ativos com ramos específicos (5 dias) | Clientes ativos para o vendedor e ramos de atividade iguais a 2 ou 12 | 5 dias |  |
| 7 | Inativos com ramos específicos (30 dias) | Ramos de atividade iguais a 3, 4, 6, 8, 15 ou 18 (que não caíram nos blocos de ativos anteriores) | 30 dias | Trata indiretamente os inativos desses ramos, já que os ativos já foram capturados nos blocos anteriores. |
| 8 | Inativos com ramos específicos (20 dias) | Ramo de atividade igual a 17 | 20 dias |  |
| 9 | Inativos com ramos específicos (15 dias) | Ramo de atividade igual a 10 | 15 dias |  |
| 10 | Inativos com ramos específicos (10 dias) | Ramos de atividade iguais a 11 ou 19 | 10 dias |  |
| 11 | Inativos restantes (Regra final) | Todos os clientes restantes da fonte que sobraram dos blocos anteriores | 5 dias | Bloco sem filtro: funciona como regra final para os clientes restantes. |

**Pontos de atenção**

- O título do bloco 11 menciona ramos 2, 7, 12 ou 14, mas o bloco não possui filtro de cliente (é uma regra final). Na prática, ele atende todos os restantes que não passaram pelos blocos anteriores.

## Regra 060

`referencias/regra_060.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times: televendas e campo. Para cada time, divide os clientes entre ativos (frequência de 7 dias) e inativos (frequência de 15 dias). O time de campo possui parametrização fixa. Os blocos são avaliados em ordem por fonte de clientes.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao do goVendas: Frequencia semanal para clientes ativos | Clientes ativos para o vendedor (segundo histórico de compras) | 7 dias | Aplica-se ao time televendas. |
| 2 | Regra Padrao do goVendas: Frequencia quinzenal para clientes inativos | Todos os clientes do time televendas que sobraram dos blocos anteriores | 15 dias | Bloco sem filtro: funciona como regra final para o televendas. |
| 3 | Regra Padrao do goVendas: Frequencia de 7 dias para clientes ativos (campo) | Clientes ativos para o vendedor (segundo histórico de compras) | 7 dias, fixo | Aplica-se ao time campo. Parametrização fixa. |
| 4 | Regra Padrao do goVendas: Frequencia de 14 dias para clientes inativos (campo) | Todos os clientes do time campo que sobraram dos blocos anteriores | 15 dias, fixo | Bloco sem filtro: funciona como regra final para o campo. Parametrização fixa. |

**Pontos de atenção**

- O nome do bloco 4 cita 14 dias, mas a ação parametrizada é de 15 dias. Confirmar qual vale.

## Regra 061

`referencias/regra_061.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dividida entre a carteira da vendedora Gesiane, a carteira do time de campo e a carteira do televendas. A vendedora Gesiane aplica frequência de 14 dias para inativos, sem venda e ativos. O time de campo não agenda inativos inadimplentes e dá 14 dias para os demais. O televendas não agenda inativos inadimplentes nem clientes sem venda, e dá 14 dias para o restante.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Gesiane Customizavel - Frequencia de 14 dias para clientes inativos da Gesiane | Clientes inativos segundo o histórico de compras com o próprio vendedor da carteira Gesiane | 14 dias |  |
| 2 | Regra Padrao da Gesiane Customizavel - Frequencia de 14 dias para clientes sem venda da Gesiane | Clientes sem nenhuma venda registrada (nunca compraram) da carteira Gesiane | 14 dias |  |
| 3 | Regra Padrao da Gesiane Customizavel - Frequencia de 14 dias para clientes ativos da Gesiane | Clientes ativos segundo o histórico de compras com o próprio vendedor da carteira Gesiane | 14 dias |  |
| 4 | Regra Padrao da Empresa Customizavel - Nao agendar inativos inadimplentes (campo) | Clientes inativos segundo o histórico de compras com o próprio vendedor e inadimplentes (com pendências financeiras em aberto) da carteira campo | Não agendar |  |
| 5 | Regra Padrao do goVendas Customizavel - Frequencia de 14 dias para ativos ou adimplentes (campo) | Todos os clientes da carteira campo que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final para a carteira campo. |
| 6 | Regra Padrao da Empresa Customizavel - Nao agendar inativos inadimplentes (televendas) | Clientes inativos segundo o histórico de compras com o próprio vendedor e inadimplentes (com pendências financeiras em aberto) da carteira televendas | Não agendar |  |
| 7 | Regra Padrao da Empresa Customizavel - Nao agendar clientes sem venda (televendas) | Clientes sem nenhuma venda registrada (nunca compraram) da carteira televendas | Não agendar |  |
| 8 | Regra Padrao do goVendas Customizavel - Frequencia de 14 dias para ativos ou adimplentes (televendas) | Todos os clientes da carteira televendas que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final para a carteira televendas. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira(carteira Gesiane): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 062

`referencias/regra_062.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK
Duplicatas: referencias/regra_064.gobr

Parametrização para as carteiras fixa do televendas e de campo. Define frequências de atendimento e regras de agendamento com base no status do cliente (ativo ou inativo para o vendedor), adimplência e histórico de vendas. Os blocos são avaliados em ordem para cada carteira.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes (televendas) | Clientes ativos para o próprio vendedor e adimplentes na carteira televendas | 7 dias |  |
| 2 | Ativos inadimplentes (televendas) | Clientes ativos para o próprio vendedor e inadimplentes na carteira televendas | 14 dias |  |
| 3 | Inativos adimplentes (televendas) | Clientes inativos para o próprio vendedor e adimplentes na carteira televendas | 14 dias |  |
| 4 | Inativos inadimplentes (televendas) | Clientes inativos para o próprio vendedor e inadimplentes na carteira televendas | Não agendar |  |
| 5 | Sem vendas (televendas) | Clientes sem nenhuma venda registrada na carteira televendas | 14 dias |  |
| 6 | Ativos adimplentes (campo) | Clientes ativos para o próprio vendedor e adimplentes na carteira campo | 7 dias |  |
| 7 | Ativos inadimplentes (campo) | Clientes ativos para o próprio vendedor e inadimplentes na carteira campo | 14 dias |  |
| 8 | Inativos adimplentes (campo) | Clientes inativos para o próprio vendedor e adimplentes na carteira campo | 14 dias | Há sobreposição de critério com o bloco 9, mas como os blocos são avaliados em ordem, este bloco atende os inativos adimplentes primeiro com 14 dias. |
| 9 | Inativos adimplentes (campo) - frequencia 30 dias | Clientes inativos para o próprio vendedor e adimplentes na carteira campo que não caíram no bloco anterior | 30 dias | O nome e o filtro do bloco repetem 'inativos adimplentes', mas na prática ele pega quem sobrou do bloco 8. |
| 10 | Sem vendas (campo) | Clientes sem nenhuma venda registrada na carteira campo | 14 dias |  |

**Pontos de atenção**

- Os blocos 3 e 4 cobrem exatamente o mesmo público (inativos inadimplentes do televendas). Como os blocos são avaliados em ordem, o bloco 3 captura esses clientes com 14 dias e o bloco 4 nunca é atingido para esse grupo.
- Os blocos 8 e 9 cobrem exatamente o mesmo público (inativos adimplentes do campo). O bloco 8 captura esses clientes com 14 dias e o bloco 9 nunca é atingido para esse grupo.
- Não há bloco final sem filtro para a carteira televendas nem para a carteira campo: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 063

`referencias/regra_063.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para as carteiras fixa do time campo e do time televendas. Todos os segmentos recebem frequência de 30 dias com preferência para dias úteis (segunda a sexta). Para o televendas, há uma regra para evitar choque de dias com o time campo.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes ativos (campo) | Clientes ativos segundo o histórico de compras com o próprio vendedor (carteira campo) | 30 dias, preferência de segunda a sexta |  |
| 2 | Clientes inativos (campo) | Clientes inativos segundo o histórico de compras com o próprio vendedor (carteira campo) | 30 dias, preferência de segunda a sexta |  |
| 3 | Clientes sem venda (campo) | Clientes sem nenhuma venda registrada, nunca compram (carteira campo) | 30 dias, preferência de segunda a sexta |  |
| 4 | Clientes ativos (televendas) | Clientes ativos segundo o histórico de compras com o próprio vendedor (carteira televendas) | 30 dias, preferência de segunda a sexta | Evitar choque de dias com o time campo. |
| 5 | Clientes inativos (televendas) | Clientes inativos segundo o histórico de compras com o próprio vendedor (carteira televendas) | 30 dias, preferência de segunda a sexta | Evitar choque de dias com o time campo. |
| 6 | Clientes sem venda (televendas) | Clientes sem nenhuma venda registrada, nunca compram (carteira televendas) | 30 dias, preferência de segunda a sexta | Evitar choque de dias com o time campo. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira carteira campo: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira carteira televendas: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 065

`referencias/regra_065.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira de televendas da Evermax. Define frequência quinzenal para quem comprou nos últimos 30 dias e mensal para os demais ou para quem nunca comprou, com preferência de atendimento de segunda a sexta-feira. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Empresa Customizavel: quinzenal para clientes que compram até 30 dias | Clientes que compraram de algum vendedor do grupo nos últimos 30 dias | 14 dias, preferência de segunda a sexta |  |
| 2 | Regra Padrao da Empresa Customizavel: mensal para clientes que não compram a mais de 30 dias | Clientes sem compra há pelo menos 30 dias que não entraram no bloco anterior | 28 dias, preferência de segunda a sexta |  |
| 3 | Regra Padrao da Empresa Customizavel: mensal para clientes que nunca comprou | Todos os clientes da carteira que sobraram dos blocos anteriores; na prática, clientes que nunca compraram | 28 dias, preferência de segunda a sexta | Bloco sem filtro: funciona como regra final. |

## Regra 066

`referencias/regra_066.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização separada para a carteira de televendas e a carteira de campo. Os clientes são segmentados com base no status de atividade para o vendedor e na adimplência, definindo frequências de atendimento e dias preferenciais úteis (segunda a sexta) ou o não agendamento. Os blocos são avaliados em ordem para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 7 dias para clientes ativos adimplentes (Internos) | Clientes da carteira televendas que estão ativos para o próprio vendedor e estão adimplentes (sem pendências financeiras) | 7 dias, preferência de dias de segunda a sexta |  |
| 2 | 14 dias para clientes ativos inadimplentes (Internos) | Clientes da carteira televendas que estão ativos para o próprio vendedor e estão inadimplentes (com pendências financeiras em aberto) | 14 dias, preferência de dias de segunda a sexta |  |
| 3 | 30 dias para clientes inativos adimplentes (Internos) | Clientes da carteira televendas que estão inativos para o próprio vendedor e estão adimplentes (sem pendências financeiras) | 30 dias, preferência de dias de segunda a sexta |  |
| 4 | Não agendar clientes inativos inadimplentes (Internos) | Clientes da carteira televendas que estão inativos para o próprio vendedor e estão inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 5 | Não agendar clientes sem vendas (Internos) | Clientes da carteira televendas sem nenhuma venda registrada (nunca compraram) | Não agendar |  |
| 6 | 7 dias para clientes ativos (Externos) | Clientes da carteira campo que estão ativos para o próprio vendedor | 7 dias, preferência de dias de segunda a sexta |  |
| 7 | 30 dias para clientes inativos adimplentes (Externos) | Clientes da carteira campo que estão inativos para o próprio vendedor e estão adimplentes (sem pendências financeiras) | 30 dias, preferência de dias de segunda a sexta |  |
| 8 | Não agendar clientes inativos inadimplentes (Externos) | Clientes da carteira campo que estão inativos para o próprio vendedor e estão inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 9 | Não agendar clientes sem vendas (Externos) | Clientes da carteira campo sem nenhuma venda registrada (nunca compraram) | Não agendar |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira(carteira televendas): clientes que não se enquadram em nenhum bloco mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira(carteira campo): clientes que não se enquadram em nenhum bloco mantêm a configuração que já tinham.

## Regra 067

`referencias/regra_067.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times de televendas, capital e interior, definindo frequências de atendimento e preferência de dias úteis (segunda a sexta) com base no histórico de compras com o próprio vendedor e na situação financeira. Os blocos são avaliados em ordem e um cliente não é reprocessado após ser parametrizado.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 14 dias para clientes ativos (televendas) | Clientes ativos para o vendedor no time televendas | 14 dias, preferência de segunda a sexta |  |
| 2 | 30 dias para clientes inativos (televendas) | Clientes inativos para o vendedor no time televendas | 30 dias, preferência de segunda a sexta |  |
| 3 | 7 dias para clientes sem venda (televendas) | Clientes sem nenhuma venda registrada no time televendas | 7 dias, preferência de segunda a sexta |  |
| 4 | 20 dias para clientes ativos adimplentes (capital) | Clientes ativos para o vendedor e adimplentes na carteira capital | 20 dias, preferência de segunda a sexta |  |
| 5 | 20 dias para clientes ativos inadimplentes (capital) | Clientes ativos para o vendedor e inadimplentes na carteira capital | 20 dias, preferência de segunda a sexta |  |
| 6 | 30 dias para clientes inativos adimplentes (capital) | Clientes inativos para o vendedor e adimplentes na carteira capital | 30 dias, preferência de segunda a sexta |  |
| 7 | 30 dias para clientes inativos inadimplentes (capital) | Clientes inativos para o vendedor e inadimplentes na carteira capital | Não agendar |  |
| 8 | 14 dias para clientes sem venda (capital) | Clientes sem nenhuma venda registrada na carteira capital | 30 dias, preferência de segunda a sexta |  |
| 9 | 21 dias para clientes ativos (interior) | Clientes ativos para o vendedor no time interior | 21 dias, preferência de segunda a sexta |  |
| 10 | 21 dias para clientes inativos adimplentes (interior) | Clientes inativos para o vendedor e adimplentes no time interior | 21 dias, preferência de segunda a sexta |  |
| 11 | 42 dias para clientes inativos inadimplentes (interior) | Clientes inativos para o vendedor e inadimplentes no time interior | 42 dias, preferência de segunda a sexta |  |
| 12 | Clientes inativos inadimplentes (interior) | Clientes inativos para o vendedor e inadimplentes na carteira capital | Não agendar | Este bloco usa a fonte carteira capital, mas está inserido após regras do time interior. |
| 13 | 14 dias para clientes sem venda (interior) | Clientes sem nenhuma venda registrada no time interior | 14 dias, preferência de segunda a sexta |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(televendas): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham (regras incrementais, Manual §7.6).
- Não há bloco final sem filtro para a fonte carteira(capital): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham (regras incrementais, Manual §7.6).
- Não há bloco final sem filtro para a fonte time(interior): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham (regras incrementais, Manual §7.6).
- O nome do bloco 8 cita 14 dias, mas a ação parametrizada é de 30 dias. Confirmar qual vale.
- O bloco 12 aplica-se à fonte carteira(capital) no meio de blocos do time(interior).

## Regra 068 Playpet

`referencias/regra_068.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dividida entre a carteira de campo e a carteira de televendas. Para o time de campo, exclui ramos específicos e pessoas físicas, define frequência para ativos adimplentes e sem venda, e remove da agenda quem sobra. Para o televendas, remove inadimplentes e define frequências para ativos, inativos adimplentes e sem venda. Os blocos são avaliados em ordem dentro de cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar plano veterinário | Clientes da carteira de campo com ramo de atividade igual a 17 | Não agendar | Aplica-se à carteira campo. |
| 2 | Não agendar pessoa física | Clientes da carteira de campo que são pessoa física (CPF) | Não agendar | Aplica-se à carteira campo. |
| 3 | Ativos adimplentes campo | Clientes ativos para o vendedor na carteira de campo e adimplentes (sem pendências financeiras) | 30 dias | Aplica-se à carteira campo. |
| 4 | Sem venda campo | Clientes sem nenhuma venda registrada na carteira de campo (nunca compraram) | 21 dias | Aplica-se à carteira campo. |
| 5 | Inadimplentes ou inativos campo | Todos os clientes restantes da carteira de campo que não se enquadraram nos blocos anteriores | Não agendar | Bloco sem filtro para a carteira campo: funciona como regra final. |
| 6 | Não agendar inadimplentes televendas | Clientes inadimplentes da carteira de televendas (com pendências financeiras em aberto) | Não agendar | Aplica-se à carteira televendas. |
| 7 | Ativos adimplentes televendas | Clientes ativos para o vendedor na carteira de televendas e adimplentes (sem pendências financeiras) | 14 dias | Aplica-se à carteira televendas. |
| 8 | Inativos adimplentes televendas | Clientes inativos para o vendedor na carteira de televendas e adimplentes (sem pendências financeiras) | 30 dias | Aplica-se à carteira televendas. |
| 9 | Sem venda televendas | Clientes sem nenhuma venda registrada na carteira de televendas (nunca compraram) | 14 dias | Aplica-se à carteira televendas. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte da carteira de televendas: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 070

`referencias/regra_070.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa do time televendas e para o time de campo. Divide os clientes entre ativos, inativos (com distinção de adimplência no televendas) e sem venda, definindo frequências específicas e preferência de atendimento de segunda a sexta-feira. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se à carteira televendas. |
| 2 | Ativos (televendas) | Clientes ativos para o vendedor | 14 dias, preferência de segunda a sexta | Aplica-se à carteira televendas. |
| 3 | Inativos adimplentes (televendas) | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 30 dias, preferência de segunda a sexta | Aplica-se à carteira televendas. |
| 4 | Sem venda (televendas) | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, preferência de segunda a sexta | Aplica-se à carteira televendas. |
| 5 | Ativos (campo) | Clientes ativos para o vendedor | 14 dias, preferência de segunda a sexta | Aplica-se ao time campo. |
| 6 | Inativos (campo) | Clientes inativos para o vendedor | 30 dias, preferência de segunda a sexta | Aplica-se ao time campo. |
| 7 | Sem venda (campo) | Clientes sem nenhuma venda registrada (nunca comprou) | Não agendar | Aplica-se ao time campo. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira (carteira televendas): clientes que não se enquadram em nenhum bloco mantêm a parametrização anterior.
- Não há bloco final sem filtro para a fonte time (campo): clientes que não se enquadram em nenhum bloco mantêm a parametrização anterior.

## Regra Palmed

`referencias/regra_071.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times de televendas da Paraíba, Piauí, Tocantins, Geral e time de campo. Define frequências de atendimento (fixas ou baseadas no histórico) e preferências de dias da semana, evitando conflito de agenda com a equipe de campo. Os blocos são avaliados em ordem e de forma incremental para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Palmed: 14 dias para inativos e inadimplentes | Clientes inativos para o vendedor e inadimplentes | 14 dias; preferência de segunda a sexta; evitar choque com time de campo | Aplica-se às carteiras do televendas do Piauí e da Paraíba. |
| 2 | Regra Padrao da Palmed: Maximo 7 dias - PI | Restante dos clientes da carteira do televendas do Piauí | Frequência do histórico, no máximo 7 dias; preferência de segunda a sábado; evitar choque com time de campo | Bloco sem filtro de cliente para esta fonte. |
| 3 | Regra Padrao da Palmed: maximo 7 dias - PB | Restante dos clientes da carteira do televendas da Paraíba | Frequência do histórico, no máximo 7 dias; preferência de segunda a sexta; evitar choque com time de campo | Bloco sem filtro de cliente para esta fonte. |
| 4 | Regra Padrao da Palmed: 14 dias para inativos e inadimplentes - Tocantins | Clientes inativos para o vendedor e inadimplentes | 14 dias; preferência de segunda a sexta; evitar choque com time de campo | Aplica-se à carteira do Tocantins. |
| 5 | Regra Padrao da Palmed: semanal para ativos | Restante dos clientes da carteira do Tocantins | Frequência do histórico, no máximo 7 dias; preferência de segunda a sábado; evitar choque com time de campo | Bloco sem filtro de cliente para esta fonte. |
| 6 | Regra Padrao da Palmed: semanal para ativos e adimplentes (segunda a sexta) - Time Televendas | Clientes ativos para o vendedor e adimplentes | Frequência do histórico, no máximo 7 dias; preferência de segunda a sexta | Aplica-se ao time televendas geral. |
| 7 | Regra Padrao da Palmed: quinzenal para ativos e inadimplente (segunda a sexta) - Time Televendas | Clientes ativos para o vendedor e inadimplentes | 14 dias; preferência de segunda a sexta | Aplica-se ao time televendas geral. |
| 8 | Regra Padrao da Palmed: semanal exceto na segunda para inativos adimplentes (terca a sexta) - Time Televendas | Clientes inativos para o vendedor e adimplentes | Frequência do histórico, no máximo 7 dias; preferência de segunda a sexta | Aplica-se ao time televendas geral. |
| 9 | Regra Padrao da Palmed: 30 dias para inativos e inadimplentes (terca a sexta) - Time Televendas | Clientes inativos para o vendedor e inadimplentes | 30 dias; preferência de segunda a sexta | Aplica-se ao time televendas geral. |
| 10 | Regra Padrao da Palmed: 7 dias de terca a sexta - Time Televendas | Restante dos clientes do time televendas geral | Frequência do histórico, no máximo 7 dias; preferência de segunda a sexta | Bloco sem filtro de cliente: funciona como regra final para o time televendas. |
| 11 | Regra Padrao da Palmed: 7 dias para todos os clientes - Time de Campo | Todos os clientes do time de campo | 7 dias | Bloco sem filtro: funciona como regra final para o time de campo. |

**Pontos de atenção**

- Não há bloco final sem filtro para as carteiras do televendas PI e PB: clientes que não se enquadram nos blocos anteriores mantêm a parametrização que já tinham.

## Regra Mais Descartaveis

`referencias/regra_072.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa. Define frequências dinâmicas baseadas na média da empresa para clientes inativos, ativos e sem vendas. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Frequencia de inativos | Clientes inativos de acordo com o histórico de compras com o próprio vendedor | Frequência média dos clientes inativos da empresa |  |
| 2 | Frequencia de ativos | Clientes ativos de acordo com o histórico de compras com o próprio vendedor | Frequência média dos clientes ativos da empresa |  |
| 3 | Frequencia de clientes sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | Frequência média dos clientes inativos da empresa |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 073

`referencias/regra_073.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa. Define frequências dinâmicas baseadas nas médias da empresa para clientes inativos, ativos e sem vendas. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Frequencia de inativos | Clientes inativos para o próprio vendedor, com base no histórico de compras | Frequência média dos clientes inativos da empresa |  |
| 2 | Frequencia de ativos | Clientes ativos para o próprio vendedor, com base no histórico de compras | Frequência média dos clientes ativos da empresa |  |
| 3 | Frequencia de clientes sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | Frequência média dos clientes inativos da empresa |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 074 Bela Forma

`referencias/regra_074.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa. Define frequências de atendimento distintas para clientes inativos, ativos e sem vendas, mantendo a preferência de dias configurada pelo vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Empresa Customizavel: 45 dias para inativos | Clientes considerados inativos segundo o histórico de compras com o próprio vendedor | 45 dias, preferência do vendedor |  |
| 2 | Regra Padrao da Empresa Customizavel: 21 dias para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor, que não entraram no bloco anterior | 21 dias, preferência do vendedor |  |
| 3 | Regra Padrao da Empresa Customizavel: 45 dias quando sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) que não entraram nos blocos anteriores | 45 dias, preferência do vendedor |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 075

`referencias/regra_075.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira fixa dos vendedores do time televendas. Inadimplentes não são agendados; ativos adimplentes têm frequência de 7 dias; inativos adimplentes e clientes sem venda têm frequência de 14 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Ativos adimplentes | Clientes ativos segundo o histórico de compras com o próprio vendedor e adimplentes (sem pendências financeiras) | 7 dias |  |
| 3 | Inativos adimplentes | Clientes inativos segundo o histórico de compras com o próprio vendedor e adimplentes (sem pendências financeiras) que não entraram nos blocos anteriores | 14 dias |  |
| 4 | Sem venda | Clientes sem nenhuma venda registrada (nunca comprou) que não entraram nos blocos anteriores | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 076

`referencias/regra_076.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia inicialmente inadimplentes, bloqueados, inativos para a empresa e quem comprou nos últimos 20 dias. Depois, define agendas para rotas de hoje, prospects, clientes com única compra, clientes com compra regular (frequência histórica) e clientes em ruptura; quem sobra não é agendado. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 3 | Não agendar inativos | Clientes inativos segundo o histórico de compras com qualquer vendedor da empresa | Não agendar |  |
| 4 | Tem compra em até 20 dias atrás | Clientes com pedido nos últimos 20 dias, com qualquer vendedor da empresa | Não agendar |  |
| 5 | Agendamento padrão - Rota | Clientes com data de rota (visita presencial programada) hoje | 1 dia |  |
| 6 | Clientes prospects | Clientes em ciclo de vida prospect com a empresa | 7 dias |  |
| 7 | Cliente ativado | Clientes que compram uma única vez com a empresa | 15 dias |  |
| 8 | Compra regularmente | Clientes com pedido nos últimos 30 dias com qualquer vendedor da empresa e frequência histórica de compra abaixo de 30 dias | Frequência do histórico, com limite mínimo de 5 e máximo de 30 dias |  |
| 9 | Em ruptura | Clientes com pedido entre 31 e 90 dias atrás com qualquer vendedor da empresa | 15 dias |  |
| 10 | Fora de rota | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final. |

## Regra 077

`referencias/regra_077.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia de início clientes bloqueados, inadimplentes ou com compra recente nos últimos 30 dias; em seguida, define frequências de 14 dias para prospects, 7 dias para ativos e 14 dias para os demais (inativos). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 2 | Não agendar clientes inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar clientes com compra nos últimos 30d | Clientes com pedido nos últimos 30 dias | Não agendar |  |
| 4 | Freq. de 14d para clientes prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 5 | Freq. de 7d para clientes ativos | Clientes em ciclo de vida ativo com a empresa (já fizeram alguma compra) | 7 dias |  |
| 6 | Freq. de 14d para clientes inativos | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 078

`referencias/regra_078.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira de clientes da empresa comercial BH (baseada em todos os vendedores da empresa). Define frequências quinzenais ou semanais para clientes ativos, inativos e sem vendas, diferenciando por adimplência, com atendimento restrito aos dias úteis. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Quinzenal para ativos inadimplentes | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias, preferência de atendimento de segunda a sexta |  |
| 2 | Semanal para ativos adimplentes | Clientes ativos para o vendedor (que não entraram no bloco anterior) | 7 dias, preferência de atendimento de segunda a sexta |  |
| 3 | Mensal para inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias, preferência de atendimento de segunda a sexta |  |
| 4 | Quinzenal para inativos adimplentes | Clientes inativos para o vendedor (que não entraram no bloco anterior) | 14 dias, preferência de atendimento de segunda a sexta |  |
| 5 | Quinzenal para sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | 14 dias, preferência de atendimento de segunda a sexta |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 079

`referencias/regra_079.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Primeiro bloqueia o agendamento de clientes com ramos de atividade diferentes de 12 a 19; depois define frequência de 7 dias para o ramo 12 e de 14 dias para os ramos restantes que sobraram. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar ramos diferentes de 12 a 19 | Clientes com ramo de atividade diferente de 12, 13, 14, 15, 16, 17, 18 e 19 | Não agendar |  |
| 2 | 7 dias para ramo 12 | Clientes com ramo de atividade igual a 12 | 7 dias |  |
| 3 | 14 dias para demais ramos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, ramos 13, 14, 15, 16, 17, 18 e 19 | 14 dias | Bloco sem filtro: funciona como regra final para os ramos permitidos que não são 12. |

## Regra Makro Services

`referencias/regra_080.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa, considerando o status de inatividade, atividade e clientes sem venda. Os blocos são avaliados em ordem e aplicam frequências quinzenais ou mensais mantendo a preferência de dias do vendedor.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Empresa Customizavel: 15 dias para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 15 dias, preferência do vendedor | Filtros adicionais da carteira exigem CNAE do ERP iniciando com 03, 47 ou 27. |
| 2 | Regra Padrao da Empresa Customizavel: mensal para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 30 dias, preferência do vendedor | Filtros adicionais da carteira exigem CNAE do ERP iniciando com 03, 47 ou 27. |
| 3 | Regra Padrao da Empresa Customizavel: 15 dias para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 15 dias, preferência do vendedor | Filtros adicionais da carteira exigem CNAE do ERP iniciando com 03, 47 ou 27. |
| 4 | Regra Padrao da Empresa Customizavel: mensal para clientes sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, preferência do vendedor | Filtros adicionais da carteira exigem CNAE do ERP iniciando com 03, 47 ou 27. |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- Os blocos 1 e 3 possuem exatamente os mesmos critérios e ações, o que pode indicar redundância na parametrização.

## Regra Recife Doces

`referencias/regra_081.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de toda a empresa. Aplica diferentes frequências e preferências de atendimento (segunda a sexta) com base no status do cliente com o próprio vendedor (ativo, inativo ou sem vendas) e na situação financeira (adimplente ou inadimplente). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Empresa Customizavel: semanal para clientes ativos e adimplentes | Clientes ativos para o vendedor | 7 dias, preferência de atendimento de segunda a sexta (demais dias bloqueados) |  |
| 2 | Regra Padrao da Empresa Customizavel: 21 dias para clientes ativos e inadimplentes | Clientes ativos para o vendedor E inadimplentes (com pendências financeiras em aberto) | 21 dias, preferência de atendimento de segunda a sexta (demais dias bloqueados) | Como os ativos adimplentes já foram capturados no bloco 1, este bloco pega apenas os ativos que também são inadimplentes. |
| 3 | Regra Padrao da Empresa Customizavel: 30 dias para clientes inativos e adimplentes | Clientes inativos para o vendedor | 30 dias, preferência de atendimento de segunda a sexta (demais dias bloqueados) | Como o filtro exige apenas inativos, na prática este bloco pega os inativos adimplentes (já que os inativos inadimplentes serão capturados no bloco seguinte). |
| 4 | Regra Padrao da Empresa Customizavel: nao agendar inativos e inadimplentes | Clientes inativos para o vendedor E inadimplentes (com pendências financeiras em aberto) | Não agendar | Como o bloco 3 exige apenas clientes inativos sem especificar inadimplência, na prática os inativos inadimplentes caem aqui e não são agendados. |
| 5 | Regra Padrao da Empresa Customizavel: 30 dias para clientes sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, preferência de atendimento de segunda a sexta (demais dias bloqueados) |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- A ordem dos blocos 3 e 4 merece atenção: o bloco 3 pega inativos sem filtrar inadimplência, o que significa que os inativos adimplentes e inadimplentes passariam por ele se não fosse a ordem. Como o bloco 3 vem antes, os inativos adimplentes param nele (30 dias) e os inadimplentes seguem para o bloco 4 (não agendar), o que parece ser o comportamento desejado apesar da ordem invertida dos critérios.

## Regra 082

`referencias/regra_082.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa. Define frequências e preferências de dias úteis com base no status de atividade para o vendedor e na adimplência, tratando clientes ativos, inativos, sem vendas e inadimplentes. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 7 dias, preferência de segunda a sexta |  |
| 2 | Ativos inadimplentes | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias, preferência de segunda a sexta |  |
| 3 | Inativos adimplentes | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 30 dias, preferência de segunda a sexta |  |
| 4 | Inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 5 | Sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | 30 dias, preferência de segunda a sexta |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 083 Brida

`referencias/regra_083.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa da empresa toda. Define frequências dinâmicas baseadas na média da empresa para clientes inativos, ativos e sem nenhuma venda registrada, avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao do goVendas Customizavel - Frequencia de inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | Frequência média dos clientes inativos da empresa |  |
| 2 | Regra Padrao do goVendas Customizavel - Frequencia de ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | Frequência média dos clientes ativos da empresa |  |
| 3 | Regra Padrao do goVendas Customizavel - Frequencia de inativos | Clientes sem nenhuma venda registrada (nunca comprou) | Frequência média dos clientes inativos da empresa |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 085

`referencias/regra_085.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira fixa dos vendedores da empresa toda (Pérola). Define frequências de atendimento de 7, 14 ou 30 dias com base na adimplência e histórico de compras com o vendedor, aplicando preferência de dias úteis no bloco final. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Adimplentes (7 dias) | Clientes adimplentes (sem pendências financeiras) | 7 dias (semanal) |  |
| 2 | Ativos e inadimplentes (14 dias) | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias |  |
| 3 | Inativos e inadimplentes (30 dias) | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias |  |
| 4 | Cliente sem vendas (regra final) | Todos os clientes da carteira que não se enquadraram nos blocos anteriores | 7 dias (semanal) com preferência de atendimento de segunda a sexta (demais dias com valor 0) | Bloco sem filtro: funciona como regra final. |

## Regra 086

`referencias/regra_086.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa. Define a frequência de atendimento combinando o status do cliente (ativo ou inativo com o próprio vendedor, ou sem vendas) com a situação financeira (adimplente ou inadimplente). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 10 dias |  |
| 2 | Ativos inadimplentes | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias |  |
| 3 | Inativos adimplentes | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 14 dias |  |
| 4 | Inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 90 dias |  |
| 5 | Clientes sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) | 21 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 087

`referencias/regra_087.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização separada para a carteira fixa do time de televendas e a carteira fixa do time de campo. Para o televendas, divide clientes ativos e inativos combinando adimplência e inadimplência, além de tratar quem nunca comprou. Para o campo, divide por adimplência e trata quem nunca comprou. Todos atendem de segunda a sexta. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes (televendas) | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 14 dias, preferência de dias de segunda a sexta |  |
| 2 | Ativos inadimplentes (televendas) | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras) | 30 dias, preferência de dias de segunda a sexta |  |
| 3 | Inativos adimplentes (televendas) | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 30 dias, preferência de dias de segunda a sexta |  |
| 4 | Inativos inadimplentes (televendas) | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras) | 60 dias, preferência de dias de segunda a sexta |  |
| 5 | Sem venda (televendas) | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, preferência de dias de segunda a sexta |  |
| 6 | Adimplentes (campo) | Clientes adimplentes (sem pendências financeiras) da carteira de campo | 14 dias, preferência de dias de segunda a sexta |  |
| 7 | Inadimplentes (campo) | Clientes inadimplentes (com pendências financeiras) da carteira de campo | 30 dias, preferência de dias de segunda a sexta |  |
| 8 | Sem venda (campo) | Clientes sem nenhuma venda registrada (nunca comprou) da carteira de campo | 30 dias, preferência de dias de segunda a sexta |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte da carteira televendas: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- Não há bloco final sem filtro para a fonte da carteira campo: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 089

`referencias/regra_089.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Define a frequência de atendimento com base no ciclo de vida (prospects), atividade para o vendedor e adimplência. Os blocos são avaliados em ordem e o cliente fica no primeiro em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 7d para Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 7 dias |  |
| 2 | Freq. de 7d para Ativos Adimplentes | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 7 dias |  |
| 3 | Freq. de 14d para Ativos Inadimplentes | Clientes ativos para o vendedor que não entraram nos blocos anteriores (na prática, inadimplentes) | 14 dias |  |
| 4 | Freq. de 7d para Inativos Adimplentes | Clientes adimplentes que não entraram nos blocos anteriores (na prática, inativos para o vendedor e adimplentes) | 7 dias |  |
| 5 | Freq. de 14d para Inativos Inadimplentes | Todos os clientes restantes da fonte que não se enquadraram nos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 090

`referencias/regra_090.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira fixa de todos os vendedores da empresa. Define frequências de atendimento para clientes ativos, inativos e sem venda, com preferência de dias de segunda a sábado. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Empresa Customizavel: semanal para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias, com preferência de atendimento de segunda a sábado |  |
| 2 | Regra Padrao da Empresa Customizavel: 14 dias para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 14 dias, com preferência de atendimento de segunda a sábado |  |
| 3 | Regra Padrao da Empresa Customizavel: 14 dias para clientes sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias, com preferência de atendimento de segunda a sábado |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 091

`referencias/regra_091.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização separada para a carteira televendas e a carteira de campo. Para o televendas, define frequências de 14 dias para ativos, 60 dias para inativos e 14 dias para sem vendas. Para o campo, divide os ativos e inativos entre adimplentes e inadimplentes, definindo frequências específicas para cada caso, além de 14 dias para sem vendas. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 14 dias para ativos (televendas) | Clientes da carteira televendas que estão ativos segundo o histórico com o próprio vendedor | 14 dias | Aplica-se apenas à carteira televendas. |
| 2 | 60 dias para inativos (televendas) | Clientes da carteira televendas que estão inativos segundo o histórico com o próprio vendedor | 60 dias | Aplica-se apenas à carteira televendas. |
| 3 | 14 dias para clientes sem vendas (televendas) | Clientes da carteira televendas sem nenhuma venda registrada (nunca compraram) | 14 dias | Aplica-se apenas à carteira televendas. |
| 4 | 7 dias ativos adimplentes (campo) | Clientes da carteira campo ativos segundo o histórico com o próprio vendedor e adimplentes (sem pendências financeiras) | 7 dias | Aplica-se apenas à carteira de campo. |
| 5 | 14 dias para ativos inadimplentes (campo) | Clientes da carteira campo ativos segundo o histórico com o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias | Aplica-se apenas à carteira de campo. |
| 6 | 30 dias inativos adimplentes (campo) | Clientes da carteira campo inativos segundo o histórico com o próprio vendedor e adimplentes (sem pendências financeiras) | 30 dias | Aplica-se apenas à carteira de campo. |
| 7 | 60 dias para inativos inadimplentes (campo) | Clientes da carteira campo inativos segundo o histórico com o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 60 dias | Aplica-se apenas à carteira de campo. |
| 8 | 14 dias para clientes sem vendas (campo) | Clientes da carteira campo sem nenhuma venda registrada (nunca compraram) | 14 dias | Aplica-se apenas à carteira de campo. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira televendas: clientes que não se enquadram em nenhum bloco mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira campo: clientes que não se enquadram em nenhum bloco mantêm a configuração que já tinham.

## Regra 093

`referencias/regra_093.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times de televendas, campo capital e campo interior, utilizando as carteiras fixas de cada vendedor. Define frequências e dias preferenciais (segunda a sexta) com base no status de atividade e adimplência. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes - televendas | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 7 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time televendas. |
| 2 | Ativos inadimplentes - televendas | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time televendas. |
| 3 | Inativos - televendas | Clientes inativos para o vendedor | 30 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time televendas. |
| 4 | Sem vendas - televendas | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time televendas. |
| 5 | Ativos adimplentes - campo capital | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 7 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time campo capital. |
| 6 | Ativos inadimplentes - campo capital | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time campo capital. |
| 7 | Inativos - campo capital | Clientes inativos para o vendedor | 30 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time campo capital. |
| 8 | Sem vendas - campo capital | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time campo capital. |
| 9 | Ativos - campo interior | Clientes ativos para o vendedor | 14 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time campo interior. Não diferencia adimplência. |
| 10 | Inativos - campo interior | Clientes inativos para o vendedor | 30 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time campo interior. |
| 11 | Sem vendas - campo interior | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, preferência de segunda a sexta | Aplica-se à carteira fixa do time campo interior. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira(carteira fixa time televendas): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira(carteira fixa time campo capital): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira(carteira fixa time interior): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 094

`referencias/regra_094.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa do time televendas (adimplentes, inadimplentes e sem venda) e para a carteira fixa do time campo (todos os restantes). Os blocos são avaliados em ordem e usam fontes de carteiras específicas.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Adimplentes (televendas) | Clientes adimplentes (sem pendências financeiras) da carteira televendas | 30 dias |  |
| 2 | Inadimplentes (televendas) | Clientes inadimplentes (com pendências financeiras em aberto) da carteira televendas que não entraram no bloco anterior | 60 dias |  |
| 3 | Sem venda (televendas) | Clientes sem nenhuma venda registrada (nunca comprou) da carteira televendas que não entraram nos blocos anteriores | 30 dias |  |
| 4 | Todos os clientes (campo) | Todos os clientes da carteira campo que sobraram | 30 dias | Bloco sem filtro para a carteira campo: funciona como regra final para este time. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte da carteira televendas: clientes desta carteira que não se enquadram em nenhum dos três primeiros blocos mantêm a parametrização que já tinham.

## Regra 098

`referencias/regra_098.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização aplicada a todos os vendedores da empresa que estão ativados. Possui um único bloco sem filtro que define a frequência de atendimento para todos os clientes da fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Teste CCN 11: 1d para todos os clientes | Todos os clientes da fonte (todos os clientes da empresa) | 1 dias | Bloco sem filtro: funciona como regra final e atende a todos os clientes. |

## Regra 099

`referencias/regra_099.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time televendas e o time de campo. O time televendas possui regras específicas baseadas em vendas e adimplência, enquanto o time de campo recebe uma frequência padrão de 30 dias para os clientes restantes. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | 7 dias para clientes sem venda | Clientes do time televendas sem nenhuma venda registrada | 7 dias | Aplica-se apenas ao time televendas. |
| 2 | 30 dias para ativos inadimplentes | Clientes do time televendas ativos para o próprio vendedor e inadimplentes | 30 dias | Aplica-se apenas ao time televendas. |
| 3 | Nao agendar inativos inadimplentes | Clientes do time televendas inativos para o próprio vendedor e inadimplentes | Não agendar | Aplica-se apenas ao time televendas. |
| 4 | 7 dias para clientes adimplentes | Clientes do time televendas adimplentes (sem pendências financeiras) | 7 dias | Aplica-se apenas ao time televendas. |
| 5 | 30 dias para clientes dos externos | Todos os clientes do time campo que não foram parametrizados por blocos anteriores | 30 dias | Bloco sem filtro para a fonte time campo: funciona como regra final para este time. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time televendas: clientes deste time que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 101

`referencias/regra_101.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para três times de vendedores: televendas, capital (vendedores de campo exceto IDs 17, 18 e 13) e interior (vendedores IDs 17, 18 e 13). Define frequências de atendimento e regras de não agendamento baseadas no status do cliente (ativo, inativo com ou sem inadimplência, ou sem venda). Os blocos são avaliados em ordem para cada fonte de clientes.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes ativos (televendas) | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias | Aplica-se ao time televendas. |
| 2 | Clientes inativos (televendas) | Clientes inativos segundo o histórico de compras com o próprio vendedor | 30 dias | Aplica-se ao time televendas. |
| 3 | Clientes sem venda (televendas) | Clientes sem nenhuma venda registrada (nunca comprou) | 7 dias | Aplica-se ao time televendas. |
| 4 | Clientes ativos (regiao metropolitana) | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias | Aplica-se ao time capital. |
| 5 | Clientes inativos adimplentes (regiao metropolitana) | Clientes inativos segundo o histórico de compras com o próprio vendedor e adimplentes (sem pendências financeiras) | 14 dias | Aplica-se ao time capital. |
| 6 | Clientes inativos inadimplentes (regiao metropolitana) | Clientes inativos segundo o histórico de compras com o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se ao time capital. |
| 7 | Clientes sem venda (regiao metropolitana) | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias | Aplica-se ao time capital. |
| 8 | Clientes ativos (interior) | Clientes ativos segundo o histórico de compras com o próprio vendedor | 14 dias | Aplica-se ao time interior. |
| 9 | Clientes inativos adimplentes (interior) | Clientes inativos segundo o histórico de compras com o próprio vendedor e adimplentes (sem pendências financeiras) | 30 dias | Aplica-se ao time interior. |
| 10 | Clientes inativos inadimplentes (interior) | Clientes inativos segundo o histórico de compras com o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se ao time interior. |
| 11 | Clientes sem venda (interior) | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias | Aplica-se ao time interior. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time (time televendas): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time (time capital): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time (time interior): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 102

`referencias/regra_102.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa do televendas e para o time de campo. O televendas diferencia clientes inativos e inadimplentes (30 dias) dos demais (14 dias), ambos com preferência para dias úteis (segunda a sexta). O time de campo possui uma regra final única de 30 dias também para dias úteis. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Inativos e inadimplentes do televendas | Clientes da carteira de televendas que estão inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias, preferência de segunda a sexta |  |
| 2 | Demais clientes do televendas | Todos os clientes restantes da carteira de televendas que não se enquadraram no bloco anterior | 14 dias, preferência de segunda a sexta | Bloco sem filtro: funciona como regra final para a fonte de televendas. |
| 3 | Clientes de campo | Todos os clientes do time de campo | 30 dias, preferência de segunda a sexta | Bloco sem filtro: funciona como regra final para a fonte de campo. |

## Regra 105

`referencias/regra_105.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa de todos os vendedores da empresa (empresa toda). Os clientes são separados entre ativos e inativos, adimplentes e inadimplentes, e sem vendas, definindo frequências específicas e preferência de atendimento de segunda a sexta. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes | Clientes ativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 7 dias, preferência de segunda a sexta (demais dias com valor 0) |  |
| 2 | Ativos inadimplentes | Clientes ativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias, preferência de segunda a sexta (demais dias com valor 0) |  |
| 3 | Inativos adimplentes | Clientes inativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 14 dias, preferência de segunda a sexta (demais dias com valor 0) |  |
| 4 | Inativos inadimplentes | Clientes inativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 5 | Clientes sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias, preferência de segunda a sexta (demais dias com valor 0) |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 106

`referencias/regra_106.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa do time televendas e do time campo. Define frequências de atendimento baseadas no histórico de compras com o próprio vendedor e na situação financeira (adimplente ou inadimplente). Os blocos são avaliados em ordem para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos adimplentes (televendas) | Clientes ativos para o próprio vendedor e adimplentes na carteira televendas | 10 dias |  |
| 2 | Ativos inadimplentes (televendas) | Clientes ativos para o próprio vendedor e inadimplentes na carteira televendas | 21 dias |  |
| 3 | Inativos adimplentes (televendas) | Clientes inativos para o próprio vendedor e adimplentes na carteira televendas | 14 dias |  |
| 4 | Inativos inadimplentes (televendas) | Clientes inativos para o próprio vendedor e inadimplentes na carteira televendas | 60 dias |  |
| 5 | Sem venda (televendas) | Clientes sem nenhuma venda registrada na carteira televendas | 30 dias |  |
| 6 | Ativos adimplentes (campo) | Clientes ativos para o próprio vendedor e adimplentes na carteira campo | 30 dias |  |
| 7 | Inativos adimplentes (campo) | Clientes inativos para o próprio vendedor e adimplentes na carteira campo | 14 dias |  |
| 8 | Não agendar inadimplentes (campo) | Clientes inadimplentes na carteira campo que não entraram nos blocos anteriores | Não agendar | Como os ativos e inativos adimplentes já passaram antes, este bloco pega os inadimplentes restantes (ativos e inativos inadimplentes). |
| 9 | Sem venda (campo) | Clientes sem nenhuma venda registrada na carteira campo | 30 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira televendas: clientes que não se enquadram em nenhum bloco mantêm a configuração anterior.
- Não há bloco final sem filtro para a fonte carteira campo: clientes que não se enquadram em nenhum bloco mantêm a configuração anterior.

## Regra 107

`referencias/regra_107.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa dos vendedores da empresa toda (Higicop). Todos os clientes, sejam inativos, ativos ou sem vendas para o vendedor, recebem frequência quinzenal (15 dias). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Empresa Customizavel: 15 dias para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 15 dias quinzenal, com preferência de dias configurada pelo vendedor |  |
| 2 | Regra Padrao da Empresa Customizavel: 15 dias para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 15 dias quinzenal, com preferência de dias configurada pelo vendedor |  |
| 3 | Regra Padrao da Empresa Customizavel: 15 dias para clientes sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) | 15 dias quinzenal |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- Como todos os três blocos aplicam exatamente a mesma frequência quinzenal e cobrem inativos, ativos e sem vendas, a separação em blocos sequenciais resulta no mesmo efeito prático de uma regra única para toda a carteira.

## Regra 108

`referencias/regra_108.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (todos os vendedores da empresa ativados). Inadimplentes não são agendados, e os demais recebem frequências de atendimento variadas baseadas no ciclo de vida, ramo de atividade (construtora ramo 37), frequência histórica e recência de compras com o próprio vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Diferpan: Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Diferpan: Freq. de 7d para cliente que nunca tirou com o vendedor | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 7 dias |  |
| 3 | Diferpan: Freq. de 21d para construtora que comprou uma unica vez com o vendedor | Clientes com compra única com o próprio vendedor e ramo de atividade igual a 37 (construtora) | 21 dias |  |
| 4 | Diferpan: Freq. de 7d para cliente que comprou uma unica vez com o vendedor | Clientes com compra única com o próprio vendedor | 7 dias |  |
| 5 | Diferpan: Freq. de 7d para clientes com frequência histórica menor do que 11 dias | Clientes com frequência histórica de compra abaixo de 11 dias | 7 dias |  |
| 6 | Diferpan: Freq. de 14d para construtora que comprou com o vendedor entre 60 dias e 89 dias | Clientes com ramo de atividade 37 e cuja última compra com o próprio vendedor NÃO ocorreu entre 60 e 89 dias atrás | 14 dias |  |
| 7 | Diferpan: Freq. de 21d para construtora que comprou com o vendedor entre 11 dias e 59 dias | Clientes com ramo de atividade 37 e cuja última compra com o próprio vendedor NÃO ocorreu entre 11 e 59 dias atrás | 21 dias |  |
| 8 | Diferpan: Freq. de 21d para clientes que comprou ultima vez com o vendedor a mais de 90 dias | Clientes em ciclo de vida inativo com o próprio vendedor | 21 dias |  |
| 9 | Diferpan: Freq. de 7d para clientes que comprou com o vendedor entre 11 dias e 89 dias | Clientes cuja última compra com o próprio vendedor NÃO ocorreu nos últimos 90 dias | 7 dias |  |
| 10 | Diferpan: Freq. de 7d para demais clientes | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | 7 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- O nome do bloco 8 (Diferpan: Freq. de 21d para clientes que comprou ultima vez com o vendedor a mais de 90 dias) cita 90 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.

## Regra 113

`referencias/regra_113.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores da empresa utilizando a carteira fixa de cada um. Define frequências de atendimento de 30 ou 60 dias (com preferência de atendimento de segunda a sexta-feira) ou o não agendamento, dependendo se o cliente nunca comprou, é ativo ou inativo, e se está adimplente ou inadimplente. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias, com preferência de atendimento de segunda a sexta-feira |  |
| 2 | Clientes ativos adimplentes | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 30 dias, com preferência de atendimento de segunda a sexta-feira |  |
| 3 | Clientes ativos inadimplentes | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 60 dias, com preferência de atendimento de segunda a sexta-feira |  |
| 4 | Clientes inativos adimplentes | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 60 dias, com preferência de atendimento de segunda a sexta-feira |  |
| 5 | Clientes inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 114

`referencias/regra_114.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para vários times (Jamile, Ruptura Elizangela, Ruptura Jamile, Interior, Capital e Televendas). Cada time possui regras específicas de agendamento, frequência de atendimento baseada no status e histórico de compras, e preferência de atendimento nos dias úteis. Os blocos são avaliados em ordem para cada fonte de clientes.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Jamile | Todos os clientes do time da Jamile | 15 dias, preferência nos dias úteis (segunda a sexta) | Bloco sem filtro: aplica-se a todos os clientes da fonte. |
| 2 | Nao agendar clientes que compraram a menos de 30 dias | Clientes do time Ruptura Jamile com compra recente global entre 0 e 30 dias atrás | Não agendar |  |
| 3 | Frequencia de 14 dias para clientes a 30 dias sem comprar | Todos os clientes restantes do time Ruptura Jamile | 14 dias | Bloco sem filtro: atende quem não caiu no bloco anterior. |
| 4 | Nao agendar clientes que compraram a menos de 30 dias | Clientes do time Ruptura Elizangela com compra recente global entre 0 e 30 dias atrás | Não agendar |  |
| 5 | Nao agendar clientes bloqueados | Clientes bloqueados para atendimento no time Ruptura Elizangela que não caíram no bloco anterior | Não agendar |  |
| 6 | Frequencia de 14 dias para clientes a 30 dias sem comprar | Todos os clientes restantes do time Ruptura Elizangela | 14 dias | Bloco sem filtro: atende quem sobra. |
| 7 | Nao agendar inativos inadimplentes (interior) | Clientes do time interior que são inativos para o vendedor e inadimplentes | Não agendar |  |
| 8 | 30 dias para clientes ativos ou adimplentes (interior) | Todos os clientes restantes do time interior | 30 dias, preferência nos dias úteis (segunda a sexta) | Bloco sem filtro: atende quem sobrou do time interior. |
| 9 | Nao agendar inativos inadimplentes (capital) | Clientes do time capital que são inativos para o vendedor e inadimplentes | Não agendar |  |
| 10 | 30 dias para clientes ativos inadimplentes (capital) | Clientes ativos para o vendedor e inadimplentes no time capital que não caíram no bloco anterior | 30 dias, preferência nos dias úteis (segunda a sexta) |  |
| 11 | 14 dias para adimplentes (capital) | Todos os clientes restantes do time capital | 14 dias, preferência nos dias úteis (segunda a sexta) | Bloco sem filtro: atende o restante do time capital. |
| 12 | Quinzenal para clientes ativos (televendas) | Clientes ativos para o vendedor no time televendas | 15 dias, preferência nos dias úteis (segunda a sexta) |  |
| 13 | Semanal para clientes inativos ou prospects (televendas) | Todos os clientes restantes do time televendas | 7 dias, preferência nos dias úteis (segunda a sexta) | Bloco sem filtro: atende o restante do time televendas. |

## Regra 115

`referencias/regra_115.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times distintos: o time atacado (vendedores 510, 617 e 596) recebe frequência de atendimento a cada 7 dias, e o time salmão (vendedores 613, 614 e 568) recebe frequência a cada 2 dias. Como não há filtros de cliente, todos os clientes de cada time são contemplados.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Frigoforte: 7 dias para atacado (televendas) | Todos os clientes do time atacado | 7 dias | Bloco sem filtro: aplica-se a todos os clientes da fonte. |
| 2 | Regra Padrao da Frigoforte: 2 dias para salmao (televendas) | Todos os clientes do time salmão | 2 dias | Bloco sem filtro: aplica-se a todos os clientes da fonte. |

## Regra 116

`referencias/regra_116.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times de televendas e campo. Filiais de ambos os times são bloqueadas de agendamento no primeiro bloco. O televendas aplica frequência fixa de 7 dias com preferência de segunda a sábado e evita choque com o time de campo. O time de campo define frequências variadas (7, 14, 30 ou 60 dias) com base no status de ativo/inativo, adimplência e clientes sem vendas. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar filiais | Clientes que são filiais (para os times televendas e campo) | Não agendar | Aplica-se a ambos os times. |
| 2 | Freq. de 7d para todos os clientes (televendas) | Todos os clientes restantes do time televendas que não são filiais | 7 dias, preferência de segunda a sábado (evitando choque de dias com o time de campo) | Bloco sem filtro de cliente para o televendas: pega o restante da fonte. |
| 3 | Freq. de 7d para Ativos Adimplentes (campo) | Clientes ativos para o próprio vendedor e adimplentes (sem pendências financeiras) no time de campo | 7 dias |  |
| 4 | Freq. de 14d para Ativos Inadimplentes (campo) | Clientes ativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) no time de campo | 14 dias |  |
| 5 | Freq. de 30d para Inativos Adimplentes (campo) | Clientes inativos para o próprio vendedor e adimplentes (sem pendências financeiras) no time de campo | 30 dias |  |
| 6 | Freq. de 60d para Inativos Inadimplentes (campo) | Clientes inativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) no time de campo | 60 dias |  |
| 7 | Freq. de 7d para sem vendas (campo) | Clientes sem nenhuma venda registrada (nunca comprou) no time de campo | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(televendas, campo) e time(campo): clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 119

`referencias/regra_119.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time televendas (vendedores do tipo televendas ativados). A frequência de atendimento e os agendamentos variam conforme o status do cliente (ativo ou inativo para o vendedor) e sua situação financeira (adimplente ou inadimplente), além de uma regra para quem nunca comprou. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes ativos adimplentes | Clientes ativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 15 dias |  |
| 2 | Clientes ativos inadimplentes | Clientes ativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias |  |
| 3 | Clientes inativos adimplentes | Clientes inativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 7 dias |  |
| 4 | Clientes inativos inadimplentes | Clientes inativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 5 | Clientes sem compra | Clientes sem nenhuma venda registrada (nunca compraram) | 15 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 120 IdealPet

`referencias/regra_120.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times Yasmim, televendas, capital e interior. Define regras específicas de não agendamento e frequências de atendimento diferenciadas (com preferência de dias úteis, de segunda a sexta) para clientes ativos, inativos, adimplentes, inadimplentes e sem venda em cada carteira. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da IdealPet: Nao agendar clientes de carteira propria para RCA 12 | Todos os clientes da fonte do time Yasmim | Não agendar | Bloco sem filtro: funciona como regra final para o time Yasmim. |
| 2 | 14 dias para clientes ativos (televendas) | Clientes ativos para o próprio vendedor na carteira televendas | 14 dias, preferência de segunda a sexta |  |
| 3 | 30 dias para clientes inativos (televendas) | Clientes inativos para o próprio vendedor na carteira televendas | 30 dias, preferência de segunda a sexta |  |
| 4 | 7 dias para clientes sem venda (televendas) | Clientes sem nenhuma venda registrada na carteira televendas | 7 dias, preferência de segunda a sexta |  |
| 5 | 20 dias para clientes ativos adimplentes (capital) | Clientes ativos e adimplentes na carteira capital | 20 dias, preferência de segunda a sexta |  |
| 6 | 20 dias para clientes ativos inadimplentes (capital) | Clientes ativos e inadimplentes na carteira capital | 20 dias, preferência de segunda a sexta |  |
| 7 | 30 dias para clientes inativos adimplentes (capital) | Clientes inativos e adimplentes na carteira capital | 30 dias, preferência de segunda a sexta |  |
| 8 | 14 dias para clientes sem venda (capital) | Clientes sem nenhuma venda registrada na carteira capital | 30 dias, preferência de segunda a sexta | Divergência: o nome do bloco cita 14 dias, mas a ação aplica 30 dias. |
| 9 | 30 dias para clientes inativos inadimplentes (capital) | Clientes inativos e inadimplentes na carteira capital | Não agendar | Divergência: o nome do bloco cita 30 dias, mas a ação define não agendar. |
| 10 | 21 dias para clientes ativos (interior) | Clientes ativos na carteira interior | 21 dias, preferência de segunda a sexta |  |
| 11 | 21 dias para clientes inativos adimplentes (interior) | Clientes inativos e adimplentes na carteira interior | 21 dias, preferência de segunda a sexta |  |
| 12 | 30 dias para clientes inativos inadimplentes (interior) | Clientes inativos e inadimplentes na carteira interior | 42 dias, preferência de segunda a sexta | Divergência: o nome do bloco cita 30 dias, mas a ação aplica 42 dias. |
| 13 | 38 dias para clientes sem venda (interior) | Clientes sem nenhuma venda registrada na carteira interior | 38 dias, preferência de segunda a sexta |  |
| 14 | Clientes inativos inadimplentes (interior) | Clientes inativos e inadimplentes na carteira interior | Não agendar | Atenção: este bloco repete exatamente o público do bloco 12 (inativos inadimplentes no interior). Como os clientes já passam pelo bloco 12 antes, este bloco só pegará quem porventura não foi atingido ou se houver sobreposição. |

**Pontos de atenção**

- Não há bloco final sem filtro para as fontes carteira(televendas), carteira(capital) e carteira(interior): clientes que não se enquadram em nenhum bloco mantêm a configuração que já tinham.
- O nome do bloco 8 cita 14 dias, mas a ação é de 30 dias.
- O nome do bloco 12 cita 30 dias, mas a ação é de 42 dias.
- O bloco 14 tem exatamente o mesmo filtro do bloco 12 (inativos inadimplentes no interior), o que torna o bloco 14 redundante já que os clientes já terão sido capturados no bloco 12.

## Regra 121

`referencias/regra_121.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia clientes baixados na Receita e filiais, define frequências específicas para reativados e compras únicas, calcula frequência dinâmica para ativos recorrentes e fixa prazos por recência para os demais. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar Filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 3 | Clientes que compraram apenas uma vez após período de inatividade | Clientes em ciclo de vida reativado com a empresa | 3 dias |  |
| 4 | Clientes com apenas uma compra | Clientes que realizaram uma única compra com a empresa | 3 dias |  |
| 5 | Ativos recorrentes (com compra em 30 dias) | Clientes com compra nos últimos 30 dias | Frequência do histórico, entre 3 e 21 dias |  |
| 6 | Ativos (com compra entre 30 e 60 dias) | Clientes com compra nos últimos 60 dias que não entraram nos blocos anteriores; na prática, último pedido entre 30 e 60 dias atrás | 14 dias |  |
| 7 | Ativos (com compra entre 60 e 90 dias) | Clientes com compra nos últimos 90 dias que não entraram nos blocos anteriores; na prática, último pedido entre 60 e 90 dias atrás | 21 dias |  |
| 8 | Ativos (com compra entre 90 e 120 dias) | Clientes com compra nos últimos 120 dias que não entraram nos blocos anteriores; na prática, último pedido entre 90 e 120 dias atrás | 14 dias |  |
| 9 | Clientes que hoje não se enquadraram nas regras padrão | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | 7 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- O bloco 8 (compras nos últimos 120 dias) oferece uma frequência de 14 dias, enquanto o bloco 7 (últimos 90 dias) oferece 21 dias. Como a avaliação é sequencial, clientes mais antigos (entre 90 e 120 dias) terão atendimento mais frequente (14 dias) do que os de 60 a 90 dias (21 dias). Confirmar se essa inversão de prazos é intencional.

## Regra 122

`referencias/regra_122.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa do time televendas. Inadimplentes não são agendados, enquanto clientes ativos e inativos adimplentes recebem frequências de 14 e 30 dias, respectivamente. Clientes sem vendas recebem frequência de 14 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Ativos adimplentes | Clientes ativos segundo o histórico de compras com o próprio vendedor e adimplentes (sem pendências financeiras) | 14 dias |  |
| 3 | Inativos adimplentes | Clientes inativos segundo o histórico de compras com o próprio vendedor e adimplentes (sem pendências financeiras) | 30 dias |  |
| 4 | Clientes sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 123

`referencias/regra_123.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dividida entre os times televendas (exceto ID 7027), time saúde televendas (ID 7027) e campo. Define frequências semanais ou quinzenal para clientes ativos e inativos, com regras específicas para o ramo de atividade 1 na saúde e parâmetros fixos para o time de campo. Os blocos são avaliados em ordem por fonte de cliente.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao do goVendas: Frequencia semanal para clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias | Aplicado ao time televendas. |
| 2 | Regra Padrao do goVendas: Frequencia quinzenal para clientes inativos | Todos os clientes do time televendas que sobraram dos blocos anteriores | 15 dias | Bloco sem filtro: funciona como regra final para o time televendas. |
| 3 | Regra Padrao do goVendas: Frequencia semanal para clientes ativos (saude) | Clientes ativos segundo o histórico de compras com o próprio vendedor e ramo de atividade igual a 1 | 7 dias | Aplicado ao time saúde televendas. |
| 4 | Regra Padrao do goVendas: Frequencia quinzenal para clientes inativos (saude) | Clientes com ramo de atividade igual a 1 que não se enquadraram no bloco anterior; na prática, inativos do ramo 1 | 15 dias | Aplicado ao time saúde televendas. |
| 5 | Regra Padrao do goVendas: Nao agendar ramo de atividade diferente de saude (saude) | Todos os clientes do time saúde televendas que sobraram dos blocos anteriores | Não agendar | Bloco sem filtro: atende clientes com ramo diferente de 1. |
| 6 | Regra Padrao do goVendas: Frequencia de 7 dias para clientes ativos (campo) | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias, fixo | Aplicado ao time campo com parametrização fixa. |
| 7 | Regra Padrao do goVendas: Frequencia de 14 dias para clientes inativos (campo) | Todos os clientes do time campo que sobraram dos blocos anteriores | 15 dias, fixo | Bloco sem filtro: funciona como regra final para o time campo. |

**Pontos de atenção**

- O nome do bloco 7 cita 14 dias, mas a ação parametrizada é de 15 dias. Confirmar qual vale.

## Regra 124

`referencias/regra_124.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times: o time campo (vendedores de campo) atende todos os clientes a cada 30 dias, e o time televendas atende clientes ativos, inativos (adimplentes e inadimplentes) e sem vendas a cada 25 dias, com preferência de atendimento de segunda a sexta e evitando choque de dias com o time campo. Os blocos são avaliados em ordem para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Roda Viva: 30 dias para todos os clientes (time externo) | Todos os clientes do time campo | 30 dias | Bloco sem filtro: aplica-se a todos os clientes do time campo. |
| 2 | Regra Padrao da Roda Viva: 25 dias para clientes ativos (televendas) | Clientes ativos para o próprio vendedor (time televendas) | 25 dias; preferência de dias de segunda a sexta; evitar choque de dias com o time campo |  |
| 3 | Regra Padrao da Roda Viva: 25 dias para clientes inativos adimplentes (televendas) | Clientes inativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 25 dias; preferência de dias de segunda a sexta; evitar choque de dias com o time campo |  |
| 4 | Regra Padrao da Roda Viva: 25 dias para clientes inativos inadimplentes (televendas) | Clientes inativos para o próprio vendedor e inadimplentes (com pendências financeiras em aberto) | 25 dias; preferência de dias de segunda a sexta; evitar choque de dias com o time campo |  |
| 5 | Regra Padrao da Roda Viva: 25 dias para clientes sem vendas (televendas) | Clientes sem nenhuma venda registrada (nunca comprou) | 25 dias; preferência de dias de segunda a sexta; evitar choque de dias com o time campo |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time televendas: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 125

`referencias/regra_125.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores da empresa, usando a carteira fixa de cada um. Os blocos definem a frequência de atendimento ou a remoção da agenda com base no status de atividade com o próprio vendedor, adimplência e histórico de vendas. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Cavalo Marinho: 7 dias para clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 2 | Regra Padrao da Cavalo Marinho: 15 dias para clientes inativos adimplentes | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 15 dias |  |
| 3 | Regra Padrao da Cavalo Marinho: nao agendar clientes inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Regra Padrao da Cavalo Marinho: 20 dias para clientes prospects | Clientes sem nenhuma venda registrada (nunca comprou) | 20 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 126

`referencias/regra_126.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dividida entre os times de ruptura global (vendedores específicos), televendas (demais ativados) e campo (vendedores de campo ativados). Cada time possui suas próprias regras de frequência baseadas em inatividade, histórico com o vendedor e adimplência. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Femac: 14 dias para clientes com mais de 31 dias sem compra com a empresa (ruptura global) | Clientes com mais de 31 dias sem compra com a empresa toda | 14 dias; preferência de dias: segunda a sexta (demais dias não atender) | Fonte: time ruptura global. |
| 2 | Regra Padrao da Femac: Não agendar cliente que compraram a menos de 31 dias (ruptura global) | Todos os clientes restantes da fonte que não se enquadraram no bloco anterior; na prática, com compra há menos de 31 dias | Não agendar | Bloco sem filtro: funciona como regra final para o time ruptura global. |
| 3 | Regra Padrao da Femac: 14 dias para ativos adimplentes (televendas) | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 14 dias; preferência de dias: segunda a sexta (demais dias não atender) | Fonte: carteira televendas. |
| 4 | Regra Padrao da Femac: 21 dias para ativos inadimplentes (televendas) | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 21 dias; preferência de dias: segunda a sexta (demais dias não atender) | Fonte: carteira televendas. |
| 5 | Regra Padrao da Femac: 30 dias para inativos adimplentes (televendas) | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 30 dias; preferência de dias: segunda a sexta (demais dias não atender) | Fonte: carteira televendas. |
| 6 | Regra Padrao da Femac: Nao agendar inativos inadimplentes (televendas) | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | Não agendar | Fonte: carteira televendas. |
| 7 | Regra Padrao da Femac: 30 dias para clientes sem venda (televendas) | Clientes sem nenhuma venda registrada (nunca comprou) | 30 dias; preferência de dias: segunda a sexta (demais dias não atender) | Fonte: carteira televendas. |
| 8 | Regra Padrao da Femac - Frequencia de 7 dias para clientes ativos (campo) | Clientes ativos para o vendedor | 7 dias; fixo | Fonte: carteira campo. |
| 9 | Regra Padrao da Femac - Frequencia de 15 dias para clientes inativos (campo) | Todos os clientes restantes da fonte que não se enquadraram no bloco anterior | 15 dias; fixo | Bloco sem filtro: funciona como regra final para o time de campo. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira televendas: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 128

`referencias/regra_128.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para vários times de televendas (tmk_1 a tmk_7), tratando clientes baixados na Receita Federal, clientes vindos de carteiras externas e clientes exclusivos do televendas. Os blocos são avaliados em ordem e aplicados de forma incremental para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal dos times de televendas | Não agendar |  |
| 2 | Prospects / Ext. Niteroi e Rio 2 para Tmk 1 | Clientes da segmentação ext_niteroi_rio2_para_tmk1 que são prospects (nunca compraram) | 7 dias |  |
| 3 | Ativos / Ext. Niteroi e Rio 2 para Tmk 1 | Clientes da segmentação ext_niteroi_rio2_para_tmk1 com pedido nos últimos 60 dias | 5 dias | A regra só é aplicada do dia 16 até o fim do mês. |
| 4 | Retenção / Ext. Niteroi e Rio 2 para Tmk 1 | Clientes da segmentação ext_niteroi_rio2_para_tmk1 com pedido nos últimos 90 dias | 7 dias |  |
| 5 | Recuperação / Ext. Niteroi e Rio 2 para Tmk 1 | Demais clientes da segmentação ext_niteroi_rio2_para_tmk1 | 7 dias |  |
| 6 | Prospects / Ext. Lagos e Norte para Tmk 2 | Clientes da segmentação ext_lagos_norte_para_tmk2 que são prospects (nunca compraram) | 7 dias |  |
| 7 | Ativos / Ext. Lagos e Norte para Tmk 2 | Clientes da segmentação ext_lagos_norte_para_tmk2 com pedido nos últimos 60 dias | 5 dias | A regra só é aplicada do dia 16 até o fim do mês. |
| 8 | Retenção / Ext. Lagos e Norte para Tmk 2 | Clientes da segmentação ext_lagos_norte_para_tmk2 com pedido nos últimos 90 dias | 7 dias |  |
| 9 | Recuperação / Ext. Lagos e Norte para Tmk 2 | Demais clientes da segmentação ext_lagos_norte_para_tmk2 | 7 dias |  |
| 10 | Prospects / Ext. Baixada 1 e Baixada 3 para Tmk 3 | Clientes da segmentação ext_baixada1_baixada3_para_tmk3 que são prospects (nunca compraram) | 7 dias |  |
| 11 | Ativos / Ext. Baixada 1 e Baixada 3 para Tmk 3 | Clientes da segmentação ext_baixada1_baixada3_para_tmk3 com pedido nos últimos 60 dias | 5 dias | A regra só é aplicada do dia 16 até o fim do mês. |
| 12 | Retenção / Ext. Baixada 1 e Baixada 3 para Tmk 3 | Clientes da segmentação ext_baixada1_baixada3_para_tmk3 com pedido nos últimos 90 dias | 7 dias |  |
| 13 | Recuperação / Ext. Baixada 1 e Baixada 3 para Tmk 3 | Demais clientes da segmentação ext_baixada1_baixada3_para_tmk3 | 7 dias |  |
| 14 | Prospects / Ext. Rio 1 e Rio 3 para Tmk 5 | Clientes da segmentação ext_rio1_rio3_para_tmk5 que são prospects (nunca compraram) | 7 dias |  |
| 15 | Ativos / Ext. Rio 1 e Rio 3 para Tmk 5 | Clientes da segmentação ext_rio1_rio3_para_tmk5 com pedido nos últimos 60 dias | 5 dias | A regra só é aplicada do dia 16 até o fim do mês. |
| 16 | Retenção / Ext. Rio 1 e Rio 3 para Tmk 5 | Clientes da segmentação ext_rio1_rio3_para_tmk5 com pedido nos últimos 90 dias | 7 dias |  |
| 17 | Recuperação / Ext. Rio 1 e Rio 3 para Tmk 5 | Demais clientes da segmentação ext_rio1_rio3_para_tmk5 | 7 dias |  |
| 18 | Prospects / Ext. Sul Flu 1 e Sul Flu 2 para Tmk 6 | Clientes da segmentação ext_sulflu1_sulflu2_para_tmk6 que são prospects (nunca compraram) | 7 dias |  |
| 19 | Ativos / Ext. Sul Flu 1 e Sul Flu 2 para Tmk 6 | Clientes da segmentação ext_sulflu1_sulflu2_para_tmk6 com pedido nos últimos 60 dias | 5 dias | A regra só é aplicada do dia 16 até o fim do mês. |
| 20 | Retenção / Ext. Sul Flu 1 e Sul Flu 2 para Tmk 6 | Clientes da segmentação ext_sulflu1_sulflu2_para_tmk6 com pedido nos últimos 90 dias | 7 dias |  |
| 21 | Recuperação / Ext. Sul Flu 1 e Sul Flu 2 para Tmk 6 | Demais clientes da segmentação ext_sulflu1_sulflu2_para_tmk6 | 7 dias |  |
| 22 | Prospects / Ext. Serrana e Baixada 2 para Tmk 7 | Clientes da segmentação ext_serrana_baixada2_para_tmk7 que são prospects (nunca compraram) | 7 dias |  |
| 23 | Ativos / Ext. Serrana e Baixada 2 para Tmk 7 | Clientes da segmentação ext_serrana_baixada2_para_tmk7 com pedido nos últimos 60 dias | 5 dias | A regra só é aplicada do dia 16 até o fim do mês. |
| 24 | Retenção / Ext. Serrana e Baixada 2 para Tmk 7 | Clientes da segmentação ext_serrana_baixada2_para_tmk7 com pedido nos últimos 90 dias | 7 dias |  |
| 25 | Recuperação / Ext. Serrana e Baixada 2 para Tmk 7 | Demais clientes da segmentação ext_serrana_baixada2_para_tmk7 | 7 dias |  |
| 26 | Prospects / Exclusivo do televendas | Clientes que são prospects (nunca compraram) nas fontes de televendas | 7 dias |  |
| 27 | Ativos / Exclusivo do televendas | Clientes com pedido nos últimos 60 dias nas fontes de televendas | 7 dias |  |
| 28 | Retenção / Exclusivo do televendas | Clientes com pedido nos últimos 90 dias nas fontes de televendas | 7 dias |  |
| 29 | Recuperação / Exclusivo do televendas | Clientes que não pertencem a nenhuma das segmentações externas listadas nas fontes de televendas | 7 dias |  |
| 30 | Clientes que hoje não se enquadraram nas regra solicitadas | Todos os clientes restantes das fontes de televendas | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(tmk_1): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(tmk_2): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(tmk_3): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(tmk_5): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(tmk_6): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(tmk_7): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- O nome do bloco 3 cita 20 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- O nome do bloco 7 cita 20 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- O nome do bloco 11 cita 20 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- O nome do bloco 15 cita 20 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- O nome do bloco 19 cita 20 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- O nome do bloco 23 cita 20 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.

## Regra 129

`referencias/regra_129.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Clientes inadimplentes ou que sejam filiais não são agendados; clientes ativos para o vendedor recebem frequência de 7 dias; e os demais (inativos) recebem 14 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Boa Praça: Não agendar clientes inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Boa Praça: Não agendar clientes filial | Clientes cuja empresa é do tipo filial | Não agendar |  |
| 3 | Boa Praça: Freq. de 7 dias para clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 4 | Boa Praça: Freq. de 14 dias para clientes inativos | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 130

`referencias/regra_130.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times: time interno (televendas) e time externo (vendedores de campo). Define regras de agendamento, não agendamento e frequências baseadas em status de atividade, adimplência e tipo de pessoa (CPF ou CNPJ). Os blocos são avaliados em ordem e por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes CPF (Televendas) | Clientes pessoa física (CPF) do time interno | Não agendar |  |
| 2 | Frequencia de 7 dias para ativos (Televendas) | Clientes ativos segundo o histórico de compras com o próprio vendedor (time interno) | 7 dias |  |
| 3 | Frequencia de 15 dias para inativos adimplentes (Televendas) | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) do time interno | 15 dias |  |
| 4 | Não agendar clientes inativos inadimplentes (Televendas) | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras) do time interno | Não agendar |  |
| 5 | Não agendar clientes sem compra e CPF (Televendas) | Clientes sem nenhuma venda registrada e pessoa física (CPF) do time interno | Não agendar |  |
| 6 | Frequencia de 20 dias para clientes sem compra e CNPJ (Televendas) | Clientes sem nenhuma venda registrada e pessoa jurídica (CNPJ) do time interno | 20 dias |  |
| 7 | Frequencia de 7 dias para clientes ativos (campo) | Clientes ativos segundo o histórico de compras com o próprio vendedor do time externo | 7 dias, fixo | Possui parametrização fixa (restrição rígida). |
| 8 | Frequencia de 15 dias para clientes inativos (campo) | Todos os clientes do time externo que sobraram dos blocos anteriores | 15 dias, fixo | Bloco sem filtro: funciona como regra final para o time externo. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time interno: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- O nome do bloco 8 cita 14 dias, mas a ação aplica 15 dias.

## Regra Labtech

`referencias/regra_131.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times de televendas e campo (vendedores ativados). Bloqueia inadimplentes e órgãos públicos, define frequência de 7 dias para sem crédito, e aplica regras específicas por CNAE e histórico de compras (modelos 1, 2 e 3) para cada time, com preferência para segunda, quarta e sexta no time de campo. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Labtech: Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) dos times televendas e campo | Não agendar |  |
| 2 | Labtech: Não agendar Administração pública e Segurança | Clientes dos times televendas e campo com CNAE 8411600 ou 8424800 | Não agendar |  |
| 3 | Labtech: Frequência de 7 dias para clientes sem crédito | Clientes sem crédito disponível dos times televendas e campo | 7 dias |  |
| 4 | Labtech: Frequência de 7 dias para clientes ativos - Modelo 1 - Televendas | Clientes ativos para o vendedor do time televendas com CNAE entre 9 opções (como 8630501, 8610101, entre outros) | 7 dias |  |
| 5 | Labtech: Frequência de 14 dias para clientes inativos - Modelo 1 - Televendas | Clientes do time televendas com CNAE entre 9 opções (como 8630501, 8610101, entre outros) que não passaram nos blocos anteriores | 14 dias |  |
| 6 | Labtech: Frequência de 21 dias para clientes ativos - Modelo 2 - Televendas | Clientes ativos para o vendedor do time televendas com CNAE igual a 8533300, 8532500, 4645101, 3250705 ou 4773300 | 21 dias |  |
| 7 | Labtech: Frequência de 30 dias para clientes inativos - Modelo 2 - Televendas | Clientes do time televendas com CNAE 8533300, 8532500, 4645101, 3250705 ou 4773300 que não passaram nos blocos anteriores | 30 dias |  |
| 8 | Labtech: Frequência de 30 dias - Modelo 3 - Televendas | Todos os clientes do time televendas que sobraram dos blocos anteriores | 30 dias | Bloco sem filtro: funciona como regra final para o televendas. |
| 9 | Labtech: Frequência de 7 dias para clientes ativos - Modelo 1 - Externos | Clientes ativos para o vendedor do time campo com CNAE entre 9 opções (como 8630501, 8610101, entre outros) | 7 dias (preferência: segunda, quarta e sexta) |  |
| 10 | Labtech: Frequência de 14 dias para clientes inativos - Modelo 1 - Externos | Clientes do time campo com CNAE entre 9 opções (como 8630501, 8610101, entre outros) que não passaram nos blocos anteriores | 14 dias (preferência: segunda, quarta e sexta) |  |
| 11 | Labtech: Frequência de 21 dias para clientes ativos - Modelo 2 - Externos | Clientes ativos para o vendedor do time campo com CNAE 8533300, 8532500, 4645101, 3250705 ou 4773300 | 21 dias (preferência: segunda, quarta e sexta) |  |
| 12 | Labtech: Frequência de 30 dias para clientes inativos - Modelo 2 - Externos | Clientes do time campo com CNAE 8533300, 8532500, 4645101, 3250705 ou 4773300 que não passaram nos blocos anteriores | 30 dias (preferência: segunda, quarta e sexta) |  |
| 13 | Labtech: Frequência de 30 dias - Modelo 3 - Externos | Todos os clientes do time campo que sobraram dos blocos anteriores | 30 dias (preferência: segunda, quarta e sexta) | Bloco sem filtro: funciona como regra final para o time campo. |

**Pontos de atenção**

- Há blocos finais sem filtro apenas para o final de cada grupo (bloco 8 para televendas e bloco 13 para campo). Clientes que caem nos bloqueios iniciais (blocos 1 a 3) param ali e não recebem frequência.

## Regra 132

`referencias/regra_132.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Inadimplentes não são agendados; os demais recebem frequência de ligação com base no ciclo de vida, histórico de compras e tempo desde o último pedido com o próprio vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Prospect - Cliente potencial | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 7 dias |  |
| 3 | Ativado - Fez um pedido e não comprou mais | Clientes que fizeram uma única compra com o próprio vendedor | 7 dias |  |
| 4 | Ativo - Compra regularmente | Clientes com frequência histórica de compra abaixo de 11 dias | 14 dias |  |
| 5 | Ativo - Estimular a regularidade de compra | Clientes com último pedido com o próprio vendedor entre 11 e 59 dias atrás | 10 dias |  |
| 6 | Em ruptura - Risco de ficar inativo | Clientes com último pedido com o próprio vendedor entre 60 e 89 dias atrás | 7 dias |  |
| 7 | Inativo - Reativar cliente sem compra | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido com o vendedor há 90 dias ou mais | 10 dias | Bloco sem filtro: funciona como regra final. |

## Regra 133

`referencias/regra_133.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de televendas e para a carteira de campo. No televendas, inadimplentes não são agendados, clientes ativos têm frequência de 7 dias e os demais recebem 14 dias. No campo, clientes ativos têm frequência fixa de 7 dias e os demais recebem frequência fixa de 15 dias. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se ao time televendas. |
| 2 | Clientes ativos (televendas) | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias | Aplica-se ao time televendas. |
| 3 | Clientes inativos (televendas) | Todos os clientes do time televendas que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final para o televendas. |
| 4 | Clientes ativos (campo) | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias (fixo) | Aplica-se à carteira campo. Possui parametrização fixa (restrição rígida). |
| 5 | Clientes inativos (campo) | Todos os clientes da carteira campo que sobraram do bloco anterior | 15 dias (fixo) | Bloco sem filtro: funciona como regra final para a carteira campo. Possui parametrização fixa (restrição rígida). |

## Regra 134

`referencias/regra_134.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para toda a empresa (todos os vendedores ativados). Aplica uma frequência fixa de atendimento para todos os clientes, sem distinção.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra padrão da Linavet | Todos os clientes da empresa | 15 dias | Bloco sem filtro: funciona como regra final para toda a base. |

## Regra 135

`referencias/regra_135.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização complexa dividida entre o time televendas_1 (excluindo o ID 0000002) e o time televendas_2 (focado no ID 0000002 com carteiras específicas por dia da semana e irrestritas). Define frequências de atendimento e preferências de dias para cada grupo. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Prospects Segunda | Clientes prospects (nunca compraram) com o próprio vendedor na carteira de segunda-feira | 7 dias (semanal); preferência na sexta (demais dias com valor 0) |  |
| 2 | Alta Frequencia Segunda | Clientes com compra nos últimos 30 dias com o próprio vendedor na carteira de segunda-feira | 7 dias (semanal); preferência na sexta (demais dias com valor 0) |  |
| 3 | Regularidade Segunda | Clientes com compra nos últimos 45 dias com o próprio vendedor na carteira de segunda-feira | 7 dias (semanal); preferência na sexta (demais dias com valor 0) |  |
| 4 | Risco Inatividade Segunda | Clientes sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira de segunda-feira | 7 dias (semanal); preferência na sexta (demais dias com valor 0) |  |
| 5 | Inativos Segunda | Clientes sem compra com vendedor do mesmo grupo nos últimos 180 dias, na carteira de segunda-feira | 7 dias (semanal); preferência na sexta (demais dias com valor 0) |  |
| 6 | Sem Regra Segunda | Todos os clientes restantes da carteira de segunda-feira que não se enquadraram nos blocos anteriores | 7 dias (semanal); preferência na sexta (demais dias com valor 0) | Bloco sem filtro: funciona como regra final para a carteira. |
| 7 | Prospects Terca | Clientes prospects (nunca compraram) com o próprio vendedor na carteira de terça-feira | 7 dias (semanal); preferência na segunda (demais dias com valor 0) |  |
| 8 | Alta Frequencia Terca | Clientes com compra nos últimos 30 dias com o próprio vendedor na carteira de terça-feira | 7 dias (semanal); preferência na segunda (demais dias com valor 0) |  |
| 9 | Regularidade Terca | Clientes com compra nos últimos 45 dias com o próprio vendedor na carteira de terça-feira | 7 dias (semanal); preferência na segunda (demais dias com valor 0) |  |
| 10 | Risco Inatividade Terca | Clientes sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira de terça-feira | 7 dias (semanal); preferência na segunda (demais dias com valor 0) |  |
| 11 | Inativos Terca | Clientes sem compra com vendedor do mesmo grupo nos últimos 180 dias, na carteira de terça-feira | 7 dias (semanal); preferência na segunda (demais dias com valor 0) |  |
| 12 | Sem Regra Terca | Todos os clientes restantes da carteira de terça-feira que não se enquadraram nos blocos anteriores | 7 dias (semanal); preferência na segunda (demais dias com valor 0) | Bloco sem filtro: funciona como regra final para a carteira. |
| 13 | Prospects Quarta | Clientes prospects (nunca compraram) com o próprio vendedor na carteira de quarta-feira | 7 dias (semanal); preferência na terça (demais dias com valor 0) |  |
| 14 | Alta Frequencia Quarta | Clientes com compra nos últimos 30 dias com o próprio vendedor na carteira de quarta-feira | 7 dias (semanal); preferência na terça (demais dias com valor 0) |  |
| 15 | Regularidade Quarta | Clientes com compra nos últimos 45 dias com o próprio vendedor na carteira de quarta-feira | 7 dias (semanal); preferência na terça (demais dias com valor 0) |  |
| 16 | Risco Inatividade Quarta | Clientes sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira de quarta-feira | 7 dias (semanal); preferência na terça (demais dias com valor 0) |  |
| 17 | Inativos Quarta | Clientes sem compra com vendedor do mesmo grupo nos últimos 180 dias, na carteira de quarta-feira | 7 dias (semanal); preferência na terça (demais dias com valor 0) |  |
| 18 | Sem Regra Quarta | Todos os clientes restantes da carteira de quarta-feira que não se enquadraram nos blocos anteriores | 7 dias (semanal); preferência na terça (demais dias com valor 0) | Bloco sem filtro: funciona como regra final para a carteira. |
| 19 | Prospects Quinta | Clientes prospects (nunca compraram) com o próprio vendedor na carteira de quinta-feira | 7 dias (semanal); preferência na quarta (demais dias com valor 0) |  |
| 20 | Alta Frequencia Quinta | Clientes com compra nos últimos 30 dias com o próprio vendedor na carteira de quinta-feira | 7 dias (semanal); preferência na quarta (demais dias com valor 0) |  |
| 21 | Regularidade Quinta | Clientes com compra nos últimos 45 dias com o próprio vendedor na carteira de quinta-feira | 7 dias (semanal); preferência na quarta (demais dias com valor 0) |  |
| 22 | Risco Inatividade Quinta | Clientes sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira de quinta-feira | 7 dias (semanal); preferência na quarta (demais dias com valor 0) |  |
| 23 | Inativos Quinta | Clientes sem compra com vendedor do mesmo grupo nos últimos 180 dias, na carteira de quinta-feira | 7 dias (semanal); preferência na quarta (demais dias com valor 0) |  |
| 24 | Sem Regra Quinta | Todos os clientes restantes da carteira de quinta-feira que não se enquadraram nos blocos anteriores | 7 dias (semanal); preferência na quarta (demais dias com valor 0) | Bloco sem filtro: funciona como regra final para a carteira. |
| 25 | Prospects Sexta | Clientes prospects (nunca compraram) com o próprio vendedor na carteira de sexta-feira | 7 dias (semanal); preferência na quinta (demais dias com valor 0) |  |
| 26 | Alta Frequencia Sexta | Clientes com compra nos últimos 30 dias com o próprio vendedor na carteira de sexta-feira | 7 dias (semanal); preferência na quinta (demais dias com valor 0) |  |
| 27 | Regularidade Sexta | Clientes com compra nos últimos 45 dias com o próprio vendedor na carteira de sexta-feira | 7 dias (semanal); preferência na quinta (demais dias com valor 0) |  |
| 28 | Risco Inatividade Sexta | Clientes sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira de sexta-feira | 7 dias (semanal); preferência na quinta (demais dias com valor 0) |  |
| 29 | Inativos Sexta | Clientes sem compra com vendedor do mesmo grupo nos últimos 180 dias, na carteira de sexta-feira | 7 dias (semanal); preferência na quinta (demais dias com valor 0) |  |
| 30 | Sem Regra Sexta | Todos os clientes restantes da carteira de sexta-feira que não se enquadraram nos blocos anteriores | 7 dias (semanal); preferência na quinta (demais dias com valor 0) | Bloco sem filtro: funciona como regra final para a carteira. |
| 31 | Irrestrito: Clientes prospects | Clientes prospects (nunca compraram) com o próprio vendedor na carteira irrestrita | 7 dias (semanal) |  |
| 32 | Irrestrito: Clientes com Alta Freq. de compra | Clientes com compra nos últimos 7 dias com vendedor do mesmo grupo na carteira irrestrita | 7 dias |  |
| 33 | Irrestrito: Clientes que compram com regularidade | Clientes com compra nos últimos 45 dias com vendedor do mesmo grupo na carteira irrestrita | 14 dias |  |
| 34 | Irrestrito: Risco de ficar inativo curva A | Clientes da curva A sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira irrestrita | 14 dias |  |
| 35 | Irrestrito: Risco de ficar inativo curva B | Clientes da curva B sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira irrestrita | 30 dias |  |
| 36 | Irrestrito: Risco de ficar inativo curva C | Clientes da curva C sem compra com qualquer vendedor da empresa nos últimos 120 dias, na carteira irrestrita | 30 dias |  |
| 37 | Irrestrito: Clientes inativos | Clientes sem compra com vendedor do mesmo grupo nos últimos 180 dias, na carteira irrestrita | 21 dias |  |
| 38 | cidade SÃO JOSE DO RIO PRETO - 30 dias | Clientes na cidade de SAO JOSE DO RIO PRETO, do time televendas_2 | 30 dias |  |
| 39 | Irrestrito: sem regra mapeada | Todos os clientes restantes do time televendas_2 que não se enquadraram nos blocos anteriores | 30 dias | Bloco sem filtro: funciona como regra final. |
| 40 | Freq. de 14d para Prospects | Clientes prospects com a empresa, do time televendas_1 | 14 dias |  |
| 41 | Ativos - recência 1 a 7 dias | Clientes com compra nos últimos 7 dias com vendedor do mesmo grupo, do time televendas_1 | 21 dias |  |
| 42 | Ativos - recência 8 a 30 dias | Clientes com compra nos últimos 30 dias com vendedor do mesmo grupo, do time televendas_1 | 30 dias |  |
| 43 | Ativos - recência 31 a 60 dias | Clientes com compra nos últimos 60 dias com vendedor do mesmo grupo, do time televendas_1 | 45 dias |  |
| 44 | Ativos - recência 61 a 90 dias | Clientes com compra nos últimos 90 dias com vendedor do mesmo grupo, do time televendas_1 | 70 dias |  |
| 45 | Ativos - recência 91 a 180 dias | Clientes com compra nos últimos 180 dias com vendedor do mesmo grupo, do time televendas_1 | 15 dias |  |
| 46 | Inativos - sem compra acima de 180 dias | Todos os clientes restantes do time televendas_1 que não se enquadraram nos blocos anteriores | 21 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira(irrestrito_televendas_2): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- As carteiras segunda_feira_televendas_2, terca_feira_televendas_2, quarta_feira_televendas_2, quinta_feira_televendas_2, sexta_feira_televendas_2 e irrestrito_televendas_2 são usadas nos blocos mas não são definidas neste arquivo, podendo estar em outro arquivo de regras do cliente.

## Regra 136

`referencias/regra_136.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização que abrange toda a empresa para bloquear ramos específicos e define regras distintas para as carteiras da capital e do interior. Clientes ativos da capital são atendidos a cada 7 dias e os inativos não são agendados. No interior, ativos têm frequência de 14 dias e inativos também não são agendados. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar ramo 19 | Clientes do ramo de atividade 19 (Funcionários) | Não agendar | Aplica-se a toda a empresa. |
| 2 | 7 dias para ativos (Capital) | Clientes ativos para o próprio vendedor na carteira capital | 7 dias |  |
| 3 | Não agendar inativos (Capital) | Todos os clientes restantes da carteira capital que não se enquadraram no bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final para a carteira capital. |
| 4 | 14 dias para ativos (Interior) | Clientes ativos para o próprio vendedor na carteira interior | 14 dias |  |
| 5 | Não agendar inativos (Interior) | Todos os clientes restantes da carteira interior que não se enquadraram no bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final para a carteira interior. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(empresa toda) além do bloco 1: clientes que não são do ramo 19 mantêm a parametrização que já tinham antes de passarem pelas regras específicas de carteira.

## Regra 137

`referencias/regra_137.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Define a frequência de atendimento para prospects (14 dias), para clientes ativos com o próprio vendedor (21 dias) e para os demais clientes restantes (14 dias). Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Fênix distribuidora: 14d para prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 2 | Fênix distribuidora: 21d para ativos/adimplentes | Clientes ativos segundo o histórico de compras com o próprio vendedor | 21 dias |  |
| 3 | Fênix distribuidora: 14d para inativos/adimplentes | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 138

`referencias/regra_138.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Clientes inadimplentes são retirados da agenda, enquanto todos os demais clientes adimplentes recebem uma frequência fixa de atendimento a cada 7 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Demais clientes adimplentes | Todos os clientes do time que não são inadimplentes (ativos, inativos e prospects) | 7 dias | Bloco sem filtro: funciona como regra final para os clientes que sobraram do bloco anterior. |

## Regra 139

`referencias/regra_139.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times: hunter_ativacao de novos (televendas ativados exceto IDs 10185 e 1824) e farm_venda na base (vendedores IDs 10185 e 1824). Os blocos aplicam restrições de não agendamento para inadimplentes e bloqueados em ambos os times, além de regras específicas de prospects para a base e frequências baseadas no histórico ou recência para cada grupo. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Prospects | Clientes em ciclo de vida prospect com a empresa | Não agendar | Aplica-se apenas ao time farm_venda na base. |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se aos times hunter_ativacao de novos e farm_venda na base. |
| 3 | Não agendar bloqueados | Clientes bloqueados para atendimento | Não agendar | Aplica-se aos times hunter_ativacao de novos e farm_venda na base. |
| 4 | Freq. do histórico para Padrão de compra em até 30d | Clientes com frequência histórica de compra abaixo de 31 dias | Frequência do histórico, com limite máximo de 30 dias | Aplica-se ao time hunter_ativacao de novos. |
| 5 | Freq. de 21d para Padrão de compra entre 30d e 90d | Clientes com frequência histórica de compra entre 31 e 90 dias | 21 dias | Aplica-se ao time hunter_ativacao de novos. |
| 6 | Freq. de 30d para Padrão de compra maior que 90d | Todos os clientes restantes do time que não se enquadraram nos blocos anteriores | 30 dias | Bloco sem filtro para o time hunter_ativacao de novos; funciona como regra final para esse time. |
| 7 | Freq. de 30d para Stimular regularidade de compra | Clientes com última compra com o próprio vendedor entre 45 e 90 dias atrás | 30 dias | Aplica-se ao time farm_venda na base. |
| 8 | Freq. de 25d para Risco de inatividade | Clientes com última compra com o próprio vendedor entre 91 e 180 dias atrás | 25 dias | Aplica-se ao time farm_venda na base. |
| 9 | Freq. de 21d para Resgate de cliente sem compra - Inativos | Clientes considerados inativos para o próprio vendedor segundo o histórico de compras | 21 dias | Aplica-se ao time farm_venda na base. |
| 10 | Freq. do histórico para Alta frequência de compra | Clientes com frequência histórica de compra abaixo de 45 dias | Frequência do histórico, com limite mínimo de 40 e máximo de 45 dias | Aplica-se ao time farm_venda na base. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(farm_venda na base): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- A ordem dos blocos do time farm_venda na base coloca regras de recência e inatividade antes da regra de alta frequência histórica (bloco 10), o que pode fazer com que clientes com alta frequência sejam capturados antes pelas regras intermediárias se também atenderem aos critérios de recência.

## Regra 140

`referencias/regra_140.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas e suas carteiras divididas por rotas. Bloqueia CPFs, filiais e inadimplentes, além de clientes com visita recente. As demais carteiras definem frequência semanal para diferentes faixas de recência de compra, com dias específicos para rotas fixas. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar CPF | Clientes pessoa física (CPF) | Não agendar |  |
| 2 | Não agendar Filiais | Clientes cuja empresa é filial | Não agendar |  |
| 3 | Não agendar Inadimplentes | Clientes inadimplentes com pendências financeiras em aberto | Não agendar |  |
| 4 | Não agendar com visita recente | Clientes das rotas 3, 4, 5, 6, 7 e dias variáveis com última visita de vendedor do mesmo grupo nos últimos 3 dias | Não agendar |  |
| 5 | Rotas 008, 009, 010 e 011 - Primeira compra | Clientes das rotas 8, 9, 10 e 11 sem venda registrada com o próprio vendedor (nunca comprou) | 7 dias (semanal) |  |
| 6 | Rotas 008, 009, 010 e 011 - Compra regularmente | Clientes das rotas 8, 9, 10 e 11 com compra nos últimos 21 dias com o próprio vendedor | 7 dias (semanal) |  |
| 7 | Rotas 008, 009, 010 e 011 - Estimular a regularidade de compra | Clientes das rotas 8, 9, 10 e 11 com compra entre 21 e 41 dias atrás | 7 dias (semanal) |  |
| 8 | Rotas 008, 009, 010 e 011 - Risco de inatividade | Clientes das rotas 8, 9, 10 e 11 com compra entre 41 e 90 dias atrás | 7 dias (semanal) |  |
| 9 | Rotas 008, 009, 010 e 011 - Cliente sem compra há mais de 90d | Clientes das rotas 8, 9, 10 e 11 sem compra nos últimos 90 dias | 7 dias (semanal) |  |
| 10 | Rotas 003 e 004 - Primeira compra | Clientes das rotas 3 e 4 sem venda registrada com o próprio vendedor | 7 dias (semanal), preferência na segunda (fixo) | Restrição rígida de frequência e preferência. |
| 11 | Rotas 003 e 004 - Compra regularmente | Clientes das rotas 3 e 4 com compra nos últimos 21 dias com o próprio vendedor | 7 dias (semanal), preferência na segunda (fixo) | Restrição rígida de frequência e preferência. |
| 12 | Rotas 003 e 004 - Estimular a regularidade de compra | Clientes das rotas 3 e 4 com compra entre 21 e 41 dias atrás | 7 dias (semanal), preferência na segunda (fixo) | Restrição rígida de frequência e preferência. |
| 13 | Rotas 003 e 004 - Risco de inatividade | Clientes das rotas 3 e 4 com compra entre 41 e 90 dias atrás | 7 dias (semanal), preferência na segunda (fixo) | Restrição rígida de frequência e preferência. |
| 14 | Rotas 003 e 004 - Cliente sem compra há mais de 90d | Clientes das rotas 3 e 4 sem compra nos últimos 90 dias | 7 dias (semanal), preferência na segunda (fixo) | Restrição rígida de frequência e preferência. |
| 15 | Rota 005 - Primeira compra | Clientes da rota 5 sem venda registrada com o próprio vendedor | 7 dias (semanal), preferência na terça (fixo) | Restrição rígida de frequência e preferência. |
| 16 | Rota 005 - Compra regularmente | Clientes da rota 5 com compra nos últimos 21 dias com o próprio vendedor | 7 dias (semanal), preferência na terça (fixo) | Restrição rígida de frequência e preferência. |
| 17 | Rota 005 - Estimular a regularidade de compra | Clientes da rota 5 com compra entre 21 e 41 dias atrás | 7 dias (semanal), preferência na terça (fixo) | Restrição rígida de frequência e preferência. |
| 18 | Rota 005 - Risco de inatividade | Clientes da rota 5 com compra entre 41 e 90 dias atrás | 7 dias (semanal), preferência na terça (fixo) | Restrição rígida de frequência e preferência. |
| 19 | Rota 005 - Cliente sem compra há mais de 90d | Clientes da rota 5 sem compra nos últimos 90 dias | 7 dias (semanal), preferência na terça (fixo) | Restrição rígida de frequência e preferência. |
| 20 | Rota 006 - Primeira compra | Clientes da rota 6 sem venda registrada com o próprio vendedor | 7 dias (semanal), preferência na quarta (fixo) | Restrição rígida de frequência e preferência. |
| 21 | Rota 006 - Compra regularmente | Clientes da rota 6 com compra nos últimos 21 dias com o próprio vendedor | 7 dias (semanal), preferência na quarta (fixo) | Restrição rígida de frequência e preferência. |
| 22 | Rota 006 - Estimular a regularidade de compra | Clientes da rota 6 com compra entre 21 e 41 dias atrás | 7 dias (semanal), preferência na quarta (fixo) | Restrição rígida de frequência e preferência. |
| 23 | Rota 006 - Risco de inatividade | Clientes da rota 6 com compra entre 41 e 90 dias atrás | 7 dias (semanal), preferência na quarta (fixo) | Restrição rígida de frequência e preferência. |
| 24 | Rota 006 - Cliente sem compra há mais de 90d | Clientes da rota 6 sem compra nos últimos 90 dias | 7 dias (semanal), preferência na quarta (fixo) | Restrição rígida de frequência e preferência. |
| 25 | Rota 007 - Primeira compra | Clientes da rota 7 sem venda registrada com o próprio vendedor | 7 dias (semanal), preferência na sexta (fixo) | Restrição rígida de frequência e preferência. |
| 26 | Rota 007 - Compra regularmente | Clientes da rota 7 com compra nos últimos 21 dias com o próprio vendedor | 7 dias (semanal), preferência na sexta (fixo) | Restrição rígida de frequência e preferência. |
| 27 | Rota 007 - Estimular a regularidade de compra | Clientes da rota 7 com compra entre 21 e 41 dias atrás | 7 dias (semanal), preferência na sexta (fixo) | Restrição rígida de frequência e preferência. |
| 28 | Rota 007 - Risco de inatividade | Clientes da rota 7 com compra entre 41 e 90 dias atrás | 7 dias (semanal), preferência na sexta (fixo) | Restrição rígida de frequência e preferência. |
| 29 | Rota 007 - Cliente sem compra há mais de 90d | Clientes da rota 7 sem compra nos últimos 90 dias | 7 dias (semanal), preferência na sexta (fixo) | Restrição rígida de frequência e preferência. |
| 30 | Clientes sem rotas associadas | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | 7 dias (semanal) | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para as carteiras de rotas específicas: clientes que não se enquadram em nenhum bloco dessas carteiras mantêm a parametrização anterior.

## Regra 141

`referencias/regra_141.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Define frequências de atendimento com base na curva ABC de faturamento e no status de ativo ou inativo para o próprio vendedor. Os blocos são avaliados em ordem e o último bloco serve como regra final para os clientes restantes.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes ativos curva A | Clientes da curva A com a empresa e ativos para o próprio vendedor | 15 dias |  |
| 2 | Clientes inativos curva A | Clientes da curva A com a empresa que não entraram no bloco anterior; na prática, inativos para o próprio vendedor | 7 dias |  |
| 3 | Clientes ativos curva B | Clientes da curva B com a empresa e ativos para o próprio vendedor | 21 dias |  |
| 4 | Clientes inativos curva B | Clientes da curva B com a empresa que não entraram no bloco anterior; na prática, inativos para o próprio vendedor | 14 dias |  |
| 5 | Clientes ativos curva C | Clientes da curva C com a empresa e ativos para o próprio vendedor | 30 dias |  |
| 6 | Clientes inativos curva C | Clientes da curva C com a empresa que não entraram no bloco anterior; na prática, inativos para o próprio vendedor | 21 dias |  |
| 7 | Prospects e demais | Todos os clientes restantes que não se enquadraram em nenhum bloco anterior | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 142

`referencias/regra_142.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dividida entre times específicos (Yara, Lúcia e Wanderson) baseada na curva de faturamento dos clientes, e uma regra geral para o time "todos" (todos os ativados exceto IDs 10, 5 e 3) baseada em inadimplência, ramos de atividade e histórico de compras. Os blocos são avaliados em ordem e cada cliente é processado na primeira regra em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Dispomed: Frequência de 3 dias para clientes curva A (Yara) | Clientes da curva A de faturamento com a empresa | 3 dias | Aplica-se apenas ao time da Yara. |
| 2 | Dispomed: Frequência de 7 dias para clientes curva B (Yara) | Clientes da curva B de faturamento com a empresa | 7 dias | Aplica-se apenas ao time da Yara. |
| 3 | Dispomed: Frequência de 14 dias para clientes curva C (Yara) | Clientes da curva C de faturamento com a empresa | 14 dias | Aplica-se apenas ao time da Yara. |
| 4 | Dispomed: Frequência de 14 dias para clientes sem classificação de curva (Yara) | Todos os clientes do time da Yara que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro de cliente: funciona como regra final para a Yara. |
| 5 | Dispomed: Frequência de 2 dias para clientes curva A (Lúcia) | Clientes da curva A de faturamento com a empresa | 2 dias | Aplica-se apenas ao time da Lúcia. |
| 6 | Dispomed: Frequência de 7 dias para clientes curva B (Lúcia) | Clientes da curva B de faturamento com a empresa | 7 dias | Aplica-se apenas ao time da Lúcia. |
| 7 | Dispomed: Frequência de 14 dias para clientes curva C (Lúcia) | Clientes da curva C de faturamento com a empresa | 14 dias | Aplica-se apenas ao time da Lúcia. |
| 8 | Dispomed: Frequência de 7 dias para clientes sem classificação de curva (Lúcia) | Todos os clientes do time da Lúcia que sobraram dos blocos anteriores | 7 dias | Bloco sem filtro de cliente: funciona como regra final para a Lúcia. |
| 9 | Dispomed: Frequência de 4 dias para clientes curva A (Wanderson) | Clientes da curva A de faturamento com a empresa | 4 dias | Aplica-se apenas ao time do Wanderson. |
| 10 | Dispomed: Frequência de 7 dias para clientes curva B (Wanderson) | Clientes da curva B de faturamento com a empresa | 7 dias | Aplica-se apenas ao time do Wanderson. |
| 11 | Dispomed: Frequência de 9 dias para clientes curva C (Wanderson) | Clientes da curva C de faturamento com a empresa | 9 dias | Aplica-se apenas ao time do Wanderson. |
| 12 | Dispomed: Frequência de 14 dias para clientes sem classificação de curva (Wanderson) | Todos os clientes do time do Wanderson que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro de cliente: funciona como regra final para o Wanderson. |
| 13 | Regra Padrão da Dispomed: Não liguar para inadimplente | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se ao time "todos". |
| 14 | Regra Padrão da Dispomed: Frequência de 14 dias para Hospitais e Clínicas | Clientes com ramo de atividade 001 (Hospital/Home Care/OS) ou 002 (Clínicas) | 14 dias | Aplica-se ao time "todos". |
| 15 | Regra Padrão da Dispomed: Frequência de 7 dias para Distribuidora | Clientes com ramo de atividade 003 (Distribuidora) | 7 dias | Aplica-se ao time "todos". |
| 16 | Regra Padrão da Dispomed: Frequência de 21 dias para Farmácias | Clientes com ramo de atividade 004 (Farmácia/Drogaria) | 21 dias | Aplica-se ao time "todos". |
| 17 | Regra Padrão da Dispomed: Não liguar para Fornecedor de uso e consumo, Orgão público e Representantes | Clientes com ramo de atividade 005 (Orgão Público), 006 (REPRESENTANTES (MEI)) ou 100 (FORNECEDOR DE USO E CONSUMO) | Não agendar | Aplica-se ao time "todos". |
| 18 | Regra Padrão da Dispomed: Frequência semanal para clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias | Aplica-se ao time "todos". |
| 19 | Regra Padrao do goVendas: Frequência quinzenal para clientes inativos | Todos os clientes do time "todos" que sobraram dos blocos anteriores | 15 dias | Bloco sem filtro: funciona como regra final para o time "todos". |

## Regra 143

`referencias/regra_143.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Primeiro bloqueia filiais e clientes com compra recente nos últimos 30 dias; depois define frequências diferenciadas para prospects e ativos segmentados por curva de faturamento e tempo sem comprar. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar filiais | Clientes que são filiais | Não agendar |  |
| 2 | Não agendar clientes com compra em 30d | Clientes com pedido nos últimos 30 dias, com qualquer vendedor da empresa | Não agendar |  |
| 3 | Prospects | Clientes em ciclo de vida prospect com a empresa | 28 dias |  |
| 4 | Ativos sem compra há mais de 30d (Curva A) | Clientes ativos com a empresa, da curva A de faturamento, e cuja última compra com qualquer vendedor não ocorreu entre 30 e 45 dias atrás | 7 dias |  |
| 5 | Ativos sem compra há mais de 30d (Curva B) | Clientes ativos com a empresa, da curva B de faturamento, e cuja última compra com qualquer vendedor não ocorreu entre 30 e 45 dias atrás | 14 dias |  |
| 6 | Ativos sem compra há mais de 30d (Curva C) | Clientes ativos com a empresa e cuja última compra com qualquer vendedor não ocorreu entre 30 e 45 dias atrás | 21 dias | Este bloco capta os ativos restantes que não são curva A ou B. |
| 7 | Ativos sem compra há mais de 45d | Clientes ativos com a empresa cuja última compra não ocorreu entre 45 e 60 dias atrás | 14 dias |  |
| 8 | Ativos sem compra há mais de 60d | Clientes ativos com a empresa | 7 dias |  |
| 9 | Inativos | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | 7 dias | Bloco sem filtro: funciona como regra final. |

## Regra 144

`referencias/regra_144.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para vários times de vendedores (todos os ativados, fabricantes, segmentos de revendas/manutenção, consumidor final recorrente, compra esporádica e consumidor final - grande porte). Define frequências de atendimento com base no ciclo de vida, inadimplência, histórico de compras e tempo de cadastro. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 14d para 'PROSPECT: FAZER O PRIMEIRO PEDIDO' (Todos) | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias | Aplica-se ao time de todos os vendedores. |
| 2 | Freq. de 21d para 'INADIMPLENTES' (Todos) | Clientes inadimplentes (com pendências financeiras em aberto) | 21 dias | Aplica-se ao time de todos os vendedores. |
| 3 | Freq. de 28d para 'BOAS VINDAS A CLIENTE COM O PRIMEIRO PEDIDO' (Todos) | Clientes com uma única compra com a empresa e cadastrados no ERP há pelo menos 30 dias | 28 dias | Aplica-se ao time de todos os vendedores. |
| 4 | Freq. de 30d para 'COM COMPRA ENTRE 31 E 60 DIAS' (Todos) | Clientes com última compra entre 31 e 60 dias atrás | 30 dias | Aplica-se ao time de todos os vendedores. Considera compras com vendedores do mesmo grupo. |
| 5 | Freq. de 10d para 'EM RUPTURA: RISCO DE INATIVIDADE' (Todos) | Clientes com última compra entre 61 e 90 dias atrás | 10 dias | Aplica-se ao time de todos os vendedores. Considera compras com vendedores do mesmo grupo. |
| 6 | Freq. de 21d 'INATIVOS: RESGATE DE CLIENTES SEM COMPRA' (Todos) | Clientes em ciclo de vida inativo com a empresa | 21 dias | Aplica-se ao time de todos os vendedores. |
| 7 | Freq. de 21d para 'ATIVO: COMPRA REGULARMENTE' (Fabricantes e Segmentos de Revendas/Manutenção) | Clientes com última compra nos últimos 30 dias | 21 dias | Aplica-se aos times fabricantes e segmentos de revendas/manutenção. Considera compras com vendedores do mesmo grupo. |
| 8 | Freq. de 28d para 'ATIVO: COMPRA REGULARMENTE' (Consumidor final recorrente, Compra exporádica e Consumidor final - Grande porte) | Clientes com última compra nos últimos 30 dias | 28 dias | Aplica-se aos times consumidor final recorrente, compra esporádica e consumidor final - grande porte. Considera compras com vendedores do mesmo grupo. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(todos): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(fabricantes, segmentos de revendas/manutencao): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(consumidor final recorrente, compra exporadica, consumidor final - grande porte): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 145

`referencias/regra_145.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Primeiro bloqueia filiais para não agendar; depois define frequências específicas para pessoas jurídicas com base no ciclo de vida (prospects), primeira compra por ramo de atividade, adimplência e recência de compras com o próprio vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Filiais | Clientes que são filiais | Não agendar |  |
| 2 | Ativação de Prospects | Pessoas jurídicas (CNPJ) em ciclo de vida prospect com o próprio vendedor | 10 dias |  |
| 3 | Primeira compra Indústria | Pessoas jurídicas (CNPJ) sem nenhuma venda registrada com o próprio vendedor e ramo de atividade 2 | 14 dias |  |
| 4 | Primeira compra Revenda | Pessoas jurídicas (CNPJ) sem nenhuma venda registrada com o próprio vendedor e ramo de atividade 1 | 7 dias |  |
| 5 | Estimular a regularidade de compra | Pessoas jurídicas (CNPJ) adimplentes, com última compra com o vendedor entre 31 e 60 dias atrás | 14 dias |  |
| 6 | Compra regularmente | Pessoas jurídicas (CNPJ) adimplentes, que compraram do próprio vendedor nos últimos 30 dias | 21 dias |  |
| 7 | Risco de inatividade | Pessoas jurídicas (CNPJ) adimplentes, com última compra com o vendedor entre 61 e 90 dias atrás | 7 dias |  |
| 8 | Resgate de clientes sem compra | Pessoas jurídicas (CNPJ) que não se enquadraram nos blocos anteriores | 21 dias | Bloco restrito a pessoas jurídicas. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time (empresa toda): clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 146

`referencias/regra_146.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de televendas (vendedores do tipo televendas ativados). Bloqueia inadimplentes, define frequências específicas para os ramos de Saúde e Food, e categoriza os demais clientes por histórico de vendas, recência de pedidos e risco de inatividade. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não Agendar Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Segmento: Saude | Clientes com ramo de atividade 37, 43 ou 15 | 7 dias |  |
| 3 | Segmento: FOOD | Clientes com ramo de atividade 41, 4 ou 25, e frequência histórica de compra de 7 dias | 7 dias |  |
| 4 | Cliente potencial | Clientes sem nenhuma venda registrada com o próprio vendedor (nunca comprou do vendedor) | 30 dias |  |
| 5 | Ativado: Fez um pedido e ainda não comprou mais | Clientes com uma única compra com o próprio vendedor e última compra global com o grupo nos últimos 30 dias | 30 dias |  |
| 6 | Ativo: compra regularmente | Clientes com frequência histórica de compra abaixo de 21 dias | 21 dias |  |
| 7 | Em ruptura: risco de ficar inativo | Clientes com última compra com o próprio vendedor entre 30 e 45 dias atrás | 21 dias |  |
| 8 | Inativo: reativar cliente sem compra | Clientes cuja última compra com o próprio vendedor não ocorreu nos últimos 46 dias (mais de 46 dias sem comprar) | 45 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra HospDrogas

`referencias/regra_147.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times time carteira (17 vendedores), time distribuidor (4 vendedores), time petvet (1 vendedor), time portal (20 vendedores) e pré-venda (3 vendedores). Define frequências de atendimento baseadas na data de cadastro, recência de visita, status de compra e curva ABC. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | HospDrogas: Frequência de 1 dia para clientes novos e sem atendimento | Clientes cadastrados a partir de 2023-07-18 e sem visita nos últimos 60 dias | 1 dia | Aplica-se aos times time carteira, time petvet e time portal. |
| 2 | HospDrogas: Frequência de 7 dias para clientes novos | Clientes cadastrados a partir de 2023-07-18 que não caíram no bloco anterior | 7 dias | Aplica-se aos times time carteira, time petvet e time portal. |
| 3 | HospDrogas: Frequência de 5 dias para clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 5 dias | Aplica-se aos times time carteira, time petvet e time portal. |
| 4 | HospDrogas: Frequência de 10 dias para clientes inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 10 dias | Aplica-se aos times time carteira, time petvet e time portal. |
| 5 | HospDrogas: Frequência de 20 dias para clientes sem venda | Clientes sem nenhuma venda registrada (nunca compraram) | 20 dias | Aplica-se aos times time carteira, time petvet e time portal. |
| 6 | HospDrogas: Frequência de 2 dias para clientes curva A | Clientes da curva A de faturamento com o próprio vendedor | 2 dias | Aplica-se ao time distribuidor. |
| 7 | HospDrogas: Frequência de 4 dias para clientes curva B | Clientes da curva B de faturamento com o próprio vendedor | 4 dias | Aplica-se ao time distribuidor. |
| 8 | HospDrogas: Frequência de 7 dias para clientes curva C | Clientes da curva C de faturamento com o próprio vendedor | 7 dias | Aplica-se ao time distribuidor. |
| 9 | HospDrogas: Frequência de 15 dias para clientes sem classificação de curva ABC | Todos os clientes do time distribuidor que sobraram dos blocos anteriores | 15 dias | Bloco sem filtro para o time distribuidor: funciona como regra final para este time. |
| 10 | HospDrogas: Freq. de 7d para todos os clientes | Todos os clientes do time pré-venda | 7 dias | Bloco sem filtro: aplica-se a todos os clientes do time pré-venda. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time (time carteira, time petvet, time portal): clientes desses times que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 148

`referencias/regra_148.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Inadimplentes não são agendados; ativos recebem frequência semanal, inativos recebem frequência quinzenal e clientes sem vendas também recebem frequência quinzenal. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Regra Padrao da Jumori: Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Regra Padrao da Jumori: Frequencia semanal para clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias (semanal) |  |
| 3 | Regra Padrao da Jumori: Frequencia quinzenal para clientes inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 15 dias (quinzenal) |  |
| 4 | Regra Padrao da Jumori: Frequencia de 14 dias para clientes sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) | 15 dias (quinzenal) |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- O nome do bloco 4 cita 14 dias, mas a ação aplica 15 dias (quinzenal). Confirmar qual vale.

## Regra Goiás Clean

`referencias/regra_149.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes com compra nos últimos 7 dias não são agendados. Os demais recebem atendimento a cada 14 dias de segunda a sábado. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ativos com compra em 7 dias | Clientes com pedido nos últimos 7 dias | Não agendar |  |
| 2 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias, preferência de segunda a sábado |  |
| 3 | Ativos com compra entre 7d e 30d | Clientes com pedido nos últimos 30 dias que não entraram no bloco anterior; na prática, último pedido entre 7 e 30 dias atrás | 14 dias, preferência de segunda a sábado |  |
| 4 | Ativos com compra entre 30d e 60d | Clientes com pedido nos últimos 60 dias que não entraram nos blocos anteriores; na prática, último pedido entre 30 e 60 dias atrás | 14 dias, preferência de segunda a sábado |  |
| 5 | Ativos com compra entre 60d e 90d | Clientes com pedido nos últimos 90 dias que não entraram nos blocos anteriores; na prática, último pedido entre 60 e 90 dias atrás | 14 dias, preferência de segunda a sábado |  |
| 6 | Clientes inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 90 dias | 14 dias, preferência de segunda a sábado | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Os blocos 2, 3, 4, 5 e 6 possuem exatamente a mesma ação (frequência de 14 dias e preferência de segunda a sábado), mudando apenas o critério de inclusão do cliente.

## Regra 150

`referencias/regra_150.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes com compra recente da empresa não são agendados, prospects e clientes caminhando para inatividade recebem frequências específicas, e os demais são tratados como inativos. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes com compra recente | Clientes com compra nos últimos 45 dias, com qualquer vendedor da empresa | Não agendar |  |
| 2 | Prospects | Clientes em ciclo de vida prospect com a empresa | 28 dias |  |
| 3 | Caminhando para inatividade | Clientes com compra entre 46 e 89 dias atrás, com qualquer vendedor da empresa | 14 dias |  |
| 4 | Inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem compra há 90 dias ou mais | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 151

`referencias/regra_151.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira de televendas fixa com ruptura de campo (clientes em ruptura do time de campo para o televendas com positivação entre 7 e 60 dias). Possui um único bloco aplicado apenas na última semana do mês para não agendar os clientes que pertencem à segmentação de cliente de ruptura.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Ativos de campo com vendas em 60 dias | Clientes que pertencem à segmentação cliente de ruptura | Não agendar | A regra só é aplicada na última semana do mês. |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram no bloco mantêm a parametrização que já tinham.
- O nome do bloco 1 cita 60 dias, mas esse número não aparece explicitamente nos filtros ou ações do bloco.

## Regra 152

`referencias/regra_152.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados) para a Br Distribuidora. Define frequências de atendimento com base no histórico de compras do cliente com o vendedor ou com o grupo. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Nunca fez pedido com o vendedor (prospect) | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 7 dias |  |
| 2 | Tirou o primeiro pedido com o vendedor | Clientes que fizeram uma única compra com o próprio vendedor | 7 dias |  |
| 3 | Teve pedido entre 0 e 7 dias | Clientes com pedido nos últimos 7 dias (com algum vendedor do mesmo grupo) | 14 dias |  |
| 4 | Teve pedido entre 7 e 30 dias | Clientes com último pedido entre 7 e 30 dias atrás (com algum vendedor do mesmo grupo) | 14 dias |  |
| 5 | Teve pedido entre 30 e 60 dias | Clientes com último pedido entre 30 e 60 dias atrás (com algum vendedor do mesmo grupo) | 14 dias |  |
| 6 | Teve pedido entre 60 e 90 dias | Clientes com último pedido entre 60 e 90 dias atrás (com algum vendedor do mesmo grupo) | 7 dias |  |
| 7 | Teve pedido há 90 dias ou mais | Todos os clientes do time que sobraram dos blocos anteriores; na prática, com último pedido há 90 dias ou mais | 7 dias | Bloco sem filtro: funciona como regra final. |

## Regra 153

`referencias/regra_153.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira fixa do time televendas (vendedores do tipo televendas). Primeiro bloqueia clientes DH sem crédito e clientes BK com menos de R$ 80 de crédito, além de inadimplentes. Depois define frequências de 7 dias para ativos do vendedor e 14 dias para inativos e sem venda. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes DH sem crédito | Clientes do tipo de cobrança DH sem crédito disponível | Não agendar |  |
| 2 | Não agendar clientes BK com menos de R$ 80 de crédito | Clientes do tipo de cobrança BK com crédito disponível abaixo de R$ 80 | Não agendar | O nome do bloco menciona crédito menor que R$ 200,00, mas o critério GOBR aplicado é de menos de R$ 80 de crédito disponível. |
| 3 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Frequência para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 5 | Frequência para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 14 dias |  |
| 6 | Frequência para sem venda | Clientes sem nenhuma venda registrada (nunca compraram) | 14 dias |  |

**Pontos de atenção**

- Divergência entre o nome do bloco 2 (crédito menor que R$ 200,00) e o filtro GOBR aplicado (menos de R$ 80 de crédito disponível). O critério segue o código.
- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra Binatti Itapema

`referencias/regra_154.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Os blocos definem rotas fixas ou dinâmicas por cidade com frequência semanal, seguidas por regras baseadas no ciclo de vida (prospects) e na curva de faturamento para clientes ativos. Os blocos são avaliados em ordem e um cliente não é reprocessado após se encaixar em uma regra.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Rota fixa de segunda-feira | Clientes nas cidades de Balneário Barra do Sul, Bela Vista, Campo Alegre, Canoinhas, Corupá, Itaiópolis, Mafra, Major Vieira, Monte Castelo, Papanduva, Porto União, Rio Negrinho, São Bento do Sul, Três Barras (14 cidades) | 7 dias, fixo na segunda | Restrição rígida de frequência e preferência. |
| 2 | Rota fixa de terça-feira | Clientes nas cidades de Apiúna, Ascurra, Benedito Novo, Blumenau, Doutor Pedrinho, Gaspar, Ibirama, Indaial, Pomerode, Presidente Getúlio, Rio dos Cedros, Timbó (12 cidades) | 7 dias, fixo na terça | Restrição rígida de frequência e preferência. |
| 3 | Rota fixa de quarta-feira | Clientes nas cidades de Araranguá, Biguaçu, Braço do Norte, Capivari de Baixo, Cocal do Sul, Criciúma e mais 23 (29 cidades no total) | 7 dias, fixo na quarta | Restrição rígida de frequência e preferência. |
| 4 | Rota fixa de quinta-feira | Clientes nas cidades de Araquari, Massaranduba, Pirabeiraba, São João do Itaperiú (4 cidades) | 7 dias, fixo na quinta | Restrição rígida de frequência e preferência. |
| 5 | Rota dinâmica de segunda, terça ou sexta | Clientes na cidade de Brusque | 7 dias, preferência na segunda, terça ou sexta |  |
| 6 | Rota dinâmica para terça ou sexta | Clientes na cidade de Nova Trento | 7 dias, preferência na terça ou sexta |  |
| 7 | Rota dinâmica de segunda ou quinta | Clientes nas cidades de Guaramirim, Jaraguá do Sul, Joinville, Schroeder (4 cidades) | 7 dias, preferência na segunda ou quinta |  |
| 8 | Rota dinâmica de terça ou quinta | Clientes nas cidades de Barra Velha, Navegantes, Penha, Balneário Piçarras (4 cidades) | 7 dias, preferência na terça ou quinta |  |
| 9 | Rota dinâmica para dias variados | Clientes nas cidades de Balneário Camboriú, Camboriú, Canelinha, Itajaí, Itapema, Porto Belo e mais 2 (8 cidades no total) | 7 dias |  |
| 10 | Prospects | Clientes em ciclo de vida prospect com a empresa | 30 dias |  |
| 11 | Ativos - Curva A | Clientes ativos para o vendedor e da curva A de faturamento com a empresa | 14 dias |  |
| 12 | Ativos - Curva B | Clientes ativos para o vendedor e da curva B de faturamento com a empresa | 21 dias |  |
| 13 | Ativos - Curva C | Clientes ativos para o vendedor | 28 dias |  |
| 14 | Inativos | Todos os clientes do time que sobraram dos blocos anteriores | 30 dias | Bloco sem filtro: funciona como regra final. |

## Regra 155

`referencias/regra_155.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia o agendamento de pessoas físicas, filiais, empresas baixadas, inadimplentes e quem comprou nos últimos 30 dias; depois, define a frequência de atendimento de prospects, novos clientes e clientes ativos por curva de faturamento e tempo sem comprar. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar PF | Clientes pessoa física (CPF) | Não agendar |  |
| 2 | Não agendar filiais | Clientes cadastrados como filial | Não agendar |  |
| 3 | Não agendar baixadas na receita federal | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 4 | Não agendar Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 5 | Não agendar clientes com compra em 30d | Clientes com compra nos últimos 30 dias | Não agendar |  |
| 6 | Ativação de um novo cliente em potencial | Prospects cadastrados no ERP há pelo menos 30 dias | 7 dias |  |
| 7 | Requalificar lead | Clientes prospects restantes que não completaram 30 dias de cadastro no ERP | 21 dias |  |
| 8 | Boas vindas a um novo cliente ativado | Clientes com uma única compra com o próprio vendedor | 7 dias |  |
| 9 | Cliente com bom histórico de compra (Curva A) | Clientes da curva A com a empresa e cuja última compra global não ocorreu entre 30 e 45 dias atrás | 14 dias |  |
| 10 | Cliente com bom histórico de compra (Curva B) | Clientes da curva B com a empresa e cuja última compra global não ocorreu entre 30 e 45 dias atrás | 28 dias |  |
| 11 | Cliente com bom histórico de compra (Curva C) | Clientes da curva C com a empresa e cuja última compra global não ocorreu entre 30 e 45 dias atrás | 45 dias |  |
| 12 | Estimular regularidade de compra | Clientes cuja última compra global não ocorreu entre 46 e 60 dias atrás | 28 dias |  |
| 13 | Atenção!!! Cliente com RISCO de ficar inativo | Clientes cuja última compra global não ocorreu entre 61 e 90 dias atrás | 21 dias |  |
| 14 | Atenção!!! Seu cliente corre RISCO de ativação por outro RCA | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 156

`referencias/regra_156.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Clientes inadimplentes não são agendados, prospects e inativos recebem frequência de 14 dias, e há frequências específicas de 10 dias para clientes com apenas uma compra e 7 dias para ativos. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | 14 dias para prospects | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 14 dias |  |
| 3 | 10 dias para clientes com apenas 1 compra | Clientes que realizaram uma única compra com o próprio vendedor | 10 dias |  |
| 4 | 7 dias para adimplentes/ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 5 | 14 dias para adimplentes/inativos | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 157

`referencias/regra_157.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para toda a empresa (todos os vendedores ativados). Define a frequência de atendimento com base no tempo sem compras e no histórico, com atendimento de segunda a sexta-feira. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Frequência de 14 dias para mais de 120 dias sem vendas | Clientes sem compra nos últimos 120 dias | 14 dias, preferência de atendimento de segunda a sexta |  |
| 2 | Frequência de 7 dias para mais de 30 dias sem vendas | Clientes sem compra nos últimos 30 dias que não entraram no bloco anterior; na prática, entre 30 e 120 dias sem comprar | 7 dias, preferência de atendimento de segunda a sexta |  |
| 3 | Frequência pelo histórico | Todos os clientes restantes que não se enquadraram nos blocos anteriores; na prática, clientes com compra nos últimos 30 dias | Frequência do histórico, entre 5 e 30 dias, preferência de atendimento de segunda a sexta | Bloco sem filtro: funciona como regra final. |

## Regra 158

`referencias/regra_158.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas). Bloqueia o agendamento de inadimplentes e baixados na Receita, e define frequências específicas para prospects, clientes com uma única compra, clientes ativos por frequência histórica ou recência, e inativos. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 3 | Prospect | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 30 dias |  |
| 4 | Ativado com única compra | Clientes com uma única compra com a empresa, pedido nos últimos 45 dias e cadastrados no ERP há pelo menos 120 dias | 21 dias |  |
| 5 | Ativo com alta frequência | Clientes com pedido nos últimos 45 dias e frequência histórica de compra abaixo de 30 dias | 14 dias |  |
| 6 | Ativo com compra regular | Clientes com pedido nos últimos 120 dias e frequência histórica abaixo de 120 dias | 30 dias |  |
| 7 | Estimular regularidade | Clientes com último pedido entre 45 e 70 dias atrás | 30 dias |  |
| 8 | Em ruptura | Clientes com último pedido entre 71 e 120 dias atrás | 21 dias |  |
| 9 | Inativo | Clientes sem pedido nos últimos 120 dias | 30 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 159

`referencias/regra_159.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times 'baby', 'pet' e 'todos os vendedores'. Para os times 'baby' e 'pet', os clientes são divididos por faturamento anual no ano com a empresa para definir a frequência (Curva A, B e C). Para o time 'todos os vendedores', separa clientes ativos e inativos. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Brasgroup: 45d para clientes Curva C (Segmento Baby) | Clientes com faturamento total no ano com a empresa abaixo de R$ 10000 ou valor desconhecido | 45 dias | Aplica-se ao time 'baby'. |
| 2 | Brasgroup: 15d para clientes Curva A (Segmento Baby) | Clientes com faturamento total no ano com a empresa acima de R$ 30000 | 15 dias | Aplica-se ao time 'baby'. |
| 3 | Brasgroup: 30d para clientes Curva B (Segmento Baby) | Restante dos clientes do time 'baby' que não se enquadraram nos blocos anteriores; na prática, faturamento entre R$ 10000 e R$ 30000 | 30 dias | Bloco sem filtro para a fonte 'baby': funciona como regra final do time. |
| 4 | Brasgroup: 45d para clientes Curva C (Segmento Pet) | Clientes com faturamento total no ano com a empresa abaixo de R$ 5000 ou valor desconhecido | 45 dias | Aplica-se ao time 'pet'. |
| 5 | Brasgroup: 15d para clientes Curva A (Segmento Pet) | Clientes com faturamento total no ano com a empresa acima de R$ 20000 | 15 dias | Aplica-se ao time 'pet'. |
| 6 | Brasgroup: 30d para clientes Curva B (Segmento Pet) | Restante dos clientes do time 'pet' que não se enquadraram nos blocos anteriores; na prática, faturamento entre R$ 5000 e R$ 20000 | 30 dias | Bloco sem filtro para a fonte 'pet': funciona como regra final do time. |
| 7 | Regra Padrao do goVendas: Frequencia semanal para clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias | Aplica-se ao time 'todos os vendedores'. |
| 8 | Regra Padrao do goVendas: Frequencia quinzenal para clientes inativos | Todos os clientes do time 'todos os vendedores' que sobraram dos blocos anteriores | 15 dias | Bloco sem filtro: funciona como regra final para a fonte 'todos os vendedores'. |

## Regra 160

`referencias/regra_160.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times de vendedores ativos e prospects (separados por IDs). Os primeiros blocos priorizam PJ com rota nos próximos 1 dia e visita entre 4 e 3000 dias atrás, aplicando frequência de 1 dia independente do histórico de compras. Depois, os blocos tratam primeira compra, risco de inatividade, regularidade, resgates e pessoa física. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Fechamento de Rota e Sem Atendimento há 3 dias - Primeira Compra | Pessoa jurídica (CNPJ) com rota nos próximos 1 dia, sem venda com o vendedor e última visita entre 4 e 3000 dias atrás | 1 dias |  |
| 2 | Fechamento de Rota e Sem Atendimento há 3 dias - Estimular Regularidade de Compra | Pessoa jurídica (CNPJ) com rota nos próximos 1 dia, última visita entre 4 e 3000 dias atrás e última compra do vendedor entre 31 e 60 dias atrás | 1 dias |  |
| 3 | Fechamento de Rota e Sem Atendimento há 3 dias - Risco de inatividade | Pessoa jurídica (CNPJ) com rota nos próximos 1 dia, última visita entre 4 e 3000 dias atrás e última compra do vendedor entre 61 e 90 dias atrás | 1 dias |  |
| 4 | Fechamento de Rota e Sem Atendimento há 3 dias - Compra regularmente | Pessoa jurídica (CNPJ) com rota nos próximos 1 dia, última visita entre 4 e 3000 dias atrás e compra do vendedor nos últimos 30 dias | 1 dias |  |
| 5 | Fechamento de Rota e Sem Atendimento há 3 dias - Resgate de cliente sem compra | Pessoa jurídica (CNPJ) com rota nos próximos 1 dia, última visita entre 4 e 3000 dias atrás e cliente inativo para o vendedor | 1 dias |  |
| 6 | Fechamento de Rota e Sem Atendimento há 3 dias | Pessoa jurídica (CNPJ) com rota nos próximos 1 dia e última visita entre 4 e 3000 dias atrás, sem se enquadrar nos blocos anteriores | 1 dias |  |
| 7 | Primeira Compra (Vendedores Prospects) | Pessoa jurídica (CNPJ) sem venda registrada com o vendedor, para o time de vendedores prospects | 7 dias |  |
| 8 | Primeira Compra (Vendedores Ativos) | Pessoa jurídica (CNPJ) sem venda registrada com o vendedor, para o time de vendedores ativos | 14 dias |  |
| 9 | Risco de inatividade | Pessoa jurídica (CNPJ) com última compra do vendedor entre 61 e 90 dias atrás | 7 dias |  |
| 10 | Estimular a regularidade de compra | Pessoa jurídica (CNPJ) com última compra do vendedor entre 31 e 60 dias atrás | 14 dias |  |
| 11 | Compra regularmente | Pessoa jurídica (CNPJ) com compra do vendedor nos últimos 30 dias | 14 dias |  |
| 12 | Resgate de cliente sem compra | Pessoa jurídica (CNPJ) inativa segundo o histórico de compras com o vendedor | 21 dias |  |
| 13 | Pessoa Física | Clientes pessoa física (CPF) | 14 dias |  |
| 14 | Pessoa Física/Jurídica (indefinido) | Todos os clientes remanescentes que não se enquadraram em nenhum bloco anterior | 14 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(vendedores_prospects): clientes que não se enquadram em nenhum bloco mantêm a configuração anterior.
- Não há bloco final sem filtro para a fonte time(vendedores_ativos): clientes que não se enquadram em nenhum bloco mantêm a configuração anterior.
- O nome do bloco 1 cita 3 dia(s), mas esse número não aparece nos filtros/ações do bloco.
- O nome do bloco 2 cita 3 dia(s), mas esse número não aparece nos filtros/ações do bloco.
- O nome do bloco 3 cita 3 dia(s), mas esse número não aparece nos filtros/ações do bloco.
- O nome do bloco 4 cita 3 dia(s), mas esse número não aparece nos filtros/ações do bloco.
- O nome do bloco 5 cita 3 dia(s), mas esse número não aparece nos filtros/ações do bloco.
- O nome do bloco 6 cita 3 dia(s), mas esse número não aparece nos filtros/ações do bloco.

## Regra 161

`referencias/regra_161.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Define frequências de atendimento diferentes para clientes ativos conforme a curva de faturamento (A, B ou C), e aplica uma frequência padrão para os demais clientes (inativos). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 15d para Ativos Curva A | Clientes ativos para o vendedor e da curva A de faturamento com a empresa | 15 dias |  |
| 2 | Freq. de 7d para Ativos Curva B | Clientes ativos para o vendedor e da curva B de faturamento com a empresa | 7 dias |  |
| 3 | Freq. de 15d para Ativos Curva C | Clientes ativos para o vendedor e da curva C de faturamento com a empresa | 15 dias |  |
| 4 | Freq. de 7d para Inativos | Todos os clientes do time que não se enquadraram em nenhum bloco anterior; na prática, clientes inativos para o vendedor | 7 dias | Bloco sem filtro: funciona como regra final. |

## Regra 162

`referencias/regra_162.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Primeiro bloqueia pessoas físicas e inadimplentes, depois define frequências específicas para prospects, inativos para o vendedor e clientes há mais de 45 dias sem compra, aplicando a frequência do histórico com limites para os demais. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar CPF | Clientes pessoa física (CPF) | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Freq. de 14d para Sem histórico de compra | Clientes prospects (nunca compraram) | 14 dias |  |
| 4 | Freq. de 14d para Inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 14 dias |  |
| 5 | Freq. de 30d para Mais de 45d sem compra | Clientes sem compra nos últimos 45 dias | 30 dias |  |
| 6 | Freq. do histórico ou no mínimo de 14 dias e no máximo de 45 dias | Todos os clientes do time que sobraram dos blocos anteriores | Frequência do histórico, entre 14 e 45 dias | Bloco sem filtro: funciona como regra final. |

## Regra 163

`referencias/regra_163.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para as carteiras 'construtora' e 'matcom' (associadas ao time de televendas). Os blocos aplicam regras específicas de agendamento e frequência com base no histórico de compras com o vendedor e com o grupo. Os blocos são avaliados em ordem para cada carteira.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes com venda em 30d (Construtoras) | Clientes da carteira construtora com compra nos últimos 30 dias com qualquer vendedor do mesmo grupo | Não agendar |  |
| 2 | Ative um novo cliente em sua carteira (Construtoras) | Clientes da carteira construtora sem nenhuma venda registrada com o próprio vendedor | 30 dias |  |
| 3 | Estabeleça relacionamento com seu novo cliente (Construtoras) | Clientes da carteira construtora com compra única com o próprio vendedor e sem compra nos últimos 60 dias com o grupo | 21 dias |  |
| 4 | Estimule a regularidade de compra do seu cliente (Construtoras) | Clientes da carteira construtora cuja última compra com o próprio vendedor não ocorreu entre 31 e 60 dias atrás | 28 dias |  |
| 5 | Cliente entrando em ruptura (Construtoras) | Clientes da carteira construtora cuja última compra com o próprio vendedor não ocorreu entre 61 e 90 dias atrás | 14 dias |  |
| 6 | Garanta que este cliente se mantenha ativo, pois ele está perdendo relacionamento com você! (Construtoras) | Todos os clientes da carteira construtora que sobraram dos blocos anteriores | 21 dias | Bloco sem filtro: funciona como regra final para a carteira construtora. |
| 7 | Ative um novo cliente em sua carteira (Matcom) | Clientes da carteira matcom sem nenhuma venda registrada com o próprio vendedor | 7 dias |  |
| 8 | Estabeleça relacionamento com seu novo cliente (Matcom) | Clientes da carteira matcom com compra única com o próprio vendedor e sem compra nos últimos 30 dias com o grupo | 14 dias |  |
| 9 | Cliente que compra com regularidade (Matcom) | Clientes da carteira matcom com compra entre 7 e 30 dias atrás com o grupo | Frequência do histórico, entre 7 e 30 dias |  |
| 10 | Estimule a regularidade de compra do seu cliente (Matcom) | Clientes da carteira matcom cuja última compra com o próprio vendedor não ocorreu entre 31 e 60 dias atrás | 14 dias |  |
| 11 | Cliente entrando em ruptura (Matcom) | Clientes da carteira matcom cuja última compra com o próprio vendedor não ocorreu entre 61 e 90 dias atrás | 7 dias |  |
| 12 | Garanta que este cliente se mantenha ativo, pois ele está perdendo relacionamento com você! (Matcom) | Todos os clientes da carteira matcom que sobraram dos blocos anteriores | 7 dias | Bloco sem filtro: funciona como regra final para a carteira matcom. |

**Pontos de atenção**

- As carteiras construtora e matcom são utilizadas nas regras, mas não são definidas neste arquivo (podem estar em outro arquivo de regras do cliente).

## Regra 164

`referencias/regra_164.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização aplicada aos times time bruna e time todos. A regra define frequências de atendimento para clientes com rótulos específicos (como condomínio e construtora) e novos cadastros, variando conforme recência de compra, curva de faturamento e localização. Os blocos são avaliados em ordem e os clientes que não se encaixam nas regras anteriores caem na regra final para o time todos.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. 14 dias para novos cadastros Condomínio vendedora Bruna | Clientes do time bruna com rótulo contendo condominio e cadastrados a partir de 2024-10-03 | 14 dias |  |
| 2 | Freq. de 7 dias para compra detectada com a empresa entre 0 e 30 dias Condomínio vendedora Bruna | Clientes do time bruna com rótulo contendo condominio e com compra nos últimos 30 dias com qualquer vendedor da empresa | 7 dias |  |
| 3 | Freq. de 30 dias para não tem compra com a empresa nos últimos 90 dias Condomínio vendedora Bruna | Clientes do time bruna com rótulo contendo condominio e sem compra nos últimos 90 dias com qualquer vendedor da empresa | 30 dias |  |
| 4 | Freq. de 7d para Ativar prospects | Clientes do time todos sem nenhuma venda registrada e cadastrados a partir de 2024-08-01 | 7 dias |  |
| 5 | Boas vindas: Frequência de 14d para construtora | Clientes do time todos com rótulo contendo construtora, com compra única com a empresa e sem compra nos últimos 60 dias com vendedor do mesmo grupo | 14 dias |  |
| 6 | Compra com regularidade no RJ - Curva A: Frequência de 7d para construtora | Clientes do time todos com rótulo construtora, frequência histórica menor que 30 dias, sem compra nos últimos 14 dias com vendedor do mesmo grupo, UF RJ e curva A de faturamento | 7 dias |  |
| 7 | Compra com regularidade no RJ - Curva B: Frequência de 10d para construtora | Clientes do time todos com rótulo construtora, frequência histórica menor que 30 dias, sem compra nos últimos 14 dias com vendedor do mesmo grupo, UF RJ e curva B de faturamento | 10 dias |  |
| 8 | Compra com regularidade no RJ - Curva C: Frequência de 14d para construtora | Clientes do time todos com rótulo construtora, frequência histórica menor que 30 dias, sem compra nos últimos 14 dias com vendedor do mesmo grupo, UF RJ e curva C de faturamento | 14 dias |  |
| 9 | Compra com regularidade: Frequência de 14d para construtora | Clientes do time todos com rótulo construtora, frequência histórica menor que 30 dias e sem compra nos últimos 14 dias com vendedor do mesmo grupo | 14 dias |  |
| 10 | Estimular regularidade: Frequência de 10d para construtora | Clientes do time todos com rótulo construtora, ativos com a empresa e sem compra global nos últimos 45 dias | 10 dias |  |
| 11 | Risco de ficar inativo: Frequência de 14d para construtora | Clientes do time todos com rótulo construtora e sem compra nos últimos 60 dias com vendedor do mesmo grupo | 14 dias |  |
| 12 | Ativar novos clientes: Frequência de 7d para construtora | Clientes do time todos com rótulo construtora e cadastrados a partir de 2024-10-03 | 7 dias |  |
| 13 | Resgate de inativos: Frequência de 45d para construtora | Clientes do time todos com rótulo contendo construtora | 45 dias |  |
| 14 | Freq. de 14 dias para Novos cadastros diversificados | Clientes do time todos com rótulo contendo shopping, supermercado, industria, estaleiro, clube, escolas e mais 7, cadastrados a partir de 2024-10-03 | 14 dias |  |
| 15 | Freq. de 7 dias para Novos cadastros diversificados | Clientes do time todos com rótulo contendo shopping, supermercado, industria, estaleiro, clube, escolas e mais 7, com compra nos últimos 30 dias com qualquer vendedor da empresa | 7 dias |  |
| 16 | Freq. de 30 dias para Novos cadastros diversificados | Clientes do time todos com rótulo contendo shopping, supermercado, industria, estaleiro, clube, escolas e mais 7, com compra nos últimos 30 dias com qualquer vendedor da empresa | 30 dias |  |
| 17 | Isocom: Não agendar - cliente não coberto por regra comercial | Todos os clientes do time todos que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time (time bruna): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Os blocos 15 e 16 possuem exatamente o mesmo filtro de recência de compra global em 30 dias para os mesmos rótulos, mas com ações diferentes (7 dias e 30 dias). Como o sistema avalia em ordem, apenas o bloco 15 será aplicado para esses clientes.

## Regra Chegatto

`referencias/regra_165.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de televendas (vendedores do tipo televendas ativados) e uso de segmentações baseadas no time de campo. O sistema avalia os blocos em ordem: inativos inadimplentes não são agendados, clientes sem compra há mais de 90 dias recebem frequência de 7 dias, grupos específicos com base na frequência histórica e recência recebem frequências variadas, e quem sobra não é agendado.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inativos inadimplentes | Clientes em ciclo de vida inativo com a empresa e inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Clientes há mais de 90 dias sem compra | Clientes sem compra nos últimos 90 dias com algum vendedor do mesmo grupo | 7 dias |  |
| 3 | Frequência histórica 1 a 7 dias | Clientes da segmentação de campo freq_hist_1a7 e sem compra entre 8 e 15 dias atrás | 14 dias |  |
| 4 | Frequência histórica 16 a 30 dias | Clientes da segmentação de campo freq_hist_16a30 e sem compra entre 31 e 45 dias atrás | 28 dias |  |
| 5 | Frequência histórica 31 a 45 dias | Clientes da segmentação de campo freq_hist_31a45 e sem compra entre 46 e 60 dias atrás | 21 dias |  |
| 6 | Frequência histórica 61 a 90 dias | Clientes da segmentação de campo freq_hist_61a90 e sem compra nos últimos 90 dias | 15 dias |  |
| 7 | Regra final | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- O uso de segmentações de carteira fixa do time de campo (campo) aplicadas a clientes do time de televendas pode cruzar regras de equipes diferentes. É importante validar se os clientes da carteira de campo também pertencem ao televendas.

## Regra 166

`referencias/regra_166.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira fixa do time de televendas. Clientes com restrições de crédito (tipo DH sem crédito ou tipo BK com menos de R$ 199 de crédito) e inadimplentes não são agendados. Os demais recebem frequência de ligação baseada no histórico com o próprio vendedor (ativos a cada 7 dias, inativos e sem venda a cada 14 dias). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes DH sem crédito | Clientes com tipo de cobrança DH e sem crédito disponível (crédito igual ou menor que R$0,00) | Não agendar |  |
| 2 | Não agendar clientes BK com crédito menor que R$200 | Clientes com tipo de cobrança BK e crédito disponível abaixo de R$ 199 | Não agendar |  |
| 3 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Frequência de 7d para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 5 | Frequência de 14d para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 14 dias |  |
| 6 | Frequência de 14d para sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 167

`referencias/regra_167.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes baixados na Receita Federal não são agendados; os demais recebem frequência de ligação variada conforme o ciclo de vida, o número de compras ou o tempo desde o último pedido (compras com vendedores do mesmo grupo). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Primeira compra | Clientes em ciclo de vida prospect com a empresa (nunca comprou) | 7 dias |  |
| 3 | Tirou o primeiro pedido | Clientes que compraram uma única vez com a empresa | 15 dias |  |
| 4 | Ativo: cliente que tem compra com a empresa em 30 dias | Clientes com pedido nos últimos 30 dias | Frequência do histórico, entre 7 e 21 dias |  |
| 5 | Aumentar a regularidade de compra | Clientes com pedido entre 31 e 90 dias atrás | 28 dias |  |
| 6 | Cliente caminhando para inatividade | Clientes com pedido entre 91 e 120 dias atrás | 45 dias |  |
| 7 | Resgate de inativos | Clientes sem venda de qualquer vendedor da empresa nos últimos 120 dias | 60 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 168

`referencias/regra_168.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas e carteiras específicas de rotas por cidade. Bloqueia clientes baixados na Receita e bloqueados para atendimento, define frequências diárias, preferências de dias, roteirização e regras fixas para diferentes carteiras conforme o dia da semana, e os demais clientes do televendas não são agendados. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 3 | Rota todo dia -> Agendamento todo dia | Todos os clientes da carteira rota_todo_dia que sobraram dos blocos anteriores | 1 dias (diaria); preferência: segunda, terça, quarta, quinta, sexta (prioritária); fixo; roteirizável |  |
| 4 | Rota de terça -> Agendamento segunda | Todos os clientes da carteira rota_terca que sobraram dos blocos anteriores | 1 dias (diaria); preferência: segunda (prioritária); fixo; roteirizável | Regra aplicada somente às segundas. |
| 5 | Rota de quarta -> Agendamento terça | Todos os clientes da carteira rota_quarta que sobraram dos blocos anteriores | 1 dias (diaria); preferência: terça (prioritária); fixo; roteirizável | Regra aplicada somente às terças. |
| 6 | Rota de quinta -> Agendamento quarta | Todos os clientes da carteira rota_quinta que sobraram dos blocos anteriores | 1 dias (diaria); preferência: quarta (prioritária); fixo; roteirizável | Regra aplicada somente às quartas. |
| 7 | Rota de sexta -> Agendamento quinta | Todos os clientes da carteira rota_sexta que sobraram dos blocos anteriores | 1 dias (diaria); preferência: quinta (prioritária); fixo; roteirizável | Regra aplicada somente às quintas. |
| 8 | Regra final televendas | Todos os clientes do time televendas que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final para a fonte televendas. |

**Pontos de atenção**

- As carteiras rota_todo_dia, rota_terca, rota_quarta, rota_quinta e rota_sexta são utilizadas nos blocos, mas não estão definidas neste arquivo (podem estar em outro arquivo de regras do cliente).
- Não há bloco final sem filtro para as carteiras de rota: clientes dessas carteiras que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 169

`referencias/regra_169.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para Motor Diesel envolvendo times de fornecedor e televendas. Define frequências e regras de não agendamento para diferentes fontes e segmentações, avaliadas em ordem sequencial para cada bloco.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias | Aplica-se às fontes segmentação televendas ruptura de fornecedor e televendas consumidor. |
| 2 | Ativos com compra entre 7d e 30d | Clientes com última compra (positivação) global nos últimos 30 dias | 14 dias | Aplica-se às fontes segmentação televendas ruptura de fornecedor e televendas consumidor. |
| 3 | Ativos com compra entre 30d e 60d | Clientes com última compra (positivação) global nos últimos 60 dias que não entraram nos blocos anteriores | 14 dias | Aplica-se às fontes segmentação televendas ruptura de fornecedor e televendas consumidor. |
| 4 | Ativos com compra entre 60d e 90d | Clientes com última compra (positivação) global nos últimos 90 dias que não entraram nos blocos anteriores | 14 dias | Aplica-se às fontes segmentação televendas ruptura de fornecedor e televendas consumidor. |
| 5 | Clientes inativos | Clientes com última compra (positivação) global entre 90 e 180 dias atrás que não entraram nos blocos anteriores | 14 dias | Aplica-se às fontes segmentação televendas ruptura de fornecedor e televendas consumidor. |
| 6 | Ativos com compra em 7 dias | Clientes com última compra (positivação) global nos últimos 7 dias | Não agendar | Aplica-se às fontes time televendas e televendas_2. |
| 7 | Não agendar Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar | Aplica-se às fontes time televendas e televendas_2. |
| 8 | Não agendar - choque de agendas | Todos os clientes da fonte que ainda não foram parametrizados por blocos anteriores | Não agendar | Bloco sem filtro, exclusivo para a fonte time televendas. |
| 9 | Freq. de 14 dias para clientes sem venda em 8 dias | Todos os clientes da fonte que ainda não foram parametrizados por blocos anteriores | 14 dias | Bloco sem filtro, exclusivo para a fonte time televendas_2. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte segmentacao(televendas ruptura de fornecedor, televendas consumidor): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(televendas, televendas_2): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- O nome do bloco 2 (Ativos com compra entre 7d e 30d) cita 7 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- O nome do bloco 9 (Freq. de 14 dias para clientes sem venda em 8 dias) cita 8 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- segmentacao(televendas consumidor) é usado nos blocos 1, 2, 3, 4, 5, mas não é definido neste arquivo (pode estar em outro arquivo de regras do cliente).

## Regra 170

`referencias/regra_170.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores da empresa. Aplica regras específicas de frequência para distribuidores e clientes regulares, remove agendamento para clientes ativos com compras recentes e define frequência mensal para inativos e prospects. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ramo distribuidor sem vendas em 60 dias | Clientes ativos para o vendedor, com ramo de atividade DISTRIBUIDOR e sem compra nos últimos 60 dias | 15 dias (quinzenal) |  |
| 2 | Compra com regularidade | Clientes sem compra global nos últimos 10 dias e com frequência histórica de compra abaixo de 7 dias | 21 dias |  |
| 3 | Não agendar ramo distribuidor com vendas em 60 dias | Clientes ativos para o vendedor e com ramo de atividade DISTRIBUIDOR que não caíram no bloco 1 (ou seja, com compras nos últimos 60 dias) | Não agendar |  |
| 4 | Ativos e sem vendas em 30 dias | Clientes ativos para o vendedor e sem compra nos últimos 30 dias | 15 dias (quinzenal) |  |
| 5 | Não agendar ativos com vendas em 30 dias | Clientes ativos para o vendedor que não caíram nos blocos anteriores (na prática, com compras nos últimos 30 dias) | Não agendar |  |
| 6 | Clientes inativos e prospects | Todos os clientes da fonte que sobraram dos blocos anteriores | 30 dias (mensal) | Bloco sem filtro: funciona como regra final. |

## Regra 171

`referencias/regra_171.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas. Primeiro remove da agenda inadimplentes, bloqueados, filiais e empresas com cadastro baixado na Receita Federal; em seguida, define frequências de atendimento específicas para prospects, clientes com única compra, ativos com base na recência e histórico, e clientes em risco ou inativos. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 3 | Não agendar filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 4 | Não agendar Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 5 | Prospect: Cliente potencial | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 6 | Ativado: fez um pedido e ainda não comprou mais | Clientes com uma única compra com a empresa e cadastrados no ERP há pelo menos 30 dias | 10 dias |  |
| 7 | Ativo: Alta frequência de compra | Clientes com último pedido global nos últimos 30 dias e frequência histórica de compra menor que 14 dias | 14 dias |  |
| 8 | Ativo: compra regularmente | Clientes com último pedido global nos últimos 30 dias e frequência histórica menor que 30 dias | Frequência do histórico, com mínimo de 14 e máximo de 28 dias |  |
| 9 | Ativo: estimular a regularidade de compra | Clientes com último pedido global entre 21 e 60 dias atrás | 14 dias |  |
| 10 | Em ruptura: risco de ficar inativo | Clientes com último pedido global entre 61 e 90 dias atrás | 7 dias |  |
| 11 | Inativo: reativar cliente sem compra | Clientes cujo último pedido global NÃO ocorreu entre 90 e 180 dias atrás | 21 dias | O filtro exclui a faixa de 90 a 180 dias, aplicando-se a quem comprou há menos de 90 dias (mas que não caiu nos filtros anteriores) ou há mais de 180 dias. |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- O nome do bloco 8 cita 21 dias, mas a ação parametrizada usa a frequência do histórico com limites de 14 a 28 dias. Confirmar qual vale.

## Regra 172

`referencias/regra_172.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas). Clientes inadimplentes e filiais não são agendados; ativos para o vendedor recebem frequência de 7 dias; e os demais recebem frequência de 14 dias. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 3 | Ativo | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 4 | Inativo | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 173

`referencias/regra_173.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Primeiro bloqueia quem não deve ser agendado (baixados na Receita, inadimplentes e clientes com rota do vendedor externo na semana); depois define a frequência de ligação pelo tempo desde a última compra (compras com vendedores do mesmo grupo); quem sobra não é agendado. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar clientes com data da rota na semana | Clientes com data de rota (visita presencial do vendedor externo) na semana atual | Não agendar | Evita que o cliente receba ligação do televendas na mesma semana da visita do externo. |
| 4 | Clientes prospects | Clientes em ciclo de vida prospect com a empresa | 14 dias |  |
| 5 | Clientes ativos | Clientes com compra nos últimos 60 dias | 14 dias |  |
| 6 | Risco de inatividade | Clientes com compra nos últimos 90 dias que não entraram nos blocos anteriores; na prática, entre 60 e 90 dias sem comprar | 7 dias |  |
| 7 | Inativos (90 dias) | Clientes com compra nos últimos 120 dias que não entraram nos blocos anteriores; na prática, entre 90 e 120 dias sem comprar | 14 dias |  |
| 8 | Inativos (120 dias) | Clientes com compra nos últimos 150 dias que não entraram nos blocos anteriores; na prática, entre 120 e 150 dias sem comprar | 21 dias |  |
| 9 | Inativos (150 dias) | Clientes com compra nos últimos 180 dias que não entraram nos blocos anteriores; na prática, entre 150 e 180 dias sem comprar | 28 dias |  |
| 10 | Clientes que não se enquadraram nas regras padrão | Todos os clientes do time que não se enquadraram em nenhum bloco anterior (por exemplo, sem compra há mais de 180 dias) | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Clientes sem compra há mais de 180 dias caem na regra final e não são agendados.

## Regra 174

`referencias/regra_174.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas. Primeiro bloqueia clientes inadimplentes e com CNPJ baixado na Receita Federal; em seguida, define a frequência de atendimento com base no ciclo de vida, histórico de compras, recência e ramo de atividade (com foco nos ramos 9 e 18). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 3 | Prospect: Cliente potencial | Clientes em ciclo de vida prospect com o próprio vendedor (nunca comprou com ele) | 14 dias |  |
| 4 | Ativado: fez um pedido e ainda não comprou mais | Clientes com uma única compra com o próprio vendedor e cadastrados no ERP há pelo menos 60 dias | 21 dias |  |
| 5 | Ativo: Alta frequência de compra | Clientes com pedido com o próprio vendedor nos últimos 30 dias e frequência histórica de compra abaixo de 14 dias | Frequência do histórico, entre 10 e 14 dias |  |
| 6 | Ativo: compra regularmente (ramos 9 e 18) | Clientes com pedido com o próprio vendedor nos últimos 60 dias, frequência histórica abaixo de 30 dias e ramo de atividade igual a 9 ou 18 | Frequência do histórico, entre 14 e 21 dias |  |
| 7 | Ativo: compra regularmente (demais ramos) | Clientes com pedido com o próprio vendedor nos últimos 60 dias, frequência histórica abaixo de 30 dias e ramo de atividade diferente de 9 e 18 | 28 dias |  |
| 8 | Ativo: estimular a regularidade de compra (ramos 9 e 18) | Clientes com pedido com o próprio vendedor entre 21 e 60 dias atrás e ramo de atividade igual a 9 ou 18 | 14 dias |  |
| 9 | Ativo: estimular a regularidade de compra (demais ramos) | Clientes com pedido com o próprio vendedor entre 21 e 60 dias atrás e ramo de atividade diferente de 9 e 18 | 21 dias |  |
| 10 | Em ruptura: risco de ficar inativo para os ramos 9 e 18 | Clientes com pedido com o próprio vendedor entre 61 e 90 dias atrás e ramo de atividade igual a 9 ou 18 | 14 dias |  |
| 11 | Em ruptura: risco de ficar inativo | Clientes com pedido com o próprio vendedor entre 61 e 90 dias atrás e ramo de atividade diferente de 9 e 18 | 14 dias |  |
| 12 | Inativo: reativar cliente sem compra | Clientes sem pedido com o próprio vendedor nos últimos 90 dias | 21 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 175

`referencias/regra_175.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira activity_in (associada ao time de televendas). Bloqueia filiais, inadimplentes e quem comprou nos últimos 30 dias; define frequências para ativos, inativos, com vendas no ano anterior mas não no atual, e sem compras desde 2023. O bloco final aplica-se ao time de televendas. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes filiais | Clientes que são filiais | Não agendar |  |
| 2 | Não agendar clientes inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar clientes com compra em 30d | Clientes com compra nos últimos 30 dias | Não agendar |  |
| 4 | Clientes ativos na empresa | Clientes ativos segundo o histórico de compras com qualquer vendedor da empresa | 14 dias |  |
| 5 | Clientes inativos na empresa | Clientes inativos segundo o histórico de compras com qualquer vendedor da empresa | 21 dias |  |
| 6 | Clientes que compraram em 2024 e estão sem vendas em 2025 | Clientes com venda da empresa no ano anterior e sem venda da empresa no ano atual | 21 dias |  |
| 7 | Clientes que compraram em 2023 e não compraram mais | Clientes com última compra entre 2023-01-01 e 2023-12-31 | 30 dias |  |
| 8 | Regra final para televendas | Todos os clientes do time de televendas que não foram parametrizados pelos blocos anteriores | Não agendar | Bloco sem filtro: funciona como regra final para a fonte televendas. |

**Pontos de atenção**

- A carteira activity_in é usada nos blocos 1 a 7, mas não é definida neste arquivo e pode estar em outro arquivo de regras.
- Não há bloco final sem filtro específico para a fonte carteira(activity_in): clientes dessa carteira que não se enquadram em nenhum bloco mantêm a parametrização anterior.
- O bloco 8 muda a fonte de aplicação para o time de televendas, enquanto os blocos anteriores usavam a carteira activity_in.

## Regra 176

`referencias/regra_176.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira fixa do time televendas. O sistema avalia os blocos em ordem: bloqueia clientes DH sem crédito, clientes BK com menos de R$ 199 de crédito e inadimplentes; depois define frequência para ativos (7 dias), inativos e sem venda (14 dias).

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Nordil AL: Não agendar clientes DH com crédito igual ou menor que R$0,00 | Clientes sem crédito disponível e com tipo de cobrança DH | Não agendar |  |
| 2 | Nordil AL: Não agendar clientes BK com crédito menor que R$200,00 | Clientes com menos de R$ 199 de crédito disponível e com tipo de cobrança BK | Não agendar |  |
| 3 | Nordil AL: Não agendar clientes inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Nordil AL: Frequência de 7d para clientes ativos/adimplentes | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 5 | Nordil AL: Frequência de 14d para clientes inativos/adimplentes | Clientes inativos segundo o histórico de compras com o próprio vendedor | 14 dias |  |
| 6 | Nordil AL: Frequência de 14d para clientes sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 177

`referencias/regra_177.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização da carteira fixa do time televendas. Os primeiros blocos bloqueiam o agendamento de clientes específicos por falta de crédito, tipo de cobrança ou inadimplência. Os blocos seguintes definem a frequência para ativos, inativos e sem venda. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes DH sem crédito | Clientes sem crédito disponível e com tipo de cobrança DH | Não agendar |  |
| 2 | Não agendar clientes BK com crédito baixo | Clientes com menos de R$ 199 de crédito disponível e com tipo de cobrança BK | Não agendar |  |
| 3 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Frequência de 7 dias para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 5 | Frequência de 14 dias para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 14 dias |  |
| 6 | Frequência de 14 dias para clientes sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 178

`referencias/regra_178.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times: televendas_1 (vendedores televendas ativados) e televendas_2 (vendedor ID 48). O primeiro time foca em controle de agendamento e recência de compras de clientes existentes, enquanto o segundo gerencia o tempo de cadastro para novos clientes. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal do time televendas_1 | Não agendar |  |
| 2 | Clientes que nunca compraram com a empresa | Clientes cadastrados no ERP há pelo menos 7 dias do time televendas_2 | Não agendar |  |
| 3 | Não agendar clientes com compra recente | Clientes com compra nos últimos 39 dias do time televendas_1 | Não agendar |  |
| 4 | Tentativa final | Clientes cadastrados no ERP há pelo menos 60 dias do time televendas_2 | 30 dias |  |
| 5 | Lead frio | Clientes cadastrados no ERP há pelo menos 30 dias do time televendas_2 | 20 dias |  |
| 6 | Lead morno | Clientes cadastrados no ERP há pelo menos 15 dias do time televendas_2 | 15 dias |  |
| 7 | Follow-up | Clientes cadastrados no ERP há pelo menos 8 dias do time televendas_2 | 15 dias |  |
| 8 | Estimular recompra | Clientes com compra entre 40 e 89 dias atrás do time televendas_1 | 15 dias |  |
| 9 | Reativação moderada | Clientes com compra entre 90 e 119 dias atrás do time televendas_1 | 7 dias |  |
| 10 | Reativação intensa | Clientes com compra entre 120 e 359 dias atrás do time televendas_1 | 7 dias |  |
| 11 | Resgate crítico | Clientes sem compra há mais de 359 dias do time televendas_1 | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(televendas_1): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(televendas_2): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 179

`referencias/regra_179.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK
Duplicatas: referencias/regra_216.gobr

Parametrização para as carteiras construtora, matcon e demais_segment, além de um time de televendas. Define a frequência de atendimento com base no ciclo de vida, última compra com o vendedor ou na empresa, separando por segmentos. Os blocos são avaliados em ordem e o cliente fica no primeiro em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ative um novo cliente em sua carteira! (Todos os segmentos) | Clientes em ciclo de vida prospect com o próprio vendedor nas carteiras construtora, matcon e demais_segment | 7 dias |  |
| 2 | Estabeleça relacionamento com seu novo cliente! (Construtoras) | Clientes com uma única compra com o próprio vendedor na carteira construtora | 14 dias |  |
| 3 | Estabeleça relacionamento com seu novo cliente! (Exceto Construtoras) | Clientes com uma única compra com o próprio vendedor nas carteiras matcon e demais_segment | 7 dias |  |
| 4 | Cliente que compra com regularidade! (Exceto Construtoras) | Clientes das carteiras matcon e demais_segment com última compra entre 7 e 30 dias atrás com vendedor do mesmo grupo | Frequência do histórico, entre 7 e 30 dias |  |
| 5 | Cliente que compra com regularidade! (Construtoras com venda em 30d) | Clientes da carteira construtora com última compra nos últimos 30 dias com vendedor do mesmo grupo | 7 dias |  |
| 6 | Cliente que compra com regularidade! (Construtoras sem venda em 30d) | Clientes da carteira construtora sem compra nos últimos 30 dias com vendedor do mesmo grupo | 14 dias |  |
| 7 | Estimule a regularidade de compra do seu cliente! (Matcon) | Clientes da carteira matcon com última compra global entre 30 e 60 dias atrás | 7 dias |  |
| 8 | Estimule a regularidade de compra do seu cliente! (Exceto Matcon) | Clientes das carteiras construtora e demais_segment com última compra global entre 30 e 60 dias atrás | 14 dias |  |
| 9 | Atenção!!! Cliente caminhando para inatividade! (Matcon) | Clientes da carteira matcon com última compra global entre 60 e 89 dias atrás | 7 dias |  |
| 10 | Atenção!!! Cliente caminhando para inatividade! (Construtoras) | Clientes da carteira construtora com última compra global entre 60 e 89 dias atrás | 14 dias |  |
| 11 | Atenção!!! Cliente caminhando para inatividade! (Exceto Matcon e Construtoras) | Clientes da carteira demais_segment com última compra global entre 60 e 89 dias atrás | 21 dias |  |
| 12 | Resgate este cliente inativo! (Matcon) | Clientes da carteira matcon com última compra global entre 90 e 179 dias atrás | 7 dias |  |
| 13 | Resgate este cliente inativo! (Construtoras) | Clientes da carteira construtora com última compra global entre 90 e 179 dias atrás | 21 dias |  |
| 14 | Resgate este cliente inativo! (Exceto Matcon e Construtoras) | Clientes da carteira demais_segment com última compra global entre 90 e 179 dias atrás | 14 dias |  |
| 15 | Requalifique e resgate este cliente! (Exceto Construtoras) | Clientes das carteiras matcon e demais_segment sem compra global nos últimos 180 dias | 14 dias |  |
| 16 | Requalifique e resgate este cliente! (Construtoras) | Clientes da carteira construtora sem compra global nos últimos 180 dias | 28 dias |  |

**Pontos de atenção**

- As carteiras construtora, matcon e demais_segment são usadas nas regras, mas não são definidas neste arquivo e podem estar em outro local.
- Não há bloco final sem filtro para as fontes de carteira, portanto clientes que não se encaixam em nenhuma regra mantêm a configuração anterior.

## Regra 180

`referencias/regra_180.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia o agendamento para filiais e empresas com situação suspensa, inapta ou baixada na Receita Federal. Em seguida, define frequência de 7 dias para ramos específicos e de 30 dias para os demais. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar filiais | Clientes que são filiais | Não agendar |  |
| 2 | Não agendar suspensos na Receita | Clientes com CNPJ suspenso na Receita Federal | Não agendar |  |
| 3 | Não agendar inaptos na Receita | Clientes com CNPJ inapto na Receita Federal | Não agendar |  |
| 4 | Não agendar baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 5 | Frequência para ramos específicos | Clientes com ramo de atividade igual a 84, 73, 69, 85 ou 22 | 7 dias |  |
| 6 | Frequência para demais clientes | Todos os clientes do time que sobraram dos blocos anteriores (fora dos ramos 84, 73, 69, 85 e 22) | 30 dias | Bloco sem filtro: funciona como regra final. |

## Regra 181

`referencias/regra_181.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para a carteira fixa da empresa cescom (todos os vendedores da empresa). Filiais não são agendadas; os demais clientes recebem frequências de 7, 14 ou 30 dias com base no status ativo/inativo para o vendedor, adimplência e histórico de vendas, mantendo a preferência de dias configurada pelo vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Restrição de agendamento - não agendar filiais | Clientes cuja empresa é filial | Não agendar |  |
| 2 | Ativos adimplentes | Clientes ativos para o vendedor e adimplentes (sem pendências financeiras) | 7 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 3 | Ativos inadimplentes | Clientes ativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 14 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 4 | Inativos adimplentes | Clientes inativos para o vendedor e adimplentes (sem pendências financeiras) | 14 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 5 | Inativos inadimplentes | Clientes inativos para o vendedor e inadimplentes (com pendências financeiras em aberto) | 30 dias, mantendo a preferência de dias configurada pelo vendedor |  |
| 6 | Clientes sem vendas | Clientes sem nenhuma venda registrada (nunca compraram) | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 182

`referencias/regra_182.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Primeiramente, bloqueia o agendamento de CPFs, inadimplentes, baixados na Receita Federal e clientes com pedido nos últimos 7 dias. Em seguida, define frequências específicas por ramo de atividade e tempo desde o último pedido. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar CPF | Clientes pessoa física (CPF) | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 4 | Não agendar cliente com pedido nos últimos 7 dias | Clientes com pedido nos últimos 7 dias | Não agendar |  |
| 5 | Prospects dos ramos de atividade 89 a 103 | Clientes prospects (nunca compraram) dos ramos de atividade 089, 090, 091, 092, 093, 094, 095, 096, 097, 098, 099, 100, 101, 102 e 103 | 7 dias |  |
| 6 | Ramo de atividade MANGUEIRAS com pedido em 45d | Clientes do ramo de atividade 089 (Mangueiras) com pedido nos últimos 45 dias | 14 dias |  |
| 7 | Ramo de atividade MANGUEIRAS com pedido acima de 45d | Clientes do ramo de atividade 089 (Mangueiras) sem pedido nos últimos 45 dias | 7 dias |  |
| 8 | Ramo de atividade MATERIAIS DE LIMPEZA com pedido em 60d | Clientes do ramo de atividade 090 (Materiais de Limpeza) com pedido nos últimos 60 dias | 21 dias |  |
| 9 | Ramo de atividade MATERIAIS DE LIMPEZA com pedido acima de 60d | Clientes do ramo de atividade 090 (Materiais de Limpeza) sem pedido nos últimos 60 dias | 10 dias |  |
| 10 | Ramo de atividade REVENDA EPI com pedido em 45d | Clientes do ramo de atividade 091 (Revenda EPI) com pedido nos últimos 45 dias | 14 dias |  |
| 11 | Ramo de atividade REVENDA EPI com pedido acima de 45d | Clientes do ramo de atividade 091 (Revenda EPI) sem pedido nos últimos 45 dias | 7 dias |  |
| 12 | Ramo de atividade MATERIAIS DE CONSTRUÇÃO com pedido em 90d | Clientes do ramo de atividade 092 (Materiais de Construção) com pedido nos últimos 90 dias | 28 dias |  |
| 13 | Ramo de atividade MATERIAIS DE CONSTRUÇÃO com pedido acima de 90d | Clientes do ramo de atividade 092 (Materiais de Construção) sem pedido nos últimos 90 dias | 14 dias |  |
| 14 | Ramo de atividade FERRAGEM E FERRAMENTAS com pedido em 45d | Clientes do ramo de atividade 093 (Ferragem e Ferramentas) com pedido nos últimos 45 dias | 14 dias |  |
| 15 | Ramo de atividade FERRAGEM E FERRAMENTAS com pedido acima de 45d | Clientes do ramo de atividade 093 (Ferragem e Ferramentas) sem pedido nos últimos 45 dias | 7 dias |  |
| 16 | Ramo de atividade AGROPECUARIA com pedido em 90d | Clientes do ramo de atividade 094 (Agropecuária) com pedido nos últimos 90 dias | 28 dias |  |
| 17 | Ramo de atividade AGROPECUARIA com pedido acima 90d | Clientes do ramo de atividade 094 (Agropecuária) sem pedido nos últimos 90 dias | 14 dias |  |
| 18 | Ramo de atividade PRESTADOR DE SERVIÇO com pedido em 75d | Clientes do ramo de atividade 095 (Prestador de Serviço) com pedido nos últimos 75 dias | 21 dias |  |
| 19 | Ramo de atividade PRESTADOR DE SERVIÇO com pedido acima de 75d | Clientes do ramo de atividade 095 (Prestador de Serviço) sem pedido nos últimos 75 dias | 14 dias |  |
| 20 | Ramo de atividade INDÚSTRIA com pedido em 75d | Clientes do ramo de atividade 096 (Indústria) com pedido nos últimos 75 dias | 28 dias |  |
| 21 | Ramo de atividade INDÚSTRIA com pedido acima de 75d | Clientes do ramo de atividade 096 (Indústria) sem pedido nos últimos 75 dias | 14 dias |  |
| 22 | Ramo de atividade COOPERATIVA com pedido em 60d | Clientes do ramo de atividade 097 (Cooperativa) com pedido nos últimos 60 dias | 21 dias |  |
| 23 | Ramo de atividade COOPERATIVA com pedido acima de 60d | Clientes do ramo de atividade 097 (Cooperativa) sem pedido nos últimos 60 dias | 10 dias |  |
| 24 | Ramo de atividade HOME CENTER com pedido em 60d | Clientes do ramo de atividade 098 (Home Center) com pedido nos últimos 60 dias | 21 dias |  |
| 25 | Ramo de atividade HOME CENTER com pedido acima de 60d | Clientes do ramo de atividade 098 (Home Center) sem pedido nos últimos 60 dias | 10 dias |  |
| 26 | Ramo de atividade ATACADO com pedido em 45d | Clientes do ramo de atividade 099 (Atacado) com pedido nos últimos 45 dias | 14 dias |  |
| 27 | Ramo de atividade ATACADO com pedido acima de 45d | Clientes do ramo de atividade 099 (Atacado) sem pedido nos últimos 45 dias | 7 dias |  |
| 28 | Ramo de atividade CONSTRUTORA com pedido em 75d | Clientes do ramo de atividade 100 (Construtora) com pedido nos últimos 75 dias | 28 dias |  |
| 29 | Ramo de atividade CONSTRUTORA com pedido acima de 75d | Clientes do ramo de atividade 100 (Construtora) sem pedido nos últimos 75 dias | 7 dias |  |
| 30 | Ramo de atividade ÓRGÃO PÚBLICO com pedido em 90d | Clientes do ramo de atividade 101 (Órgão Público) com pedido nos últimos 90 dias | 28 dias |  |
| 31 | Ramo de atividade ÓRGÃO PÚBLICO com pedido acima de 90d | Clientes do ramo de atividade 101 (Órgão Público) sem pedido nos últimos 90 dias | 14 dias |  |
| 32 | Ramo de atividade E-COMMERCE com pedido em 45d | Clientes do ramo de atividade 102 (E-commerce) com pedido nos últimos 45 dias | 14 dias |  |
| 33 | Ramo de atividade E-COMMERCE com pedido acima de 45d | Clientes do ramo de atividade 102 (E-commerce) sem pedido nos últimos 45 dias | 7 dias |  |
| 34 | Ramo de atividade PRODUTOR RURAL com pedido em 90d | Clientes do ramo de atividade 103 (Produtor Rural) com pedido nos últimos 90 dias | 28 dias |  |
| 35 | Ramo de atividade PRODUTOR RURAL com pedido acima de 90d | Clientes do ramo de atividade 103 (Produtor Rural) sem pedido nos últimos 90 dias | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(televendas): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 183

`referencias/regra_183.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores de IDs 522, 353, 519, 520 e 523). Primeiro bloqueia inadimplentes, depois define frequências específicas para prospects, clientes ativos com base no histórico, compras recentes e inativos. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Freq. de 21d para prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 21 dias |  |
| 3 | Freq. do histórico para Alta frequência de compra | Clientes ativos para o próprio vendedor e com frequência histórica de compra menor que 30 dias | Frequência do histórico, entre 5 e 30 dias |  |
| 4 | Freq. de 14d para Compra regularmente Sem pedido em 30d | Clientes ativos para o próprio vendedor e com frequência histórica de compra maior que 30 dias | 14 dias |  |
| 5 | Freq. de 14d para Compra regularmente Com pedido em 30d | Clientes ativos para o próprio vendedor, com frequência histórica de compra maior que 30 dias e que compraram do próprio vendedor nos últimos 30 dias | 14 dias | Os blocos 4 e 5 possuem a mesma ação de 14 dias, sendo que o bloco 5 exige adicionalmente um pedido nos últimos 30 dias. |
| 6 | Freq. de 21 para inativos | Clientes em ciclo de vida inativo com a empresa | 21 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 184

`referencias/regra_184.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times: televendas (exceto IDs específicos) e São Paulo (vendedores específicos). O time televendas tem regras baseadas na recência de compra e histórico, enquanto o time São Paulo baseia-se na frequência histórica de compra com preferência para segundas-feiras e regras fixas. Há um bloco final sem filtro para ambos os times. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Garantir recorrência de compra | Clientes do time televendas com compra única com a empresa e última compra no mês atual | 5 dias |  |
| 2 | Alta frequência de compra | Clientes do time televendas com última compra entre 1 e 7 dias atrás | Frequência do histórico, entre 1 e 5 dias; preferência na segunda e na terça-feira, demais dias não atender |  |
| 3 | Manter regularidade de compra | Clientes do time televendas com última compra entre 7 e 14 dias atrás | Frequência do histórico, entre 7 e 12 dias |  |
| 4 | Estimular compra dentro do mês | Clientes do time televendas com última compra entre 14 e 30 dias atrás | Frequência do histórico, entre 14 e 28 dias |  |
| 5 | Gerar relacionamento e estimular compra | Clientes do time televendas com última compra entre 31 e 90 dias atrás | 14 dias |  |
| 6 | Resgate de clientes inativos | Clientes do time televendas com última compra entre 91 e 180 dias atrás | 14 dias |  |
| 7 | Requalificar perfil e ativar cliente | Clientes do time televendas sem compra nos últimos 360 dias | 21 dias |  |
| 8 | Clientes com freq. semanal (Time São Paulo) | Clientes do time São Paulo com frequência histórica de compra de 7 dias | 7 dias; preferência prioritária na segunda-feira, demais dias não atender; fixo |  |
| 9 | Clientes com freq. quinzenal (Time São Paulo) | Clientes do time São Paulo com frequência histórica de compra de 14 dias | 14 dias; preferência prioritária na segunda-feira, demais dias não atender; fixo |  |
| 10 | Clientes com freq. mensal (Time São Paulo) | Clientes do time São Paulo com frequência histórica de compra de 28 dias | 28 dias; preferência prioritária na segunda-feira, demais dias não atender; fixo |  |
| 11 | Clientes com freq. bimestral (Time São Paulo) | Clientes do time São Paulo com frequência histórica de compra de 56 dias | 56 dias; preferência prioritária na segunda-feira, demais dias não atender; fixo |  |
| 12 | Clientes com freq. trimestral (Time São Paulo) | Clientes do time São Paulo com frequência histórica de compra de 84 dias | 84 dias; preferência prioritária na segunda-feira, demais dias não atender; fixo |  |
| 13 | Clientes que não se enquadraram nas demais regras | Todos os clientes dos times televendas e São Paulo que sobraram dos blocos anteriores | 30 dias | Bloco sem filtro: funciona como regra final para ambas as fontes. |

**Pontos de atenção**

- O bloco 13 é aplicado para ambos os times, cobrindo eventuais clientes que não se encaixaram nas regras anteriores da ficha.

## Regra 185

`referencias/regra_185.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Pessoa física e empresas baixadas na Receita não são agendadas; prospects e inativos recebem frequência de 14 dias, e ativos recebem frequência de 7 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Pessoa Física | Clientes pessoa física (CPF) | Não agendar |  |
| 2 | Não agendar baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 3 | Freq. de 14d para Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 4 | Freq. de 7d para Ativos | Clientes em ciclo de vida ativo com a empresa (já compraram) | 7 dias |  |
| 5 | Freq. de 14 dias para Inativos | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 186

`referencias/regra_186.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de televendas (vendedores do tipo televendas ativados). O sistema avalia os blocos em ordem: bloqueia o agendamento de quem comprou recentemente ou tem rota futura, define frequências para reativação e clientes em diferentes faixas de recência de compra, e aplica uma regra final para os demais. O cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes que compraram com o televendas em 7d. | Clientes com venda do próprio vendedor nos últimos 7 dias | Não agendar |  |
| 2 | Não agendar clientes que tem rota em 7 dias à frente. | Clientes com data de rota (visita presencial programada) nos próximos 7 dias | Não agendar |  |
| 3 | Ative este cliente! (Nunca tirou pedido) | Clientes sem nenhuma venda registrada com a empresa (nunca comprou) | 14 dias |  |
| 4 | Ative este cliente! | Clientes com venda no ano passado e última compra com o grupo entre 180 e 360 dias atrás | 14 dias |  |
| 5 | Restabeleça relacionamento com este cliente que foi ativado! | Clientes com venda da empresa nos últimos 14 dias e entre 181 e 360 dias atrás, mas sem venda entre 15 e 180 dias atrás | 14 dias |  |
| 6 | Mantenha a regularidade de compra do cliente que teve pedido detectado nos últimos 30d e foi visitado na semana anterior! | Clientes com rota anterior aos últimos 7 dias, visitados na semana anterior e com venda da empresa entre 7 e 30 dias atrás | 7 dias |  |
| 7 | Garanta regularidade de compra e relacionamento com este cliente! Seu último pedido foi entre 30d e 60d atrás. | Clientes com rota anterior aos últimos 7 dias, visitados na semana anterior e com venda da empresa entre 31 e 60 dias atrás | 7 dias |  |
| 8 | Cliente caminhando para INATIVIDADE! Seu último pedido foi entre 60d e 90d atrás. | Clientes com última compra (global) entre 61 e 90 dias atrás | 7 dias |  |
| 9 | Resgaste este cliente! Seu último pedido foi entre 90d e 180d atrás. | Clientes com última compra (global) entre 91 e 180 dias atrás | 7 dias |  |
| 10 | Atendimento ao cliente que não se enquadrou nas demais regras. | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | 28 dias | Bloco sem filtro: funciona como regra final. |

## Regra 187

`referencias/regra_187.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Bloqueia o agendamento de clientes baixados na Receita, filiais, inadimplentes, recém-cadastrados ou com compras recentes; os demais recebem frequência de atendimento baseada no tempo desde a última compra. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 3 | Não agendar Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Não agendar clientes recém-cadastrados em 60d | Clientes cadastrados no ERP há pelo menos 60 dias | Não agendar |  |
| 5 | Não agendar clientes com compras em 60d | Clientes com compra nos últimos 60 dias, com qualquer vendedor da empresa | Não agendar |  |
| 6 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 7 | Inativos Recentes | Clientes com compra nos últimos 90 dias que não entraram nos blocos anteriores; na prática, último pedido entre 60 e 90 dias atrás | 7 dias | Considera compras com vendedores do mesmo grupo do dono da carteira. |
| 8 | Inativos Médio | Clientes com compra nos últimos 120 dias que não entraram nos blocos anteriores; na prática, entre 90 e 120 dias sem comprar | 7 dias | Considera compras com vendedores do mesmo grupo do dono da carteira. |
| 9 | Inativos Antigos | Clientes com compra nos últimos 180 dias que não entraram nos blocos anteriores; na prática, entre 120 e 180 dias sem comprar | 14 dias | Considera compras com vendedores do mesmo grupo do dono da carteira. |
| 10 | Requalificação de Inativos | Clientes com compra nos últimos 360 dias que não entraram nos blocos anteriores; na prática, entre 180 e 360 dias sem comprar | 21 dias | Considera compras com vendedores do mesmo grupo do dono da carteira. |
| 11 | Requalificar o cliente do zero | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem compra há mais de 360 dias | 28 dias | Bloco sem filtro: funciona como regra final. |

## Regra 188

`referencias/regra_188.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Primeiro bloqueia inadimplentes, filiais e clientes baixados na Receita; depois define a frequência para novos clientes, ativos com base no histórico e clientes sem comprar há algum tempo. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar clientes filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 3 | Não agendar Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 4 | Pré-qualificado (Novos clientes) | Clientes sem nenhuma venda registrada com o próprio vendedor | 21 dias |  |
| 5 | Cliente com compra regular | Clientes com pedido nos últimos 30 dias com vendedor do mesmo grupo | Frequência do histórico, entre 7 e 30 dias |  |
| 6 | Estimule a regularidade | Clientes com última compra fora do período entre 31 e 45 dias atrás | 14 dias |  |
| 7 | Cliente deixando de comprar | Clientes com última compra fora do período entre 46 e 60 dias atrás | 7 dias |  |
| 8 | Resgate de cliente | Todos os clientes restantes que não se enquadraram nos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Os blocos 6 e utilizam filtros do tipo 'fora da recência' (negativação), o que pode gerar comportamentos complexos dependendo da ordem dos blocos anteriores. Vale revisar a lógica pretendida para esses intervalos.

## Regra 189

`referencias/regra_189.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Divide os clientes em blocos avaliados em ordem sequencial com base em vendas no ano atual, ticket médio, histórico de compras e recência de pedidos.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Base de valor alto | Clientes sem venda de qualquer vendedor da empresa no ano atual e com ticket médio acima de R$ 4999 | 7 dias, fixo, preferência na segunda e na sexta | Parametrização fixa com restrição rígida de preferência de dias. |
| 2 | Base de valor médio | Clientes sem venda de qualquer vendedor da empresa no ano atual e com ticket médio abaixo de R$ 4999 | 7 dias, fixo, preferência na terça e na sexta | Parametrização fixa com restrição rígida de preferência de dias. |
| 3 | Última compra em 2024 | Clientes sem venda de qualquer vendedor da empresa no ano atual e com venda de qualquer vendedor da empresa no ano anterior | 7 dias, preferência na quarta e na quinta |  |
| 4 | Ativação de um novo cliente em potencial | Clientes sem nenhuma venda registrada com o próprio vendedor (nunca comprou) | 7 dias |  |
| 5 | Boas vindas a um novo cliente ativado | Clientes que compram uma única vez com o próprio vendedor | 7 dias |  |
| 6 | Clientes com bom histórico de compra | Clientes com frequência histórica de compra entre 0 e 14 dias | Frequência do histórico, com mínimo de 4 e máximo de 6 dias |  |
| 7 | Atenção!!! Cliente com RISCO de ficar inativo | Clientes cuja última compra com o próprio vendedor dono da carteira não ocorreu entre 25 e 30 dias atrás | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(televendas): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 190

`referencias/regra_190.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de Televendas (todos os vendedores da empresa ativados). A frequência de atendimento é definida por ciclos de vida, adimplência, recência de compra, curva ABC de faturamento e vendas no mês atual. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Prospect | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 21 dias |  |
| 2 | Boas-vindas primeiro pedido | Clientes com uma única compra com a empresa e cadastrados no ERP há pelo menos 30 dias | 10 dias |  |
| 3 | Risco de inatividade | Clientes adimplentes com última compra entre 61 e 90 dias atrás | 7 dias |  |
| 4 | Inativos | Clientes adimplentes em ciclo de vida inativo com a empresa | 14 dias |  |
| 5 | Curva A com compra no mês | Clientes da curva A de faturamento com a empresa e com venda de algum vendedor do grupo no mês atual | Frequência do histórico, no máximo de 30 dias |  |
| 6 | Curva A sem compra no mês | Clientes da curva A de faturamento com a empresa que não entraram no bloco anterior | 7 dias |  |
| 7 | Curva B com compra no mês | Clientes da curva B de faturamento com a empresa e com venda de algum vendedor do grupo no mês atual | Frequência do histórico, no máximo de 30 dias |  |
| 8 | Curva B sem compra no mês | Clientes da curva B de faturamento com a empresa que não entraram nos blocos anteriores | 14 dias |  |
| 9 | Curva C com compra no mês | Clientes com venda de algum vendedor do grupo no mês atual que não entraram nos blocos anteriores | Frequência do histórico, no máximo de 30 dias |  |
| 10 | Curva C sem compra no mês | Todos os clientes restantes da fonte que não se enquadraram em nenhum bloco anterior | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 191

`referencias/regra_191.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes baixados na Receita e inadimplentes não são agendados; os demais recebem frequência de ligação fixa ou baseada no histórico, conforme o tempo desde o último pedido. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa | 21 dias |  |
| 4 | Pós-venda | Clientes com pedido nos últimos 7 dias | 21 dias |  |
| 5 | Alta regularidade | Clientes com pedido nos últimos 30 dias que não entraram nos blocos anteriores; na prática, entre 7 e 30 dias atrás | Frequência do histórico mais 3 dias, entre 14 e 30 dias |  |
| 6 | Estimular regularidade | Clientes com pedido nos últimos 45 dias que não entraram nos blocos anteriores; na prática, entre 30 e 45 dias atrás | 7 dias |  |
| 7 | Risco de inatividade | Clientes com pedido nos últimos 60 dias que não entraram nos blocos anteriores; na prática, entre 45 e 60 dias atrás | 7 dias |  |
| 8 | Clientes Inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 60 dias | 7 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Os blocos 6, 7 e 8 possuem exatamente a mesma ação (7 dias), o que significa que qualquer cliente que comprou nos últimos 45 dias, nos últimos 60 dias ou há mais de 60 dias receberá a mesma frequência de atendimento.

## Regra 192

`referencias/regra_192.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes baixados na Receita Federal não são agendados; prospects recebem frequência fixa; e os demais clientes têm a frequência definida pelo tempo desde a última compra. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 3 | Clientes Ativos | Clientes com compra nos últimos 15 dias | 7 dias |  |
| 4 | Risco de Inatividade | Clientes com compra nos últimos 30 dias que não entraram nos blocos anteriores; na prática, último pedido entre 15 e 30 dias atrás | 3 dias |  |
| 5 | Inativos 30d | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 30 dias | 5 dias | Bloco sem filtro: funciona como regra final. |

## Regra 193

`referencias/regra_193.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas e de carteiras específicas baseadas no ramo de atividade. Primeiro bloqueia filiais, empresas baixadas na Receita e clientes com rota futura nos próximos 21 dias e compra nos últimos 60 dias. Depois define frequências de 14 ou 21 dias para ramos específicos com compra recente, e aplica frequência de 7 dias para quem sobrou do time. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes filiais | Clientes que possuem cadastro do tipo filial | Não agendar |  |
| 2 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 3 | Não agendar clientes fora da semana de cobertura | Clientes com data de rota futura do próprio vendedor nos próximos 21 dias e com pedido nos últimos 60 dias (com qualquer vendedor da empresa) | Não agendar |  |
| 4 | Freq. de 14d para ramos de atividade específicos, com venda em 60d | Clientes da carteira ramos_freq_14 (ramos 30, 583, 33, 26, 42, 34 e mais 26, totalizando 32 ramos) com pedido nos últimos 60 dias com qualquer vendedor da empresa | 14 dias |  |
| 5 | Freq. de 21d para ramos de atividade específicos, com venda em 60d | Clientes da carteira ramos_freq_21 (demais ramos de atividade, excluindo os 32 ramos anteriores) com pedido nos últimos 60 dias com qualquer vendedor da empresa | 21 dias |  |
| 6 | Freq. de 7d para todos os ramos de atividade, sem venda em 60d | Todos os clientes do time televendas que sobraram dos blocos anteriores | 7 dias | Bloco sem filtro: funciona como regra final para a fonte do time. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte carteira(ramos_freq_14): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte carteira(ramos_freq_21): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.

## Regra 194

`referencias/regra_194.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes baixados na Receita Federal não são agendados; os demais recebem uma frequência de ligação conforme o tempo desde o último pedido. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Baixados na Receita Federal | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Prospects | Clientes em ciclo de vida prospect com a empresa (nunca tiraram pedido) | 7 dias |  |
| 3 | Ativo | Clientes com pedido nos últimos 60 dias, com qualquer vendedor da empresa | 14 dias |  |
| 4 | Risco de inatividade | Clientes com pedido nos últimos 90 dias que não entraram em Ativo; na prática, último pedido entre 60 e 90 dias atrás | 7 dias | Aqui só contam pedidos com vendedores do mesmo grupo do dono da carteira (o bloco Ativo considera qualquer vendedor da empresa). |
| 5 | Inativo | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 90 dias | 28 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- O bloco Ativo usa compras com qualquer vendedor da empresa (global), mas o Risco de inatividade usa só vendedores do mesmo grupo. Um cliente que comprou há 70 dias apenas com um vendedor de outro grupo cai em Inativo (28 dias). Confirmar se é intencional.

## Regra 195

`referencias/regra_195.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Primeiro exclui da agenda pessoas físicas, empresas baixadas na Receita e quem comprou nos últimos 7 dias; os demais recebem frequências específicas de atendimento com base no histórico de compras, prospects e clientes com uma única compra. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar PF | Clientes pessoa física (CPF) | Não agendar |  |
| 2 | Não agendar Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 3 | Não agendar clientes com pedido em 7d | Clientes com pedido nos últimos 7 dias | Não agendar |  |
| 4 | Manter contato com cliente que comprou no mês | Clientes com pedido entre 7 e 30 dias atrás | 21 dias |  |
| 5 | Ativação de novos | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 6 | Fazer relacionamento com o cliente | Clientes que realizaram uma única compra com a empresa | 21 dias |  |
| 7 | Manter a regularidade de compra | Clientes com pedido entre 31 e 60 dias atrás com o próprio vendedor dono da carteira | 21 dias |  |
| 8 | Atuar para que o cliente não fique inativo | Clientes com pedido entre 61 e 90 dias atrás com o próprio vendedor dono da carteira | 7 dias |  |
| 9 | Resgatar o cliente inativo | Todos os clientes do time que sobraram dos blocos anteriores | 14 dias | Bloco sem filtro: funciona como regra final. |

## Regra 196

`referencias/regra_196.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Inadimplentes e clientes de Fortaleza com compra recente não são agendados; prospects, ativos e inativos recebem frequências específicas de atendimento. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar Fortaleza com compra recente | Clientes da cidade de FORTALEZA com compra nos últimos 60 dias | Não agendar |  |
| 3 | Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 40 dias |  |
| 4 | Ativos adimplentes | Clientes ativos segundo o histórico de compras com o próprio vendedor | 15 dias |  |
| 5 | Inativos adimplentes | Todos os clientes do time que sobraram dos blocos anteriores | 20 dias | Bloco sem filtro: funciona como regra final. |

## Regra 197

`referencias/regra_197.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Bloqueia o agendamento de clientes baixados na Receita, inadimplentes e com rota na semana; os demais recebem frequência de atendimento conforme o histórico de pedidos, com uma regra final para todos os restantes. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar clientes com data da rota na semana | Clientes com data de rota (visita presencial programada) na semana atual | Não agendar | Evita o agendamento de ligações para clientes que receberão visita presencial na mesma semana. |
| 4 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa (nunca comprou) | 14 dias |  |
| 5 | Clientes Ativos | Clientes com pedido nos últimos 60 dias, com qualquer vendedor da empresa | 7 dias |  |
| 6 | Risco de Inatividade | Clientes com pedido nos últimos 90 dias que não entraram em Ativo; na prática, último pedido entre 60 e 90 dias atrás | 7 dias | Considera pedidos globais com qualquer vendedor da empresa. |
| 7 | Inativos + 90d | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 90 dias | 7 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Os blocos 5, 6 e 7 possuem exatamente a mesma ação (frequência a cada 7 dias), o que torna a separação por recência redundante para fins de frequência, embora segmente os clientes por tempo sem compra.

## Regra 198

`referencias/regra_198.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Define frequências de atendimento específicas para prospects, novos clientes com apenas um pedido, clientes com alta frequência recente de compra e clientes ativos, aplicando uma frequência padrão de 21 dias para os demais. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 25d para Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 25 dias |  |
| 2 | Freq. de 14d para Boas vindas | Clientes com apenas uma compra com a empresa, sem venda com o próprio vendedor dono da carteira nos últimos 30 dias | 14 dias |  |
| 3 | Freq. do histórico para Alta frequência | Clientes com compra (positivação) com o próprio vendedor dono da carteira nos últimos 30 dias | Frequência do histórico, entre 7 e 30 dias |  |
| 4 | Freq. de 14d para Ativos | Clientes em ciclo de vida ativo com a empresa (já fizeram alguma compra) que não caíram nos blocos anteriores | 14 dias |  |
| 5 | Freq. de 21d para Inativos | Todos os clientes do time que sobraram dos blocos anteriores | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 199

`referencias/regra_199.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas). Primeiro bloqueia inadimplentes e clientes bloqueados para atendimento; em seguida, define a frequência de ligação com base no ciclo de vida e histórico de compras (prospects, única compra recente, ativos frequentes, recência global e inativos). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 3 | Prospect: Cliente potencial | Clientes em ciclo de vida prospect com a empresa (nunca comprou) | 30 dias |  |
| 4 | Ativado: fez um pedido e ainda não comprou mais | Clientes com uma única compra com a empresa e última compra com vendedor do mesmo grupo nos últimos 40 dias | 30 dias |  |
| 5 | Ativo: compra regularmente | Clientes ativos para o próprio vendedor e com frequência histórica de compra menor que 21 dias | 90 dias |  |
| 6 | Ativo: estimular a regularidade de compra | Clientes com última compra global (com qualquer vendedor da empresa) entre 31 e 59 dias atrás | 30 dias |  |
| 7 | Em ruptura: risco de ficar inativo | Clientes com última compra global entre 60 e 89 dias atrás | 21 dias |  |
| 8 | Inativo: reativar cliente sem compra | Clientes sem compra global nos últimos 90 dias | 45 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 200

`referencias/regra_200.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas, exceto o vendedor de ID 1. Define frequências de atendimento com base no ciclo de vida (prospects e clientes com uma única compra), no histórico de visitas e no tempo desde a última compra (compras com o vendedor ou com o grupo). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 21d para Prospect | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 21 dias |  |
| 2 | Freq. de 10d para única compra | Clientes que fizeram uma única compra com a empresa | 10 dias |  |
| 3 | Freq. do histórico para alta frequência | Clientes com pedido nos últimos 30 dias com algum vendedor do mesmo grupo do dono da carteira | Frequência do histórico mais 5 dias, com limite máximo de 30 dias |  |
| 4 | Freq. de 14d para compra regular | Clientes com pedido nos últimos 30 dias com o próprio vendedor dono da carteira | 14 dias |  |
| 5 | Freq. de 7d para estimular regularidade | Clientes com último pedido entre 31 e 60 dias atrás com algum vendedor do mesmo grupo | 7 dias |  |
| 6 | Freq. de 7d para risco de inatividade | Clientes com último pedido entre 61 e 90 dias atrás com algum vendedor do mesmo grupo | 7 dias |  |
| 7 | Freq. de 21d para resgate de inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 90 dias | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 201

`referencias/regra_201.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia primeiro clientes baixados, inadimplentes, bloqueados e filiais, e depois aplica regras de frequência baseadas no ciclo de vida e histórico de compras. Clientes que não se encaixam em nenhuma regra anterior caem no bloco final e não são agendados. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes Baixados na Receita Federal | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Clientes Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Clientes Bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 4 | Não agendar Filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 5 | Prospect | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram) | 7 dias |  |
| 6 | Inativo | Clientes sem compra nos últimos 90 dias com qualquer vendedor do mesmo grupo | 28 dias | Colocado antes dos ativos para capturar os inativos devido à lógica de precedência. |
| 7 | Ativado | Clientes cadastrados no ERP há pelo menos 60 dias e que fizeram uma única compra com o próprio vendedor | 30 dias |  |
| 8 | Ativo: Alta frequência de compra | Clientes com compra nos últimos 30 dias e frequência histórica de compra abaixo de 30 dias | 30 dias |  |
| 9 | Ativo: Compra regularmente | Clientes com compra nos últimos 30 dias e frequência histórica de compra abaixo de 90 dias | 30 dias |  |
| 10 | Ativo: Estimular a regularidade de compra | Clientes com compra entre 30 e 60 dias atrás | 10 dias |  |
| 11 | Em ruptura | Clientes com compra entre 61 e 90 dias atrás | 14 dias |  |
| 12 | Regra final | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final. |

## Regra 202

`referencias/regra_202.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Define a frequência de atendimento com base na recência de compras e no histórico do cliente. Os blocos são avaliados em ordem e o cliente fica no primeiro em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 7d para clientes sem compra em 60d | Clientes sem pedido nos últimos 60 dias (considerando vendedores do mesmo grupo) | 7 dias |  |
| 2 | Ative um novo cliente na sua carteira | Clientes sem nenhuma venda registrada com o próprio vendedor (nunca comprou com ele) | 7 dias |  |
| 3 | Estabeleça relacionamento com seu novo cliente | Clientes com uma única compra com o próprio vendedor e sem pedido nos últimos 7 dias (com vendedores do mesmo grupo) | 7 dias |  |
| 4 | Cliente com alta frequência de compra | Clientes com pedido nos últimos 30 dias (com vendedores do mesmo grupo) | Frequência do histórico, com limite máximo de 30 dias |  |
| 5 | Estimule a regularidade de compra | Clientes cuja última compra (com o grupo) não ocorreu entre 31 e 60 dias atrás | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 203

`referencias/regra_203.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia o agendamento de clientes baixados na Receita, filiais (exceto o ID 36979), inadimplentes, prospects e quem não compra há mais de 95 dias. Os demais recebem frequência de atendimento baseada no histórico de compras. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar filiais | Clientes que são filiais e cujo ID do cliente principal é diferente de 36979 | Não agendar | A filial de ID principal 36979 não é afetada por esta regra. |
| 3 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Não agendar prospects | Clientes sem nenhuma venda registrada (nunca comprou) | Não agendar |  |
| 5 | Não agendar sem compra em 95 dias | Clientes sem compra nos últimos 95 dias | Não agendar |  |
| 6 | Clientes com uma compra | Clientes que comprou uma única vez com a empresa | 28 dias |  |
| 7 | Freq. hist. entre 0 e 7 dias | Clientes com frequência histórica de compra entre 0 e 7 dias | 6 dias |  |
| 8 | Freq. hist. entre 8 e 14 dias | Clientes com frequência histórica de compra entre 8 e 14 dias | 9 dias |  |
| 9 | Freq. hist. entre 15 e 21 dias | Clientes com frequência histórica de compra entre 15 e 21 dias | 16 dias |  |
| 10 | Freq. hist. entre 22 e 28 dias | Clientes com frequência histórica de compra entre 22 e 28 dias | 23 dias |  |
| 11 | Freq. hist. entre 29 e 38 dias | Clientes com frequência histórica de compra entre 29 e 38 dias | 29 dias |  |
| 12 | Freq. hist. entre 39 e 60 dias | Clientes com frequência histórica de compra entre 39 e 60 dias | 35 dias |  |
| 13 | Regra final | Todos os clientes restantes da fonte que não se enquadraram nos blocos anteriores; na prática, frequência histórica entre 61 e 95 dias | 55 dias | Bloco sem filtro: funciona como regra final para os ativos restantes dentro do limite de 95 dias. |

## Regra 204

`referencias/regra_204.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema primeiro bloqueia o agendamento para quem comprou nos últimos 7 dias, depois define frequências baseadas no tempo desde a última compra (compras com vendedores do mesmo grupo), e finaliza com uma frequência padrão para quem sobra. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes com compra em 7d | Clientes com venda de algum vendedor do grupo nos últimos 7 dias | Não agendar |  |
| 2 | Manter a Regularidade de Compra | Clientes com pedido nos últimos 30 dias | 14 dias |  |
| 3 | Garantir a Positivação da Carteira | Clientes com pedido entre 31 e 60 dias atrás | 14 dias |  |
| 4 | Cliente com Risco de Inatividade | Clientes com pedido entre 61 e 90 dias atrás | 7 dias |  |
| 5 | Clientes Inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 90 dias | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 205

`referencias/regra_205.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de televendas e carteiras de rotas específicas. Define frequências para prospects e inativos do televendas, e regras semanais com preferência de dias específicos para clientes ativos em diferentes carteiras de rotas. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 28d para Prospects | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 28 dias | Aplica-se a clientes do time televendas. |
| 2 | Freq. de 14d para Inativos | Clientes sem compra nos últimos 90 dias com algum vendedor do mesmo grupo do dono da carteira | 14 dias | Aplica-se a clientes do time televendas que não entraram no bloco anterior. |
| 3 | Cliente ativo na rota de hoje (Quinta ou Segunda) | Todos os clientes restantes da carteira rota_quinta_segunda | 7 dias (semanal), preferência na quinta e na segunda | Bloco sem filtro de cliente para esta fonte; demais dias têm valor 0 (não atender). |
| 4 | Cliente ativo na rota de hoje (Terça) | Todos os clientes restantes da carteira rota_terca | 7 dias (semanal), preferência na terça | Bloco sem filtro de cliente para esta fonte; demais dias têm valor 0 (não atender). |
| 5 | Cliente ativo na rota de hoje (Quarta) | Todos os clientes restantes da carteira rota_quarta | 7 dias (semanal), preferência na quarta | Bloco sem filtro de cliente para esta fonte; demais dias têm valor 0 (não atender). |
| 6 | Cliente ativo na rota de hoje (Sexta) | Todos os clientes restantes da carteira rota_sexta | 7 dias (semanal), preferência na sexta | Bloco sem filtro de cliente para esta fonte; demais dias têm valor 0 (não atender). |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(televendas): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- A carteira rota_quinta_segunda é usada no bloco 3, mas não é definida neste arquivo.
- A carteira rota_terca é usada no bloco 4, mas não é definida neste arquivo.
- A carteira rota_quarta é usada no bloco 5, mas não é definida neste arquivo.
- A carteira rota_sexta é usada no bloco 6, mas não é definida neste arquivo.

## Regra 206

`referencias/regra_206.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para os times ativo_inativo e prospeccao, além de carteiras específicas. Inicialmente remove filiais, inadimplentes e prospects do time ativo_inativo da agenda. Em seguida, define frequências de atendimento baseadas no ramo de atividade e na carteira ou time do cliente.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar filiais | Clientes que são filiais | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar Prospects | Clientes em ciclo de vida prospect com a empresa | Não agendar |  |
| 4 | Posto de molas, empresa ônibus, auto peças e mineração (0_90) | Clientes com ramo de atividade 1, 2, 4 ou 12 da carteira 0_90 | 7 dias |  |
| 5 | Transportadora (0_90) | Clientes com ramo de atividade 3 da carteira 0_90 | 15 dias |  |
| 6 | Outros segmentos (0_90) | Demais clientes da carteira 0_90 que não se enquadraram nos blocos anteriores | 28 dias | Bloco sem filtro: funciona como regra final para a carteira. |
| 7 | Posto de molas, empresa ônibus, auto peças e mineração (90_180) | Clientes com ramo de atividade 1, 2, 4 ou 12 da carteira 90_180 | 7 dias |  |
| 8 | Transportadora (90_180) | Clientes com ramo de atividade 3 da carteira 90_180 | 15 dias |  |
| 9 | Outros segmentos (90_180) | Demais clientes da carteira 90_180 que não se enquadraram nos blocos anteriores | 28 dias | Bloco sem filtro: funciona como regra final para a carteira. |
| 10 | Posto de molas, empresa ônibus, auto peças e mineração (prospecção) | Clientes com ramo de atividade 1, 2, 4 ou 12 do time prospecção | 7 dias |  |
| 11 | Transportadora (prospecção) | Clientes com ramo de atividade 3 do time prospecção | 15 dias |  |
| 12 | Outros segmentos (prospecção) | Demais clientes do time prospecção que não se enquadraram nos blocos anteriores | 28 dias | Bloco sem filtro: funciona como regra final para a fonte. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(ativo_inativo, prospeccao) e time(ativo_inativo): clientes que não se enquadram em nenhum bloco mantêm a parametrização anterior.
- Os nomes dos blocos 4 ao 9 citam períodos em dias (90d, 180d) que não aparecem nos filtros técnicos do GOBR.
- As carteiras 0_90 e 90_180 são usadas nos blocos mas não estão definidas neste arquivo, podendo estar em outro arquivo de regras.

## Regra 207

`referencias/regra_207.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes com CPF não são agendados; os demais recebem frequências variadas com base no tempo desde a última compra e histórico, avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar CPF | Clientes pessoa física (CPF) | Não agendar |  |
| 2 | Clientes sem pedido com a empresa | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |
| 3 | Clientes ativos com alta regularidade | Clientes com pedido nos últimos 14 dias | Frequência do histórico mais 7 dias, com limite máximo de 14 dias |  |
| 4 | Manter a regularidade | Clientes com pedido entre 14 e 30 dias atrás | 14 dias |  |
| 5 | Sem pedido entre 30 a 45d | Clientes com pedido entre 30 e 45 dias atrás | 21 dias |  |
| 6 | Risco de ficar inativo | Clientes com pedido entre 45 e 90 dias atrás | 14 dias |  |
| 7 | Resgate de inativos | Clientes sem pedido nos últimos 90 dias | 28 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 208

`referencias/regra_208.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia primeiro os clientes que não devem ser agendados (baixados na Receita, inadimplentes, bloqueados e filiais), depois define a frequência para novos, únicos e ativos com base no histórico de compras e recência, e os clientes restantes não são agendados. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 4 | Não agendar filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 5 | Ativação de novos | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 7 dias |  |
| 6 | Fazer relacionamento com o cliente | Clientes com uma única compra com o próprio vendedor | 14 dias |  |
| 7 | Manter contato com o cliente que comprou no mês | Clientes com compra no mês atual e frequência histórica de compra entre 90 e 120 dias | 14 dias |  |
| 8 | Manter a regularidade de compra | Clientes com compra nos últimos 30 dias | 14 dias |  |
| 9 | Atuar para o cliente não ficar inativo | Clientes com compra nos últimos 89 dias que não entraram nos blocos anteriores; na prática, último pedido entre 30 e 89 dias atrás | 7 dias |  |
| 10 | Resgatar cliente inativo | Clientes com compra nos últimos 120 dias que não entraram nos blocos anteriores; na prática, último pedido entre 89 e 120 dias atrás | 3 dias |  |
| 11 | Não mapeados nas regras | Todos os clientes do time que não se enquadraram em nenhum bloco anterior; na prática, sem compra há mais de 120 dias | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Clientes sem compra há mais de 120 dias caem na regra final e não são agendados.

## Regra 209

`referencias/regra_209.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema bloqueia inadimplentes, filiais e clientes sem compra com o vendedor há mais de 90 dias, e define frequências para novos clientes (prospects) e clientes com compras recentes. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 3 | Não agendar fora de recência | Clientes cuja última compra com o próprio vendedor dono da carteira não ocorreu nos últimos 90 dias | Não agendar |  |
| 4 | Prospects | Clientes em ciclo de vida prospect (nunca compraram) com o próprio vendedor | 7 dias |  |
| 5 | Cliente compra com regularidade | Clientes com frequência histórica de compra entre 0 e 30 dias e cuja última compra com o próprio vendedor ocorreu nos últimos 30 dias | 7 dias |  |
| 6 | Cliente precisa de acompanhamento | Clientes cuja última compra com o próprio vendedor não ocorreu entre 31 e 90 dias atrás | 17 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 210

`referencias/regra_210.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Primeiro bloqueia filiais, inadimplentes e clientes bloqueados para atendimento; depois define frequência de 30 dias para os demais grupos (compra única, esquecidos, inativos há mais de 1 ano e ativos fidelizados). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Filiais | Clientes cujo cadastro é uma filial | Não agendar |  |
| 2 | Não agendar Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Não agendar Bloqueados | Clientes bloqueados para atendimento | Não agendar |  |
| 4 | Freq. de 30d para com uma única compra | Clientes que fizeram uma única compra com o próprio vendedor | 30 dias |  |
| 5 | Freq. de 30d para Esquecido | Clientes com última compra entre 181 e 365 dias atrás | 30 dias |  |
| 6 | Freq. de 30d para Inativo | Clientes sem compra nos últimos 365 dias | 30 dias |  |
| 7 | Freq. de 30d para Ativo fidelizado | Todos os clientes do time que sobraram dos blocos anteriores | 30 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Todos os blocos de agendamento (blocos 4 a 7) possuem exatamente a mesma frequência de 30 dias, fazendo com que a segmentação anterior sirva apenas para fins de organização, já que a ação prática final é idêntica para todos eles.

## Regra 211

`referencias/regra_211.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de ativação (vendedores de IDs 965 e 945). Os clientes que compraram nos últimos 30 dias recebem frequência de 21 dias, e os demais recebem frequência de 15 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Cliente com pedido nos últimos 30 dias | Clientes com pedido nos últimos 30 dias, com vendedor do mesmo grupo | 21 dias |  |
| 2 | Cliente sem pedido nos últimos 30 dias | Todos os clientes do time que sobraram do bloco anterior; na prática, sem pedido nos últimos 30 dias | 15 dias | Bloco sem filtro: funciona como regra final. |

## Regra 212

`referencias/regra_212.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). O sistema avalia os blocos em ordem: bloqueia o agendamento de quem tem rota nos próximos 7 dias ou comprou nos últimos 14 dias; define frequências específicas para clientes com base no histórico de pedidos e visitas; e aplica uma regra final de 7 dias para quem não se enquadrou.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar rota em 7 dias | Clientes com data de rota (visita presencial) programada nos próximos 7 dias | Não agendar |  |
| 2 | Não agendar compra recente | Clientes com última compra (positivação) com qualquer vendedor da empresa nos últimos 14 dias | Não agendar |  |
| 3 | Regularidade de compra (14 a 30 dias) | Clientes com data de rota anterior a 7 dias, visitados na semana anterior e com último pedido entre 14 e 30 dias atrás | 7 dias |  |
| 4 | Regularidade e relacionamento (31 a 60 dias) | Clientes com data de rota anterior a 7 dias, visitados na semana anterior e com último pedido entre 31 e 60 dias atrás | 20 dias |  |
| 5 | Ativação de prospects | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |
| 6 | Ativação (180 a 360 dias) | Clientes com último pedido no ano anterior e entre 180 e 360 dias atrás | 14 dias |  |
| 7 | Risco de inatividade (61 a 90 dias) | Clientes com último pedido entre 61 e 90 dias atrás | 7 dias |  |
| 8 | Resgate (91 a 180 dias) | Clientes com último pedido entre 91 e 180 dias atrás | 7 dias |  |
| 9 | Regra final | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | 7 dias | Bloco sem filtro: funciona como regra final. |

## Regra 213

`referencias/regra_213.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time televendas separada por carteiras de rotas semanais. O primeiro bloco bloqueia clientes filiais para que não sejam agendados. Os blocos seguintes segmentam as carteiras de segunda a sexta entre clientes ativos e inativos, aplicando frequência fixa e preferência para o dia correspondente. A carteira Curitiba recebe atendimento semanal sem dia fixo.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar Clientes Filiais | Clientes filiais do time time televendas | Não agendar | Avaliado primeiro para remover filiais da agenda. |
| 2 | Clientes Ativos (segunda) | Clientes ativos para o vendedor na carteira de segunda (rotas 24, 523, 524, 525, 526) | 7 dias, fixo, preferência na segunda |  |
| 3 | Clientes Inativos (segunda) | Clientes da carteira de segunda que sobraram dos blocos anteriores | 28 dias, fixo, preferência na segunda | Bloco sem filtro de cliente para a fonte. |
| 4 | Clientes Ativos (terça) | Clientes ativos para o vendedor na carteira de terça (rotas 3, 4, 17, 500, 512, 514 e mais 1) | 7 dias, fixo, preferência na terça |  |
| 5 | Clientes Inativos (terça) | Clientes da carteira de terça que sobraram dos blocos anteriores | 28 dias, fixo, preferência na terça | Bloco sem filtro de cliente para a fonte. |
| 6 | Clientes Ativos (quarta) | Clientes ativos para o vendedor na carteira de quarta (rotas 502, 530, 531) | 7 dias, fixo, preferência na quarta |  |
| 7 | Clientes Inativos (quarta) | Clientes da carteira de quarta que sobraram dos blocos anteriores | 28 dias, fixo, preferência na quarta | Bloco sem filtro de cliente para a fonte. |
| 8 | Clientes Ativos (quinta) | Clientes ativos para o vendedor na carteira de quinta (rotas 20, 501, 504, 505, 506, 508 e mais 4) | 7 dias, fixo, preferência na quinta |  |
| 9 | Clientes Inativos (quinta) | Clientes da carteira de quinta que sobraram dos blocos anteriores | 28 dias, fixo, preferência na quinta | Bloco sem filtro de cliente para a fonte. |
| 10 | Clientes Ativos (sexta) | Clientes ativos para o vendedor na carteira de sexta (rotas 5, 19, 510, 511, 521) | 7 dias, fixo, preferência na sexta |  |
| 11 | Clientes Inativos (sexta) | Clientes da carteira de sexta que sobraram dos blocos anteriores | 28 dias, fixo, preferência na sexta | Bloco sem filtro de cliente para a fonte. |
| 12 | Clientes sem dia específico | Clientes da carteira de Curitiba (rotas 10, 11) que sobraram dos blocos anteriores | 7 dias | Bloco sem filtro de cliente para a fonte. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(time televendas): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham (regras incrementais, Manual §7.6).

## Regra 214

`referencias/regra_214.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas). Primeiro bloqueia clientes inadimplentes, depois define a frequência de atendimento e preferência de dias (segunda a sábado) com base no histórico de compras do vendedor e no ramo de atividade. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Cliente sem pedido com o vendedor | Clientes que compraram uma única vez com o próprio vendedor | 14 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 3 | Ativado (Ramo 29) | Clientes que compraram uma única vez com o próprio vendedor, com última compra global nos últimos 30 dias e ramo de atividade 29 | 21 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 4 | Ativado (Outros ramos) | Clientes que compraram uma única vez com o próprio vendedor, com última compra global nos últimos 30 dias e ramo de atividade diferente de 29 | 14 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 5 | Ativo com compra regular | Clientes ativos para o vendedor com frequência histórica de compra abaixo de 14 dias | 10 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 6 | Estimular regularidade (Ramo 29) | Última compra com o próprio vendedor entre 21 e 59 dias atrás e ramo de atividade 29 | 30 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 7 | Estimular regularidade (Outros ramos) | Última compra com o próprio vendedor entre 21 e 59 dias atrás e ramo de atividade diferente de 29 | 14 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 8 | Em ruptura (Ramo 29) | Última compra com o próprio vendedor entre 60 e 89 dias atrás e ramo de atividade 29 | 14 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 9 | Em ruptura (Outros ramos) | Última compra com o próprio vendedor entre 60 e 89 dias atrás e ramo de atividade diferente de 29 | 14 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). |
| 10 | Resgate de cliente sem compra | Última compra com o próprio vendedor há mais de 90 dias | 10 dias; preferência de atendimento de segunda a sábado | Demais dias com valor 0 (não atender). Pega os clientes que não se enquadraram nos blocos anteriores devido aos filtros de recência e histórico. |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 215

`referencias/regra_215.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas. Define uma frequência de atendimento fixa de 7 dias para diferentes perfis de clientes com base no ciclo de vida e no tempo desde a última compra com o vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 7d para Primeira compra | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 7 dias |  |
| 2 | Freq. de 7d para Prospect ativado | Clientes com uma única compra com o próprio vendedor e sem compra recente com o mesmo grupo nos últimos 20 dias | 7 dias |  |
| 3 | Freq. de 7d para Compra regularmente | Clientes com pedido com o próprio vendedor nos últimos 30 dias | 7 dias |  |
| 4 | Freq. de 7d para Ativo: estimular a regularidade de compra | Clientes com pedido com o próprio vendedor entre 31 e 60 dias atrás | 7 dias |  |
| 5 | Freq. de 7d para Risco de inatividade | Clientes com pedido com o próprio vendedor entre 60 e 90 dias atrás | 7 dias |  |
| 6 | Freq. de 7d para Resgate de cliente sem compra | Clientes sem pedido com o próprio vendedor nos últimos 90 dias que não se enquadraram nos blocos anteriores | 7 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- Como todos os blocos aplicam exatamente a mesma ação de 7 dias, a divisão em múltiplos blocos com critérios complexos resulta na mesma frequência prática para qualquer cliente da carteira.

## Regra 217

`referencias/regra_217.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes com uma única compra com o próprio vendedor recebem frequência de 7 dias, e aqueles com compra recente entre 7 e 30 dias recebem frequência baseada no histórico. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Fazer relacionamento com o cliente | Clientes que fizeram uma única compra com o próprio vendedor | 7 dias |  |
| 2 | Manter a regularidade de compra | Clientes com pedido entre 7 e 30 dias atrás (com vendedor do mesmo grupo do dono da carteira) | Frequência do histórico, com mínimo de 14 e máximo de 28 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 218

`referencias/regra_218.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dividida entre o time televendas_1 (vendedores televendas ativados, exceto o ID 4504) e o time televendas_2 (vendedor ID 4504). Para o primeiro time, define frequências baseadas em recência de compra e histórico; para o segundo time, trata prospects e clientes com base no tempo desde a última compra. Os blocos são avaliados em ordem para cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 5d para clientes sem compra em 7d | Clientes do time televendas_1 sem pedido nos últimos 7 dias | 5 dias |  |
| 2 | Freq. do histórico para clientes com recência de compra entre 0 e 14d | Clientes do time televendas_1 com pedido nos últimos 14 dias que não entraram no bloco anterior; na prática, último pedido entre 7 e 14 dias atrás | Frequência do histórico, no máximo de 14 dias |  |
| 3 | Freq. de 14d para clientes sem compra em 14d | Todos os clientes restantes do time televendas_1 que não se enquadraram nos blocos anteriores; na prática, sem pedido há mais de 14 dias | 14 dias | Bloco sem filtro: funciona como regra final para a fonte televendas_1. |
| 4 | Freq. de 14d para clientes sem pedido | Clientes do time televendas_2 em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 14 dias |  |
| 5 | Freq. de 14d para clientes com compra em 30d | Clientes do time televendas_2 com pedido nos últimos 30 dias que não entraram no bloco anterior | 14 dias |  |
| 6 | Freq. de 7d para clientes sem compra em 30d | Todos os clientes restantes do time televendas_2 que não se enquadraram nos blocos anteriores; na prática, sem pedido há mais de 30 dias | 7 dias | Bloco sem filtro: funciona como regra final para a fonte televendas_2. |

## Regra 219

`referencias/regra_219.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes baixados na Receita ou com compra recente em até 25 dias não são agendados; os demais recebem frequência de ligação baseada no tempo desde a última compra com a empresa ou se são prospects do vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar baixados na Receita Federal | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar com compra em 25d | Clientes com pedido nos últimos 25 dias, com qualquer vendedor da empresa | Não agendar |  |
| 3 | Ative essa oportunidade - Cliente nunca tirou pedido com o vendedor | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 21 dias |  |
| 4 | Cliente com pedido com a empresa entre 25 e 60 dias | Clientes com pedido entre 26 e 60 dias atrás, com qualquer vendedor da empresa | 14 dias |  |
| 5 | Cliente com pedido com a empresa entre 60 e 90 dias | Clientes com pedido entre 61 e 90 dias atrás, com qualquer vendedor da empresa | 7 dias |  |
| 6 | Atenda esse cliente inativo há mais de 90 dias | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido com a empresa há mais de 90 dias | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 220

`referencias/regra_220.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para três times diferentes (carteira regional, carteira reativação e carteira direta), identificados por IDs específicos de vendedores. Cada time possui regras próprias para definir quem deve ou não ser agendado e qual a frequência de atendimento. Os blocos são avaliados em ordem dentro de cada fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar com compra nos últimos 30 dias | Clientes da carteira regional com pedido nos últimos 30 dias, com qualquer vendedor da empresa | Não agendar | Aplica-se ao time carteira regional. |
| 2 | Frequência padrão regional | Todos os clientes restantes da carteira regional que não passaram pelo bloco anterior | 7 dias | Bloco sem filtro: funciona como regra final para a carteira regional. |
| 3 | Inativos com mais de 149 dias sem compra | Clientes da carteira reativação sem compra há pelo menos 149 dias com a empresa toda | 14 dias | Aplica-se ao time carteira reativação. |
| 4 | Sem nenhuma venda registrada | Clientes da carteira reativação sem nenhuma venda registrada (nunca comprou) que não se encaixaram no bloco anterior | 14 dias | Aplica-se ao time carteira reativação. |
| 5 | Regra final carteira reativação | Todos os clientes restantes da carteira reativação que não foram parametrizados nos blocos anteriores | Não agendar | Bloco sem filtro: funciona como regra final para a carteira reativação. |
| 6 | Frequência padrão carteira direta | Todos os clientes da carteira direta | 7 dias | Bloco sem filtro: aplica-se a todos os clientes deste time. |

**Pontos de atenção**

- O nome do bloco 2 cita 150 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.
- O nome do bloco 3 cita 150 dia(s), mas o filtro usa 149 dias. Confirmar qual vale.
- O nome do bloco 5 cita 150 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.

## Regra 221

`referencias/regra_221.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados) baseada no histórico de compras com o vendedor e com o grupo. Todos os segmentos possuem preferência de atendimento de segunda-feira a sábado. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Pré-qualificado | Clientes sem nenhuma venda registrada com o próprio vendedor (nunca comprou) | 21 dias, preferência de segunda a sábado |  |
| 2 | Ativado | Clientes com compra única com o próprio vendedor e sem compra com o grupo nos últimos 30 dias | 14 dias, preferência de segunda a sábado |  |
| 3 | Compra regular | Clientes com compra com o grupo nos últimos 30 dias, mas fora da recência de 21 dias | 14 dias, preferência de segunda a sábado | Na prática, recência entre 21 e 30 dias. |
| 4 | Estimule a regularidade | Clientes fora da recência de positivação entre 31 e 60 dias atrás | 14 dias, preferência de segunda a sábado |  |
| 5 | Deixando de comprar | Clientes fora da recência de positivação entre 61 e 90 dias atrás | 7 dias, preferência de segunda a sábado |  |
| 6 | Resgate | Clientes fora da recência de positivação entre 91 e 360 dias atrás | 28 dias, preferência de segunda a sábado |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 222

`referencias/regra_222.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para dois times de vendedores: ruptura_global (IDs 8506, 8507, 8508, 8509, 8512) e carteira (IDs 602, 607, 8406). O time ruptura_global define frequências para adimplentes com base em ramos de atividade específicos e tempo sem venda; o time carteira define frequências por curva ABC de faturamento e tempo da última compra. Os blocos são avaliados em ordem por fonte.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 14d para 'Sem venda há mais de 30d' | Clientes adimplentes, sem venda do grupo nos últimos 30 dias e com ramo de atividade entre 12 ramos especificados (6, 7, 8, 10, 28, 32, 33, 37, 38, 40, 41 e 42) | 14 dias | Aplica-se apenas ao time ruptura_global. |
| 2 | Freq. de 14d para 'Sem venda há mais de 45d' | Clientes adimplentes, sem compra nos últimos 45 dias e com ramo de atividade entre 30 ramos especificados (1, 2, 3, 4, 11, 12 e mais 24) | 14 dias | Aplica-se apenas ao time ruptura_global. |
| 3 | Freq. de 14d para curva A e com compra em 90 dias | Clientes da curva A com compra nos últimos 90 dias | 14 dias | Aplica-se apenas ao time carteira. |
| 4 | Freq. de 21d para curva B e com compra em 90 dias | Clientes da curva B com compra nos últimos 90 dias | 21 dias | Aplica-se apenas ao time carteira. |
| 5 | Freq. de 28d para curva C e com compra em 90 dias | Clientes da curva C com compra nos últimos 90 dias | 28 dias | Aplica-se apenas ao time carteira. |
| 6 | Freq. de 21d para sem classificação de curva e com compra em 90 dias | Clientes sem classificação de curva e com compra nos últimos 90 dias | 21 dias | Aplica-se apenas ao time carteira. |
| 7 | Freq. de 21d para sem compra há mais de 90 dias | Todos os clientes do time carteira que sobraram dos blocos anteriores; na prática, sem compra há mais de 90 dias | 21 dias | Bloco sem filtro para o time carteira: funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(ruptura_global): clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 223

`referencias/regra_223.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para três times de vendedores: ativacao (IDs 970, 967, 973, 974), generalista (14 vendedores, incluindo IDs 511, 803, 510, entre outros) e construtora (IDs 956, 954, 958, 971, 520). Cada time possui regras específicas de frequência ou bloqueio de agenda baseadas na recência de compras. Os blocos são avaliados em ordem por fonte de clientes.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Cliente com pedido nos últimos 30 dias | Clientes com pedido nos últimos 30 dias | 21 dias | Aplica-se ao time ativacao. |
| 2 | Cliente sem pedido nos últimos 30 dias | Todos os clientes do time que sobraram do bloco anterior; na prática, sem pedido nos últimos 30 dias | 15 dias | Bloco sem filtro para o time ativacao: funciona como regra final da fonte. |
| 3 | Cliente com compra na semana corrente | Clientes com pedido na semana atual (entre segunda e sexta-feira) | Não agendar | Aplica-se ao time generalista. |
| 4 | Cliente semanal - padrão | Todos os clientes do time generalista que sobraram do bloco anterior | 7 dias | Bloco sem filtro para o time generalista: funciona como regra final da fonte. |
| 5 | Todos os clientes | Todos os clientes do time construtora | 14 dias | Bloco sem filtro para o time construtora: aplica-se a todos os clientes da fonte. |

## Regra 224

`referencias/regra_224.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes baixados na Receita Federal e com rota na semana não são agendados; prospects e clientes ativos recebem frequências específicas de atendimento; e a regra final atende todos os demais com a mesma frequência. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar clientes com data da rota na semana | Clientes com data de rota (visita presencial programada) na semana atual | Não agendar | Evita que o cliente receba ligação do televendas na mesma semana da visita do externo. |
| 3 | Clientes Prospects | Clientes em ciclo de vida prospect com a empresa | 14 dias |  |
| 4 | Clientes Ativos | Clientes com pedido nos últimos 60 dias, com qualquer vendedor da empresa | 7 dias |  |
| 5 | Risco de Inatividade | Clientes com pedido nos últimos 90 dias que não entraram em Ativo; na prática, último pedido entre 60 e 90 dias atrás | 7 dias | Considera compras com qualquer vendedor da empresa. |
| 6 | Inativos + 90d | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 90 dias | 7 dias | Bloco sem filtro: funciona como regra final. |

## Regra 225

`referencias/regra_225.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Define frequências de atendimento e preferência de dias úteis e sábado para prospects, ativos e inativos, diferenciando por adimplência. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. de 10d para Prospects | Clientes em ciclo de vida prospect com a empresa | 10 dias, preferência de segunda a sábado |  |
| 2 | Freq. de 21d para Ativos Adimplentes | Clientes ativos para o próprio vendedor e adimplentes (sem pendências financeiras) | 21 dias, preferência de segunda a sábado |  |
| 3 | Freq. de 10d para Ativos Inadimplentes | Clientes ativos para o próprio vendedor que não entraram no bloco anterior (inadimplentes) | 10 dias, preferência de segunda a sábado | Na prática, pega clientes ativos inadimplentes. |
| 4 | Freq. de 14d para Inativos Adimplentes | Clientes adimplentes que não se encaixaram nos blocos anteriores | 14 dias, preferência de segunda a sábado | Na prática, pega inativos adimplentes. |
| 5 | Freq. de 21d para Inativos Inadimplentes | Todos os clientes do time que sobraram dos blocos anteriores | 21 dias, preferência de segunda a sábado | Bloco sem filtro: funciona como regra final, pegando na prática os inativos inadimplentes. |

## Regra 226

`referencias/regra_226.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). A regra define frequências de atendimento com base no histórico de vendas, última compra (global ou do vendedor) e frequência histórica. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ative essa oportunidade | Clientes sem nenhuma venda registrada com a empresa (nunca comprou) | 7 dias |  |
| 2 | Cliente ativado | Clientes com pedido nos últimos 30 dias (global) e que compraram uma única vez com a empresa | 14 dias |  |
| 3 | Clientes que compram mensalmente | Clientes com frequência histórica de compra de 30 dias e com pedido nos últimos 120 dias (global) | 28 dias |  |
| 4 | Recência de atendimento igual a recência de compra | Clientes com última compra (positivação) do próprio vendedor dono da carteira entre 20 e 30 dias atrás | Frequência do histórico, com limite máximo de 60 dias |  |
| 5 | Mantenha seu cliente ativo | Clientes cuja última compra com qualquer vendedor da empresa NÃO ocorreu nos últimos 120 dias | 14 dias |  |
| 6 | Resgate seu cliente inativo | Clientes cuja última compra com qualquer vendedor da empresa NÃO ocorreu nos últimos 180 dias | 28 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 227

`referencias/regra_227.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time felipe (vendedores do tipo televendas ativados, com exclusão de 7 IDs específicos). Trata cobertura de rota, não agendamento para ativos recentes, e frequências variadas para prospects, ativos antigos e inativos, com uma regra final redundante. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Cobertura de rota de visita | Clientes com data de rota (visita presencial) há 7 dias atrás | 1 dia, fixo | Parametrização fixa. |
| 2 | Não agendar clientes com compra em 30 dias | Clientes com pedido nos últimos 30 dias, com qualquer vendedor da empresa | Não agendar |  |
| 3 | Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 60 dias |  |
| 4 | Ativos | Clientes com pedido entre 30 e 90 dias atrás, com qualquer vendedor da empresa | 15 dias |  |
| 5 | Inativos | Todos os clientes restantes do time que não se enquadraram nos blocos anteriores | 10 dias | Bloco sem filtro: funciona como regra final para os clientes restantes. |
| 6 | Não agendar clientes não cobertos | Todos os clientes restantes que não foram parametrizados por blocos anteriores | Não agendar | Bloco sem filtro posicionado após outro bloco sem filtro. |

**Pontos de atenção**

- O bloco 6 vem depois do bloco 5, que já pega todos os clientes restantes da fonte sem filtro. Pela regra 'sem repetição', o bloco 6 não alcançará nenhum cliente.

## Regra 228

`referencias/regra_228.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). A frequência de atendimento é definida com base no ciclo de vida (prospects ou primeira compra), na recência de compras e na curva de faturamento do cliente. Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ative este novo cliente! | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 28 dias |  |
| 2 | Cliente ativado! | Clientes que fizeram uma única compra com o próprio vendedor | 21 dias |  |
| 3 | Compra com regularidade! (Curva C) | Clientes com pedido nos últimos 90 dias que pertencem à curva C de faturamento com a empresa | 7 dias |  |
| 4 | Compra com regularidade! (Curva A e B) | Clientes com pedido nos últimos 90 dias que não entraram no bloco anterior; na prática, curvas A e B com pedido nos últimos 90 dias | 14 dias | Considera compras com algum vendedor do mesmo grupo do dono da carteira. |
| 5 | Cliente caminhando para inatividade! | Clientes com último pedido entre 91 e 180 dias atrás | 28 dias |  |
| 6 | Resgatar cliente inativo! | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 180 dias | 45 dias | Bloco sem filtro: funciona como regra final. |

## Regra 229

`referencias/regra_229.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time farm (vendedores específicos por ID). Clientes com compra recente não são agendados, enquanto os demais recebem frequências de atendimento variadas com base no tempo sem compras ou se são prospects. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes com compra em 30 dias | Clientes com pedido nos últimos 30 dias | Não agendar |  |
| 2 | Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 14 dias |  |
| 3 | Cobertura mensal de positivação | Clientes cuja última compra não ocorreu no intervalo entre 31 e 60 dias atrás (avaliado após os blocos anteriores) | 14 dias | O filtro GOBR indica 'fora da recencia de positivacao entre 31 dias e 60 dias'. |
| 4 | Risco de inatividade | Clientes cuja última compra não ocorreu no intervalo entre 61 e 90 dias atrás (avaliado após os blocos anteriores) | 21 dias | O filtro GOBR indica 'fora da recencia de positivacao entre 61 dias e 90 dias'. |
| 5 | Inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, há mais de 90 dias sem compra | 28 dias | Bloco sem filtro: funciona como regra final. |

## Regra 230

`referencias/regra_230.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas). Clientes inadimplentes não são agendados; os demais recebem frequências de atendimento variadas com base no ciclo de vida, histórico de compras e tempo desde o último pedido com o próprio vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Prospect: Cliente potencial | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 14 dias |  |
| 3 | Ativado: fez um pedido e ainda não comprou mais | Clientes com uma única compra com o próprio vendedor | 7 dias |  |
| 4 | Ativo: compra regularmente | Clientes ativos para o vendedor com frequência histórica de compra abaixo de 16 dias | 14 dias |  |
| 5 | Ativo: estimular a regularidade de compra | Clientes com último pedido com o próprio vendedor entre 16 e 45 dias atrás | 14 dias |  |
| 6 | Em ruptura: risco de ficar inativo | Clientes com último pedido com o próprio vendedor entre 60 e 89 dias atrás | 7 dias | Há uma lacuna entre 45 e 60 dias sem compra que não é coberta por este bloco nem pelo anterior. |
| 7 | Inativo: reativar cliente sem compra | Clientes sem pedido com o próprio vendedor nos últimos 60 dias | 21 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.
- Existe um intervalo de tempo sem compras (entre 45 e 60 dias atrás) que não se encaixa nas regras de 16 a 45 dias nem na faixa de 60 a 89 dias, podendo cair diretamente na regra de inativos (> 60 dias) dependendo da ordem e do histórico.

## Regra 231

`referencias/regra_231.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para três times de vendedores (carteira regional, carteira reativação e carteira direta). O primeiro bloco bloqueia clientes baixados na Receita Federal para todos os times; os blocos seguintes definem regras específicas de agendamento e frequência baseadas no histórico de compras para cada carteira. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Baixados na receita | Clientes com CNPJ baixado na Receita Federal dos times carteira_regional (vendedores 7 IDs citados), carteira_reativacao (vendedores 706, 763) e carteira_direta (vendedores 708, 736, 737, 755) | Não agendar | Aplica-se aos três times simultaneamente. |
| 2 | Clientes com compra nos últimos 30 dias | Clientes com compra nos últimos 30 dias com qualquer vendedor da empresa, do time carteira_regional | Não agendar |  |
| 3 | Clientes com compra entre 30 e 150 dias | Clientes com compra entre 30 e 150 dias atrás com qualquer vendedor da empresa, do time carteira_regional | 7 dias |  |
| 4 | Clientes com compra em 150 dias | Clientes com compra nos últimos 150 dias com qualquer vendedor da empresa, do time carteira_reativacao | Não agendar |  |
| 5 | Clientes sem compra | Clientes em ciclo de vida prospect com a empresa, do time carteira_reativacao | 14 dias |  |
| 6 | Clientes sem compra em 150 dias | Clientes sem compra há pelo menos 149 dias com a empresa toda, do time carteira_reativacao | 14 dias |  |
| 7 | Freq. de 7d para todos os clientes | Todos os clientes do time carteira_direta que não foram parametrizados nos blocos anteriores | 7 dias | Bloco sem filtro para o time carteira_direta. |

**Pontos de atenção**

- Não há bloco final sem filtro para as fontes time(carteira_regional) e time(carteira_reativacao): clientes que não se enquadram em nenhum bloco mantêm a parametrização anterior.

## Regra 232

`referencias/regra_232.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Filiais e inadimplentes não são agendados; os demais recebem frequência de atendimento conforme o ciclo de vida (prospects) ou o tempo desde a última compra (compras com vendedores do mesmo grupo). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar filiais | Clientes cuja empresa é uma filial | Não agendar |  |
| 2 | Não agendar clientes Inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Freq. de 21d para clientes Prospects | Clientes em ciclo de vida prospect com a empresa | 21 dias |  |
| 4 | Freq. do histórico para clientes com compra entre 1 e 29 dias | Clientes com pedido nos últimos 29 dias | Frequência do histórico, com mínimo de 14 e máximo de 30 dias |  |
| 5 | Freq. de 21d para clientes com compra entre 30 e 59 dias | Clientes com pedido entre 30 e 59 dias atrás | 21 dias |  |
| 6 | Freq. de 21d para clientes com compra entre 60 e 89 dias | Clientes com pedido entre 60 e 89 dias atrás | 21 dias |  |
| 7 | Freq. de 21d para clientes sem compra em 90 dias | Todos os clientes do time que sobraram dos blocos anteriores | 21 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- O nome do bloco 7 cita sem compra em 90 dias, mas o bloco não possui filtro de clientes, funcionando como uma regra final genérica para todos os restantes.

## Regra 233

`referencias/regra_233.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Bloqueia o agendamento de clientes com cobrança DH sem crédito, cobrança BK com menos de R$ 199 de crédito ou inadimplentes; define frequências de 7 ou 14 dias para ativos, inativos e sem venda. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes DH sem crédito | Clientes sem crédito disponível e com tipo de cobrança DH | Não agendar |  |
| 2 | Não agendar clientes BK com menos de R$ 200 de crédito | Clientes com crédito disponível abaixo de R$ 199 e com tipo de cobrança BK | Não agendar |  |
| 3 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 4 | Frequência para ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | 7 dias |  |
| 5 | Frequência para inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | 14 dias |  |
| 6 | Frequência para sem venda | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 234

`referencias/regra_234.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para toda a empresa aplicando regras por ordem de prioridade. Identifica clientes em queda de faturamento, inativos há muito tempo, clientes em Goiânia, ativos, inativos e sem vendas, aplicando frequências específicas e preferências de dias da semana para o atendimento.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Queda de faturamento | Clientes com queda de faturamento acima de 5% | 3 dias |  |
| 2 | Inativos há mais de 1138 dias | Clientes com última compra entre 1138 e 9999 dias atrás | Não agendar |  |
| 3 | Teste cidade Goiânia | Clientes na cidade de Goiânia | Frequência média dos clientes inativos da empresa; preferência de atendimento de segunda a domingo |  |
| 4 | Clientes ativos | Clientes ativos segundo o histórico de compras com o próprio vendedor | Frequência média dos clientes ativos da empresa; preferência de atendimento de segunda a domingo |  |
| 5 | Clientes inativos | Clientes inativos segundo o histórico de compras com o próprio vendedor | Frequência média dos clientes inativos da empresa; preferência de atendimento de segunda a domingo |  |
| 6 | Clientes sem vendas | Clientes sem nenhuma venda registrada (nunca comprou) | Frequência média dos clientes inativos da empresa; preferência de atendimento de segunda a domingo |  |
| 7 | Regra padrão default | Todos os clientes da carteira que não se enquadraram nos blocos anteriores | 7 dias; preferência de atendimento nos dias úteis (segunda a sexta) | Bloco sem filtro: funciona como regra final. |

## Regra 235

`referencias/regra_235.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização dos times de televendas (felipe, paola_1, paola_2 e temporario_2meses). O sistema avalia os blocos em ordem para cada fonte, aplicando bloqueios iniciais para clientes baixados na Receita, rotas e compras recentes, seguido por regras de frequência e preferência de dias úteis e sábado.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Nao agendar - clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar | Aplica-se aos times felipe, paola_1, paola_2 e temporario_2meses. |
| 2 | Nao agendar - clientes com rota futura em 7 dias | Clientes com data de rota (visita presencial programada) dentro de 7 dias à frente | Não agendar | Aplica-se aos times paola_1 e paola_2. |
| 3 | Nao agendar - clientes com recencia de positivacao em 7 dias | Clientes com compra nos últimos 7 dias (com vendedor do mesmo grupo) | Não agendar | Aplica-se aos times paola_1 e paola_2. |
| 4 | Clientes com compra em 30 dias | Clientes com compra nos últimos 30 dias (com vendedor do mesmo grupo) | Não agendar | Aplica-se ao time felipe. |
| 5 | Cobertura de rota de visita exatamente 14 dias depois | Clientes com data de rota há 14 dias atrás e com crédito disponível de pelo menos 5% do limite | 1 dia, preferência de segunda a sábado (demais dias não atender) | Aplica-se ao time temporario_2meses. |
| 6 | Clientes com compra entre 30 e 90 dias | Clientes com compra entre 30 e 90 dias atrás (com vendedor do mesmo grupo) | 15 dias, preferência de segunda a sábado (demais dias não atender) | Aplica-se ao time felipe. |
| 7 | Clientes sem compra em 90 dias | Todos os clientes do time felipe que sobraram dos blocos anteriores | 10 dias, preferência de segunda a sábado (demais dias não atender) | Bloco sem filtro para o time felipe; funciona como regra final para este time. |
| 8 | Clientes com rota ha 7 dias ou mais | Clientes com data de rota dentro de um intervalo de 7 dias e com crédito disponível de pelo menos 5% do limite | 14 dias, preferência de segunda a sábado (demais dias não atender) | Aplica-se aos times paola_1 e paola_2. |
| 9 | Clientes com compra entre 7 e 30 dias | Clientes com compra global (qualquer vendedor da empresa) entre 7 e 30 dias atrás e com crédito disponível de pelo menos 5% do limite | 14 dias, preferência de segunda a sábado (demais dias não atender) | Aplica-se aos times paola_1 e paola_2. |
| 10 | Clientes com compra entre 31 e 60 dias | Clientes com compra global (qualquer vendedor da empresa) entre 31 e 60 dias atrás e com crédito disponível de pelo menos 5% do limite | 14 dias, preferência de segunda a sábado (demais dias não atender) | Aplica-se aos times paola_1 e paola_2. |
| 11 | Clientes com compra entre 61 e 89 dias | Clientes com compra global (qualquer vendedor da empresa) entre 61 e 89 dias atrás e com crédito disponível de pelo menos 5% do limite | 7 dias, preferência de segunda a sábado (demais dias não atender) | Aplica-se aos times paola_1 e paola_2. |
| 12 | Clientes com compra entre 90 e 179 dias | Clientes com compra global (qualquer vendedor da empresa) entre 90 e 179 dias atrás e com crédito disponível de pelo menos 5% do limite | 14 dias, preferência de segunda a sábado (demais dias não atender) | Aplica-se aos times paola_1 e paola_2. |
| 13 | Clientes sem compra em 180 dias | Clientes com crédito disponível de pelo menos 5% do limite que não se enquadraram nos blocos anteriores | 21 dias, preferência de segunda a sábado (demais dias não atender) | Aplica-se aos times paola_1 e paola_2. |
| 14 | Clientes que hoje não se enquadraram nas regras padrão | Todos os clientes dos times felipe, paola_1, paola_2 e temporario_2meses que não foram parametrizados por blocos anteriores | Não agendar | Bloco sem filtro geral; funciona como regra final. |

**Pontos de atenção**

- Não há bloco final sem filtro para a fonte time(paola_1, paola_2): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- Não há bloco final sem filtro para a fonte time(temporario_2meses): clientes que não se enquadram em nenhum bloco não recebem parametrização desta regra e mantêm a configuração que já tinham.
- O nome do bloco 13 (Clientes sem compra em 180 dias) cita 180 dia(s), mas esse número não aparece nos filtros/ações do bloco. Confirmar qual vale.

## Regra 236

`referencias/regra_236.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização que atende o time de televendas e diversas carteiras específicas. O televendas bloqueia clientes baixados na Receita e não agenda quem sobra no fim. As carteiras recebem frequências e preferências de dias específicas (segunda, quarta e sexta ou terça e quinta) com base na última compra. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar baixados na Receita | Clientes do time televendas com CNPJ baixado na Receita Federal | Não agendar | Aplica-se à fonte time televendas. |
| 2 | Rota todos os dias (com venda recente) | Clientes das carteiras cidades_todo_dia, bairros_todo_dia com compra nos últimos 1 dia | A cada 7 dias (semanal) | Aplica-se às carteiras citadas. |
| 3 | Rota todos os dias | Todos os clientes restantes das carteiras cidades_todo_dia, bairros_todo_dia que não passaram pelos blocos anteriores | 2 dias | Bloco sem filtro para as carteiras citadas. |
| 4 | Rota segunda, quarta e sexta | Clientes das carteiras cidades_seg_qua_sex, bairros_seg_qua_sex sem compra na semana atual | A cada 7 dias (semanal); preferência de dias: segunda, quarta e sexta | Demais dias da semana ficam com valor 0 (não atender). |
| 5 | Rota terça e quinta | Clientes das carteiras cidades_rj_ter_qui, bairros_rj_ter_qui, cidades_sp_ter_qui sem compra na semana atual | A cada 7 dias (semanal); preferência de dias: terça e quinta | Demais dias da semana ficam com valor 0 (não atender). |
| 6 | Não agendar clientes fora das regras padrão | Todos os clientes restantes do time televendas que não se enquadraram nos blocos anteriores | Não agendar | Bloco sem filtro para a fonte time televendas. |

**Pontos de atenção**

- Não há bloco final sem filtro para as carteiras cidades_seg_qua_sex, bairros_seg_qua_sex: clientes que não se enquadram mantêm a configuração anterior.
- Não há bloco final sem filtro para as carteiras cidades_rj_ter_qui, bairros_rj_ter_qui, cidades_sp_ter_qui: clientes que não se enquadram mantêm a configuração anterior.
- As carteiras cidades_todo_dia, bairros_todo_dia, cidades_seg_qua_sex, bairros_seg_qua_sex, cidades_rj_ter_qui, bairros_rj_ter_qui e cidades_sp_ter_qui são usadas mas não são definidas neste arquivo (podem estar em outro arquivo de regras).

## Regra 237

`referencias/regra_237.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Define frequências de atendimento com base no histórico de vendas e no tempo desde a última compra (compradores regulares, com necessidade de estimular regularidade, resgates e inativos). Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes ativados | Clientes sem nenhuma venda registrada (nunca comprou) | 14 dias |  |
| 2 | Compra com regularidade | Clientes com pedido nos últimos 30 dias e frequência histórica de compra abaixo de 30 dias | Frequência do histórico, entre 0 e 30 dias |  |
| 3 | Estimular a regularidade | Clientes com pedido entre 30 e 60 dias atrás | 14 dias |  |
| 4 | Clientes resgatados | Clientes sem pedido nos últimos 60 dias e frequência histórica de compra acima de 30 dias | 14 dias |  |
| 5 | Resgatar inativos | Clientes sem pedido nos últimos 60 dias | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 238

`referencias/regra_238.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Todos os clientes, independentemente do tempo desde a última compra ou se estão inativos, recebem a mesma frequência de atendimento a cada 14 dias. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Matenha relacionamento com seu cliente | Clientes com pedido nos últimos 59 dias, com qualquer vendedor da empresa | 14 dias |  |
| 2 | Se não mantiver a regularidade de compra, o cliente ficará inativo | Clientes com pedido nos últimos 89 dias que não entraram no bloco anterior; na prática, último pedido entre 59 e 89 dias atrás | 14 dias | Considera compras com qualquer vendedor da empresa (global). |
| 3 | Resgate seu cliente inativo | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem pedido há mais de 89 dias | 14 dias | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Todos os três blocos definem exatamente a mesma frequência (14 dias), tornando a divisão em múltiplos blocos baseada na recência redundante para a definição da ação, embora separe os clientes por faixa de inatividade.

## Regra 239

`referencias/regra_239.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Primeiro bloqueia quem tem CNPJ baixado na Receita ou rota na semana; depois define a frequência de ligação pelo tempo desde a última compra (compras com vendedores do mesmo grupo). Quem sobra cai na regra final e não é agendado. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Não agendar clientes com data da rota na semana | Clientes com data de rota (visita presencial do vendedor externo) na semana atual | Não agendar | Evita que o cliente receba ligação do televendas na mesma semana da visita do externo. |
| 3 | Clients ativos | Clientes com compra nos últimos 60 dias | 14 dias |  |
| 4 | Risco de inatividade | Clientes com compra nos últimos 90 dias que não entraram nos blocos anteriores; na prática, entre 60 e 90 dias sem comprar | 7 dias |  |
| 5 | Inativos 90 dias | Clientes com compra nos últimos 120 dias que não entraram nos blocos anteriores; na prática, entre 90 e 120 dias sem comprar | 14 dias |  |
| 6 | Inativos 120 dias | Clientes com compra nos últimos 150 dias que não entraram nos blocos anteriores; na prática, entre 120 e 150 dias sem comprar | 21 dias |  |
| 7 | Inativos 150 dias | Clientes com compra nos últimos 180 dias que não entraram nos blocos anteriores; na prática, entre 150 e 180 dias sem comprar | 28 dias |  |
| 8 | Clientes não mapeados nas regras | Todos os clientes do time que não se enquadraram em nenhum bloco anterior (por exemplo, sem compra há mais de 180 dias) | Não agendar | Bloco sem filtro: funciona como regra final. |

**Pontos de atenção**

- Clientes sem compra há mais de 180 dias caem na regra final e não são agendados.

## Regra 240

`referencias/regra_240.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados). Clientes com compra recente não são agendados; os demais recebem frequência de ligação conforme o tempo desde o último pedido (compras com vendedores do mesmo grupo). Os blocos são avaliados em ordem: o cliente fica no primeiro bloco em que se encaixar.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Clientes com compra em 7d | Clientes com compra nos últimos 7 dias | Não agendar |  |
| 2 | Manter a regularidade de compra | Clientes com compra nos últimos 30 dias que não entraram no bloco anterior | 14 dias |  |
| 3 | Garantir a positivação da carteira | Clientes com compra nos últimos 60 dias que não entraram nos blocos anteriores; na prática, entre 30 e 60 dias sem comprar | 14 dias |  |
| 4 | Cliente com risco de inatividade | Clientes com compra nos últimos 90 dias que não entraram nos blocos anteriores; na prática, entre 60 e 90 dias sem comprar | 7 dias |  |
| 5 | Clientes inativos | Todos os clientes do time que sobraram dos blocos anteriores; na prática, sem compra há mais de 90 dias | 21 dias | Bloco sem filtro: funciona como regra final. |

## Regra 241

`referencias/regra_241.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados) baseada no ramo de atividade dos clientes. Clientes baixados na Receita não são agendados; ramos específicos recebem frequências de 7, 14 ou 28 dias; e clientes fora dos ramos mapeados não são agendados. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar clientes baixados na receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Clientes revenda freq 7 dias | Clientes com ramo de atividade igual a 106, 139, 109, 143, 141 ou 142 | 7 dias |  |
| 3 | Clientes revenda freq 14 dias | Clientes com ramo de atividade igual a 140, 146 ou 148 | 14 dias |  |
| 4 | Clientes revenda freq 28 dias | Clientes com ramo de atividade igual a 138 | 28 dias |  |
| 5 | Clientes comsumo freq 7 dias | Clientes com ramo de atividade igual a 144, 147 ou 108 | 7 dias |  |
| 6 | Clientes comsumo freq 14 dias | Clientes com ramo de atividade igual a 111, 100, 110, 112, 145, 107, 113 (7 ramos no total) | 14 dias |  |
| 7 | Clientes comsumo freq 28 dias | Clientes com ramo de atividade igual a 114 | 28 dias |  |
| 8 | Clientes fora dos ramos mapeados | Todos os clientes do time que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final. |

## Regra 242

`referencias/regra_242.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados) baseada na frequência histórica de compra e na recência do último pedido (compras com vendedores do mesmo grupo). Os blocos são avaliados em ordem e definem frequências de atendimento específicas para cada combinação.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Freq. hist. de 0 a 30d - sem compra em 20d | Frequência histórica de compra entre 0 e 30 dias e último pedido entre 20 e 30 dias atrás | 21 dias |  |
| 2 | Freq. hist. de 31 a 60d - sem compra em 29d | Frequência histórica de compra entre 31 e 60 dias e último pedido entre 29 e 44 dias atrás | 21 dias |  |
| 3 | Freq. hist. de 31 a 60d - sem compra em 44d | Frequência histórica de compra entre 31 e 60 dias e último pedido entre 44 e 60 dias atrás | 21 dias |  |
| 4 | Freq. hist. de 61 a 90d - sem compra em 60d | Frequência histórica de compra entre 61 e 90 dias e último pedido entre 61 e 90 dias atrás | 15 dias |  |
| 5 | Freq. hist. de 61 a 90d - sem compra em 90d | Frequência histórica de compra entre 61 e 90 dias e último pedido entre 90 e 180 dias atrás | 21 dias |  |
| 6 | Freq. hist. de 91 a 180d - sem compra em 44d | Frequência histórica de compra entre 91 e 180 dias e último pedido entre 44 e 120 dias atrás | 21 dias |  |
| 7 | Freq. hist. de 91 a 180d - sem compra em 120d | Frequência histórica de compra entre 91 e 180 dias e último pedido entre 120 e 180 dias atrás | 15 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 243

`referencias/regra_243.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas (vendedores do tipo televendas ativados) voltada para pessoas jurídicas. Clientes novos ou com compras recentes recebem frequências específicas de atendimento de segunda a sábado, enquanto os demais casos ou não-PJ ficam fora da agenda. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Ative este cliente! | Clientes pessoa jurídica (CNPJ) sem nenhuma venda registrada | 21 dias; preferência de atendimento de segunda a sábado |  |
| 2 | Faça seu pós-vendas! | Clientes pessoa jurídica (CNPJ) com compra nos últimos 20 dias | 3 dias; preferência de atendimento de segunda a sábado |  |
| 3 | Mantenha o cliente engajado! | Clientes pessoa jurídica (CNPJ) com última compra entre 20 e 33 dias atrás | Frequência do histórico mais 2 dias, entre 20 e 33 dias; preferência de atendimento de segunda a sábado |  |
| 4 | Não agendar clientes sem compra em 33 dias | Clientes pessoa jurídica (CNPJ) que não se enquadraram nos blocos anteriores (sem compra há mais de 33 dias) | Não agendar | Bloco aplicável apenas a PJ devido ao filtro do bloco. |
| 5 | Não agendar se não for PJ | Todos os clientes restantes do time que não são pessoa jurídica | Não agendar | Bloco sem filtro: funciona como regra final para os demais perfis. |

## Regra 244

`referencias/regra_244.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para todos os vendedores ativados da empresa. Filiais e inadimplentes não são agendados. Os demais clientes recebem frequências específicas com base no ciclo de vida, histórico ou tempo desde a última compra com o próprio vendedor. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar filiais | Clientes que são filiais | Não agendar |  |
| 2 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 3 | Prospect: Cliente potencial | Clientes em ciclo de vida prospect com o próprio vendedor (nunca compraram com ele) | 14 dias |  |
| 4 | Ativado: Fez um pedido e ainda não comprou mais | Clientes que fizeram uma única compra com o próprio vendedor | 7 dias |  |
| 5 | Freq. histórica para Ativo: compra regularmente | Clientes ativos para o vendedor com frequência histórica de compra menor que 8 dias | Frequência do histórico, com mínimo de 5 e máximo de 7 dias |  |
| 6 | Estimular a regularidade de compra | Clientes com última compra com o próprio vendedor entre 8 e 30 dias atrás | 14 dias |  |
| 7 | Em ruptura: risco de ficar inativo | Clientes com última compra com o próprio vendedor entre 31 e 60 dias atrás | 7 dias |  |
| 8 | Inativo: reativar cliente sem compra | Clientes sem compra com o próprio vendedor nos últimos 60 dias | 14 dias |  |

**Pontos de atenção**

- Não há bloco final sem filtro: clientes que não se enquadram em nenhum bloco mantêm a parametrização que já tinham.

## Regra 245

`referencias/regra_245.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização do time de televendas e carteiras específicas de rotas por cidade. Primeiramente bloqueia inadimplentes, baixados, sem crédito e quem comprou nos últimos 60 dias. Em seguida, aplica regras de frequência e preferência de dias conforme a rota e o histórico de atendimento. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Não agendar inadimplentes | Clientes inadimplentes (com pendências financeiras em aberto) | Não agendar |  |
| 2 | Não agendar baixados na Receita | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 3 | Não agendar sem crédito | Clientes sem crédito disponível | Não agendar |  |
| 4 | Não agendar clientes com compra em 60d | Clientes com compra nos últimos 60 dias | Não agendar |  |
| 5 | Com atendimento/venda na semana / Rota: Todos os dias | Clientes da carteira rota_todo_dia com visita na semana atual | Frequência do histórico, entre 7 e 14 dias |  |
| 6 | Sem atendimento/venda na semana / Rota: Todos os dias | Clientes da carteira rota_todo_dia que não tiveram visita na semana atual | Frequência do histórico mais 2 dias, entre 3 e 7 dias | Bloco sem filtro: funciona como regra final para a carteira rota_todo_dia. |
| 7 | Com atendimento/venda na semana / Rota: Ter | Clientes da carteira rota_terca com visita na semana atual | 7 dias, preferência na segunda-feira |  |
| 8 | Sem atendimento/venda na semana / Rota: Ter | Clientes da carteira rota_terca que não tiveram visita na semana atual | 7 dias, preferência na segunda-feira | Bloco sem filtro: funciona como regra final para a carteira rota_terca. |
| 9 | Com atendimento/venda na semana / Rota: Qua | Clientes da carteira rota_quarta com visita na semana atual | 7 dias, preferência na terça-feira |  |
| 10 | Sem atendimento/venda na semana / Rota: Qua | Clientes da carteira rota_quarta que não tiveram visita na semana atual | 7 dias, preferência na terça-feira | Bloco sem filtro: funciona como regra final para a carteira rota_quarta. |
| 11 | Com atendimento/venda na semana / Rota: Qui | Clientes da carteira rota_quinta com visita na semana atual | 7 dias, preferência na quarta-feira |  |
| 12 | Sem atendimento/venda na semana / Rota: Qui | Clientes da carteira rota_quinta que não tiveram visita na semana atual | 7 dias, preferência na quarta-feira | Bloco sem filtro: funciona como regra final para a carteira rota_quinta. |
| 13 | Com atendimento/venda na semana / Rota: Sex | Clientes da carteira rota_sexta com visita na semana atual | 7 dias, preferência na quinta-feira |  |
| 14 | Sem atendimento/venda na semana / Rota: Sex | Clientes da carteira rota_sexta que não tiveram visita na semana atual | 7 dias, preferência na quinta-feira | Bloco sem filtro: funciona como regra final para a carteira rota_sexta. |
| 15 | Com atendimento/venda na semana / Rota: Seg | Clientes da carteira rota_segunda com visita na semana atual | 7 dias, preferência na sexta-feira |  |
| 16 | Sem atendimento/venda na semana / Rota: Seg | Clientes da carteira rota_segunda que não tiveram visita na semana atual | 7 dias, preferência na sexta-feira | Bloco sem filtro: funciona como regra final para a carteira rota_segunda. |
| 17 | Com atendimento/venda na semana - Cidades não informadas nas rotas | Clientes do time televendas com visita na semana atual | Frequência do histórico, entre 7 e 14 dias |  |
| 18 | Sem atendimento/venda na semana - Cidades não informadas nas rotas | Clientes do time televendas que não tiveram visita na semana atual | Frequência do histórico menos 1 dia, entre 1 e 7 dias | Bloco sem filtro: funciona como regra final para o time televendas. |

**Pontos de atenção**

- As carteiras rota_todo_dia, rota_terca, rota_quarta, rota_quinta, rota_sexta e rota_segunda são utilizadas nos blocos mas não estão definidas neste arquivo, podendo estar em outro arquivo de regras.

## Regra 246

`referencias/regra_246.gobr` · origem: llm (gemini-3.5-flash-lite) · verificação: OK

Parametrização para o time de televendas e carteiras separadas por ramos de atividade. O sistema bloqueia clientes baixados na Receita e prospects do time televendas, aplica regras específicas de frequência (ativos e inativos) para quatro grupos de ramos de atividade (ramos_1, ramos_2, ramos_3 e ramos_4), e por fim descarta os clientes do televendas que não se enquadraram nas regras. Os blocos são avaliados em ordem.

| # | Segmento | Critério | Ação | Observação |
|---|---|---|---|---|
| 1 | Baixados na Receita Federal | Clientes com CNPJ baixado na Receita Federal | Não agendar |  |
| 2 | Prospects | Clientes em ciclo de vida prospect com a empresa (nunca compraram) | 7 dias |  |
| 3 | Ativos dos ramos de atividade do grupo 1 | Clientes da carteira ramos_1 com pedido nos últimos 45 dias, incluindo postos, farmácias, supermercados, transportadoras, entre outros | 14 dias |  |
| 4 | Inativos dos ramos de atividade do grupo 1 | Clientes da carteira ramos_1 que não se enquadraram no bloco anterior; na prática, sem pedido há mais de 45 dias | 7 dias | Bloco sem filtro: funciona como regra final para a carteira ramos_1. |
| 5 | Ativos dos ramos de atividade do grupo 2 | Clientes da carteira ramos_2 com pedido nos últimos 60 dias, abrangendo distribuidores, concessionárias, indústrias, laboratórios e outros | 21 dias |  |
| 6 | Inativos dos ramos de atividade do grupo 2 | Clientes da carteira ramos_2 que não se enquadraram no bloco anterior; na prática, sem pedido há mais de 60 dias | 10 dias | Bloco sem filtro: funciona como regra final para a carteira ramos_2. |
| 7 | Ativos dos ramos de atividade do grupo 3 | Clientes da carteira ramos_3 com pedido nos últimos 75 dias, incluindo materiais de construção, restaurantes, hotéis e indústrias diversas | 28 dias |  |
| 8 | Inativos dos ramos de atividade do grupo 3 | Clientes da carteira ramos_3 que não se enquadraram no bloco anterior; na prática, sem pedido há mais de 75 dias | 14 dias | Bloco sem filtro: funciona como regra final para a carteira ramos_3. |
| 9 | Ativos dos ramos de atividade do grupo 4 | Clientes da carteira ramos_4 com pedido nos últimos 90 dias, englobando 8 ramos como vidraçarias, eventos, promotores de venda e outros | 28 dias |  |
| 10 | Inativos dos ramos de atividade do grupo 4 | Clientes da carteira ramos_4 que não se enquadraram no bloco anterior; na prática, sem pedido há mais de 90 dias | 14 dias | Bloco sem filtro: funciona como regra final para a carteira ramos_4. |
| 11 | Clientes que hoje não se enquadraram nas regras padrão | Todos os clientes do time televendas que não se enquadraram em nenhum bloco anterior | Não agendar | Bloco sem filtro: funciona como regra final para o time televendas. |

**Pontos de atenção**

- As carteiras ramos_1, ramos_2, ramos_3 e ramos_4 são utilizadas nos blocos 3 a 10, mas não são definidas neste arquivo (provavelmente estão definidas em outro arquivo de regras do cliente).
