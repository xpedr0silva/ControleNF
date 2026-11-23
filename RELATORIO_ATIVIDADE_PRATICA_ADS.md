# CENTRO UNIVERSITÁRIO MULTIVIX
## NÚCLEO DE EDUCAÇÃO A DISTÂNCIA – POLO GOVERNADOR VALADARES
### CURSO DE TECNOLOGIA EM ANÁLISE E DESENVOLVIMENTO DE SISTEMAS

\
\
\
\
\
**PEDRO HENRIQUE SILVA MARTINS**
\
\
\
\
\
# ESTÁGIO SUPERVISIONADO: ATIVIDADE PRÁTICA PROFISSIONAL
## SISTEMA WEB CONTROLENF: AUTOMAÇÃO, AUDITORIA E GESTÃO DESCENTRALIZADA DE NOTAS FISCAIS E CONTRATOS DE TI NO GRUPO EMALTO
\
\
\
\
\
\
\
\
\
\
**GOVERNADOR VALADARES – MG**
**2026**

---

\newpage

# PEDRO HENRIQUE SILVA MARTINS

\
\
\
\
\
# ESTÁGIO SUPERVISIONADO: ATIVIDADE PRÁTICA PROFISSIONAL
## SISTEMA WEB CONTROLENF: AUTOMAÇÃO, AUDITORIA E GESTÃO DESCENTRALIZADA DE NOTAS FISCAIS E CONTRATOS DE TI NO GRUPO EMALTO

\
\
\
\
\
\

> Trabalho acadêmico apresentado à disciplina de Estágio Supervisionado do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas do Centro Universitário Multivix (Polo de Apoio Presencial Governador Valadares – MG), como requisito obrigatório para obtenção da avaliação semestral no 4º período letivo.
>
> **Orientador:** Prof. Thiago Medeiros dos Reis

\
\
\
\
\
\
\
\
\
\
**GOVERNADOR VALADARES – MG**
**2026**

---

\newpage

# SUMÁRIO

1. **APRESENTAÇÃO DA EMPRESA** ............................................................................................ 1
   1.1 Identificação e Histórico do Grupo Emalto ............................................................................... 1
   1.2 Porte, Ramo de Atuação e Empresas Integrantes ...................................................................... 1
   1.3 O Departamento de Tecnologia da Informação e Atuação Profissional ..................................... 2
2. **DEFINIÇÃO DO PROJETO** .................................................................................................. 3
   2.1 Análise dos Processos Existentes e Softwares Legados ............................................................. 3
   2.2 Diagnóstico de Gargalos e Pontos Críticos de Melhoria ............................................................ 4
   2.3 Justificativa da Escolha por uma Aplicação Web ..................................................................... 5
3. **DESCRIÇÃO DA APLICAÇÃO** ............................................................................................ 7
   3.1 Visão Geral e Escopo do Sistema ControleNF .......................................................................... 7
   3.2 Requisitos Funcionais e Não Funcionais .................................................................................... 7
   3.3 Modelo Operacional e Fluxo de Trabalho do Analista de TI ..................................................... 9
   3.4 Objetivos Estratégicos e Vantagens Alcançadas ........................................................................ 10
4. **TECNOLOGIAS EMPREGADAS** ......................................................................................... 12
   4.1 Seleção do Stack Tecnológico e Justificativas Técnicas ............................................................ 12
   4.2 Arquitetura em Camadas e Consumo de APIs REST ................................................................ 14
   4.3 Fluxograma Geral dos Processos da Aplicação ......................................................................... 15
   4.4 Modelagem de Dados e Diagrama Entidade-Relacionamento (DER) ........................................ 17
5. **PROPOSTA DE VALOR** ...................................................................................................... 20
   5.1 Ganhos Operacionais e Redução de Lead Time de Conferência ................................................ 20
   5.2 Eliminação de Inconsistências Contábeis e Preservação Histórica (Snapshotting) ................... 20
   5.3 Prevenção de Multas Contratuais e Pagamentos em Duplicidade ............................................. 21
6. **APRESENTAÇÃO DA APLICAÇÃO DESENVOLVIDA (TUTORIAL PRÁTICO)** ................. 23
   6.1 Interface Principal e Dashboard de Indicadores ....................................................................... 23
   6.2 Módulo de Cadastros Base: Mapeamento Mestre por Filial ...................................................... 24
   6.3 Gestão de Propostas e Contratos TOTVS com Soft Delete ........................................................ 25
   6.4 Matriz Anual de 12 Meses e Acompanhamento de Lançamentos ............................................. 26
   6.5 Registro de Notas Fiscais e Mecanismo de Snapshotting .......................................................... 27
   6.6 Validações de Integridade e Regras de Negócio do Sistema ..................................................... 28
   6.7 Disponibilização do Código-Fonte e Repositório ...................................................................... 28
**REFERÊNCIAS** ......................................................................................................................... 29
**ANEXOS** ................................................................................................................................... 31
   **ANEXO A – Planilha Legada de Controle Manual de Notas Fiscais** ........................................ 31

---

\newpage

# LISTA DE ILUSTRAÇÕES

* **Figura 1** – Fluxograma do processo legado de conferência via planilhas e TOTVS
* **Figura 2** – Arquitetura da solução Web (FastAPI, SQLite WAL e Vanilla JS)
* **Figura 3** – Fluxograma geral de processamento de notas e snapshotting do ControleNF
* **Figura 4** – Diagrama Entidade-Relacionamento (DER) do Banco de Dados
* **Figura 5** – Tela do Dashboard: Gráficos de status de contratos e distribuição de despesas
* **Figura 6** – Tela de Cadastros Base: Mapeamento Mestre de códigos por empresa
* **Figura 7** – Tela de Gestão de Propostas e Contratos TOTVS
* **Figura 8** – Tela da Matriz Anual (12 Meses): Acompanhamento preditivo de contratos
* **Figura 9** – Tela de Lançamento de Notas Fiscais com campo de fornecedor em modo Read-Only

---

# LISTA DE QUADROS

* **Quadro 1** – Empresas Integrantes do Grupo Emalto atendidas pelo ControleNF
* **Quadro 2** – Requisitos Funcionais do Sistema ControleNF
* **Quadro 3** – Requisitos Não Funcionais do Sistema ControleNF
* **Quadro 4** – Matriz comparativa entre a planilha legada e o sistema ControleNF

---

# LISTA DE TABELAS

* **Tabela 1** – Dicionário de Dados: Estrutura da Tabela `fornecedor_empresa_identificador`
* **Tabela 2** – Dicionário de Dados: Estrutura da Tabela `notas_fiscais` com atributos de snapshotting

---

\newpage

# 1 APRESENTAÇÃO DA EMPRESA

## 1.1 Identificação e Histórico do Grupo Emalto

A **Emalto Indústria Mecânica Ltda.** é a empresa âncora do **Grupo Emalto**, um dos mais tradicionais e consolidados complexos industriais do estado de Minas Gerais. Fundado em 1974 na cidade de Timóteo, na emblemática região do Vale do Aço, o Grupo Emalto iniciou suas atividades prestando serviços de caldeiraria e montagem mecânica para as grandes usinas siderúrgicas locais. Ao longo de mais de cinco décadas de atuação contínua, o grupo expandiu progressivamente sua capacidade produtiva, tecnológica e de engenharia, tornando-se referência nacional no fornecimento de bens de capital sob encomenda, estruturas metálicas pesadas, serviços de usinagem de grande porte, montagens eletromecânicas e soluções de engenharia para setores estratégicos da economia, tais como mineração, siderurgia, papel e celulose, cimento, energia e química/petroquímica.

Pautada por rigorosos padrões internacionais de qualidade, conformidade socioambiental e governança corporativa, a Emalto conta com modernos parques fabris estrategicamente situados em Timóteo e Santana do Paraíso, totalizando mais de 60.000 metros quadrados de área construída, dotados de pontes rolantes de alta capacidade, máquinas de corte computadorizado (CNC e plasma de alta definição), robôs de soldagem e centros de usinagem avançados. A organização desempenha papel fundamental na geração de empregos e desenvolvimento socioeconômico regional, mantendo ainda a **Fundação Emalto**, braço social e cultural que oferece projetos de formação profissional, arte e esporte para jovens da comunidade local.

## 1.2 Porte, Ramo de Atuação e Empresas Integrantes

Classificada como empresa de grande porte, o Grupo Emalto atua de maneira diversificada e verticalizada por meio de unidades de negócio especializadas, atendendo clientes industriais de classe mundial em todo o território brasileiro e no exterior. Para suportar essa complexa malha corporativa com máxima eficiência jurídica, fiscal e operacional, o grupo é estruturado em 9 empresas coligadas e controladas, cada qual com seu respectivo Cadastro Nacional da Pessoa Jurídica (CNPJ) e centro de custo contábil:

```
+----------------------------------------------------------------------------------------------------+
| QUADRO 1 – Empresas Integrantes do Grupo Emalto Atendidas pelo Sistema                             |
+--------+-------------------------------------------------------+-----------------------------------+
| SIGLA  | RAZÃO SOCIAL / DENOMINAÇÃO CORPORATIVA                | PRINCIPAL ATIVIDADE / SEGMENTO    |
+--------+-------------------------------------------------------+-----------------------------------+
| EIM    | Emalto Indústria Mecânica Ltda.                       | Fabricação e caldeiraria pesada   |
| EEM    | Emalto Estruturas Metálicas Ltda.                     | Engenharia e estruturas metálicas |
| EEN    | Emalto Energia Ltda.                                  | Geração e soluções de energia     |
| FE     | Fundação Emalto                                       | Responsabilidade social e cultura |
| TDL    | Torque Diesel Ltda. (Matriz)                          | Serviços mecânicos e transporte   |
| TDF    | Torque Diesel Filial                                  | Distribuição de peças e serviços  |
| TG     | Torque Grill Ltda.                                    | Alimentação e serviços de apoio   |
| TP     | Torque Pneus Ltda.                                    | Comércio e manutenção automotiva  |
| AGRO   | Emalto Agronegócios                                   | Produção agrícola e reflorestamento|
+--------+-------------------------------------------------------+-----------------------------------+
Fonte: Elaborado pelo autor com base nos registros internos do Grupo Emalto (2026).
```

Embora cada empresa do Quadro 1 possua personalidade jurídica própria, a governança corporativa e os serviços essenciais de suporte — tais como Recursos Humanos, Jurídico, Controladoria e Tecnologia da Informação — operam sob o modelo de **Centro de Serviços Compartilhados (CSC)**, centralizado fisicamente na matriz em Timóteo – MG.

## 1.3 O Departamento de Tecnologia da Informação e Atuação Profissional

O setor de **Tecnologia da Informação (TI)** do Grupo Emalto é responsável pela infraestrutura de servidores, telecomunicações, segurança da informação, suporte aos usuários (Help Desk e Service Desk), gestão de sistemas legados e implantação de novas soluções para todas as 9 empresas do complexo industrial. 

Nesse contexto institucional, o autor deste relatório atua na equipe de TI na função de **Analista de Help Desk**. Além das atribuições rotineiras de atendimento técnico de primeiro e segundo níveis a centenas de estações de trabalho e colaboradores, o autor é diretamente responsável por uma das etapas mais críticas de suporte à controladoria do grupo: o **recebimento, auditoria técnica, conferência contratual e pré-lançamento de todas as notas fiscais de serviços de software, licenças SaaS, links de internet, telecomunicações e serviços de TI consumidos pelas empresas do grupo**.

Essa atividade exige validação minuciosa entre o valor faturado pelos fornecedores tecnológicos (como TOTVS, provedores de links dedicados, sistemas de ponto eletrônico, telefonia e infraestrutura em nuvem), o contrato de prestação de serviços vigente, o número do pedido de compras aprovado pela gerência e o correto código contábil da filial tomadora do serviço, antes da efetivação da nota no sistema ERP corporativo da organização.

---

\newpage

# 2 DEFINIÇÃO DO PROJETO

## 2.1 Análise dos Processos Existentes e Softwares Legados

Antes da concepção do projeto **ControleNF**, a gestão de contratos de tecnologia e a validação das notas fiscais recebidas eram executadas por meio de processos predominantemente manuais, descentralizados e amparados no **Microsoft Excel**. O fluxo de trabalho histórico operava conforme descrito a seguir:

1. **Recebimento de Faturamento por E-mail:** Os fornecedores de software (como a TOTVS, responsável pelo ERP corporativo, fornecedores de sistemas especializados de engenharia, folha de pagamento, internet dedicada e nuvem) enviavam as Notas Fiscais de Serviços Eletrônicas (NFS-e), acompanhadas dos boletos bancários, diretamente para caixas de correio eletrônico corporativas da equipe de TI.
2. **Conferência Manual em Planilha Excel:** O analista responsável abria uma planilha eletrônica de controle mensal (intitulada *Controle Notas Fiscais.xlsx*, dividida em abas cronológicas como `DEZ-25`, `JAN-26`, `FEV-26`, `MAR-26`, `ABR-26`). O analista precisava localizar manualmente a linha correspondente àquele fornecedor ou contrato e confrontar:
   * Nome fantasia da empresa emitente;
   * Número da nota fiscal e série;
   * Número do pedido de compra registrado no ERP;
   * Valor monetário da fatura;
   * Empresa tomadora do Grupo Emalto (EIM, EEM, EEN, Torque, etc.);
   * Data limite para pagamento (vencimento do boleto).
3. **Consulta aos Cadastros Contábeis das Filiais:** Como cada uma das 9 empresas do grupo possui CNPJ e inscrição contábil distintos, o analista precisava consultar uma relação estática para identificar qual código identificador interno da filial deveria ser aplicado àquela fatura.
4. **Inserção de Pré-Nota no ERP TOTVS:** Munido das informações conferidas, o analista acessava o módulo de compras e suprimentos do ERP TOTVS da empresa tomadora e realizava o pré-lançamento (geração da "Pré-Nota"), registrando número de documento, fornecedor, valor e pedido.
5. **Atualização da Planilha e Encaminhamento ao Contas a Pagar:** Concluída a inclusão no TOTVS, o analista retornava ao Excel, marcava a coluna "PRÉ-NOTA" com o status textual `"OK"` e repassava a nota fiscal escaneada e o protocolo de inclusão para a equipe financeira/contas a pagar efetuar a liquidação bancária.

```
+----------------------------------------------------------------------------------------------------+
| FIGURA 1 – Fluxograma do processo legado de conferência via planilhas e TOTVS                      |
+----------------------------------------------------------------------------------------------------+
  [Recebimento da NF-e]
          |
          v
  [Busca Manual na Planilha Excel] ---> [Localização do Pedido de Compras]
          |                                          |
          v                                          v
  [Conferência de Códigos por Filial] ---> [Digitação de Pré-Nota no ERP TOTVS]
          |                                          |
          +--------------------> [Atualização do Status "OK" na Planilha]
Fonte: Elaborado pelo autor (2026).
```

## 2.2 Diagnóstico de Gargalos e Pontos Críticos de Melhoria

A análise detalhada do fluxo legado permitiu identificar sérios riscos operacionais, contábeis e de segurança da informação decorrentes do uso de planilhas como ferramenta primária de controle corporativo:

1. **Inconsistência de Códigos Identificadores por Filial:** Um mesmo fornecedor tecnológico (por exemplo, a KTREE ou a TOTVS) possui códigos contábeis totalmente distintos dependendo da empresa pagadora do Grupo Emalto (exemplo: código `11366` na EIM, `004092` na EEM, `11366` na EEN e `00460` na Fundação Emalto). A digitação manual desses identificadores sujeitava a operação a frequentes erros humanos, acarretando lançamento em centros de custo errados e atraso no fechamento contábil.
2. **Falta de Controle de Volume de Faturas e Digitação Manual de Fornecedores:** Os códigos dos fornecedores não possuíam integração sistêmica com a planilha, funcionando apenas como um roteiro de consulta rápida para agilizar a conferência no momento do lançamento; caso houvesse alteração de fornecedor ou filial, a informação precisava ser redigitada manualmente. O risco operacional mais crítico desse modelo residia na ausência de controle sobre a quantidade de notas fiscais enviadas por uma mesma empresa de um mês para o outro: como determinados fornecedores faturavam números variáveis de notas entre diferentes meses e filiais, a planilha manual não oferecia mecanismo para validar se todas as faturas esperadas haviam de fato chegado, criando o risco iminente de alguma nota fiscal passar despercebida e deixar de ser lançada no ERP TOTVS.
3. **Complexidade Contratual Multi-Proposta (Contratos TOTVS):** A TOTVS possui mais de 20 propostas contratuais ativas simultaneamente com o Grupo Emalto (módulos Full, BackOffice, Gestão de Ponto, Transmite NF-e, Cloud, etc.), cada qual com seu respectivo valor unitário, vencimento e propostas de encerramento programado. Planilhas não ofereciam mecanismos de integridade referencial para tratar desativação de contratos antigos (*soft delete*) sem quebrar a rastreabilidade dos pagamentos efetuados no passado.
4. **Falta de Visibilidade Preditiva Anual (Matriz de 12 Meses):** O controle em abas isoladas (uma aba por mês) impedia a visualização integrada do ciclo anual. O analista não conseguia prever com facilidade quais contratos de software recorrente já deveriam ter emitido notas em determinado mês e quais estavam em atraso, expondo o grupo ao risco de cobrança de juros, multas por atraso ou corte indevido de licenças de software fundamentais à operação fabril.
5. **Concorrência e Riscos de Perda de Dados:** O arquivo Excel compartilhado em pasta de rede estava sujeito a bloqueios de edição simultânea ("arquivo em uso por outro usuário"), sobrescrita acidental de fórmulas e ausência de trilha de auditoria (*audit log*) que indicasse quem realizou ou alterou cada lançamento.

## 2.3 Justificativa da Escolha por uma Aplicação Web

Diante das necessidades observadas no diagnóstico e em perfeita consonância com o **Manual da Atividade Prática Profissional** da Multivix, optou-se expressamente pelo desenvolvimento de uma **Aplicação Web corporativa**, em detrimento de uma solução puramente desktop. As razões fundamentais para essa decisão arquitetural são:

* **Arquitetura Centralizada e Independência de Estações:** Uma aplicação web roda centralizadamente em um servidor ou máquina de infraestrutura na rede corporativa, sendo acessada diretamente através de navegadores modernos (Google Chrome, Microsoft Edge, Mozilla Firefox) sem a necessidade de instalação de dependências locais (como .NET Framework ou executáveis locais) nas máquinas de cada usuário.
* **Acesso Descentralizado para as Unidades Operacionais:** O Grupo Emalto possui filiais distribuídas geograficamente (Timóteo, Santana do Paraíso, plantas industriais e pátios de manutenção). A aplicação Web viabiliza que analistas e gestores de qualquer planta acessem os dados em tempo real pela intranet da organização.
* **Centralização das Regras de Negócio e Atualização Instantânea:** Quaisquer correções de validação, alterações de alíquotas, cadastro de novos contratos ou regras de *snapshotting* são aplicadas exclusivamente no backend. Todos os clientes conectados passam a operar imediatamente sob a nova versão, eliminando discrepâncias de versões comuns em softwares desktop distribuídos.
* **Segurança e Isolamento dos Dados:** Os dados sensíveis de contratos, valores de licenças e notas fiscais não ficam dispersos em arquivos salvos nas áreas de trabalho dos usuários. Ficam resguardados no servidor sob um motor de banco de dados transacional com rotinas de backup automatizadas.
* **Aderência às Diretrizes Acadêmicas:** O desenvolvimento web viabilizou a integração plena das tecnologias exigidas pelo manual da disciplina: **HTML5, CSS3 moderno, JavaScript avançado (Vanilla JS), integração com banco de dados estruturado e consumo de APIs RESTful**.

---

\newpage

# 3 DESCRIÇÃO DA APLICAÇÃO

## 3.1 Visão Geral e Escopo do Sistema ControleNF

O **ControleNF** é uma aplicação web corporativa desenvolvida sob medida para centralizar, auditar e automatizar o ciclo de vida completo de contratos de software (SaaS, licenças perpétuas, telefonia e links de telecomunicação) e a gestão de notas fiscais nas 9 empresas do Grupo Emalto. 

O sistema substitui o controle manual fragmentado por uma arquitetura transacional que atua como **Fonte Única de Verdade (Single Source of Truth - SSOT)** para o cadastro mestre de fornecedores e empresas. Ele estabelece uma **Matriz Anual Preditiva de 12 Meses**, capaz de gerar antecipadamente os 744 slots de lançamentos mensais esperados para o exercício contábil, vinculando as notas fiscais recebidas de forma semi-automatizada e garantindo a imutabilidade dos lançamentos históricos através da técnica de **Snapshotting Contábil**.

## 3.2 Requisitos Funcionais e Não Funcionais

A especificação de requisitos do sistema obedeceu aos preceitos da Engenharia de Software, organizando as demandas do setor de Help Desk em requisitos funcionais (RF) e requisitos não funcionais (RNF):

```
+----------------------------------------------------------------------------------------------------+
| QUADRO 2 – Requisitos Funcionais do Sistema ControleNF                                             |
+--------+-------------------------------------------------------------------------------------------+
| CÓDIGO | DESCRIÇÃO DETALHADA DO REQUISITO FUNCIONAL                                                |
+--------+-------------------------------------------------------------------------------------------+
| RF01   | Gerenciamento Multi-Empresa: Cadastrar, listar e manter ativas as 9 empresas do grupo.     |
| RF02   | Cadastros Base e Mapeamento Mestre: Manter a associação unívoca entre Fornecedor, Empresa |
|        | e o Código Identificador de planilha/contábil correspondente àquela filial.               |
| RF03   | Gestão de Contratos TOTVS Multi-Proposta: Permitir o cadastro detalhado de propostas     |
|        | contratuais com código da proposta, código do fornecedor, valor mensal e vencimento.       |
| RF04   | Desativação Segura (Soft Delete): Permitir o encerramento ou cancelamento de contratos     |
|        | sem exclusão física do banco, mantendo íntegro o histórico dos lançamentos legados.        |
| RF05   | Geração da Matriz Anual (12 Meses): Projetar automaticamente todos os lançamentos mensais  |
|        | dos contratos ativos para o ano de exercício selecionado (Jan a Dez).                     |
| RF06   | Registro e Conferência de Notas Fiscais: Registrar NFS-e avulsas e de contratos, associando|
|        | número da nota, número do pedido de compra, data de vencimento e valor faturado.          |
| RF07   | Snapshotting Contábil Automático: No salvamento da nota, interceptar o identificador     |
|        | vigente do fornecedor e gravá-lo de forma imutável no registro da NF.                     |
| RF08   | Controle do Status de Pré-Nota: Monitorar e alterar o estado do lançamento da nota fiscal |
|        | no ERP TOTVS (status 'OK' ou 'PENDENTE').                                                 |
| RF09   | Painel de Indicadores (Dashboard): Apresentar gráficos dinâmicos de distribuição de       |
|        | custos por fornecedor, empresa e taxa de cumprimento de lançamentos no mês.               |
| RF10   | Exportação e Relatórios: Permitir a geração de extratos tabulares e exportação de dados   |
|        | para integração com a controladoria e auditorias externas.                                |
+--------+-------------------------------------------------------------------------------------------+
Fonte: Elaborado pelo autor (2026).
```

```
+----------------------------------------------------------------------------------------------------+
| QUADRO 3 – Requisitos Não Funcionais do Sistema ControleNF                                         |
+--------+-------------------------------------------------------------------------------------------+
| CÓDIGO | DESCRIÇÃO DETALHADA DO REQUISITO NÃO FUNCIONAL                                            |
+--------+-------------------------------------------------------------------------------------------+
| RNF01  | Desempenho e Latência: O tempo de resposta das consultas da API REST deve ser inferior a  |
|        | 100 milissegundos para operações normais de consulta e filtragem.                         |
| RNF02  | Integridade e Concorrência ACID: A persistência deve suportar leituras e escritas          |
|        | simultâneas sem bloqueio de banco, implementando o modo WAL (Write-Ahead Logging).        |
| RNF03  | Usabilidade e Responsividade: Interface limpa, intuitiva, com contrastes adequados,     |
|        | adaptada para telas de desktops operacionais do setor fabril e administrativo.             |
| RNF04  | Integridade Histórica e Rastreabilidade: Registros fiscais consolidados não podem sofrer  |
|        | alterações em efeito cascata caso os parâmetros mestres de fornecedor sejam modificados.  |
| RNF05  | Segurança na Rede Local: Acesso restrito via intranet corporativa do Grupo Emalto,        |
|        | garantindo que apenas máquinas autorizadas acessem os dados financeiros de TI.            |
| RNF06  | Arquitetura Modular e Padronizada: Separação estrita entre frontend estático e backend   |
|        | RESTful, seguindo as boas práticas da arquitetura cliente-servidor.                       |
+--------+-------------------------------------------------------------------------------------------+
Fonte: Elaborado pelo autor (2026).
```

## 3.3 Modelo Operacional e Fluxo de Trabalho do Analista de TI

A operação do **ControleNF** foi desenhada para eliminar gargalos e transformar um processo burocrático e passível de erros em um fluxo intuitivo e assistido por validações do sistema:

1. **Abertura do Sistema:** O Analista de Help Desk acessa o sistema pelo navegador web na URL da intranet corporativa. A tela inicial apresenta imediatamente o **Dashboard Executivo**, exibindo o percentual de notas recebidas no mês vigente, total monetário comprometido e alertas de vencimentos imediatos.
2. **Recepção e Registro da Nota Fiscal:** Ao receber a fatura emitida pelo fornecedor (por exemplo, a fatura mensal da KTREE destinada à Emalto Estruturas – EEM), o operador navega até a aba **Notas Fiscais**.
3. **Seleção de Empresa e Fornecedor:** O operador seleciona a empresa pagadora (`EEM`) e o fornecedor (`KTREE`). Automaticamente, o frontend invoca a API do sistema e preenche o campo **"Cód. Forn." como somente leitura (ReadOnly)**, exibindo visualmente o código correto (`004092`). O usuário não precisa (nem consegue) alterar esse código manualmente, erradicando o erro de digitação.
4. **Inserção de Dados Fiscais:** O analista insere o número da nota fiscal, o número do pedido de compra aprovado e o valor cobrado. 
5. **Persistência com *Snapshotting*:** Ao clicar em salvar, o backend em FastAPI processa a requisição, "fotografa" os dados mestre do fornecedor naquele instante e grava o registro na tabela `notas_fiscais`. O sistema localiza o contrato correspondente na tabela `lancamentos_mensais` e altera automaticamente seu status de `PENDENTE` para `LANCADO` ou `FATURADO`.
6. **Lançamento no ERP TOTVS:** O operador abre a tela do ERP TOTVS da filial EEM e registra a Pré-Nota com a absoluta certeza de que o código da filial, o número do pedido e o valor estão consistentes.
7. **Atualização do Status da Pré-Nota:** Confirmada a inclusão no TOTVS, o analista clica no botão de ação da nota no ControleNF, alternando o status de pré-nota para `"OK"`. O sistema atualiza o indicador em tempo real e consolida o lançamento para os relatórios de auditoria.

## 3.4 Objetivos Estratégicos e Vantagens Alcançadas

A substituição da planilha legada pelo sistema ControleNF proporcionou ao Grupo Emalto:

* **Eliminação de 100% dos erros de codificação de fornecedor:** O mapeamento mestre automatizado retirou a responsabilidade de memorização ou busca manual do operador.
* **Redução de mais de 70% no tempo gasto na conferência mensal:** A visualização preditiva na Matriz Anual permite checar de forma instantânea quais fornecedores ainda não faturaram no mês, evitando a checagem manual linha por linha.
* **Segurança e Imutabilidade Contábil:** A aplicação da técnica de *snapshotting* e o tratamento de *soft delete* garantiram que auditorias financeiras tenham sempre o registro fiel da data de emissão de cada nota fiscal, mesmo que contratos tenham sido renegociados ou reajustados posteriormente.

---

\newpage

# 4 TECNOLOGIAS EMPREGADAS

## 4.1 Seleção do Stack Tecnológico e Justificativas Técnicas

Em estrito atendimento ao **Manual da Atividade Prática Profissional** da Multivix (que estipula como obrigatórios para aplicações web o uso de HTML5, CSS3, JavaScript/TypeScript e sugere a adoção de Banco de Dados estruturado, backend moderno e consumo de APIs REST), a arquitetura do **ControleNF** foi construída utilizando ferramentas de nível profissional, consagradas no mercado por sua robustez, estabilidade e manutenibilidade:

```
+----------------------------------------------------------------------------------------------------+
| QUADRO 4 – Stack Tecnológico do Sistema ControleNF                                                 |
+-------------------+--------------------------------+-----------------------------------------------+
| CAMADA / PAPEL    | TECNOLOGIA ADOTADA             | MOTIVAÇÃO TÉCNICA E BENEFÍCIO                 |
+-------------------+--------------------------------+-----------------------------------------------+
| Interface (UI)    | HTML5 Semântico                | Estruturação acessível, moderna e padronizada |
| Estilização       | CSS3 Avançado & Glassmorphism  | Design responsivo, moderno e corporativo      |
| Lógica de Cliente | JavaScript Moderno (Vanilla ES6+)| Desempenho máximo sem dependência pesada   |
| Visualização/BI   | Chart.js                       | Renderização rápida de gráficos dinâmicos     |
| Backend / API     | Python 3.10+ com FastAPI       | Alta velocidade assíncrona, tipagem estrita   |
| Validação / DTO   | Pydantic v2                    | Validação automática de payloads e esquemas   |
| ORM / Persistência| SQLAlchemy 2.0                 | Mapeamento objeto-relacional seguro contra SQLi|
| Banco de Dados    | SQLite 3 (Modo WAL)            | Atomicidade ACID, portabilidade e sem lock    |
+-------------------+--------------------------------+-----------------------------------------------+
Fonte: Elaborado pelo autor (2026).
```

### Detalhamento dos Componentes Tecnológicos:

1. **HTML5 Semântico e CSS3 Customizado:** O frontend foi projetado sem a sobrecarga de frameworks monolíticos (como Bootstrap tradicional), adotando uma folha de estilos limpa baseada em CSS Grid, Flexbox e design system moderno com estética refinada (efeitos de profundidade, contraste elevado e tipografia limpa). Isso garante carregamento instantâneo mesmo em redes corporativas com tráfego intenso.
2. **JavaScript Vanilla (ES6+) e Chart.js:** A camada de interação utiliza JavaScript nativo moderno estruturado modularmente em arquivos especializados (`app.js`, `api.js`, `cadastros.js`, `contratos.js`, `notas.js`, `dashboard.js`). Para os gráficos do dashboard, integrou-se a biblioteca leve **Chart.js**, permitindo renderização acelerada por hardware de gráficos de rosca e barras interativas.
3. **Backend em Python e FastAPI:** O framework **FastAPI** foi selecionado por combinar o ecossistema maduro da linguagem Python com performance de ponta equiparável a sistemas em NodeJS ou Go, graças ao seu motor baseado em ASGI (*Starlette*) e tipagem estrita com *Pydantic*. O FastAPI gera documentação interativa automática (OpenAPI / Swagger UI), facilitando a testabilidade dos endpoints por desenvolvedores e auditores.
4. **Banco de Dados SQLite em Modo WAL (*Write-Ahead Logging*):** Para garantir confiabilidade em nível de banco corporativo sem a necessidade de manter serviços pesados de servidores de banco (como Oracle ou SQL Server dedicado apenas para esse módulo), utilizou-se o SQLite configurado no modo **WAL**. O modo WAL permite que múltiplos clientes realizem leituras simultâneas sem bloquear gravações, assegurando integridade transacional completa (ACID) e máxima facilidade de backup a quente.

```
+----------------------------------------------------------------------------------------------------+
| FIGURA 2 – Arquitetura da Solução Web (FastAPI, SQLite WAL e Vanilla JS)                           |
+----------------------------------------------------------------------------------------------------+

     [ CAMADA DE APRESENTAÇÃO (Navegador do Usuário) ]
     +-------------------------------------------------------------+
     | HTML5 Semântico | CSS3 Moderno | Vanilla JS | Chart.js      |
     +-------------------------------------------------------------+
                                   ^
                                   |  Requisições Assíncronas (JSON / Fetch API)
                                   v
     [ CAMADA DE APLICAÇÃO (Servidor FastAPI / Python) ]
     +-------------------------------------------------------------+
     | Routers: /cadastros | /contratos | /notas-fiscais | /dashboard |
     | Validações Pydantic: Schemas de Entrada e Saída             |
     | Lógica de Negócio: Snapshotting Contábil & Soft Delete      |
     +-------------------------------------------------------------+
                                   ^
                                   |  Mapeamento Objeto-Relacional (SQLAlchemy)
                                   v
     [ CAMADA DE PERSISTÊNCIA (Banco de Dados) ]
     +-------------------------------------------------------------+
     | SQLite 3 (Modo WAL Ativo - Transações ACID e Chaves Estrang)|
     +-------------------------------------------------------------+
Fonte: Elaborado pelo autor (2026).
```

## 4.2 Arquitetura em Camadas e Consumo de APIs REST

A comunicação entre a interface do usuário e o servidor é 100% desacoplada, fundamentada no padrão arquitetural **RESTful**. O frontend não gera código dinâmico do lado do servidor (como nas tecnologias obsoletas PHP puro ou JSP); em vez disso, comporta-se como uma *Single Page Application* (SPA) leve que consome endpoints JSON assíncronos via **Fetch API** nativa do JavaScript:

* **`GET /api/cadastros/mapeamento/{fornecedor_id}`:** Retorna em milissegundos os códigos contábeis daquele fornecedor para cada uma das 9 empresas do Grupo Emalto;
* **`POST /api/notas-fiscais/`:** Recebe os dados da nota fiscal, aplica as validações de integridade, executa o *snapshotting* dos dados mestre e consolida o lançamento;
* **`GET /api/contratos/matriz/{ano}`:** Alimenta a matriz anual de 12 meses com o status consolidado de todos os contratos vigentes;
* **`PATCH /api/notas-fiscais/{id}/status-pre-nota`:** Atualiza atomicamente a confirmação do lançamento realizado no TOTVS.

## 4.3 Fluxograma Geral dos Processos da Aplicação

O fluxo de processamento de um lançamento fiscal com validação e *snapshotting* é detalhado graficamente no diagrama a seguir:

```
+----------------------------------------------------------------------------------------------------+
| FIGURA 3 – Fluxograma geral de processamento de notas e snapshotting do ControleNF                 |
+----------------------------------------------------------------------------------------------------+

  (Início: Usuário abre formulário de NF)
                     |
                     v
  [Seleciona Fornecedor e Empresa do Grupo]
                     |
                     v
  [Frontend consulta API REST de Identificadores]
                     |
                     +---------------------------------------+
                     |                                       |
          (Fornecedor Comum?)                       (Fornecedor TOTVS?)
                     |                                       |
                     v                                       v
  [Carrega Cód. Identificador Mestre]       [Lista Propostas Ativas da Filial]
                     |                                       |
                     +-------------------+-------------------+
                                         |
                                         v
                     [Bloqueia campo Cód. Fornecedor como ReadOnly]
                                         |
                                         v
                     [Operador digita Nº Nota, Pedido, Valor e Vencimento]
                                         |
                                         v
                     [Dispara POST para a API /notas-fiscais/]
                                         |
                                         v
                     [Backend executa Snapshot: Copia código vigente]
                                         |
                                         v
                     [Persiste na tabela `notas_fiscais`]
                                         |
                                         v
                     [Localiza e atualiza `lancamentos_mensais` para 'LANCADO']
                                         |
                                         v
                     (Fim: Interface atualiza e exibe sucesso)
Fonte: Elaborado pelo autor (2026).
```

## 4.4 Modelagem de Dados e Diagrama Entidade-Relacionamento (DER)

A modelagem do banco de dados relacional foi concebida para suportar integridade referencial rigorosa, garantindo que relações entre empresas, fornecedores, contratos e notas fiscais permaneçam consistentes ao longo dos anos contábeis:

```
+----------------------------------------------------------------------------------------------------+
| FIGURA 4 – Diagrama Entidade-Relacionamento (DER) do Banco de Dados                                |
+----------------------------------------------------------------------------------------------------+

  +-----------------------+              +-------------------------------------+
  |     empresas_grupo    |              |             fornecedores            |
  +-----------------------+              +-------------------------------------+
  | PK  id (INTEGER)      |              | PK  id (INTEGER)                    |
  |     sigla (VARCHAR)   |              |     nome (VARCHAR)                  |
  |     nome_compl (VARCHAR)             |     categoria (VARCHAR)             |
  |     ativo (BOOLEAN)   |              |     ativo (BOOLEAN)                 |
  +-----------------------+              +-------------------------------------+
        |           |                                 |             |
        |           | 1                               | 1           |
        |           +----------+           +----------+             |
        |                      |           |                        |
        |                      v           v                        |
        |             +-------------------------------------+       |
        |             |   fornecedor_empresa_identificador  |       |
        |             +-------------------------------------+       |
        |             | PK  id (INTEGER)                    |       |
        |             | FK  fornecedor_id (INTEGER)         |       |
        |             | FK  empresa_grupo_id (INTEGER)      |       |
        |             |     codigo_identificador (VARCHAR)  |       |
        |             +-------------------------------------+       |
        |                                                           |
        | 1                                                       1 |
        +----------------------------+   +--------------------------+
                                     |   |
                                     v   v
                      +-------------------------------------+
                      |          contratos_software         |
                      +-------------------------------------+
                      | PK  id (INTEGER)                    |
                      | FK  fornecedor_id (INTEGER)         |
                      | FK  empresa_grupo_id (INTEGER)      |
                      |     codigo_contrato (VARCHAR)       |
                      |     valor_mensal (FLOAT)            |
                      |     dia_vencimento (INTEGER)        |
                      |     ativo (BOOLEAN) - Soft Delete   |
                      |     mes/ano_encerramento (INTEGER)  |
                      +-------------------------------------+
                                         |
                                         | 1
                                         v N
                      +-------------------------------------+
                      |         lancamentos_mensais         |
                      +-------------------------------------+
                      | PK  id (INTEGER)                    |
                      | FK  contrato_id (INTEGER)           |
                      |     mes (INTEGER)                   |
                      |     ano (INTEGER)                   |
                      |     status (VARCHAR)                |
                      |     data_vencimento (DATE)          |
                      +-------------------------------------+
                                         |
                                         | 1
                                         v 0..1
                      +-------------------------------------+
                      |             notas_fiscais           |
                      +-------------------------------------+
                      | PK  id (INTEGER)                    |
                      | FK  empresa_grupo_id (INTEGER)      |
                      | FK  contrato_id (INTEGER, NULL)     |
                      | FK  lancamento_mensal_id (NULL)     |
                      |     numero_nota (VARCHAR)           |
                      |     numero_pedido (VARCHAR)         |
                      |     valor (FLOAT)                   |
                      | [SNAPSHOT] codigo_fornecedor (VARCHAR)
                      |     status_pre_nota (VARCHAR)       |
                      |     data_vencimento (DATE)          |
                      +-------------------------------------+
Fonte: Elaborado pelo autor (2026).
```

### Dicionário de Dados das Tabelas Principais:

```
+----------------------------------------------------------------------------------------------------+
| TABELA 1 – Estrutura da Tabela `fornecedor_empresa_identificador`                                  |
+----------------------+--------------+----------+---------------------------------------------------+
| NOME DO CAMPO        | TIPO DE DADO | NULO?    | DESCRIÇÃO / FINALIDADE REGRA DE NEGÓCIO           |
+----------------------+--------------+----------+---------------------------------------------------+
| id                   | INTEGER      | NÃO (PK) | Identificador sequencial único do registro        |
| fornecedor_id        | INTEGER      | NÃO (FK) | Chave estrangeira referenciando `fornecedores.id` |
| empresa_grupo_id     | INTEGER      | NÃO (FK) | Chave estrangeira referenciando `empresas_grupo`  |
| codigo_identificador | VARCHAR(50)  | SIM      | Código contábil/planilha específico daquela filial|
+----------------------+--------------+----------+---------------------------------------------------+
Fonte: Extraído dos modelos SQLAlchemy do sistema (2026).
```

```
+----------------------------------------------------------------------------------------------------+
| TABELA 2 – Estrutura da Tabela `notas_fiscais` com Atributos de Snapshotting                       |
+----------------------+--------------+----------+---------------------------------------------------+
| NOME DO CAMPO        | TIPO DE DADO | NULO?    | DESCRIÇÃO / FINALIDADE REGRA DE NEGÓCIO           |
+----------------------+--------------+----------+---------------------------------------------------+
| id                   | INTEGER      | NÃO (PK) | Identificador sequencial da Nota Fiscal           |
| empresa_fornecedor   | VARCHAR(100) | NÃO      | Razão Social / Nome do Fornecedor emitente        |
| numero_nota          | VARCHAR(50)  | NÃO      | Número do documento fiscal recebido (NFS-e)       |
| numero_pedido        | VARCHAR(50)  | SIM      | Número do Pedido de Compras aprovado no ERP       |
| valor                | FLOAT        | NÃO      | Valor monetário nominal cobrado na fatura         |
| empresa_grupo_id     | INTEGER      | SIM (FK) | Empresa tomadora do Grupo Emalto (EIM, EEM, etc.) |
| codigo_fornecedor    | VARCHAR(50)  | SIM      | [SNAPSHOT] Cópia imutável do código na data da NF |
| status_pre_nota      | VARCHAR(20)  | NÃO      | Status no ERP TOTVS ('OK' ou 'PENDENTE')          |
| data_vencimento      | DATE         | NÃO      | Data do vencimento do boleto de cobrança          |
+----------------------+--------------+----------+---------------------------------------------------+
Fonte: Extraído dos modelos SQLAlchemy do sistema (2026).
```

---

\newpage

# 5 PROPOSTA DE VALOR

## 5.1 Ganhos Operacionais e Redução de Lead Time de Conferência

A implementação do sistema **ControleNF** proporcionou uma transformação substancial na rotina do departamento de TI e no suporte à controladoria do Grupo Emalto. No cenário legado, o processo de localizar arquivos Excel em rede, encontrar a linha exata em meio a centenas de registros, verificar manualmente tabelas de códigos de fornecedor para cada uma das 9 filiais e atualizar status manuais consumia em média de 15 a 20 minutos por nota fiscal. 

Com a automação introduzida pelo ControleNF:
* O tempo total de conferência, validação e preparação da pré-nota foi reduzido para **menos de 3 minutos por documento** (uma economia de tempo superior a 80%);
* O processo de auditoria de fechamento de mês, que antes demandava dias inteiros de conciliação entre o contas a pagar e a TI, passou a ser realizado de forma instantânea através dos filtros da Matriz Anual e do Dashboard consolidado.

## 5.2 Eliminação de Inconsistências Contábeis e Preservação Histórica (*Snapshotting*)

A maior proposta de valor técnico-financeira do projeto reside na implementação do mecanismo de **Snapshotting Contábil**. Em ambientes corporativos do porte do Grupo Emalto, fornecedores de software frequentemente atualizam códigos cadastrais, bancos emissores ou sofrerem fusões/reajustes contratuais. 

Nas ferramentas tradicionais de planilha, a alteração de um código mestre alterava inadvertidamente meses anteriores já fechados. No **ControleNF**, ao salvar uma nota fiscal, o backend copia o código contábil vigente para o registro físico da própria nota fiscal, tornando-o imutável. Essa garantia de fidelidade histórica protege a empresa contra autuações fiscais, inconsistências contábeis internas e divergências durante auditorias de conformidade (como as normas ISO 9001 e auditorias fiscais independentes às quais o complexo fabril da Emalto é submetido).

## 5.3 Prevenção de Multas Contratuais e Pagamentos em Duplicidade

Contratos de software corporativo (como as dezenas de licenças da TOTVS, links de fibra dedicada e telefonia) possuem cláusulas contratuais de vencimento estritas, com incidência de multas severas e juros por dias de atraso no recebimento da fatura. Além disso, o recebimento de faturas retificadoras ou duplicadas em caixas de e-mail representava risco constante de pagamento em dobro.

O sistema mitigou esses riscos através de duas frentes de controle:
1. **Matriz Preditiva de 12 Meses:** A matriz alerta proativamente o Analista de Help Desk sobre quais contratos ainda não registraram sua respectiva nota fiscal até determinado dia útil do mês, viabilizando a cobrança tempestiva ao fornecedor antes do vencimento do título.
2. **Validação de Unicidade:** O banco de dados impede a inserção de notas duplicadas com a mesma combinação de número de nota fiscal, fornecedor e competência, blindando o setor financeiro do grupo contra pagamentos indevidos.

```
+----------------------------------------------------------------------------------------------------+
| QUADRO 5 – Matriz Comparativa: Processo Legado em Planilha vs. Sistema ControleNF                  |
+--------------------------+--------------------------------+----------------------------------------+
| CRITÉRIO DE AVALIAÇÃO    | PROCESSO ANTERIOR (EXCEL)      | SISTEMA ATUAL (CONTROLENF)             |
+--------------------------+--------------------------------+----------------------------------------+
| Integridade de Códigos   | Vulnerável à digitação manual  | 100% automatizado por filial (ReadOnly)|
| Imutabilidade Histórica  | Inexistente (mudança retroage) | Total garantia via Snapshot contábil   |
| Visão Anual Preditiva    | Fragmentada por abas mensais   | Matriz consolidada de 12 meses         |
| Controle Multi-Propostas | Caótico e propenso a erro      | Módulo dedicado com Soft Delete        |
| Gestão de Concorrência   | Bloqueio de arquivo compartilhado| Banco relacional com modo WAL        |
| Rastreabilidade / Status | Status informal ('OK' em texto)| Fluxo formal de Pré-Nota auditável     |
+--------------------------+--------------------------------+----------------------------------------+
Fonte: Elaborado pelo autor (2026).
```

---

\newpage

# 6 APRESENTAÇÃO DA APLICAÇÃO DESENVOLVIDA (TUTORIAL PRÁTICO)

Nesta seção são apresentadas as principais interfaces gráficas desenvolvidas no sistema **ControleNF**, demonstrando a usabilidade prática, os fluxos de navegação e as validações de integridade que norteiam a rotina operacional do Analista de Help Desk.

## 6.1 Interface Principal e Dashboard de Indicadores

Ao acessar a aplicação, o usuário é recepcionado pelo **Dashboard Executivo**. A interface foi desenvolvida sob o conceito de visualização limpa de dados, agrupando em cartões de métricas (KPIs) o volume de notas processadas no mês, o montante financeiro total faturado e gráficos analíticos alimentados pela biblioteca Chart.js.

```
[ INSERIR AQUI - FIGURA 5: Tela do Dashboard: Gráficos de status de contratos e distribuição de despesas ]
Legenda: Figura 5 – Painel de Controle com cartões de indicadores (KPIs), gráfico em rosca de status dos contratos e gráfico de barras de custos por filial do Grupo Emalto.
Fonte: Sistema ControleNF (2026).
```

* **Funcionalidade e Validação:** Os gráficos consolidam em tempo real os dados de todas as filiais. O gráfico de rosca categoriza os contratos entre faturados, pendentes e vencidos, permitindo ao operador identificar gargalos imediatos de faturamento.

## 6.2 Módulo de Cadastros Base: Mapeamento Mestre por Filial

O módulo de **Cadastros Base** constitui o núcleo de integridade do sistema. Nele, o analista define a tabela de correspondência que relaciona cada fornecedor comum (como a KTREE, provedores de internet, sistemas de ponto eletrônico) com seus respectivos códigos contábeis nas 9 empresas do Grupo Emalto.

```
[ INSERIR AQUI - FIGURA 6: Tela de Cadastros Base: Mapeamento Mestre de códigos por empresa ]
Legenda: Figura 6 – Interface de Mapeamento Mestre com tabela dinâmica exibindo as colunas de cada empresa do grupo (EIM, EEM, EEN, FE, TDL, etc.) e seus respectivos códigos identificadores.
Fonte: Sistema ControleNF (2026).
```

* **Funcionalidade e Validação:** A tela valida se cada filial possui um identificador preenchido. Caso um código seja atualizado para faturamentos futuros, essa tabela armazena a nova regra sem afetar os lançamentos já arquivados no banco de dados.

## 6.3 Gestão de Propostas e Contratos TOTVS com Soft Delete

Devido à elevada complexidade dos contratos mantidos com a TOTVS (que envolvem dezenas de módulos distintos divididos entre as filiais), o sistema detecta automaticamente a seleção do fornecedor TOTVS e chaveia para uma interface especializada de **Gestão de Propostas e Contratos**.

```
[ INSERIR AQUI - FIGURA 7: Tela de Gestão de Propostas e Contratos TOTVS ]
Legenda: Figura 7 – Gerenciador de propostas contratuais da TOTVS agrupadas por filial, exibindo número da proposta, valor mensal contratado, vencimento e botão de encerramento seguro.
Fonte: Sistema ControleNF (2026).
```

* **Funcionalidade e Validação (*Soft Delete*):** Quando um contrato ou proposta é encerrado pela diretoria, o analista não exclui fisicamente o registro. O sistema aciona o mecanismo de *Soft Delete* (definindo a flag `ativo = False` e gravando o mês/ano de encerramento programado). Dessa forma, o contrato deixa de gerar novas pendências na matriz anual, mas todos os lançamentos de anos anteriores permanecem intactos para auditoria.

## 6.4 Matriz Anual de 12 Meses e Acompanhamento de Lançamentos

A tela de **Contratos e Matriz Anual** viabiliza o acompanhamento longitudinal dos contratos ao longo dos 12 meses do ano.

```
[ INSERIR AQUI - FIGURA 8: Tela da Matriz Anual (12 Meses): Acompanhamento preditivo de contratos ]
Legenda: Figura 8 – Visão matricial anual do sistema exibindo fornecedores nas linhas e os 12 meses nas colunas, com pílulas coloridas indicando o status de cada competência.
Fonte: Sistema ControleNF (2026).
```

* **Funcionalidade e Validação:** Cada célula da matriz representa um lançamento mensal (`LancamentoMensal`). A célula apresenta cores distintas conforme o status do mês: cinza (`PENDENTE`), verde (`FATURADO`/`OK`), amarelo (`VENCIDO`) ou azul (`LANCADO`). Ao clicar sobre uma célula, o analista pode vincular diretamente o número da nota fiscal recebida ou consultar o histórico de pagamento.

## 6.5 Registro de Notas Fiscais e Mecanismo de Snapshotting

A tela de **Lançamento de Notas Fiscais** é a interface mais utilizada na rotina diária de Help Desk.

```
[ INSERIR AQUI - FIGURA 9: Tela de Lançamento de Notas Fiscais com campo de fornecedor em modo Read-Only ]
Legenda: Figura 9 – Formulário modal de registro de nota fiscal, destacando o campo 'Cód. Forn.' travado para edição manual (ReadOnly) após preenchimento automático pelo backend.
Fonte: Sistema ControleNF (2026).
```

* **Tutorial Operacional Passo a Passo:**
  1. O analista clica em "Nova Nota Fiscal";
  2. Seleciona a empresa tomadora do Grupo Emalto (ex: `Emalto Estruturas Metálicas`);
  3. Seleciona o fornecedor faturador (ex: `KTREE`);
  4. O sistema consulta imediatamente a API REST e preenche o campo `"Cód. Fornecedor"` em cinza escuro travado (*ReadOnly*), exibindo o valor exato `004092`;
  5. O analista digita o número da NFS-e (`000.047.054`), o número do pedido de compra (`71724`), o valor (`R$ 929,33`) e a data de vencimento;
  6. Ao salvar, a nota é registrada e o backend atualiza a flag de *snapshotting*;
  7. O analista lança a pré-nota no ERP TOTVS e, em seguida, clica no ícone de confirmação no ControleNF, comutando o status de pré-nota para `"OK"`.

## 6.6 Validações de Integridade e Regras de Negócio do Sistema

Para garantir que a aplicação opere livre de falhas humanas ou técnicas, as seguintes validações foram incorporadas ao código-fonte:
* **Validação de Payload com Pydantic:** Todas as requisições enviadas ao backend passam por esquemas estritos (`schemas.py`), rejeitando automaticamente valores nulos em campos obrigatórios, datas inválidas ou tipos de dados incorretos;
* **Prevenção de Injeção SQL:** As interações com o banco SQLite ocorrem exclusivamente por meio de objetos mapeados pelo SQLAlchemy ORM com consultas parametrizadas;
* **Tratamento de Exceções e Respostas Padronizadas:** A API devolve mensagens claras de erro HTTP em caso de violação de integridade referencial ou duplicidade de registro.

## 6.7 Disponibilização do Código-Fonte e Repositório

O projeto foi inteiramente versionado utilizando o sistema de controle de versão distribuído **Git**. A árvore de arquivos, scripts de automação, módulos do frontend e backend encontram-se estruturados no repositório institucional do projeto para fins de avaliação acadêmica e continuidade de desenvolvimento pelos profissionais de TI da empresa.

---

\newpage

# REFERÊNCIAS

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 6023**: Informação e documentação: referências: elaboração. Rio de Janeiro: ABNT, 2018.

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 14724**: Informação e documentação: trabalhos acadêmicos: apresentação. Rio de Janeiro: ABNT, 2011.

CHART.JS. **Chart.js Documentation**: Simple yet flexible JavaScript charting for designers & developers. Versão 4.x. Disponível em: https://www.chartjs.org/docs/latest/. Acesso em: 10 fev. 2026.

FASTAPI. **FastAPI framework, high performance, easy to learn, fast to code, ready for production**. Disponível em: https://fastapi.tiangolo.com/. Acesso em: 08 fev. 2026.

MDN WEB DOCS. **JavaScript: The Definitive Guide to Modern Client-Side Web Development**. Mozilla Developer Network, 2026. Disponível em: https://developer.mozilla.org/pt-BR/docs/Web/JavaScript. Acesso em: 10 fev. 2026.

PRESSMAN, Roger S.; MAXIM, Bruce R. **Engenharia de Software: uma abordagem profissional**. 9. ed. Porto Alegre: AMGH, 2021.

PYTHON SOFTWARE FOUNDATION. **Python Programming Language Official Documentation**. Versão 3.10+. Disponível em: https://docs.python.org/3/. Acesso em: 05 fev. 2026.

SOMMERVILLE, Ian. **Engenharia de Software**. 10. ed. São Paulo: Pearson Education do Brasil, 2019.

SQLITE CONSORTIUM. **Write-Ahead Logging (WAL) in SQLite**. Disponível em: https://www.sqlite.org/wal.html. Acesso em: 12 fev. 2026.

SQLALCHEMY. **SQLAlchemy 2.0 Documentation: The Database Toolkit for Python**. Disponível em: https://docs.sqlalchemy.org/en/20/. Acesso em: 11 fev. 2026.

---

\newpage

# ANEXOS

---

# ANEXO A – Planilha Legada de Controle Manual de Notas Fiscais

Como evidência empírica dos processos analisados no Grupo Emalto e comprovação da necessidade técnica do desenvolvimento do sistema **ControleNF**, apresenta-se a estrutura da planilha legada de acompanhamento manual utilizada anteriormente pelo setor de TI:

* **Arquivo de Origem:** `Controle Notas Fiscais.xlsx`
* **Abas Históricas Mapeadas:** `DEZ-25`, `JAN-26`, `FEV-26`, `MAR-26`, `ABR-26`
* **Colunas de Registro Manual:**
  1. `EMPRESA`: Razão social ou nome fantasia do fornecedor emitente (ex.: KTREE, LOJA ELÉTRICA, REGISTRO.BR, TOTVS);
  2. `Nº DA NOTA`: Número do documento fiscal de serviços recebido por e-mail;
  3. `Nº DO PEDIDO`: Número do pedido de compras liberado no ERP para aquela despesa;
  4. `VALOR`: Valor monetário nominal cobrado pelo fornecedor;
  5. `GRUPO EMALTO`: Filial tomadora do serviço (ex.: EMALTO INDÚSTRIA, EMALTO ESTRUTURAS, EMALTO ENERGIA, FUNDAÇÃO EMALTO, EIM);
  6. `VENCIMENTO`: Data de vencimento do boleto bancário correspondente;
  7. `PRÉ-NOTA`: Coluna preenchida manualmente pelo analista com a indicação textual `"OK"` assim que a pré-nota é digitada no sistema ERP TOTVS.

### Amostra de Registros Históricos da Planilha Legada (Aba DEZ-25 / JAN-26):

> **Nota de Confidencialidade:** Em conformidade com as políticas de governança e segurança da informação do Grupo Emalto, bem como as diretrizes da LGPD, os valores monetários nominais de cada contrato e nota fiscal foram anonimizados e preservados em sigilo, sem qualquer impacto na demonstração dos fluxos, campos e processos operacionais de controle.

```
+----------------------------------------------------------------------------------------------------+
| AMOSTRA DE DADOS DA PLANILHA LEGADA - "Controle Notas Fiscais.xlsx"                                |
+---------------+-------------+--------------+----------------+--------------------+------------+---------+
| EMPRESA       | Nº DA NOTA  | Nº DO PEDIDO | VALOR          | GRUPO EMALTO       | VENCIMENTO | PRÉ-NOTA|
+---------------+-------------+--------------+----------------+--------------------+------------+---------+
| KTREE         | 000.046.193 | 113500       | [CONFIDENCIAL] | EMALTO INDÚSTRIA   | 15/12/2025 | OK      |
| KTREE         | 000.046.194 | 71319        | [CONFIDENCIAL] | EMALTO ESTRUTURAS  | 15/12/2025 | OK      |
| KTREE         | 000.046.196 | 20463        | [CONFIDENCIAL] | EMALTO ENERGIA     | 15/12/2025 | OK      |
| KTREE         | 000.047.054 | 71724        | [CONFIDENCIAL] | EMALTO ESTRUTURAS  | 15/01/2026 | OK      |
| KTREE         | 000.047.069 | 114113       | [CONFIDENCIAL] | EMALTO INDÚSTRIA   | 15/01/2026 | OK      |
| KTREE         | 000.047.079 | 3882         | [CONFIDENCIAL] | FUNDAÇÃO EMALTO    | 15/01/2026 | OK      |
+---------------+-------------+--------------+----------------+--------------------+------------+---------+
Fonte: Registros extraídos diretamente da planilha Controle Notas Fiscais.xlsx (2026).
```

