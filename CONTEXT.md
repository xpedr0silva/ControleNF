# Contexto do Projeto - ControleNF - Grupo Emalto

## Evolução e Arquitetura do Sistema

O sistema evoluiu de planilhas locais para uma arquitetura centralizada. Uma das maiores mudanças foi a transição para a lógica de **Fonte Única de Verdade (Single Source of Truth)** para o cadastro de identificadores e contratos, garantindo consistência, e **Snapshotting (Fotografia)** no lançamento de Notas Fiscais, garantindo a imutabilidade do histórico.

---

## Decisões Tomadas e Implementações

### 1. Novo Módulo Central: "Cadastros Base" (12/Mai/2026)

**Problema:** Antigamente, o usuário precisava digitar o `codigo_fornecedor` diretamente na Nota Fiscal (ou no contrato, que acabava conflitando). Como uma mesma empresa (ex: KTREE) possui códigos diferentes dependendo da filial (EIM, EEM, etc), ocorriam erros de preenchimento. A lógica descentralizada tornava a manutenção caótica.

**Solução:** Foi criada a interface centralizada **Cadastros Base**. Ela substituiu as antigas abas de "Empresas" e "Fornecedores".
A tela possui dois modos de funcionamento inteligente com base no Fornecedor selecionado:

#### A. Modo Comum ("Mapeamento Mestre")
Aplicado a fornecedores convencionais (ex: KTREE). Exibe uma tabela onde o usuário vincula o código de planilha usado para aquele fornecedor em cada uma das filiais do grupo Emalto.
- **Implementação:** Criação da tabela `fornecedor_empresa_identificador` (`models.py`) e novo roteador `backend/routers/cadastros.py`.

#### B. Modo TOTVS (Propostas e Contratos Específicos)
Aplicado automaticamente se o nome do fornecedor contiver a palavra "TOTVS". Devido à complexidade e quantidade de contratos diferentes da TOTVS, a tela muda para um gerenciador de Propostas/Contratos agrupados por Empresa.
- **Funcionalidade:** Permite adicionar contratos (com `código da proposta`, `código do fornecedor (planilha)`, `valor mensal` e `dia de vencimento`) diretamente associados a uma empresa.
- **Soft Delete:** Para evitar o erro de violação de chaves estrangeiras (`IntegrityError`) ao excluir contratos vinculados a NFs passadas, o botão de exclusão de contratos da TOTVS agora realiza um **Soft Delete** (`ativo = False`), ocultando o contrato do sistema sem quebrar os registros históricos.

### 2. Snapshotting Automático nas Notas Fiscais (12/Mai/2026)

**Problema:** Se um código de fornecedor fosse alterado no cadastro mestre, isso poderia reescrever os registros do passado, quebrando a contabilidade de meses fechados.

**Solução:** Implementada a lógica de "Fotografia" (Snapshot). A Nota Fiscal funciona como um registro imutável do que ocorreu naquele momento.

**Implementação:**
- Ao salvar/editar uma Nota Fiscal (`backend/routers/notas_fiscais.py`), o sistema não espera receber o `codigo_fornecedor` do FrontEnd.
- O sistema intercepta o salvamento e procura no Banco de Dados:
  1. É um contrato TOTVS especificado pelo usuário? Copia o `codigo_fornecedor` salvo dentro do contrato (Fotografia do Contrato).
  2. É um fornecedor comum? Copia o código diretamente do "Mapeamento Mestre" correspondente àquela empresa (Fotografia do Identificador).
- A interface da Nota Fiscal (`frontend/js/notas.js`) passou a ter o campo **"Cód. Forn." como ReadOnly (Apenas Leitura)**, servindo apenas de confirmação visual para o usuário de qual código será copiado pelo backend.

### 3. Novos Status para Lançamentos Mensais (11/Mai/2026)

**Problema:** Havia situações onde um lançamento mensal não deveria receber nota fiscal (ex: Junsoft/Torque Pneus em Jan/2026 não teve lançamento; TOTVS/Torque Diesel Grill a partir de maio terá cancelamentos).

**Solução:** Adicionados dois novos status na matriz de contratos (`LancamentoMensal.status`):
- `CANCELADO` — para NFs canceladas/transferidas
- `NAO_SE_APLICA` — para meses sem lançamento intencional
- **Bloqueio:** O backend impede o lançamento de Notas Fiscais nesses meses.
- **UI:** Exibição com cores distintas (`roxo` e `cinza`) na tabela "Contratos Mensais".

### 4. Cancelamentos TOTVS Programados (Maio 2026)

Com base nos registros reais, os seguintes contratos têm cancelamento programado:
- **AAJR37** (Transmite) — cancelamento 10/2026 — Ticket 27263881
- **AAMVUZ/02** (APP BackOffice Suprimentos) — cancelamento 10/2026 — Ticket 27263988
- **AAKUW5/10** (TEF/Conciliador) — cancelamento 05/2026 — Ticket 27264142/27264375
- **AANRDS/01** (Totvs Inteligência Tributária) — em análise — Ticket 27263793
- **354414/01** (Full) — cancelamento em análise — Ticket 27263655
- **Transferência 354970** (13 licenças para EMALTO foco Gestão Projetos) — Ticket 27277905

---

## Dicionário de Negócios & Alias

- **EIM:** Emalto Indústria (São a mesma empresa; EIM é utilizado nos sistemas internos e na Planilha).
- **Mapeamento Mestre:** A tabela central (Aba Cadastros Base) que substitui as antigas planilhas locais para ditar a relação "De/Para" entre Fornecedor e Empresa.
- **Lançamentos Mensais:** Os 12 "slots" gerados pela Matriz de Contratos (Janeiro a Dezembro) que aguardam o recebimento e vinculação de uma Nota Fiscal para passarem ao status "LANCADO".

---

## Estrutura de Diretórios e Arquivos Relevantes

- `backend/models.py`: Tabelas `ContratoSoftware`, `NotaFiscal`, `LancamentoMensal`, `FornecedorEmpresaIdentificador`.
- `backend/schemas.py`: Permite Nulls em propriedades `valor_mensal`, `dia_vencimento` para compatibilidade retroativa com dados TOTVS legados.
- `backend/routers/notas_fiscais.py`: Rotas CRUD. Responsável pelo **Snapshot** dos códigos de fornecedor e pela auto-vinculação.
- `backend/routers/contratos.py`: Rota de exclusão modificada para **Soft Delete** (`ativo = False`).
- `backend/services/vinculacao.py`: Serviço injetável que acopla ou desacopla a NF ao Lançamento da Matriz no mês correto, suportando múltiplas notas no mesmo slot.
- `frontend/js/cadastros.js`: Módulo visual que controla o De/Para e o CRUD de propostas TOTVS.
- `frontend/js/notas.js`: Formulário inteligente que esconde campos da TOTVS se não aplicável e traz informações visuais "ReadOnly" em tempo real.
